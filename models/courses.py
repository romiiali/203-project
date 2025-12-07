from .user import User
from .student import Student

class Course:
    def __init__(self, id, code, name, description=None, instructor_id=None, ta_id=None, 
                 credits=3, max_seats=30, schedule="TBA", department="General"):
        self.id = id
        self.code = code
        self.name = name
        self.description = description or f"Course: {name}"
        self.instructor_id = instructor_id
        self.ta_id = ta_id
        self.credits = credits
        self.max_seats = max_seats
        self.seats_left = max_seats
        self.schedule = schedule
        self.department = department
        
        # Derived attributes for compatibility with old code
        self.course_code = code
        self.instructor = f"Instructor #{instructor_id}" if instructor_id else "Not Assigned"
        self.TA = f"TA #{ta_id}" if ta_id else "Not Assigned"
        self.seats = max_seats
        
        # Internal lists for announcements and assignments
        self.announcements = []
        self.assignments = []
        self.enrolled_students = []
    
    @staticmethod
    def get_all():
        """Get all courses in the system"""
        return [
            Course(1, "CS101", "Introduction to Computer Science", 
                  "Fundamentals of computer science and programming", 2, 3, 3, 30, "Mon/Wed 10:00-11:30", "CS"),
            Course(2, "MATH201", "Calculus I", 
                  "Introduction to differential and integral calculus", 2, 3, 4, 25, "Tue/Thu 9:00-10:30", "MATH"),
            Course(3, "PHY301", "Advanced Physics", 
                  "Advanced topics in classical and modern physics", 2, 3, 4, 20, "Mon/Wed 2:00-3:30", "PHY"),
            Course(4, "ENG102", "English Composition", 
                  "Academic writing and critical thinking skills", 2, 3, 3, 35, "Tue/Thu 1:00-2:30", "ENG"),
            Course(5, "BIO150", "Biology Fundamentals", 
                  "Introduction to biological concepts and principles", 2, 3, 3, 28, "Mon/Wed 11:00-12:30", "BIO"),
            Course(6, "CHEM210", "Organic Chemistry", 
                  "Structure, properties, and reactions of organic compounds", 2, 3, 4, 22, "Tue/Thu 10:00-11:30", "CHEM"),
            Course(7, "CS205", "Data Structures", 
                  "Fundamental data structures and algorithms", 2, 3, 3, 24, "Mon/Wed 3:00-4:30", "CS"),
            Course(8, "ART110", "Digital Art Design", 
                  "Introduction to digital art creation and design principles", 2, 3, 2, 18, "Tue/Thu 2:00-3:30", "ART"),
            Course(9, "CSAI203", "Introduction to Software Engineering", 
                  "Fundamental software engineering principles", 2, 3, 3, 50, "Mon/Wed 10:00-11:30", "CSAI"),
            Course(10, "MATH202", "Calculus II", 
                  "Continuation of Calculus I, covering techniques of integration", 2, 3, 4, 40, "Tue/Thu 9:00-10:30", "MATH"),
            Course(11, "ENG150", "Academic Writing", 
                  "Academic writing, research, and critical analysis", 2, 3, 3, 35, "Mon/Wed 2:00-3:30", "ENG"),
            Course(12, "PHY101", "Physics I: Mechanics", 
                  "An introductory course covering the principles of mechanics", 2, 3, 4, 45, "Tue/Thu 11:00-12:30", "PHY")
        ]
    
    @staticmethod
    def get_by_id(course_id):
        """Get a course by its ID"""
        for course in Course.get_all():
            if course.id == course_id:
                return course
        return None
    
    @staticmethod
    def get_by_code(course_code):
        """Get a course by its code (e.g., CS101)"""
        for course in Course.get_all():
            if course.code == course_code:
                return course
        return None
    
    @staticmethod
    def search_courses(search_term=""):
        """
        Search courses by code, name, instructor, or TA
        Supports both enhanced search and basic string matching
        """
        all_courses = Course.get_all()
        
        if not search_term or search_term.strip() == "":
            return all_courses
        
        search_term = search_term.lower().strip()
        matching_courses = []
        
        for course in all_courses:
            # Search in code
            if search_term in course.code.lower():
                matching_courses.append(course)
                continue
                
            # Search in name
            if search_term in course.name.lower():
                matching_courses.append(course)
                continue
                
            # Search in instructor info
            if course.instructor_id:
                from user import User
                instructor = User.get_by_id(course.instructor_id)
                if instructor and search_term in instructor.name.lower():
                    matching_courses.append(course)
                    continue
            
            # Search in TA info
            if course.ta_id:
                from user import User
                ta = User.get_by_id(course.ta_id)
                if ta and search_term in ta.name.lower():
                    matching_courses.append(course)
                    continue
            
            # Search in department
            if search_term in course.department.lower():
                matching_courses.append(course)
                continue
        
        return matching_courses
    
    @staticmethod
    def add_course(code, name, description, instructor_id, ta_id, credits, max_seats, schedule, department):
        """Create a new course and add it to the system"""
        # In a real system, this would generate a unique ID and save to database
        new_id = len(Course.get_all()) + 1
        new_course = Course(new_id, code, name, description, instructor_id, ta_id, 
                           credits, max_seats, schedule, department)
        # Note: In a real implementation, this would save to a database
        return new_course
    
    @staticmethod
    def edit_course(course_id, code=None, name=None, description=None, instructor_id=None, 
                   ta_id=None, credits=None, max_seats=None, schedule=None, department=None):
        """Edit an existing course"""
        course = Course.get_by_id(course_id)
        if not course:
            return None
        
        if code: course.code = code
        if name: course.name = name
        if description: course.description = description
        if instructor_id: course.instructor_id = instructor_id
        if ta_id: course.ta_id = ta_id
        if credits: course.credits = credits
        if max_seats: 
            course.max_seats = max_seats
            course.seats = max_seats
        if schedule: course.schedule = schedule
        if department: course.department = department
        
        # Update derived attributes
        course.course_code = course.code
        course.instructor = f"Instructor #{course.instructor_id}" if course.instructor_id else "Not Assigned"
        course.TA = f"TA #{course.ta_id}" if course.ta_id else "Not Assigned"
        
        return course
    
    @staticmethod
    def delete_course(course_id):
        """Delete a course from the system"""
        # In a real system, this would remove from database
        # For now, we'll just return success/failure
        course = Course.get_by_id(course_id)
        return course is not None
    
    def get_instructor(self):
        """Get the instructor object for this course"""
        if self.instructor_id:
            from user import User
            return User.get_by_id(self.instructor_id)
        return None
    
    def get_ta(self):
        """Get the TA object for this course"""
        if self.ta_id:
            from user import User
            return User.get_by_id(self.ta_id)
        return None
    
    def add_announcement(self, title, content, poster_id):
        """Add an announcement to this course"""
        from announcement import Announcement
        announcement = Announcement(len(self.announcements) + 1, title, content, poster_id, self.id)
        self.announcements.append(announcement)
        return announcement
    
    def get_announcements(self):
        """Get all announcements for this course"""
        # First check internal list, then fall back to static method
        if self.announcements:
            return self.announcements
        
        from announcement import Announcement
        return Announcement.get_by_course(self.id)
    
    def add_assignment(self, title, description, due_date):
        """Add an assignment to this course"""
        from assignment import Assignment
        assignment = Assignment(len(self.assignments) + 1, title, description, due_date, self.id)
        self.assignments.append(assignment)
        return assignment
    
    def get_assignments(self):
        """Get all assignments for this course"""
        # First check internal list, then fall back to static method
        if self.assignments:
            return self.assignments
        
        from assignment import Assignment
        return Assignment.get_by_course(self.id)
    
    def enroll_student(self, student_id):
        """Enroll a student in this course"""
        if student_id not in self.enrolled_students:
            if self.seats_left > 0:
                self.enrolled_students.append(student_id)
                self.seats_left -= 1
                return True, "Enrolled successfully"
            return False, "No seats available"
        return False, "Already enrolled in this course"
    
    def drop_student(self, student_id):
        """Drop a student from this course"""
        if student_id in self.enrolled_students:
            self.enrolled_students.remove(student_id)
            self.seats_left += 1
            return True, "Dropped successfully"
        return False, "Not enrolled in this course"
    
    def is_student_enrolled(self, student_id):
        """Check if a student is enrolled in this course"""
        return student_id in self.enrolled_students
    
    def get_enrolled_students(self):
        """Get list of enrolled student objects"""
        from student import Student
        enrolled = []
        for student_id in self.enrolled_students:
            student = Student.get_by_id(student_id)
            if student:
                enrolled.append(student)
        return enrolled
    
    def get_assignment_by_id(self, assignment_id):
        """Get a specific assignment by ID"""
        for assignment in self.get_assignments():
            if assignment.id == assignment_id:
                return assignment
        return None
    
    def get_announcement_by_id(self, announcement_id):
        """Get a specific announcement by ID"""
        for announcement in self.get_announcements():
            if announcement.id == announcement_id:
                return announcement
        return None
    
    def get_course_info(self):
        """Get comprehensive course information"""
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'instructor': self.get_instructor(),
            'ta': self.get_ta(),
            'credits': self.credits,
            'seats_left': self.seats_left,
            'max_seats': self.max_seats,
            'schedule': self.schedule,
            'department': self.department,
            'enrolled_count': len(self.enrolled_students),
            'announcements_count': len(self.get_announcements()),
            'assignments_count': len(self.get_assignments())
        }
    
    def __repr__(self):
        return f"Course({self.code}: {self.name})"