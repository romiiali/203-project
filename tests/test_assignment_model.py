# tests/test_assignment.py
import pytest
from datetime import datetime, timedelta
from models.assignment import Assignment
from models.courses import Course
from models.submission import Submission
from models.user import User
from extensions import db

class TestAssignment:
    """Test cases for Assignment model"""
    
    def test_assignment_creation(self, init_database, test_course):
        """Test creating an assignment"""
        due_date = datetime.now() + timedelta(days=7)
        assignment = Assignment(
            title="Test Assignment",
            description="Complete this test assignment",
            due_date=due_date,
            course_id=test_course.id
        )
        
        db.session.add(assignment)
        db.session.commit()
        
        assert assignment.id is not None
        assert assignment.title == "Test Assignment"
        assert assignment.description == "Complete this test assignment"
        assert assignment.due_date == due_date
        assert assignment.course_id == test_course.id
        assert isinstance(assignment.created_at, datetime)
    
    def test_assignment_get_by_course(self, init_database, test_course):
        """Test getting assignments by course ID"""
        # Create multiple assignments with different due dates
        assignments_data = [
            ("Assignment 1", datetime.now() + timedelta(days=3)),
            ("Assignment 2", datetime.now() + timedelta(days=1)),
            ("Assignment 3", datetime.now() + timedelta(days=5)),
        ]
        
        for title, due_date in assignments_data:
            assignment = Assignment(
                title=title,
                description="Description",
                due_date=due_date,
                course_id=test_course.id
            )
            db.session.add(assignment)
        db.session.commit()
        
        # Get assignments for course
        assignments = Assignment.get_by_course(test_course.id)
        
        assert len(assignments) >= 3
        # Should be ordered by due_date ascending
        for i in range(len(assignments) - 1):
            assert assignments[i].due_date <= assignments[i + 1].due_date
    
    def test_assignment_get_by_id(self, test_assignment):
        """Test getting assignment by ID"""
        assignment = Assignment.get_by_id(test_assignment.id)
        
        assert assignment is not None
        assert assignment.id == test_assignment.id
        assert assignment.title == test_assignment.title
    
    def test_assignment_get_upcoming(self, init_database):
        """Test getting upcoming assignments"""
        # Create past, present, and future assignments
        past = Assignment(
            title="Past Assignment",
            description="Past",
            due_date=datetime.now() - timedelta(days=1),
            course_id=1
        )
        
        future = Assignment(
            title="Future Assignment",
            description="Future",
            due_date=datetime.now() + timedelta(days=1),
            course_id=1
        )
        
        db.session.add_all([past, future])
        db.session.commit()
        
        upcoming = Assignment.get_upcoming()
        
        # Only future assignments should be in upcoming
        assert any(a.id == future.id for a in upcoming)
        assert not any(a.id == past.id for a in upcoming)
    
    def test_add_submission(self, test_assignment, test_student):
        """Test adding a submission to an assignment"""
        # Add new submission
        success, message = test_assignment.add_submission(
            test_student.id,
            "My submission text"
        )
        
        assert success is True
        assert "added" in message.lower()
        
        # Verify submission was created
        submission = test_assignment.get_submission(test_student.id)
        assert submission is not None
        assert submission.submission_text == "My submission text"
        
        # Update existing submission
        success, message = test_assignment.add_submission(
            test_student.id,
            "Updated submission text"
        )
        
        assert success is True
        assert "updated" in message.lower()
        
        submission = test_assignment.get_submission(test_student.id)
        assert submission.submission_text == "Updated submission text"
    
    def test_grade_submission(self, test_assignment_with_submission):
        """Test grading a submission"""
        assignment, student = test_assignment_with_submission
        
        # Grade the submission
        success, message = assignment.grade_submission(
            student.id,
            95.5,
            "Excellent work!"
        )
        
        assert success is True
        assert "successfully" in message.lower()
        
        # Verify grade was set
        submission = assignment.get_submission(student.id)
        assert submission.grade == 95.5
        assert submission.feedback == "Excellent work!"
        
        # Test invalid grade
        success, message = assignment.grade_submission(
            student.id,
            105,  # Invalid grade > 100
            "Too high"
        )
        
        assert success is False
        assert "between 0 and 100" in message.lower()
        
        # Test invalid grade format
        success, message = assignment.grade_submission(
            student.id,
            "not a number",
            "Bad grade"
        )
        
        assert success is False
        assert "invalid" in message.lower()
    
    def test_get_all_submissions(self, test_assignment, test_students):
        """Test getting all submissions for an assignment"""
        # Add submissions from multiple students
        for i, student in enumerate(test_students[:3]):
            submission = Submission(
                submission_text=f"Submission from student {i}",
                assignment_id=test_assignment.id,
                student_id=student.id
            )
            db.session.add(submission)
        db.session.commit()
        
        # Get all submissions
        submissions = test_assignment.get_all_submissions()
        
        assert len(submissions) == 3
        
        for result in submissions:
            assert 'submission' in result
            assert 'student' in result
            assert 'grade' in result
            assert 'feedback' in result
            assert isinstance(result['submission'], Submission)
            assert isinstance(result['student'], User)
    
    def test_is_past_due(self, test_assignment):
        """Test checking if assignment is past due"""
        # Set future due date
        test_assignment.due_date = datetime.now() + timedelta(days=1)
        assert test_assignment.is_past_due() is False
        
        # Set past due date
        test_assignment.due_date = datetime.now() - timedelta(days=1)
        assert test_assignment.is_past_due() is True
    
    def test_to_dict(self, test_assignment):
        """Test converting assignment to dictionary"""
        assignment_dict = test_assignment.to_dict()
        
        assert isinstance(assignment_dict, dict)
        assert 'id' in assignment_dict
        assert 'title' in assignment_dict
        assert 'description' in assignment_dict
        assert 'due_date' in assignment_dict
        assert 'created_at' in assignment_dict
        assert 'course_id' in assignment_dict
        assert 'is_past_due' in assignment_dict
        assert 'time_remaining' in assignment_dict
        assert 'submission_count' in assignment_dict
        assert 'average_grade' in assignment_dict
        
        # Check ISO format dates
        assert 'T' in assignment_dict['due_date']  # ISO format indicator