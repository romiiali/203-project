# This should be renamed to instructor_model.py to avoid confusion with the Blueprint
from extensions import db
from models.user import User
from models.courses import Course
from models.enrollment import Enrollment

class Instructor:
    """Instructor model that works with the User model"""
    
    @staticmethod
    def get_by_id(instructor_id):
        """Get instructor by ID"""
        user = User.get_by_id(instructor_id)
        if user and user.role == 'instructor':
            return user
        return None
    
    @staticmethod
    def get_courses_taught(instructor_id):
        """Get all courses taught by this instructor"""
        return Course.query.filter_by(instructor_id=instructor_id).all()
    
    @staticmethod
    def get_students_in_course(course_code):
        """Get all students enrolled in a course taught by this instructor"""
        course = Course.get_by_code(course_code)
        if not course:
            return []
        return course.get_enrolled_students()
    
    @staticmethod
    def add_course(code, name, description=None, credits=3, max_seats=30, 
                   schedule="TBA", department="General"):
        """Add a new course (assuming current instructor is adding it)"""
        from flask import session
        instructor_id = session.get('user_id')
        
        if not instructor_id:
            return None
        
        course = Course(
            code=code,
            name=name,
            description=description,
            instructor_id=instructor_id,
            credits=credits,
            max_seats=max_seats,
            schedule=schedule,
            department=department
        )
        
        db.session.add(course)
        db.session.commit()
        return course
    
    @staticmethod
    def update_course(course_code, **kwargs):
        """Update course information"""
        course = Course.get_by_code(course_code)
        if not course:
            return False
        
        for key, value in kwargs.items():
            if hasattr(course, key) and value is not None:
                setattr(course, key, value)
        
        db.session.commit()
        return True
    
    @staticmethod
    def get_assignment_stats(course_code):
        """Get statistics for assignments in a course"""
        course = Course.get_by_code(course_code)
        if not course:
            return {}
        
        assignments = course.assignments
        stats = {
            'total_assignments': len(assignments),
            'assignments_with_submissions': 0,
            'average_grades': {}
        }
        
        for assignment in assignments:
            submissions = assignment.get_submissions()
            if submissions:
                stats['assignments_with_submissions'] += 1
                total_grade = sum(s.grade for s in submissions if s.grade)
                avg_grade = total_grade / len(submissions) if submissions else 0
                stats['average_grades'][assignment.title] = avg_grade
        
        return stats