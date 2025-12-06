class SimpleCourse:
    def __init__(self, course_code, name, TA, instructor, credits, seats):
        self.course_code = course_code
        self.name = name
        self.TA = TA
        self.credits = credits
        self.seats = seats
        self.instructor = instructor

    def get_all_courses(self):
        return [
            SimpleCourse("CS101", "Introduction to Computer Science", "John Smith", "Dr. Alice Johnson", 3, 30),
            SimpleCourse("MATH201", "Calculus I", "Emily Chen", "Dr. Robert Brown", 4, 25),
            SimpleCourse("PHY301", "Advanced Physics", "Mike Wilson", "Dr. Sarah Davis", 4, 20),
            SimpleCourse("ENG102", "English Composition", "Lisa Garcia", "Prof. James Miller", 3, 35),
            SimpleCourse("BIO150", "Biology Fundamentals", "David Lee", "Dr. Maria Garcia", 3, 28),
            SimpleCourse("CHEM210", "Organic Chemistry", "Anna Taylor", "Dr. Kevin Wilson", 4, 22),
            SimpleCourse("CS205", "Data Structures", "Chris Evans", "Dr. Jennifer Lopez", 3, 24),
            SimpleCourse("ART110", "Digital Art Design", "Sophia Martinez", "Prof. Daniel Kim", 2, 18)
        ]

    def get_course(self, course_code):
        courses_data = self.get_all_courses()
        for course in courses_data:
            if course.course_code == course_code:
                return course
        return None
    
    def add_course(self, course_code, name, TA, instructor, credits, seats):
        new_course = SimpleCourse(course_code, name, TA, instructor, credits, seats)
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


class EnhancedCourse:
    def __init__(self, id, code, name, description, instructor_id, credits, max_seats, schedule, department):
        self.id = id
        self.code = code
        self.name = name
        self.description = description
        self.instructor_id = instructor_id
        self.credits = credits
        self.max_seats = max_seats
        self.seats_left = max_seats
        self.schedule = schedule
        self.department = department
        self.announcements = []
        self.assignments = []
    
    @staticmethod
    def get_all():
        return [
            EnhancedCourse(1, "CSAI 203", "Introduction to Software Engineering", 
                          "Fundamental software engineering principles", 2, 3, 50, "Mon/Wed 10:00-11:30", "CSAI"),
            EnhancedCourse(2, "MATH 201", "Calculus II", 
                          "Continuation of Calculus I", 2, 4, 40, "Tue/Thu 9:00-10:30", "MATH"),
            EnhancedCourse(3, "ENG 150", "Academic Writing", 
                          "Academic writing and research skills", 2, 3, 35, "Mon/Wed 2:00-3:30", "ENG"),
            EnhancedCourse(4, "PHY 101", "Physics I: Mechanics", 
                          "Introductory mechanics course", 2, 4, 45, "Tue/Thu 11:00-12:30", "PHY")
        ]
    
    @staticmethod
    def get_by_id(course_id):
        for course in EnhancedCourse.get_all():
            if course.id == course_id:
                return course
        return None
    
    @staticmethod
    def search_courses(keyword="", department=""):
        courses = EnhancedCourse.get_all()
        filtered_courses = []
        
        for course in courses:
            if keyword and keyword.lower() not in course.name.lower() and keyword.lower() not in course.code.lower():
                continue
            if department and course.department != department:
                continue
            filtered_courses.append(course)
        
        return filtered_courses
    
    def add_announcement(self, title, content, poster_id):
        announcement = Announcement(len(self.announcements) + 1, title, content, poster_id, self.id)
        self.announcements.append(announcement)
        return announcement
    
    def get_announcements(self):
        return self.announcements
    
    def add_assignment(self, title, description, due_date):
        assignment = Assignment(len(self.assignments) + 1, title, description, due_date, self.id)
        self.assignments.append(assignment)
        return assignment
    
    def get_assignments(self):
        return self.assignments


class Announcement:
    def __init__(self, id, title, content, poster_id, course_id):
        self.id = id
        self.title = title
        self.content = content
        self.poster_id = poster_id
        self.course_id = course_id
        self.timestamp = "2023-10-15"


class Assignment:
    def __init__(self, id, title, description, due_date, course_id):
        self.id = id
        self.title = title
        self.description = description
        self.due_date = due_date
        self.course_id = course_id
        self.submissions = {}


class Course:
    def __init__(self, course_code=None, name=None, TA=None, instructor=None, credits=None, seats=None,
                 id=None, code=None, description=None, instructor_id=None, max_seats=None, schedule=None, department=None):
        
        if course_code is not None:
            self.course_code = course_code
            self.name = name
            self.TA = TA
            self.credits = credits
            self.seats = seats
            self.instructor = instructor
            self.id = hash(course_code)
            self.code = course_code
            self.description = f"Course: {name}"
            self.instructor_id = 1
            self.max_seats = seats
            self.seats_left = seats
            self.schedule = "TBA"
            self.department = "General"
        else:
            self.id = id
            self.code = code
            self.name = name
            self.description = description
            self.instructor_id = instructor_id
            self.credits = credits
            self.max_seats = max_seats
            self.seats_left = max_seats
            self.schedule = schedule
            self.department = department
            self.course_code = code
            self.TA = "TBA"
            self.instructor = f"Instructor #{instructor_id}"
            self.seats = max_seats
    
    @staticmethod
    def get_all():
        simple = SimpleCourse("", "", "", "", 0, 0)
        simple_courses = simple.get_all_courses()
        
        courses = []
        for i, sc in enumerate(simple_courses, 1):
            course = Course(
                course_code=sc.course_code,
                name=sc.name,
                TA=sc.TA,
                instructor=sc.instructor,
                credits=sc.credits,
                seats=sc.seats
            )
            course.id = i
            courses.append(course)
        return courses
    
    @staticmethod
    def get_by_code(course_code):
        simple = SimpleCourse("", "", "", "", 0, 0)
        sc = simple.get_course(course_code)
        if sc:
            course = Course(
                course_code=sc.course_code,
                name=sc.name,
                TA=sc.TA,
                instructor=sc.instructor,
                credits=sc.credits,
                seats=sc.seats
            )
            course.id = hash(course_code)
            return course
        return None
    
    @staticmethod
    def search_courses(search_term=""):
        simple = SimpleCourse("", "", "", "", 0, 0)
        simple_results = simple.search_courses(search_term)
        
        courses = []
        for i, sc in enumerate(simple_results, 1):
            course = Course(
                course_code=sc.course_code,
                name=sc.name,
                TA=sc.TA,
                instructor=sc.instructor,
                credits=sc.credits,
                seats=sc.seats
            )
            course.id = i
            courses.append(course)
        return courses