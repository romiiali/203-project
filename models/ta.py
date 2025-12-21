from models.user import User
from models.courses import Course
from extensions import db

class TA(User):
   
    
    def __init__(self, name, email, password=None, office=None, office_hours=None):
        super().__init__(name=name, email=email, role='ta', 
                        password=password, office=office, office_hours=office_hours)
    
    
    def assign_to_course(self, course_id):
        """Assign this TA to a course"""
        from models.courses import Course
        course = Course.query.get(course_id)
        if course:
            # Check if already assigned
            if course.ta_id == self.id:
                return False, "Already assigned to this course"
            
            # Assign TA to course
            course.ta_id = self.id
            db.session.commit()
            return True, "Assigned to course successfully"
        return False, "Course not found"
    
    def get_assigned_courses(self):
        """Get all courses this TA is assigned to"""
        from models.courses import Course
        return Course.query.filter_by(ta_id=self.id).all()
    
    def is_assigned_to_course(self, course_id):
        """Check if TA is assigned to a specific course"""
        from models.courses import Course
        course = Course.query.get(course_id)
        return course and course.ta_id == self.id
    
    def get_course_assignments(self, course_id):
        """Get assignments for a course (only if TA is assigned to it)"""
        from models.assignment import Assignment
        if self.is_assigned_to_course(course_id):
            return Assignment.query.filter_by(course_id=course_id).all()
        return []
    
    def get_submissions_for_assignment(self, assignment_id):
        from models.assignment import Assignment
        from models.submission import Submission
        # Get the assignment
        assignment = Assignment.query.get(assignment_id)
        if not assignment:
            return []
        
        # Check if TA is assigned to this course
        ta_course_ids = [course.id for course in self.assigned_courses]
        if assignment.course_id not in ta_course_ids:
            return []
        
        # Return all submissions for this assignment
        return Submission.query.filter_by(assignment_id=assignment_id).all()
    
    @staticmethod
    def get_by_id(ta_id):
        return TA.query.filter_by(id=ta_id, role='ta').first()
    
    @staticmethod
    def get_all():
        return TA.query.filter_by(role='ta').all()
    
    @property
    def assigned_courses(self):
        """Property alias for get_assigned_courses (for compatibility)"""
        return self.get_assigned_courses()
    
    def is_assigned_to_course(self, course_id):
        """Check if TA is assigned to a specific course"""
        course = Course.query.get(course_id)
        return course and course.ta_id == self.id