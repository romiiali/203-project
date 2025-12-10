import pytest
from models.courses import Course
from models.user import User
from models.enrollment import Enrollment
from extensions import db

class TestCourseModel:
    """Tests for Course model"""
    
    def test_course_creation(self, session_db):
        """Test creating a new course"""
        course = Course(
            code="CS101",
            name="Introduction to Computer Science",
            description="Basic CS concepts",
            credits=3,
            max_seats=30,
            schedule="MWF 10:00-11:00",
            department="Computer Science"
        )
        
        session_db.add(course)
        session_db.commit()
        
        assert course.id is not None
        assert course.code == "CS101"
        assert course.name == "Introduction to Computer Science"
        assert course.credits == 3
        assert course.max_seats == 30
        assert course.seats_left == 30  # Should match max_seats initially
        assert course.department == "Computer Science"
    
    def test_course_with_instructor(self, session_db):
        """Test creating course with instructor"""
        # Create instructor first
        instructor = User(
            name="Dr. Smith",
            email="smith@test.com",
            role="instructor",
            password="password123"
        )
        session_db.add(instructor)
        session_db.commit()
        
        # Create course with instructor
        course = Course(
            code="MATH101",
            name="Calculus I",
            instructor_id=instructor.id
        )
        session_db.add(course)
        session_db.commit()
        
        assert course.instructor_id == instructor.id
        assert course.instructor == instructor
    
    def test_course_with_ta(self, session_db):
        """Test creating course with TA"""
        # Create TA first
        ta = User(
            name="TA User",
            email="ta@test.com",
            role="ta",
            password="password123"
        )
        session_db.add(ta)
        session_db.commit()
        
        # Create course with TA
        course = Course(
            code="PHYS101",
            name="Physics I",
            ta_id=ta.id
        )
        session_db.add(course)
        session_db.commit()
        
        assert course.ta_id == ta.id
        assert course.ta == ta
    
    def test_get_all_courses(self, session_db):
        """Test getting all courses"""
        courses = [
            Course(code="CS101", name="CS 101"),
            Course(code="MATH101", name="Math 101"),
            Course(code="PHYS101", name="Physics 101")
        ]
        
        for course in courses:
            session_db.add(course)
        session_db.commit()
        
        all_courses = Course.get_all()
        assert len(all_courses) >= 3
    
    def test_get_by_id(self, session_db):
        """Test retrieving course by ID"""
        course = Course(code="TEST101", name="Test Course")
        session_db.add(course)
        session_db.commit()
        
        retrieved = Course.get_by_id(course.id)
        assert retrieved is not None
        assert retrieved.id == course.id
        assert retrieved.code == "TEST101"
    
    def test_get_by_code(self, session_db):
        """Test retrieving course by code"""
        course = Course(code="UNIQUE101", name="Unique Course")
        session_db.add(course)
        session_db.commit()
        
        retrieved = Course.get_by_code("UNIQUE101")
        assert retrieved is not None
        assert retrieved.code == "UNIQUE101"
    
    def test_search_courses_by_code(self, session_db):
        """Test searching courses by code"""
        course = Course(
            code="CS101",
            name="Computer Science 101",
            description="Intro to CS"
        )
        session_db.add(course)
        session_db.commit()
        
        results = Course.search_courses("CS101")
        assert len(results) >= 1
        assert any(course.code == "CS101" for course in results)
    
    def test_search_courses_by_name(self, session_db):
        """Test searching courses by name"""
        course = Course(
            code="MATH101",
            name="Calculus I",
            description="Differential calculus"
        )
        session_db.add(course)
        session_db.commit()
        
        results = Course.search_courses("Calculus")
        assert len(results) >= 1
        assert any("Calculus" in course.name for course in results)
    
    def test_search_courses_by_department(self, session_db):
        """Test searching courses by department"""
        course = Course(
            code="PHYS101",
            name="Physics I",
            department="Physics"
        )
        session_db.add(course)
        session_db.commit()
        
        results = Course.search_courses("Physics")
        assert len(results) >= 1
        assert any(course.department == "Physics" for course in results)
    
    def test_search_courses_by_instructor_name(self, session_db):
        """Test searching courses by instructor name"""
        # Create instructor
        instructor = User(
            name="Dr. Johnson",
            email="johnson@test.com",
            role="instructor",
            password="password123"
        )
        session_db.add(instructor)
        session_db.commit()
        
        # Create course with instructor
        course = Course(
            code="BIO101",
            name="Biology I",
            instructor_id=instructor.id
        )
        session_db.add(course)
        session_db.commit()
        
        results = Course.search_courses("Johnson")
        assert len(results) >= 1
    
    def test_search_courses_empty_term(self, session_db):
        """Test searching with empty term returns all"""
        courses = [
            Course(code="C1", name="Course 1"),
            Course(code="C2", name="Course 2")
        ]
        
        for course in courses:
            session_db.add(course)
        session_db.commit()
        
        results = Course.search_courses("")
        assert len(results) >= 2
    
    def test_get_enrolled_students(self, session_db):
        """Test getting enrolled students for a course"""
        # Create course
        course = Course(code="CS101", name="CS 101")
        session_db.add(course)
        
        # Create students
        student1 = User(
            name="Student1",
            email="student1@test.com",
            role="student",
            password="pass1"
        )
        student2 = User(
            name="Student2",
            email="student2@test.com",
            role="student",
            password="pass2"
        )
        session_db.add(student1)
        session_db.add(student2)
        session_db.commit()
        
        # Enroll students
        enrollment1 = Enrollment(student_id=student1.id, course_id=course.id)
        enrollment2 = Enrollment(student_id=student2.id, course_id=course.id)
        session_db.add(enrollment1)
        session_db.add(enrollment2)
        session_db.commit()
        
        # Get enrolled students
        enrolled = course.get_enrolled_students()
        assert len(enrolled) == 2
        assert all(student.role == "student" for student in enrolled)
    
    def test_enroll_student_success(self, session_db):
        """Test enrolling a student successfully"""
        # Create course with seats
        course = Course(code="CS101", name="CS 101", max_seats=2)
        session_db.add(course)
        
        # Create student
        student = User(
            name="Student",
            email="student@test.com",
            role="student",
            password="password123"
        )
        session_db.add(student)
        session_db.commit()
        
        # Enroll student
        result = course.enroll_student(student.id)
        assert result is True
        assert course.seats_left == 1
        
        # Verify enrollment exists
        enrollment = session_db.query(Enrollment).filter_by(
            student_id=student.id,
            course_id=course.id
        ).first()
        assert enrollment is not None
    
    def test_enroll_student_no_seats(self, session_db):
        """Test enrolling when no seats available"""
        # Create course with no seats
        course = Course(code="CS101", name="CS 101", max_seats=0)
        session_db.add(course)
        
        # Create student
        student = User(
            name="Student",
            email="student@test.com",
            role="student",
            password="password123"
        )
        session_db.add(student)
        session_db.commit()
        
        # Try to enroll
        result = course.enroll_student(student.id)
        assert result is False
        assert course.seats_left == 0
    
    def test_drop_student_success(self, session_db):
        """Test dropping a student successfully"""
        # Create course and student
        course = Course(code="CS101", name="CS 101", max_seats=2)
        student = User(
            name="Student",
            email="student@test.com",
            role="student",
            password="password123"
        )
        session_db.add(course)
        session_db.add(student)
        session_db.commit()
        
        # Enroll first
        enrollment = Enrollment(student_id=student.id, course_id=course.id)
        session_db.add(enrollment)
        course.seats_left = 1
        session_db.commit()
        
        # Drop student
        result = course.drop_student(student.id)
        assert result is True
        assert course.seats_left == 2
        
        # Verify enrollment removed
        enrollment = session_db.query(Enrollment).filter_by(
            student_id=student.id,
            course_id=course.id
        ).first()
        assert enrollment is None
    
    def test_drop_student_not_enrolled(self, session_db):
        """Test dropping student not enrolled"""
        course = Course(code="CS101", name="CS 101")
        student = User(
            name="Student",
            email="student@test.com",
            role="student",
            password="password123"
        )
        session_db.add(course)
        session_db.add(student)
        session_db.commit()
        
        result = course.drop_student(student.id)
        assert result is False
    
    def test_to_dict(self, session_db):
        """Test converting course to dictionary"""
        # Create instructor and TA
        instructor = User(
            name="Dr. Instructor",
            email="instructor@test.com",
            role="instructor",
            password="pass"
        )
        ta = User(
            name="TA Assistant",
            email="ta@test.com",
            role="ta",
            password="pass"
        )
        session_db.add(instructor)
        session_db.add(ta)
        session_db.commit()
        
        # Create course
        course = Course(
            code="CS101",
            name="CS 101",
            description="Test course",
            instructor_id=instructor.id,
            ta_id=ta.id,
            credits=3,
            max_seats=30,
            schedule="MWF 10:00",
            department="Computer Science"
        )
        session_db.add(course)
        session_db.commit()
        
        course_dict = course.to_dict()
        
        assert course_dict['id'] == course.id
        assert course_dict['code'] == "CS101"
        assert course_dict['name'] == "CS 101"
        assert course_dict['description'] == "Test course"
        assert course_dict['instructor'] == "Dr. Instructor"
        assert course_dict['instructor_id'] == instructor.id
        assert course_dict['ta'] == "TA Assistant"
        assert course_dict['ta_id'] == ta.id
        assert course_dict['credits'] == 3
        assert course_dict['seats'] == 30
        assert course_dict['max_seats'] == 30
        assert course_dict['schedule'] == "MWF 10:00"
        assert course_dict['department'] == "Computer Science"
    
    def test_to_dict_no_instructor_ta(self, session_db):
        """Test to_dict when no instructor or TA"""
        course = Course(
            code="CS101",
            name="CS 101"
        )
        session_db.add(course)
        session_db.commit()
        
        course_dict = course.to_dict()
        
        assert course_dict['instructor'] is None
        assert course_dict['instructor_id'] is None
        assert course_dict['ta'] is None
        assert course_dict['ta_id'] is None
    
    def test_relationships(self, session_db):
        """Test course relationships"""
        course = Course(code="CS101", name="CS 101")
        session_db.add(course)
        session_db.commit()
        
        # Test relationships exist
        assert hasattr(course, 'announcements')
        assert hasattr(course, 'assignments')
        assert hasattr(course, 'enrollments')
        assert hasattr(course, 'instructor')  # From backref
        assert hasattr(course, 'ta')  # From backref
    
    def test_unique_code_constraint(self, session_db):
        """Test that course code must be unique"""
        course1 = Course(code="DUPLICATE101", name="Course 1")
        course2 = Course(code="DUPLICATE101", name="Course 2")  # Same code
        
        session_db.add(course1)
        session_db.commit()
        
        # Second course with same code should raise integrity error
        session_db.add(course2)
        with pytest.raises(Exception):
            session_db.commit()
        
        session_db.rollback()
    
    def test_default_values(self, session_db):
        """Test default values for course"""
        course = Course(code="TEST101", name="Test Course")
        session_db.add(course)
        session_db.commit()
        
        assert course.credits == 3
        assert course.max_seats == 30
        assert course.seats_left == 30
        assert course.schedule == "TBA"
        assert course.department == "General"
        assert course.description == "Course: Test Course"