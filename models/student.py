from models.user import User
from extensions import db
from models.enrollment import Enrollment

class Student(User):
    def __init__(self, id, name, email, major, level):
        self.id = id
        self.name = name
        self.email = email
        self.major = major
        self.level = level
    
    @staticmethod
    def get_by_id(student_id):
        """Get student by ID - query the database"""
        user = User.query.get(student_id)
        if user and user.role == 'student':
            # You might want to store major and level in User model or separate table
            return Student(user.id, user.name, user.email, "N/A", "N/A")
        return None
    
    @staticmethod
    def get_all_students():
        """Get all students"""
        users = User.query.filter_by(role='student').all()
        students = []
        for user in users:
            students.append(Student(user.id, user.name, user.email, "N/A", "N/A"))
        return students
    
    def get_enrolled_courses(self):
        """Get courses this student is enrolled in"""
        from models.courses import Course
        enrollments = Enrollment.query.filter_by(student_id=self.id).all()
        courses = []
        for enrollment in enrollments:
            course = Course.get_by_id(enrollment.course_id)
            if course:
                courses.append(course)
        return courses
    
    def is_enrolled_in_course(self, course_id):
        """Check if student is enrolled in a course"""
        enrollment = Enrollment.query.filter_by(
            student_id=self.id,
            course_id=course_id
        ).first()
        return enrollment is not None
    
    @staticmethod
    def search_students(query=""):
        """Search students by name or email"""
        users = User.query.filter(
            User.role == 'student',
            (User.name.ilike(f"%{query}%") | User.email.ilike(f"%{query}%"))
        ).all()
        
        students = []
        for user in users:
            students.append(Student(user.id, user.name, user.email, "N/A", "N/A"))
        return students