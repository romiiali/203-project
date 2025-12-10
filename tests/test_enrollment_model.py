import pytest
from models.enrollment import Enrollment
from models.courses import Course
from models.user import User
from extensions import db

class TestEnrollmentModel:
    """Tests for Enrollment model"""
    
    def test_enrollment_creation(self, session_db):
        """Test creating a new enrollment"""
        # Create course and student
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
    
    def test_enrolled_at_default(self, session_db):
        """Test that enrolled_at is set automatically"""
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
        
        enrollment = Enrollment(
            student_id=student.id,
            course_id=course.id
        )
        session_db.add(enrollment)
        session_db.commit()
        
        assert enrollment.enrolled_at is not None
    
    def test_unique_constraint(self, session_db):
        """Test that student can only enroll once per course"""
        # Create course and student
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
        
        # Create first enrollment
        enrollment1 = Enrollment(
            student_id=student.id,
            course_id=course.id
        )
        session_db.add(enrollment1)
        session_db.commit()
        
        # Try to create second enrollment (should violate unique constraint)
        enrollment2 = Enrollment(
            student_id=student.id,  # Same student
            course_id=course.id     # Same course
        )
        session_db.add(enrollment2)
        with pytest.raises(Exception):
            session_db.commit()
        
        session_db.rollback()
    
    def test_relationships(self, session_db):
        """Test enrollment relationships"""
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
        
        enrollment = Enrollment(
            student_id=student.id,
            course_id=course.id
        )
        session_db.add(enrollment)
        session_db.commit()
        
        # Test relationships exist
        assert hasattr(enrollment, 'course')  # From backref
        assert hasattr(enrollment, 'student')  # Should exist if relationship is defined
    
    def test_foreign_key_constraints(self, session_db):
        """Test that enrollment requires valid course and student"""
        # Test with non-existent student
        course = Course(code="CS101", name="CS 101")
        session_db.add(course)
        session_db.commit()
        
        enrollment1 = Enrollment(
            student_id=99999,  # Non-existent
            course_id=course.id
        )
        session_db.add(enrollment1)
        with pytest.raises(Exception):
            session_db.commit()
        session_db.rollback()
        
        # Test with non-existent course
        student = User(
            name="Student",
            email="student@test.com",
            role="student",
            password="password123"
        )
        session_db.add(student)
        session_db.commit()
        
        enrollment2 = Enrollment(
            student_id=student.id,
            course_id=99999  # Non-existent
        )
        session_db.add(enrollment2)
        with pytest.raises(Exception):
            session_db.commit()
        
        session_db.rollback()
    
    def test_enrollment_between_different_students_courses(self, session_db):
        """Test multiple enrollments between different students and courses"""
        # Create courses
        courses = [
            Course(code="CS101", name="CS 101"),
            Course(code="MATH101", name="Math 101")
        ]
        
        # Create students
        students = [
            User(name="Student1", email="s1@test.com", role="student", password="pass1"),
            User(name="Student2", email="s2@test.com", role="student", password="pass2")
        ]
        
        for course in courses:
            session_db.add(course)
        for student in students:
            session_db.add(student)
        session_db.commit()
        
        # Create enrollments
        enrollments = []
        for student in students:
            for course in courses:
                enrollment = Enrollment(
                    student_id=student.id,
                    course_id=course.id
                )
                enrollments.append(enrollment)
                session_db.add(enrollment)
        
        session_db.commit()
        
        # Should have 4 enrollments (2 students × 2 courses)
        all_enrollments = session_db.query(Enrollment).all()
        assert len(all_enrollments) == 4