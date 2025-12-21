import pytest
from unittest.mock import Mock, patch

class TestTAController:
    """Tests for TA_controller.py"""
    
    def test_dashboard_requires_login(self, client):
        """Test dashboard requires authentication"""
        response = client.get('/ta/dashboard')
        assert response.status_code == 302
        assert '/login' in response.location
    
    @patch('controllers.TA_controller.TA')
    def test_dashboard_success(self, mock_ta, client, auth_client):
        """Test successful dashboard access"""
        auth_client.login_as('ta', 3)
        
        mock_ta_instance = Mock()
        mock_ta_instance.get_assigned_courses.return_value = [
            Mock(id=1, name="Course 1")
        ]
        mock_ta.get_by_id.return_value = mock_ta_instance
        
        response = client.get('/ta/dashboard')
        assert response.status_code == 200
    
    @patch('controllers.TA_controller.Course')
    def test_search_course(self, mock_course, client, auth_client):
        """Test course search"""
        auth_client.login_as('ta', 3)
        
        mock_course.search_courses.return_value = [
            Mock(id=1, name="Course 1")
        ]
        
        data = {'query': 'math'}
        response = client.post('/ta/search_course', data=data, follow_redirects=True)
        assert response.status_code == 200
    
    @patch('controllers.TA_controller.User')
    def test_search_student(self, mock_user, client, auth_client):
        """Test student search"""
        auth_client.login_as('ta', 3)
        
        # Mock user search results
        mock_student = Mock()
        mock_student.role = 'student'
        mock_user.search_users.return_value = [mock_student]
        
        data = {'query': 'john'}
        response = client.post('/ta/search_student', data=data, follow_redirects=True)
        assert response.status_code == 200
    
    @patch('controllers.TA_controller.Course')
    def test_course_details(self, mock_course, client, auth_client):
        """Test viewing course details"""
        auth_client.login_as('ta', 3)
        
        mock_course_instance = Mock()
        mock_course.get_by_id.return_value = mock_course_instance
        
        # Mock student
        with patch('controllers.TA_controller.Student') as mock_student:
            mock_student.get_all_students.return_value = [
                Mock(id=4, name="Student 1")
            ]
            
            response = client.get('/ta/course/1')
            assert response.status_code == 200
    
    @patch('controllers.TA_controller.Assignment')
    def test_view_submissions(self, mock_assignment, client, auth_client):
        """Test viewing assignment submissions"""
        auth_client.login_as('ta', 3)
        
        mock_assignment_instance = Mock()
        mock_assignment_instance.get_all_submissions.return_value = {
            4: {'grade': None, 'feedback': None, 'timestamp': '2024-01-01', 'text': 'Submission'}
        }
        mock_assignment.get_by_id.return_value = mock_assignment_instance
        
        # Mock student
        with patch('controllers.TA_controller.Student') as mock_student:
            mock_student_instance = Mock()
            mock_student_instance.name = "Test Student"
            mock_student.get_by_id.return_value = mock_student_instance
            
            response = client.get('/ta/assignment/1/submissions')
            assert response.status_code == 200
    
    @patch('controllers.TA_controller.Assignment')
    def test_submit_grade(self, mock_assignment, client, auth_client):
        """Test submitting a grade"""
        auth_client.login_as('ta', 3)
        
        mock_assignment_instance = Mock()
        mock_assignment_instance.grade_submission.return_value = (True, "Graded successfully")
        mock_assignment.get_by_id.return_value = mock_assignment_instance
        
        data = {
            'assignment_id': '1',
            'grade': '90',
            'feedback': 'Good work!'
        }
        
        response = client.post('/ta/submission/4/grade', data=data, follow_redirects=False)
        assert response.status_code == 302