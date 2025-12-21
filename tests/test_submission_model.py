import pytest
from datetime import datetime
from models.submission import Submission
from models.assignment import Assignment
from models.courses import Course
from models.user import User
from extensions import db

class TestSubmissionModel:
    """Tests for Submission model"""
    
    def test_submission_creation(self, session_db):
        """Test creating a new submission"""
        # Create course, assignment, and student
        course = Course(code="CS101", name="CS 101")
        assignment = Assignment(
            title="HW1",
            description="Homework 1",
            due_date=datetime.now(),
            course_id=course.id
        )
        student = User(
            name="Student",
            email="student@test.com",
            role="student",
            password="password123"
        )
        
        session_db.add(course)
        session_db.add(assignment)
        session_db.add(student)
        session_db.commit()
        
        # Create submission
        submission = Submission(
            assignment_id=assignment.id,
            student_id=student.id,
            submission_text="My submission text",
            grade=85.5,
            feedback="Good work!"
        )
        
        session_db.add(submission)
        session_db.commit()
        
        assert submission.id is not None
        assert submission.submission_text == "My submission text"
        assert submission.grade == 85.5
        assert submission.feedback == "Good work!"
        assert submission.assignment_id == assignment.id
        assert submission.student_id == student.id
        assert submission.submitted_at is not None
    
    def test_submitted_at_default(self, session_db):
        """Test that submitted_at is set automatically"""
        course = Course(code="CS101", name="CS 101")
        assignment = Assignment(
            title="HW1",
            description="Homework 1",
            due_date=datetime.now(),
            course_id=course.id
        )
        student = User(
            name="Student",
            email="student@test.com",
            role="student",
            password="password123"
        )
        
        session_db.add(course)
        session_db.add(assignment)
        session_db.add(student)
        session_db.commit()
        
        submission = Submission(
            assignment_id=assignment.id,
            student_id=student.id,
            submission_text="Text"
        )
        session_db.add(submission)
        session_db.commit()
        
        assert submission.submitted_at is not None
    
    def test_grade_can_be_null(self, session_db):
        """Test that grade can be null (ungraded)"""
        course = Course(code="CS101", name="CS 101")
        assignment = Assignment(
            title="HW1",
            description="Homework 1",
            due_date=datetime.now(),
            course_id=course.id
        )
        student = User(
            name="Student",
            email="student@test.com",
            role="student",
            password="password123"
        )
        
        session_db.add(course)
        session_db.add(assignment)
        session_db.add(student)
        session_db.commit()
        
        submission = Submission(
            assignment_id=assignment.id,
            student_id=student.id,
            submission_text="Text",
            # grade is not set
        )
        session_db.add(submission)
        session_db.commit()
        
        assert submission.grade is None
    
    def test_feedback_can_be_null(self, session_db):
        """Test that feedback can be null"""
        course = Course(code="CS101", name="CS 101")
        assignment = Assignment(
            title="HW1",
            description="Homework 1",
            due_date=datetime.now(),
            course_id=course.id
        )
        student = User(
            name="Student",
            email="student@test.com",
            role="student",
            password="password123"
        )
        
        session_db.add(course)
        session_db.add(assignment)
        session_db.add(student)
        session_db.commit()
        
        submission = Submission(
            assignment_id=assignment.id,
            student_id=student.id,
            submission_text="Text",
            # feedback is not set
        )
        session_db.add(submission)
        session_db.commit()
        
        assert submission.feedback is None
    
    def test_unique_constraint(self, session_db):
        """Test that student can only submit once per assignment"""
        # Create course, assignment, and student
        course = Course(code="CS101", name="CS 101")
        assignment = Assignment(
            title="HW1",
            description="Homework 1",
            due_date=datetime.now(),
            course_id=course.id
        )
        student = User(
            name="Student",
            email="student@test.com",
            role="student",
            password="password123"
        )
        
        session_db.add(course)
        session_db.add(assignment)
        session_db.add(student)
        session_db.commit()
        
        # Create first submission
        submission1 = Submission(
            assignment_id=assignment.id,
            student_id=student.id,
            submission_text="First submission"
        )
        session_db.add(submission1)
        session_db.commit()
        
        # Try to create second submission (should violate unique constraint)
        submission2 = Submission(
            assignment_id=assignment.id,
            student_id=student.id,  # Same student and assignment
            submission_text="Second submission"
        )
        session_db.add(submission2)
        with pytest.raises(Exception):
            session_db.commit()
        
        session_db.rollback()
    
    def test_relationships(self, session_db):
        """Test submission relationships"""
        course = Course(code="CS101", name="CS 101")
        assignment = Assignment(
            title="HW1",
            description="Homework 1",
            due_date=datetime.now(),
            course_id=course.id
        )
        student = User(
            name="Student",
            email="student@test.com",
            role="student",
            password="password123"
        )
        
        session_db.add(course)
        session_db.add(assignment)
        session_db.add(student)
        session_db.commit()
        
        submission = Submission(
            assignment_id=assignment.id,
            student_id=student.id,
            submission_text="Text"
        )
        session_db.add(submission)
        session_db.commit()
        
        # Test relationships exist
        assert hasattr(submission, 'assignment')  # From backref
        assert hasattr(submission, 'student')  # From backref
    
    def test_foreign_key_constraints(self, session_db):
        """Test that submission requires valid assignment and student"""
        # Test with non-existent assignment
        submission1 = Submission(
            assignment_id=99999,  # Non-existent
            student_id=1,
            submission_text="Text"
        )
        session_db.add(submission1)
        with pytest.raises(Exception):
            session_db.commit()
        session_db.rollback()
        
        # Test with non-existent student
        course = Course(code="CS101", name="CS 101")
        assignment = Assignment(
            title="HW1",
            description="Homework 1",
            due_date=datetime.now(),
            course_id=course.id
        )
        session_db.add(course)
        session_db.add(assignment)
        session_db.commit()
        
        submission2 = Submission(
            assignment_id=assignment.id,
            student_id=99999,  # Non-existent
            submission_text="Text"
        )
        session_db.add(submission2)
        with pytest.raises(Exception):
            session_db.commit()
        
        session_db.rollback()
    
    def test_grade_update(self, session_db):
        """Test updating grade on a submission"""
        course = Course(code="CS101", name="CS 101")
        assignment = Assignment(
            title="HW1",
            description="Homework 1",
            due_date=datetime.now(),
            course_id=course.id
        )
        student = User(
            name="Student",
            email="student@test.com",
            role="student",
            password="password123"
        )
        
        session_db.add(course)
        session_db.add(assignment)
        session_db.add(student)
        session_db.commit()
        
        # Create submission without grade
        submission = Submission(
            assignment_id=assignment.id,
            student_id=student.id,
            submission_text="Text"
        )
        session_db.add(submission)
        session_db.commit()
        
        assert submission.grade is None
        
        # Update grade
        submission.grade = 90.0
        submission.feedback = "Excellent work!"
        session_db.commit()
        
        # Verify update
        updated = session_db.query(Submission).get(submission.id)
        assert updated.grade == 90.0
        assert updated.feedback == "Excellent work!"