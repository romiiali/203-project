from .user import User
from .courses import Course

class Instructor(User):
    def __init__(self, id, name, email, password):
        super().__init__(id, name, email, password, "instructor")
        self.teaching_courses = []
    
    def assign_to_course(self, course_id):
        if course_id not in self.teaching_courses:
            self.teaching_courses.append(course_id)
            return True
        return False
    
    def get_teaching_courses(self):
        from courses import Course
        courses = []
        for course_id in self.teaching_courses:
            course = Course.get_by_id(course_id)
            if course:
                courses.append(course)
        return courses
    
    def create_assignment(self, course_id, title, description, due_date):
        from courses import Course
        course = Course.get_by_id(course_id)
        if course:
            return course.add_assignment(title, description, due_date)
        return None
    
    def create_announcement(self, course_id, title, content):
        from courses import Course
        course = Course.get_by_id(course_id)
        if course:
            return course.add_announcement(title, content, self.id)
        return None
    
    @staticmethod
    def get_by_id(instructor_id):
        instructors = [
            Instructor(2, "Dr. Sarah Johnson", "sarah@instructor.edu", "pass123")
        ]
        
        for instructor in instructors:
            if instructor.id == instructor_id:
                return instructor
        return None