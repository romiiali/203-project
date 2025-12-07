<<<<<<< HEAD
from models.user import User

class Student(User):
    def __init__(self, id, name, email, password, major, level):
        super().__init__(id, name, email, password, "student")
        self.major = major
        self.level = level
        self.enrolled_courses = []
    
    def enroll_course(self, course_code):
        from models.courses import Course
        course = Course.get_by_code(course_code)
        
        if not course:
            return False, "Course not found"
        
        if course.seats_left <= 0:
            return False, "No seats available"
        
        if course_code in self.enrolled_courses:
            return False, "Already enrolled"
        
        self.enrolled_courses.append(course_code)
        course.seats_left -= 1
        return True, "Enrolled successfully"
    
    def drop_course(self, course_code):
        if course_code in self.enrolled_courses:
            self.enrolled_courses.remove(course_code)
            
            from models.courses import Course
            course = Course.get_by_code(course_code)
            if course:
                course.seats_left += 1
            return True, "Course dropped"
        return False, "Not enrolled in this course"
    
    def get_enrolled_courses(self):
        from models.courses import Course
        courses = []
        for course_code in self.enrolled_courses:
            course = Course.get_by_code(course_code)
            if course:
                courses.append(course)
        return courses
    
    @staticmethod
    def get_by_id(student_id):
        students = [
            Student(1, "John Doe", "john@student.edu", "pass123", "Computer Science", "Sophomore"),
            Student(2, "Jane Smith", "jane@student.edu", "pass123", "Mathematics", "Junior"),
            Student(3, "Mike Johnson", "mike@student.edu", "pass123", "Physics", "Freshman")
        ]
        
        for student in students:
            if student.id == student_id:
                return student
=======
from models.user import User

class Student(User):
    def __init__(self, id, name, email, password, major, level):
        super().__init__(id, name, email, password, "student")
        self.major = major
        self.level = level
        self.enrolled_courses = []
    
    def enroll_course(self, course_code):
        from models.courses import Course
        course = Course.get_by_code(course_code)
        
        if not course:
            return False, "Course not found"
        
        if course.seats_left <= 0:
            return False, "No seats available"
        
        if course_code in self.enrolled_courses:
            return False, "Already enrolled"
        
        self.enrolled_courses.append(course_code)
        course.seats_left -= 1
        return True, "Enrolled successfully"
    
    def drop_course(self, course_code):
        if course_code in self.enrolled_courses:
            self.enrolled_courses.remove(course_code)
            
            from models.courses import Course
            course = Course.get_by_code(course_code)
            if course:
                course.seats_left += 1
            return True, "Course dropped"
        return False, "Not enrolled in this course"
    
    def get_enrolled_courses(self):
        from models.courses import Course
        courses = []
        for course_code in self.enrolled_courses:
            course = Course.get_by_code(course_code)
            if course:
                courses.append(course)
        return courses
    
    @staticmethod
    def get_by_id(student_id):
        students = [
            Student(1, "John Doe", "john@student.edu", "pass123", "Computer Science", "Sophomore"),
            Student(2, "Jane Smith", "jane@student.edu", "pass123", "Mathematics", "Junior"),
            Student(3, "Mike Johnson", "mike@student.edu", "pass123", "Physics", "Freshman")
        ]
        
        for student in students:
            if student.id == student_id:
                return student
>>>>>>> 20617a8a8979aaf50a951e6b8ac6723f6f13f32b
        return None