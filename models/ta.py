from extensions import db
from models.user import User
from models.courses import Course

class TA(User):
    def __init__(self, id, name, email, password):
        super().__init__(id, name, email, password, "ta")
        self.assigned_courses = []
    
    def assign_to_course(self, course_id):
        from models.courses import Course
        if course_id not in self.assigned_courses:
            self.assigned_courses.append(course_id)
            return True
        return False
    
    def get_assigned_courses(self):
        from models.courses import Course
        courses = []
        for course_id in self.assigned_courses:
            course = Course.get_by_id(course_id)
            if course:
                courses.append(course)
        return courses
    
    def get_course_assignments(self, course_id):
        from models.assignment import Assignment
        assignments = Assignment.get_by_course(course_id)
        return assignments
    
    def get_submissions_for_assignment(self, assignment_id):
        from models.assignment import Assignment
        assignment = Assignment.get_by_id(assignment_id)
        if assignment:
            return assignment.get_all_submissions()
        return []
    
    @staticmethod
    def get_by_id(ta_id):
        """Get TA by ID - this should query the database"""
        # First check if user exists and is a TA
        user = User.query.get(ta_id)
        if user and user.role == 'ta':
            ta = TA(user.id, user.name, user.email, "")
            course = Course.query.filter_by(ta_id=ta_id).all()
            # You might want to load assigned courses from the database here
            return ta
        return None
    
    @staticmethod
    def get_all():
        """Get all TAs"""
        users = User.query.filter_by(role='ta').all()
        tas = []
        for user in users:
            tas.append(TA(user.id, user.name, user.email, ""))
        return tas