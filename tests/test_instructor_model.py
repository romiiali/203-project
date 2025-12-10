import pytest
from unittest.mock import Mock, patch
from models.instructor import Instructor
from models.courses import Course

class TestInstructorModel:
    """Tests for Instructor model"""
    
    def test_instructor_creation(self):
        """Test creating an instructor instance"""
        instructor = Instructor(
            id=2,
            name="Dr. Sarah Johnson",
            email="sarah@instructor.edu",
            password="pass123"
        )
        
        assert instructor.id == 2
        assert instructor.name == "Dr. Sarah Johnson"
        assert instructor.email == "sarah@instructor.edu"
        assert instructor.role == "instructor"
        assert instructor.teaching_courses == []
    
    def test_get_by_id_static(self):
        """Test getting instructor by ID using static method"""
        instructor = Instructor.get_by_id(2)
        assert instructor is not None
        assert instructor.id == 2
        assert instructor.name == "Dr. Sarah Johnson"
        assert instructor.email == "sarah@instructor.edu"
    
    def test_get_by_id_not_found(self):
        """Test getting non-existent instructor"""
        instructor = Instructor.get_by_id(999)
        assert instructor is None
    
    def test_assign_to_course_success(self):
        """Test assigning instructor to course"""
        instructor = Instructor(2, "Dr. Smith", "smith@test.com", "pass")
        
        # Initially not assigned
        assert instructor.teaching_courses == []
        
        # Assign to course
        result = instructor.assign_to_course(101)
        
        assert result is True
        assert 101 in instructor.teaching_courses
    
    def test_assign_to_course_already_assigned(self):
        """Test assigning to course already assigned"""
        instructor = Instructor(2, "Dr. Smith", "smith@test.com", "pass")
        instructor.teaching_courses = [101]
        
        # Try to assign again
        result = instructor.assign_to_course(101)
        
        assert result is False
        assert len(instructor.teaching_courses) == 1
    
    @patch('models.instructor.Course')
    def test_get_teaching_courses(self, mock_course):
        """Test getting teaching courses"""
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
        
        instructor = Instructor(2, "Dr. Smith", "smith@test.com", "pass")
        instructor.teaching_courses = [101, 102]
        
        courses = instructor.get_teaching_courses()
        
        assert len(courses) == 2
        assert any(course.name == "CS101" for course in courses)
        assert any(course.name == "MATH101" for course in courses)
    
    @patch('models.instructor.Course')
    def test_create_assignment_success(self, mock_course):
        """Test creating assignment for course"""
        # Mock course
        mock_course_instance = Mock()
        mock_course_instance.add_assignment.return_value = Mock()
        mock_course.get_by_id.return_value = mock_course_instance
        
        instructor = Instructor(2, "Dr. Smith", "smith@test.com", "pass")
        
        assignment = instructor.create_assignment(
            course_id=101,
            title="HW1",
            description="Homework 1",
            due_date="2024-12-31"
        )
        
        assert assignment is not None
        mock_course_instance.add_assignment.assert_called_once_with(
            "HW1", "Homework 1", "2024-12-31"
        )
    
    @patch('models.instructor.Course')
    def test_create_assignment_course_not_found(self, mock_course):
        """Test creating assignment for non-existent course"""
        mock_course.get_by_id.return_value = None
        
        instructor = Instructor(2, "Dr. Smith", "smith@test.com", "pass")
        
        assignment = instructor.create_assignment(
            course_id=999,
            title="HW1",
            description="Homework 1",
            due_date="2024-12-31"
        )
        
        assert assignment is None
    
    @patch('models.instructor.Course')
    def test_create_announcement_success(self, mock_course):
        """Test creating announcement for course"""
        # Mock course
        mock_course_instance = Mock()
        mock_course_instance.add_announcement.return_value = Mock()
        mock_course.get_by_id.return_value = mock_course_instance
        
        instructor = Instructor(2, "Dr. Smith", "smith@test.com", "pass")
        
        announcement = instructor.create_announcement(
            course_id=101,
            title="Important",
            content="Class cancelled"
        )
        
        assert announcement is not None
        mock_course_instance.add_announcement.assert_called_once_with(
            "Important", "Class cancelled", instructor.id
        )
    
    @patch('models.instructor.Course')
    def test_create_announcement_course_not_found(self, mock_course):
        """Test creating announcement for non-existent course"""
        mock_course.get_by_id.return_value = None
        
        instructor = Instructor(2, "Dr. Smith", "smith@test.com", "pass")
        
        announcement = instructor.create_announcement(
            course_id=999,
            title="Important",
            content="Class cancelled"
        )
        
        assert announcement is None