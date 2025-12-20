from models.user import User
from extensions import db

class Student(User):
    __mapper_args__ = {
        'polymorphic_identity': 'student'
    }
    
    def __init__(self, name, email, password=None, major=None, level=None):
        super().__init__(name=name, email=email, role='student', 
                        password=password, major=major, level=level)
    
    def enroll_course(self, course_id):
        """Enroll student in a course"""
        from models.enrollment import Enrollment
        from models.courses import Course
        
        course = Course.query.get(course_id)
        if not course:
            return False, "Course not found"
        
        # Check if already enrolled
        existing = Enrollment.query.filter_by(
            student_id=self.id, 
            course_id=course_id
        ).first()
        if existing:
            return False, "Already enrolled in this course"
        
        # Check if seats available
        if course.seats_left <= 0:
            return False, "No seats available"
        
        # Create enrollment
        enrollment = Enrollment(student_id=self.id, course_id=course_id)
        course.seats_left -= 1
        
        db.session.add(enrollment)
        db.session.commit()
        return True, "Enrolled successfully"
    
    def drop_course(self, course_id):
        """Drop a course"""
        from models.enrollment import Enrollment
        from models.courses import Course
        
        enrollment = Enrollment.query.filter_by(
            student_id=self.id, 
            course_id=course_id
        ).first()
        
        if not enrollment:
            return False, "Not enrolled in this course"
        
        course = Course.query.get(course_id)
        if course:
            course.seats_left += 1
        
        db.session.delete(enrollment)
        db.session.commit()
        return True, "Course dropped successfully"
    
    def get_enrolled_courses(self):
        from models.courses import Course
        from models.enrollment import Enrollment
        courses = []
        return Course.query.join(Enrollment).filter(Enrollment.student_id == self.id).all()
    
    def is_enrolled_in_course(self, course_id):
        from models.enrollment import Enrollment
        return Enrollment.query.filter_by(student_id=self.id, course_id=course_id).first() is not None

    def get_assignment_status(self, assignment_id):
        """Get submission status for a specific assignment"""
        from models.assignment import Assignment
        from models.submission import Submission
        
        assignment = Assignment.query.get(assignment_id)
        if not assignment:
            return {'submitted': False, 'grade': None, 'feedback': None}
        
        submission = Submission.query.filter_by(
            assignment_id=assignment_id,
            student_id=self.id
        ).first()
        
        if submission:
            return {
                'submitted': True,
                'grade': submission.grade,
                'feedback': submission.feedback,
                'submitted_at': submission.submitted_at
            }
        return {'submitted': False, 'grade': None, 'feedback': None}
    
    @staticmethod
    def get_by_id(student_id):
        return Student.query.filter_by(id=student_id, role='student').first()
    
    @staticmethod
    def get_all_students():
        return Student.query.filter_by(role='student').all()