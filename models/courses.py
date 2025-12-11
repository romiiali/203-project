from extensions import db
from models.enrollment import Enrollment

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    credits = db.Column(db.Integer, nullable=False, default=3)
    max_seats = db.Column(db.Integer, nullable=False, default=30)
    seats_left = db.Column(db.Integer, nullable=False, default=30)
    schedule = db.Column(db.String(100))
    department = db.Column(db.String(100))
    
    # Foreign keys
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ta_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    announcements = db.relationship('Announcement', backref='course', cascade='all, delete-orphan')
    assignments = db.relationship('Assignment', backref='course', cascade='all, delete-orphan')
    enrollments = db.relationship('Enrollment', backref='course', cascade='all, delete-orphan')
    
    def __init__(self, code, name, description=None, instructor_id=None, ta_id=None, 
                 credits=3, max_seats=30, schedule="TBA", department="General"):
        self.code = code
        self.name = name
        self.description = description or f"Course: {name}"
        self.instructor_id = instructor_id
        self.ta_id = ta_id
        self.credits = credits
        self.max_seats = max_seats
        self.seats_left = max_seats
        self.schedule = schedule
        self.department = department
    
    @staticmethod
    def get_all():
        return Course.query.all()
    
    @staticmethod
    def get_by_id(course_id):
        return Course.query.get(course_id)

    @classmethod
    def get_courses_by_instructor(cls, instructor_name):
        return [cls(**data) for data in cls._courses_data if data['instructor'] == instructor_name]
    
    @staticmethod
    def get_by_code(course_code):
        return Course.query.filter_by(code=course_code).first()
    
    @staticmethod
    def search_courses(search_term=""):
        if not search_term:
            return Course.query.all()
        
        search = f"%{search_term}%"
        from models.user import User
        import sqlalchemy as sa
        
        return Course.query.filter(
            (Course.code.ilike(search)) |
            (Course.name.ilike(search)) |
            (Course.description.ilike(search)) |
            (Course.department.ilike(search)) |
            (sa.exists().where(
                (User.id == Course.instructor_id) & 
                (User.name.ilike(search))
            )) |
            (sa.exists().where(
                (User.id == Course.ta_id) & 
                (User.name.ilike(search))
            ))
        ).all()
    
    def get_enrolled_students(self):
        """Get enrolled students for this course"""
        from models.user import User
        return User.query.join(Enrollment).filter(
            Enrollment.course_id == self.id,
            User.role == 'student'
        ).all()
    
    def enroll_student(self, student_id):
        """Enroll a student in this course"""
        from models.enrollment import Enrollment
        if self.seats_left > 0:
            enrollment = Enrollment(student_id=student_id, course_id=self.id)
            db.session.add(enrollment)
            self.seats_left -= 1
            db.session.commit()
            return True
        return False
    
    def drop_student(self, student_id):
        """Drop a student from this course"""
        from models.enrollment import Enrollment
        enrollment = Enrollment.query.filter_by(student_id=student_id, course_id=self.id).first()
        if enrollment:
            db.session.delete(enrollment)
            self.seats_left += 1
            db.session.commit()
            return True
        return False
    
    def to_dict(self):
        """Convert course to dictionary"""
        instructor_name = None
        ta_name = None
        
        if self.instructor:
            instructor_name = self.instructor.name
        
        if self.ta:
            ta_name = self.ta.name
        
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'instructor': instructor_name,
            'instructor_id': self.instructor_id,
            'ta': ta_name,
            'ta_id': self.ta_id,
            'credits': self.credits,
            'seats': self.seats_left,
            'max_seats': self.max_seats,
            'schedule': self.schedule,
            'department': self.department
        }