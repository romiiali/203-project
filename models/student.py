from models.user import User

class Student(User):
    def __init__(self, id, name, email, password, major, level):
        super().__init__(id, name, email, password, "student")
        self.major = major
        self.level = level
        self.enrolled_courses = []
    
    def enroll_course(self, course_id):
        from models.courses import Course
        course = Course.get_by_id(course_id)
        
        if not course:
            return False, "Course not found"
        
        if course.seats_left <= 0:
            return False, "No seats available"
        
        if course_id in self.enrolled_courses:
            return False, "Already enrolled"
        
        self.enrolled_courses.append(course_id)
        course.enrolled_students.append(self.id)
        course.seats_left -= 1
        return True, "Enrolled successfully"
    
    def drop_course(self, course_id):
        if course_id in self.enrolled_courses:
            self.enrolled_courses.remove(course_id)
            
            from models.courses import Course
            course = Course.get_by_id(course_id)
            if course:
                if self.id in course.enrolled_students:
                    course.enrolled_students.remove(self.id)
                course.seats_left += 1
            return True, "Course dropped"
        return False, "Not enrolled in this course"
    
    def get_enrolled_courses(self):
        from models.courses import Course
        courses = []
        for course_id in self.enrolled_courses:
            course = Course.get_by_id(course_id)
            if course:
                courses.append(course)
        return courses
    
    def is_enrolled_in_course(self, course_id):
        return course_id in self.enrolled_courses
    
    def get_assignment_status(self, assignment_id):
        from models.assignment import Assignment
        assignment = Assignment.get_by_id(assignment_id)
        if assignment:
            return assignment.get_submission_status(self.id)
        return {'submitted': False, 'grade': None, 'timestamp': None}
    
    @staticmethod
    def get_by_id(student_id):
        students = [
            Student(1, "John Doe", "john@student.edu", "pass123", "Computer Science", "Sophomore"),
            Student(5, "Jane Smith", "jane@student.edu", "pass123", "Mathematics", "Junior"),
            Student(6, "Mike Johnson", "mike@student.edu", "pass123", "Physics", "Freshman")
        ]
        
        for student in students:
            if student.id == student_id:
                return student
        return None
    
    @staticmethod
    def get_all_students():
        return [
            Student(1, "John Doe", "john@student.edu", "pass123", "Computer Science", "Sophomore"),
            Student(5, "Jane Smith", "jane@student.edu", "pass123", "Mathematics", "Junior"),
            Student(6, "Mike Johnson", "mike@student.edu", "pass123", "Physics", "Freshman")
        ]