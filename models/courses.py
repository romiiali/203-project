from extensions import db
from models.announcement import Announcement
from models.assignment import Assignment
from models.enrollment import Enrollment
from models.submission import Submission
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
    instructor_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)

    ta_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=True)

    instructor = db.relationship('User',foreign_keys=[instructor_id],back_populates='courses_instructing')

    ta = db.relationship('User',foreign_keys=[ta_id],back_populates='courses_ta')
    
    # Relationships - Use string references
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
    
    @staticmethod
    def get_by_code(course_code):
        return Course.query.filter_by(code=course_code).first()
    
    @staticmethod
    def search_courses(search_term=""):
        from models.courses import Course
        if not search_term:
            return Course.query.all()
        
        search = f"%{search_term}%"
        from models.courses import Course
        
        return Course.query.filter(
            (Course.code.ilike(search)) |
            (Course.name.ilike(search)) |
            (Course.description.ilike(search)) |
            (Course.department.ilike(search))
        ).all()
    
    def get_enrolled_students(self):
        """Get enrolled students for this course"""
        from models.enrollment import Enrollment
        from models.user import User
        return db.session.query(User).join(Enrollment).filter(
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
    
    def get_announcements(self):
        """Get announcements for this course"""
        from models.announcement import Announcement
        return Announcement.query.filter_by(course_id=self.id).order_by(
            Announcement.created_at.desc()
        ).all()
    
    def get_assignments(self):
        """Get assignments for this course"""
        from models.assignment import Assignment
        return Assignment.query.filter_by(course_id=self.id).all()
    
    def get_ta(self):
        """Get TA assigned to this course"""
        from models.user import User
        return User.query.get(self.ta_id) if self.ta_id else None
    
    def get_instructor(self):
        """Get instructor teaching this course"""
        from models.user import User
        return User.query.get(self.instructor_id) if self.instructor_id else None
    
    def add_assignment(self, title, description, due_date):
        """Add assignment to course"""
        from models.assignment import Assignment
        assignment = Assignment(
            title=title,
            description=description,
            due_date=due_date,
            course_id=self.id
        )
        db.session.add(assignment)
        db.session.commit()
        return assignment
    
    def add_announcement(self, title, content, poster_id):
        """Add announcement to course"""
        from models.announcement import Announcement
        announcement = Announcement(
            title=title,
            content=content,
            poster_id=poster_id,
            course_id=self.id
        )
        db.session.add(announcement)
        db.session.commit()
        return announcement
    
    def to_dict(self):
        """Convert course to dictionary"""
        instructor_name = None
        ta_name = None
        
        instructor = self.get_instructor()
        ta = self.get_ta()
        
        if instructor:
            instructor_name = instructor.name
        
        if ta:
            ta_name = ta.name
        
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