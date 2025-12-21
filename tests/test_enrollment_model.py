import pytest
from datetime import datetime
from models.enrollment import Enrollment
from models.courses import Course
from models.user import User

class TestEnrollmentModel:
    """Tests for Enrollment model"""
    
    def test_enrollment_creation(self, session_db):
        """Test creating an enrollment"""
        # Create student and course first
        student = User(
            name="Test Student",
            email="student@test.com",
            role="student",
            password="password123"
        )
        
        instructor = User(
            name="Instructor",
            email="instructor@test.com",
            role="instructor",
            password="password123"
        )
        
        course = Course(
            code="CS101",
            name="Test Course",
            instructor_id=instructor.id
        )
        
        session_db.add(student)
        session_db.add(instructor)
        session_db.add(course)
        session_db.commit()
        
        # Create enrollment
        enrollment = Enrollment(
            student_id=student.id,
            course_id=course.id
        )
        
        session_db.add(enrollment)
        session_db.commit()
        
        assert enrollment.id is not None
        assert enrollment.student_id == student.id
        assert enrollment.course_id == course.id
        assert enrollment.enrolled_at is not None
    
    def test_unique_constraint(self, session_db):
        """Test that same student can't enroll twice"""
        student = User(
            name="Student",
            email="student@test.com",
            role="student",
            password="password123"
        )
        
        instructor = User(
            name="Instructor",
            email="instructor@test.com",
            role="instructor",
            password="password123"
        )
        
        course = Course(
            code="CS101",
            name="Test Course",
            instructor_id=instructor.id
        )
        
        session_db.add(student)
        session_db.add(instructor)
        session_db.add(course)
        session_db.commit()
        
        # First enrollment
        enrollment1 = Enrollment(
            student_id=student.id,
            course_id=course.id
        )
        session_db.add(enrollment1)
        session_db.commit()
        
        # Try second enrollment (should fail)
        enrollment2 = Enrollment(
            student_id=student.id,
            course_id=course.id
        )
        session_db.add(enrollment2)
        
        with pytest.raises(Exception):
            session_db.commit()
        
        session_db.rollback()
    
    def test_relationships(self, session_db):
        """Test enrollment relationships"""
        student = User(
            name="Student",
            email="student@test.com",
            role="student",
            password="password123"
        )
        
        instructor = User(
            name="Instructor",
            email="instructor@test.com",
            role="instructor",
            password="password123"
        )
        
        course = Course(
            code="CS101",
            name="Test Course",
            instructor_id=instructor.id
        )
        
        session_db.add(student)
        session_db.add(instructor)
        session_db.add(course)
        session_db.commit()
        
        enrollment = Enrollment(
            student_id=student.id,
            course_id=course.id
        )
        session_db.add(enrollment)
        session_db.commit()
        
        # Test relationships
        assert enrollment.enrolled_student is not None
        assert enrollment.enrolled_student.id == student.id
        
        assert enrollment.course is not None
        assert enrollment.course.id == course.id