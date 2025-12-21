from models.user import User
from extensions import db

class Instructor(User):
    
    
    def __init__(self, name, email, password=None, office=None, office_hours=None):
        super().__init__(name=name, email=email, role='instructor', 
                        password=password, office=office, office_hours=office_hours)
    
    def assign_to_course(self, course_id):
        """Assign this instructor to a course"""
        from models.courses import Course
        course = Course.query.get(course_id)
        if course:
            # Check if already assigned
            if course.instructor_id == self.id:
                return False, "Already assigned to this course"
            
            # Assign instructor to course
            course.instructor_id = self.id
            db.session.commit()
            return True, "Assigned to course successfully"
        return False, "Course not found"
    
    def get_teaching_courses(self):
        """Get all courses this instructor teaches"""
        from models.courses import Course
        return Course.query.filter_by(instructor_id=self.id).all()
    
    def create_assignment(self, course_id, title, description, due_date):
        """Create assignment for a course (if instructor teaches it)"""
        from models.courses import Course
        course = Course.query.get(course_id)
        if course and course.instructor_id == self.id:
            return course.add_assignment(title, description, due_date)
        return None
    
    def create_announcement(self, course_id, title, content):
        """Create announcement for a course (if instructor teaches it)"""
        from models.courses import Course
        course = Course.query.get(course_id)
        if course and course.instructor_id == self.id:
            return course.add_announcement(title, content, self.id)
        return None
    
    @staticmethod
    def get_by_id(instructor_id):
        """Get instructor by ID"""
        return Instructor.query.filter_by(id=instructor_id, role='instructor').first()
    
    @staticmethod
    def get_all():
        """Get all instructors"""
        return Instructor.query.filter_by(role='instructor').all()
    
    @property
    def teaching_courses_ids(self):
        """Get list of course IDs the instructor teaches (for compatibility)"""
        return [course.id for course in self.get_teaching_courses()]
    
    def is_teaching_course(self, course_id):
        """Check if instructor is teaching a specific course"""
        from models.courses import Course
        course = Course.query.get(course_id)
        return course and course.instructor_id == self.id