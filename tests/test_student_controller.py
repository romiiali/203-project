import pytest
from unittest.mock import Mock, patch

class TestStudentController:
    """Tests for student_controller.py"""
    
    def test_dashboard_requires_login(self, client):
        """Test dashboard requires authentication"""
        response = client.get('/student/dashboard')
        assert response.status_code == 302
        assert '/login' in response.location
    
    @patch('controllers.student_controller.Student')
    def test_dashboard_success(self, mock_student, client, auth_client):
        """Test successful dashboard access"""
        auth_client.login_as('student', 4)
        
        # Mock student
        mock_student_instance = Mock()
        mock_student_instance.get_enrolled_courses.return_value = [
            Mock(id=1, name="Course 1"),
            Mock(id=2, name="Course 2")
        ]
        mock_student.get_by_id.return_value = mock_student_instance
        
        response = client.get('/student/dashboard')
        assert response.status_code == 200
    
    @patch('controllers.student_controller.Student')
    def test_view_courses(self, mock_student, client, auth_client):
        """Test viewing enrolled courses"""
        auth_client.login_as('student', 4)
        
        mock_student_instance = Mock()
        mock_student_instance.get_enrolled_courses.return_value = [
            Mock(id=1, name="Course 1")
        ]
        mock_student.get_by_id.return_value = mock_student_instance
        
        response = client.get('/student/courses')
        assert response.status_code == 200
    
    @patch('controllers.student_controller.Course')
    @patch('controllers.student_controller.Student')
    def test_search_courses(self, mock_student, mock_course, client, auth_client):
        """Test course search"""
        auth_client.login_as('student', 4)
        
        # Mock student
        mock_student_instance = Mock()
        mock_student_instance.get_enrolled_courses.return_value = [
            Mock(id=1, name="Enrolled Course")
        ]
        mock_student.get_by_id.return_value = mock_student_instance
        
        # Mock course search
        mock_course.search_courses.return_value = [
            Mock(id=1, name="Course 1"),
            Mock(id=2, name="Course 2")
        ]
        
        response = client.get('/student/search?keyword=math')
        assert response.status_code == 200
        mock_course.search_courses.assert_called_once_with('math')
    
    @patch('controllers.student_controller.Student')
    def test_enroll_course(self, mock_student, client, auth_client):
        """Test enrolling in a course"""
        auth_client.login_as('student', 4)
        
        mock_student_instance = Mock()
        mock_student_instance.enroll_course.return_value = (True, "Enrolled successfully")
        mock_student.get_by_id.return_value = mock_student_instance
        
        response = client.get('/student/enroll/1', follow_redirects=False)
        assert response.status_code == 302
        assert '/student/courses' in response.location
    
    @patch('controllers.student_controller.Student')
    def test_drop_course(self, mock_student, client, auth_client):
        """Test dropping a course"""
        auth_client.login_as('student', 4)
        
        mock_student_instance = Mock()
        mock_student_instance.drop_course.return_value = (True, "Dropped successfully")
        mock_student.get_by_id.return_value = mock_student_instance
        
        response = client.get('/student/drop/1', follow_redirects=False)
        assert response.status_code == 302
        assert '/student/courses' in response.location
    
    @patch('controllers.student_controller.Course')
    @patch('controllers.student_controller.Student')
    def test_view_course_details(self, mock_student, mock_course, client, auth_client):
        """Test viewing course details"""
        auth_client.login_as('student', 4)
        
        # Mock student
        mock_student_instance = Mock()
        mock_student_instance.is_enrolled_in_course.return_value = True
        mock_student.get_by_id.return_value = mock_student_instance
        
        # Mock course
        mock_course_instance = Mock()
        mock_course_instance.get_announcements.return_value = [
            Mock(title="Announcement 1")
        ]
        mock_course_instance.get_assignments.return_value = [
            Mock(id=1, title="Assignment 1")
        ]
        mock_course.get_by_id.return_value = mock_course_instance
        
        # Mock assignment status
        mock_student_instance.get_assignment_status.return_value = {
            'submitted': False,
            'grade': None
        }
        
        response = client.get('/student/course/1')
        assert response.status_code == 200
    
    @patch('controllers.student_controller.Assignment')
    @patch('controllers.student_controller.Course')
    @patch('controllers.student_controller.Student')
    def test_submit_assignment(self, mock_student, mock_course, mock_assignment, client, auth_client):
        """Test submitting an assignment"""
        auth_client.login_as('student', 4)
        
        # Mock assignment
        mock_assignment_instance = Mock()
        mock_assignment_instance.course_id = 1
        mock_assignment_instance.add_submission.return_value = (True, "Submitted successfully")
        mock_assignment.get_by_id.return_value = mock_assignment_instance
        
        # Mock course
        mock_course_instance = Mock()
        mock_course_instance.id = 1
        mock_course.get_by_id.return_value = mock_course_instance
        
        # Mock student
        mock_student_instance = Mock()
        mock_student_instance.id = 4
        mock_student_instance.is_enrolled_in_course.return_value = True
        mock_student.get_by_id.return_value = mock_student_instance
        
        data = {
            'submission_text': 'My submission text'
        }
        
        response = client.post('/student/assignment/1/submit', data=data, follow_redirects=False)
        assert response.status_code == 302
    
    @patch('controllers.student_controller.Student')
    def test_view_grades(self, mock_student, client, auth_client):
        """Test viewing grades"""
        auth_client.login_as('student', 4)
        
        # Mock student with enrolled courses and assignments
        mock_course = Mock()
        mock_course.name = "Math 101"
        
        mock_assignment = Mock()
        mock_assignment.title = "Homework 1"
        mock_assignment.get_submission.return_value = {'feedback': 'Good work!'}
        mock_course.get_assignments.return_value = [mock_assignment]
        
        mock_student_instance = Mock()
        mock_student_instance.get_enrolled_courses.return_value = [mock_course]
        mock_student_instance.get_assignment_status.return_value = {
            'submitted': True,
            'grade': 85
        }
        mock_student.get_by_id.return_value = mock_student_instance
        
        response = client.get('/student/grades')
        assert response.status_code == 200