from user import User

class TA(User):
    def __init__(self, id, name, email, password):
        super().__init__(id, name, email, password, "ta")
        self.assigned_courses = []
    
    def assign_to_course(self, course_id):
        if course_id not in self.assigned_courses:
            self.assigned_courses.append(course_id)
            return True
        return False
    
    def get_assigned_courses(self):
        from courses import EnhancedCourse
        courses = []
        for course_id in self.assigned_courses:
            course = EnhancedCourse.get_by_id(course_id)
            if course:
                courses.append(course)
        return courses
    
    def get_course_assignments(self, course_id):
        from assignment import Assignment
        assignments = Assignment.get_by_course(course_id)
        return assignments
    
    def get_submissions_for_assignment(self, assignment_id):
        from assignment import Assignment
        assignment = Assignment.get_by_id(assignment_id)
        if assignment:
            return assignment.get_all_submissions()
        return {}
    
    @staticmethod
    def get_by_id(ta_id):
        tas = [
            TA(3, "Alex Chen", "alex@ta.edu", "pass123")
        ]
        
        for ta in tas:
            if ta.id == ta_id:
                return ta
        return None