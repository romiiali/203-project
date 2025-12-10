import pytest
from unittest.mock import Mock, patch
from models.ta import TA
from models.courses import Course
from models.assignment import Assignment

class TestTAModel:
    """Tests for TA model"""
    
    def test_ta_creation(self):
        """Test creating a TA instance"""
        ta = TA(
            id=3,
            name="Alex Chen",
            email="alex@ta.edu",
            password="pass123"
        )
        
        assert ta.id == 3
        assert ta.name == "Alex Chen"
        assert ta.email == "alex@ta.edu"
        assert ta.role == "ta"
        assert ta.assigned_courses == []
    
    def test_get_by_id_static(self):
        """Test getting TA by ID using static method"""
        ta = TA.get_by_id(3)
        assert ta is not None
        assert ta.id == 3
        assert ta.name == "Alex Chen"
        assert ta.email == "alex@ta.edu"
    
    def test_get_by_id_not_found(self):
        """Test getting non-existent TA"""
        ta = TA.get_by_id(999)
        assert ta is None
    
    def test_assign_to_course_success(self):
        """Test assigning TA to course"""
        ta = TA(3, "Alex", "alex@test.com", "pass")
        
        # Initially not assigned
        assert ta.assigned_courses == []
        
        # Assign to course
        result = ta.assign_to_course(101)
        
        assert result is True
        assert 101 in ta.assigned_courses
    
    def test_assign_to_course_already_assigned(self):
        """Test assigning to course already assigned"""
        ta = TA(3, "Alex", "alex@test.com", "pass")
        ta.assigned_courses = [101]
        
        # Try to assign again
        result = ta.assign_to_course(101)
        
        assert result is False
        assert len(ta.assigned_courses) == 1
    
    @patch('models.ta.Course')
    def test_get_assigned_courses(self, mock_course):
        """Test getting assigned courses"""
        # Mock course instances
        course1 = Mock()
        course1.id = 101
        course1.name = "CS101"
        
        course2 = Mock()
        course2.id = 102
        course2.name = "MATH101"
        
        mock_course.get_by_id.side_effect = lambda course_id: {
            101: course1,
            102: course2
        }.get(course_id)
        
        ta = TA(3, "Alex", "alex@test.com", "pass")
        ta.assigned_courses = [101, 102]
        
        courses = ta.get_assigned_courses()
        
        assert len(courses) == 2
        assert any(course.name == "CS101" for course in courses)
        assert any(course.name == "MATH101" for course in courses)
    
    @patch('models.ta.Assignment')
    def test_get_course_assignments(self, mock_assignment):
        """Test getting assignments for a course"""
        # Mock assignments
        assignment1 = Mock()
        assignment1.id = 201
        assignment1.title = "HW1"
        
        assignment2 = Mock()
        assignment2.id = 202
        assignment2.title = "HW2"
        
        mock_assignment.get_by_course.return_value = [assignment1, assignment2]
        
        ta = TA(3, "Alex", "alex@test.com", "pass")
        
        assignments = ta.get_course_assignments(101)
        
        assert len(assignments) == 2
        mock_assignment.get_by_course.assert_called_once_with(101)
    
    @patch('models.ta.Assignment')
    def test_get_submissions_for_assignment(self, mock_assignment):
        """Test getting submissions for an assignment"""
        # Mock assignment with submissions
        mock_assignment_instance = Mock()
        mock_assignment_instance.get_all_submissions.return_value = {
            1: {"grade": 85, "text": "Submission 1"},
            2: {"grade": 90, "text": "Submission 2"}
        }
        mock_assignment.get_by_id.return_value = mock_assignment_instance
        
        ta = TA(3, "Alex", "alex@test.com", "pass")
        
        submissions = ta.get_submissions_for_assignment(201)
        
        assert submissions is not None
        assert len(submissions) == 2
        mock_assignment.get_by_id.assert_called_once_with(201)
    
    @patch('models.ta.Assignment')
    def test_get_submissions_assignment_not_found(self, mock_assignment):
        """Test getting submissions for non-existent assignment"""
        mock_assignment.get_by_id.return_value = None
        
        ta = TA(3, "Alex", "alex@test.com", "pass")
        
        submissions = ta.get_submissions_for_assignment(999)
        
        assert submissions == {}