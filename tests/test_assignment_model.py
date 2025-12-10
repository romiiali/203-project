import pytest
from datetime import datetime
from models.assignment import Assignment
from models.courses import Course
from models.user import User
from models.submission import Submission
from extensions import db

class TestAssignmentModel:
    """Tests for Assignment model"""
    
    def test_assignment_creation(self, session_db):
        """Test creating a new assignment"""
        # Create course first
        course = Course(code="CS101", name="CS 101")
        session_db.add(course)
        session_db.commit()
        
        # Create assignment
        assignment = Assignment(
            title="Homework 1",
            description="Complete exercises 1-10",
            due_date=datetime(2024, 12, 31, 23, 59, 59),
            course_id=course.id
        )
        
        session_db.add(assignment)
        session_db.commit()
        
        assert assignment.id is not None
        assert assignment.title == "Homework 1"
        assert assignment.description == "Complete exercises 1-10"
        assert assignment.course_id == course.id
        assert assignment.course == course
    
    def test_get_by_course(self, session_db):
        """Test getting assignments by course"""
        # Create course
        course = Course(code="CS101", name="CS 101")
        session_db.add(course)
        session_db.commit()
        
        # Create assignments for the course
        assignments = [
            Assignment(title="HW1", description="HW1 desc", due_date=datetime.now(), course_id=course.id),
            Assignment(title="HW2", description="HW2 desc", due_date=datetime.now(), course_id=course.id),
            Assignment(title="HW3", description="HW3 desc", due_date=datetime.now(), course_id=course.id)
        ]
        
        for assignment in assignments:
            session_db.add(assignment)
        session_db.commit()
        
        # Get assignments for course
        course_assignments = Assignment.get_by_course(course.id)
        assert len(course_assignments) == 3
        assert all(assignment.course_id == course.id for assignment in course_assignments)
    
    def test_get_by_id(self, session_db):
        """Test retrieving assignment by ID"""
        # Create course and assignment
        course = Course(code="CS101", name="CS 101")
        session_db.add(course)
        session_db.commit()
        
        assignment = Assignment(
            title="Test Assignment",
            description="Test description",
            due_date=datetime.now(),
            course_id=course.id
        )
        session_db.add(assignment)
        session_db.commit()
        
        retrieved = Assignment.get_by_id(assignment.id)
        assert retrieved is not None
        assert retrieved.id == assignment.id
        assert retrieved.title == "Test Assignment"
    
    def test_add_submission(self, session_db):
        """Test adding a submission to an assignment"""
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
        
        # Add submission
        result = assignment.add_submission(student.id, "My submission text")
        assert result is True
        
        # Verify submission was created
        submission = session_db.query(Submission).filter_by(
            assignment_id=assignment.id,
            student_id=student.id
        ).first()
        assert submission is not None
        assert submission.submission_text == "My submission text"
    
    def test_get_submission(self, session_db):
        """Test getting submission for a specific student"""
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
            submission_text="My answer"
        )
        session_db.add(submission)
        session_db.commit()
        
        # Get submission
        result = assignment.get_submission(student.id)
        assert result is not None
        assert result.submission_text == "My answer"
        assert result.assignment_id == assignment.id
        assert result.student_id == student.id
    
    def test_get_submission_none(self, session_db):
        """Test getting submission when none exists"""
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
        
        # Get submission (should be None)
        result = assignment.get_submission(student.id)
        assert result is None
    
    def test_get_all_submissions(self, session_db):
        """Test getting all submissions for an assignment"""
        # Create course and assignment
        course = Course(code="CS101", name="CS 101")
        assignment = Assignment(
            title="HW1",
            description="Homework 1",
            due_date=datetime.now(),
            course_id=course.id
        )
        session_db.add(course)
        session_db.add(assignment)
        
        # Create multiple students and submissions
        students = []
        for i in range(3):
            student = User(
                name=f"Student{i}",
                email=f"student{i}@test.com",
                role="student",
                password="password123"
            )
            students.append(student)
            session_db.add(student)
        
        session_db.commit()
        
        # Create submissions
        for student in students:
            submission = Submission(
                assignment_id=assignment.id,
                student_id=student.id,
                submission_text=f"Submission from {student.name}"
            )
            session_db.add(submission)
        
        session_db.commit()
        
        # Get all submissions
        submissions = assignment.get_all_submissions()
        assert len(submissions) == 3
    
    def test_get_all_submissions_empty(self, session_db):
        """Test getting submissions when none exist"""
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
        
        submissions = assignment.get_all_submissions()
        assert len(submissions) == 0
    
    def test_created_at_default(self, session_db):
        """Test that created_at is set automatically"""
        course = Course(code="CS101", name="CS 101")
        session_db.add(course)
        session_db.commit()
        
        assignment = Assignment(
            title="Test",
            description="Test",
            due_date=datetime.now(),
            course_id=course.id
        )
        session_db.add(assignment)
        session_db.commit()
        
        assert assignment.created_at is not None
    
    def test_relationships(self, session_db):
        """Test assignment relationships"""
        course = Course(code="CS101", name="CS 101")
        assignment = Assignment(
            title="Test",
            description="Test",
            due_date=datetime.now(),
            course_id=course.id
        )
        session_db.add(course)
        session_db.add(assignment)
        session_db.commit()
        
        # Test relationships exist
        assert hasattr(assignment, 'submissions')
        assert hasattr(assignment, 'course')  # From backref
    
    def test_foreign_key_constraint(self, session_db):
        """Test that assignment requires valid course"""
        assignment = Assignment(
            title="Test",
            description="Test",
            due_date=datetime.now(),
            course_id=99999  # Non-existent course
        )
        
        session_db.add(assignment)
        with pytest.raises(Exception):
            session_db.commit()
        
        session_db.rollback()