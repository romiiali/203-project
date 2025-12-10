import pytest
from unittest.mock import Mock, patch

class TestInstructorController:
    """Tests for instructor_controller.py"""
    
    def test_dashboard_requires_login(self, client):
        """Test dashboard requires authentication"""
        response = client.get('/instructor/dashboard')
        assert response.status_code == 302
        assert '/login' in response.location
    
    @patch('controllers.instructor_controller.Instructor')
    def test_dashboard_success(self, mock_instructor, client, auth_client):
        """Test successful dashboard access"""
        auth_client.login_as('instructor', 2)
        
        mock_instructor_instance = Mock()
        mock_instructor_instance.get_teaching_courses.return_value = [
            Mock(id=1, name="Course 1")
        ]
        mock_instructor.get_by_id.return_value = mock_instructor_instance
        
        response = client.get('/instructor/dashboard')
        assert response.status_code == 200
    
    @patch('controllers.instructor_controller.Course')
    @patch('controllers.instructor_controller.Instructor')
    def test_course_details(self, mock_instructor, mock_course, client, auth_client):
        """Test viewing course details"""
        auth_client.login_as('instructor', 2)
        
        # Mock instructor
        mock_instructor_instance = Mock()
        mock_instructor_instance.teaching_courses = [1, 2]
        mock_instructor.get_by_id.return_value = mock_instructor_instance
        
        # Mock course
        mock_course_instance = Mock()
        mock_course_instance.id = 1
        mock_course_instance.get_announcements.return_value = []
        mock_course_instance.get_assignments.return_value = []
        mock_course_instance.get_enrolled_students.return_value = []
        mock_course.get_by_id.return_value = mock_course_instance
        
        response = client.get('/instructor/course/1')
        assert response.status_code == 200
    
    @patch('controllers.instructor_controller.Course')
    def test_add_assignment(self, mock_course, client, auth_client):
        """Test adding an assignment"""
        auth_client.login_as('instructor', 2)
        
        # Mock course
        mock_course_instance = Mock()
        mock_course_instance.add_assignment.return_value = Mock()
        mock_course.get_by_id.return_value = mock_course_instance
        
        data = {
            'title': 'New Assignment',
            'description': 'Assignment description',
            'due_date': '2024-12-31'
        }
        
        response = client.post('/instructor/course/1/add_assignment', 
                              data=data, follow_redirects=False)
        assert response.status_code == 302
    
    @patch('controllers.instructor_controller.Assignment')
    @patch('controllers.instructor_controller.Course')
    def test_view_submissions(self, mock_course, mock_assignment, client, auth_client):
        """Test viewing assignment submissions"""
        auth_client.login_as('instructor', 2)
        
        # Mock assignment
        mock_assignment_instance = Mock()
        mock_assignment_instance.course_id = 1
        mock_assignment_instance.get_all_submissions.return_value = {
            4: {'grade': 85, 'feedback': 'Good', 'timestamp': '2024-01-01', 'text': 'Submission text'}
        }
        mock_assignment.get_by_id.return_value = mock_assignment_instance
        
        # Mock course
        mock_course_instance = Mock()
        mock_course.get_by_id.return_value = mock_course_instance
        
        # Mock student
        with patch('controllers.instructor_controller.Student') as mock_student:
            mock_student_instance = Mock()
            mock_student_instance.name = "Test Student"
            mock_student.get_by_id.return_value = mock_student_instance
            
            response = client.get('/instructor/assignment/1/submissions')
            assert response.status_code == 200