class Course:
    def __init__(self, course_code, name, TA, instructor,credits,seats):
        self.course_code = course_code
        self.name=name
        self.TA = TA
        self.credits=credits
        self.seats=seats
        self.instructor = instructor

    def get_all_courses(self):
        return[
            Course("CS101", "Introduction to Computer Science", "John Smith", "Dr. Alice Johnson", 3, 30),
            Course("MATH201", "Calculus I", "Emily Chen", "Dr. Robert Brown", 4, 25),
            Course("PHY301", "Advanced Physics", "Mike Wilson", "Dr. Sarah Davis", 4, 20),
            Course("ENG102", "English Composition", "Lisa Garcia", "Prof. James Miller", 3, 35),
            Course("BIO150", "Biology Fundamentals", "David Lee", "Dr. Maria Garcia", 3, 28),
            Course("CHEM210", "Organic Chemistry", "Anna Taylor", "Dr. Kevin Wilson", 4, 22),
            Course("CS205", "Data Structures", "Chris Evans", "Dr. Jennifer Lopez", 3, 24),
            Course("ART110", "Digital Art Design", "Sophia Martinez", "Prof. Daniel Kim", 2, 18)
        ]

    def get_course(self,course_code):
        courses_data = self.get_all_courses()
        for course in courses_data:
            if course.course_code == course_code:
                return course
        return None
    
    def add_course(self, course_code, name, TA, instructor, credits, seats):
        new_course = Course(course_code, name, TA, instructor, credits, seats)
        courses_data = self.get_all_courses()
        courses_data.append(new_course)
        return courses_data
    
    def edit_course(self, course_code, name, TA, instructor, credits, seats):
        courses_data = self.get_all_courses()
        for course in courses_data:
            if course.course_code == course_code:
                course.name = name
                course.TA = TA
                course.instructor = instructor
                course.credits = credits
                course.seats = seats
                return course
        return None

    def delete_course(self, course_code):
        courses_data = self.get_all_courses()
        for course in courses_data:
            if course.course_code == course_code:
                courses_data.remove(course)
                return courses_data
        return None
    
    def search_courses(self, search_term=""):
        all_courses = self.get_all_courses()

        if not search_term or search_term.strip() == "":
            return all_courses
        
        search_term = search_term.lower().strip()
        matching_courses = []
        
        for course in all_courses:
            if (search_term in course.course_code.lower() or 
                search_term in course.name.lower() or 
                search_term in course.instructor.lower() or
                search_term in course.TA.lower()):
                matching_courses.append(course)
        
        return matching_courses
