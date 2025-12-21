# tests/test_submission.py
import pytest
from datetime import datetime
from models.submission import Submission
from models.assignment import Assignment
from models.user import User
from extensions import db

class TestSubmission:
    """Test cases for Submission model"""
    
    def test_submission_creation(self, init_database, test_assignment, test_student):
        """Test creating a submission"""
        submission = Submission(
            submission_text="This is my submission",
            assignment_id=test_assignment.id,
            student_id=test_student.id,
            grade=85.5,
            feedback="Good work!"
        )
        
        db.session.add(submission)
        db.session.commit()
        
        assert submission.id is not None
        assert submission.submission_text == "This is my submission"
        assert submission.assignment_id == test_assignment.id
        assert submission.student_id == test_student.id
        assert submission.grade == 85.5
        assert submission.feedback == "Good work!"
        assert isinstance(submission.submitted_at, datetime)
    
    def test_unique_constraint(self, init_database, test_assignment, test_student):
        """Test unique constraint on assignment-student combination"""
        # Create first submission
        submission1 = Submission(
            submission_text="First submission",
            assignment_id=test_assignment.id,
            student_id=test_student.id
        )
        db.session.add(submission1)
        db.session.commit()
        
        # Try to create duplicate submission
        submission2 = Submission(
            submission_text="Second submission",
            assignment_id=test_assignment.id,
            student_id=test_student.id
        )
        db.session.add(submission2)
        
        with pytest.raises(Exception):  # Should raise integrity error
            db.session.commit()
        
        db.session.rollback()
    
    def test_submission_grade_range(self, test_submission):
        """Test that grade can be within valid range"""
        submission = test_submission
        
        # Test valid grades
        submission.grade = 0.0
        assert submission.grade == 0.0
        
        submission.grade = 100.0
        assert submission.grade == 100.0
        
        submission.grade = 50.5
        assert submission.grade == 50.5
    
    def test_submission_optional_fields(self, init_database, test_assignment, test_student):
        """Test that grade and feedback are optional"""
        submission = Submission(
            submission_text="Submission without grade",
            assignment_id=test_assignment.id,
            student_id=test_student.id
            # No grade or feedback
        )
        
        db.session.add(submission)
        db.session.commit()
        
        assert submission.grade is None
        assert submission.feedback is None
    
    def test_submission_required_fields(self, init_database):
        """Test that required fields cannot be null"""
        submission = Submission()
        
        with pytest.raises(Exception):
            db.session.add(submission)
            db.session.commit()