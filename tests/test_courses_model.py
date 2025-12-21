import pytest
from models.courses import Course
from models.user import User
from extensions import db

class TestCourseModel:
    """Tests for Course model"""
    
    def test_course_creation(self, session_db):
        """Test creating a new course"""
        # First create an instructor
        instructor = User(
            name="Dr. Instructor",
            email="instructor@test.com",
            role="instructor",
            password="password123"
        )
        session_db.add(instructor)
        session_db.commit()
        
        # Create course
        course = Course(
            code="CS101",
            name="Intro to Computer Science",
            description="Introduction to programming",
            instructor_id=instructor.id,
            credits=3,
            max_seats=30
        )
        
        session_db.add(course)
        session_db.commit()
        
        assert course.id is not None
        assert course.code == "CS101"
        assert course.name == "Intro to Computer Science"
        assert course.instructor_id == instructor.id
        assert course.seats_left == 30
        assert course.max_seats == 30
    
    def test_get_all_courses(self, session_db):
        """Test getting all courses"""
        # Create some courses
        instructor = User(
            name="Instructor",
            email="instructor@test.com",
            role="instructor",
            password="password123"
        )
        session_db.add(instructor)
        session_db.commit()
        
        courses = [
            Course(code="CS101", name="CS 101", instructor_id=instructor.id),
            Course(code="MATH101", name="Math 101", instructor_id=instructor.id),
        ]
        
        for course in courses:
            session_db.add(course)
        session_db.commit()
        
        all_courses = Course.get_all()
        assert len(all_courses) >= 2
    
    def test_search_courses(self, session_db):
        """Test searching courses"""
        instructor = User(
            name="Instructor",
            email="instructor@test.com",
            role="instructor",
            password="password123"
        )
        session_db.add(instructor)
        session_db.commit()
        
        course = Course(
            code="CS301",
            name="Advanced Programming",
            description="Python and algorithms",
            department="Computer Science",
            instructor_id=instructor.id
        )
        session_db.add(course)
        session_db.commit()
        
        # Search by code
        results = Course.search_courses("CS301")
        assert len(results) >= 1
        assert any(c.code == "CS301" for c in results)
        
        # Search by name
        results = Course.search_courses("Advanced")
        assert len(results) >= 1
        assert any("Advanced" in c.name for c in results)
        
        # Search by department
        results = Course.search_courses("Computer")
        assert len(results) >= 1
        assert any("Computer" in c.department for c in results)
    
    def test_enroll_student(self, session_db):
        """Test enrolling a student in a course"""
        # Create instructor
        instructor = User(
            name="Instructor",
            email="instructor@test.com",
            role="instructor",
            password="password123"
        )
        
        # Create student
        student = User(
            name="Student",
            email="student@test.com",
            role="student",
            password="password123"
        )
        
        # Create course
        course = Course(
            code="CS101",
            name="Test Course",
            instructor_id=instructor.id,
            max_seats=5
        )
        
        session_db.add(instructor)
        session_db.add(student)
        session_db.add(course)
        session_db.commit()
        
        # Initially 5 seats left
        assert course.seats_left == 5
        
        # Enroll student
        result = course.enroll_student(student.id)
        assert result is True
        assert course.seats_left == 4
        
        # Verify enrollment exists
        from models.enrollment import Enrollment
        enrollment = Enrollment.query.filter_by(
            student_id=student.id,
            course_id=course.id
        ).first()
        assert enrollment is not None
    
    def test_course_full(self, session_db):
        """Test enrolling when course is full"""
        instructor = User(
            name="Instructor",
            email="instructor@test.com",
            role="instructor",
            password="password123"
        )
        
        course = Course(
            code="CS101",
            name="Full Course",
            instructor_id=instructor.id,
            max_seats=0  # No seats
        )
        
        student = User(
            name="Student",
            email="student@test.com",
            role="student",
            password="password123"
        )
        
        session_db.add(instructor)
        session_db.add(course)
        session_db.add(student)
        session_db.commit()
        
        result = course.enroll_student(student.id)
        assert result is False  # Should fail
        assert course.seats_left == 0