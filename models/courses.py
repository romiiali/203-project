from extensions import db
from models.enrollment import Enrollment
from models.user import User

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
        """Get all courses"""
        return Course.query.all()
    
    @staticmethod
    def get_by_id(course_id):
        """Get course by ID"""
        return Course.query.get(course_id)
    
    @staticmethod
    def get_course_by_id(course_code):
        """Get course by code (for compatibility with instructor routes)"""
        return Course.query.filter_by(code=course_code).first()
    
    @staticmethod
    def get_courses_by_instructor(instructor_name):
        """Get courses by instructor name"""
        # First find the instructor user by name
        instructor = User.query.filter_by(
            name=instructor_name, 
            role='instructor'
        ).first()
        
        if instructor:
            return Course.query.filter_by(instructor_id=instructor.id).all()
        return []
    
    @staticmethod
    def get_by_code(course_code):
        """Get course by code"""
        return Course.query.filter_by(code=course_code).first()
    
    @staticmethod
    def search_courses(search_term=""):
        """Search courses by various criteria"""
        if not search_term:
            return Course.query.all()
        
        search = f"%{search_term}%"
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
        return User.query.join(Enrollment).filter(
            Enrollment.course_id == self.id,
            User.role == 'student'
        ).all()
    
    def enroll_student(self, student_id):
        """Enroll a student in this course"""
        # Check if student is already enrolled
        existing = Enrollment.query.filter_by(
            student_id=student_id, 
            course_id=self.id
        ).first()
        
        if existing:
            return False  # Already enrolled
        
        if self.seats_left > 0:
            enrollment = Enrollment(student_id=student_id, course_id=self.id)
            db.session.add(enrollment)
            self.seats_left -= 1
            db.session.commit()
            return True
        return False
    
    def drop_student(self, student_id):
        """Drop a student from this course"""
        enrollment = Enrollment.query.filter_by(
            student_id=student_id, 
            course_id=self.id
        ).first()
        
        if enrollment:
            db.session.delete(enrollment)
            self.seats_left = min(self.max_seats, self.seats_left + 1)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def edit_course(course_code, name, ta_name, instructor_name, credits, seats):
        """Edit course details - for compatibility with instructor routes"""
        course = Course.query.filter_by(code=course_code).first()
        if not course:
            return False
        
        course.name = name
        course.credits = int(credits)
        course.max_seats = int(seats)
        course.seats_left = min(course.seats_left, int(seats))
        
        # Find TA by name
        if ta_name:
            ta = User.query.filter_by(name=ta_name, role='ta').first()
            course.ta_id = ta.id if ta else None
        
        # Find instructor by name (optional - might not want to change instructor)
        if instructor_name:
            instructor = User.query.filter_by(
                name=instructor_name, 
                role='instructor'
            ).first()
            course.instructor_id = instructor.id if instructor else course.instructor_id
        
        db.session.commit()
        return True
    
    @staticmethod
    def add_course(code, name, description=None, instructor_id=None, ta_id=None, 
                   credits=3, max_seats=30, schedule="TBA", department="General"):
        """Add a new course"""
        # Check if course code already exists
        existing = Course.query.filter_by(code=code).first()
        if existing:
            return None
        
        course = Course(
            code=code,
            name=name,
            description=description,
            instructor_id=instructor_id,
            ta_id=ta_id,
            credits=credits,
            max_seats=max_seats,
            schedule=schedule,
            department=department
        )
        
        db.session.add(course)
        db.session.commit()
        return course
    
    @staticmethod
    def delete_course(course_id):
        """Delete a course"""
        course = Course.query.get(course_id)
        if course:
            db.session.delete(course)
            db.session.commit()
            return True
        return False
    
    def get_announcements(self):
        """Get all announcements for this course"""
        return self.announcements
    
    def get_assignments(self):
        """Get all assignments for this course"""
        return self.assignments
    
    def get_instructor(self):
        """Get the instructor for this course"""
        if self.instructor_id:
            return User.query.get(self.instructor_id)
        return None
    
    def get_ta(self):
        """Get the TA for this course"""
        if self.ta_id:
            return User.query.get(self.ta_id)
        return None
    
    def is_enrolled(self, student_id):
        """Check if a student is enrolled in this course"""
        enrollment = Enrollment.query.filter_by(
            student_id=student_id,
            course_id=self.id
        ).first()
        return enrollment is not None
    
    def get_enrollment_count(self):
        """Get the number of enrolled students"""
        return self.max_seats - self.seats_left
    
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
            'department': self.department,
            'enrollment_count': self.get_enrollment_count()
        }
    
    def __repr__(self):
        return f'<Course {self.code}: {self.name}>'