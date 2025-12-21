# tests/test_instructor_controller.py
import pytest
from unittest.mock import Mock, patch

class TestInstructorController:
    """Test cases for instructor controller"""
    
    @pytest.fixture
    def instructor_session(self, client):
        """Set up instructor session for testing"""
        with client.session_transaction() as session:
            session['user_id'] = 2
            session['role'] = 'instructor'
        return client
    
    def test_dashboard_requires_login(self, client):
        """Test instructor dashboard requires login"""
        response = client.get('/instructor/dashboard', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_dashboard_requires_instructor_role(self, client):
        """Test dashboard redirects when wrong role"""
        with client.session_transaction() as session:
            session['user_id'] = 1
            session['role'] = 'student'
        
        response = client.get('/instructor/dashboard', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location
    
    @patch('models.instructor.Instructor.get_by_id')
    def test_dashboard_success(self, mock_get_instructor, instructor_session):
        """Test instructor dashboard loads successfully"""
        mock_instructor = Mock()
        mock_instructor.get_teaching_courses.return_value = []
        mock_get_instructor.return_value = mock_instructor
        
        response = instructor_session.get('/instructor/dashboard')
        assert response.status_code == 200
        assert b'Dashboard' in response.data
    
    @patch('models.instructor.Instructor.get_by_id')
    @patch('models.courses.Course.get_by_id')
    @patch('models.instructor.Instructor.is_teaching_course')
    def test_course_details(self, mock_is_teaching, mock_get_course, mock_get_instructor, instructor_session):
        """Test viewing course details"""
        mock_instructor = Mock()
        mock_get_instructor.return_value = mock_instructor
        
        mock_course = Mock()
        mock_course.name = "CS101"
        mock_course.get_announcements.return_value = []
        mock_course.get_assignments.return_value = []
        mock_course.get_enrolled_students.return_value = []
        mock_get_course.return_value = mock_course
        
        mock_is_teaching.return_value = True
        
        response = instructor_session.get('/instructor/course/1')
        assert response.status_code == 200
        assert b'CS101' in response.data
    
    @patch('models.instructor.Instructor.get_by_id')
    @patch('models.courses.Course.get_by_id')
    @patch('models.instructor.Instructor.is_teaching_course')
    def test_course_details_not_teaching(self, mock_is_teaching, mock_get_course, mock_get_instructor, instructor_session):
        """Test viewing course when not teaching"""
        mock_instructor = Mock()
        mock_get_instructor.return_value = mock_instructor
        
        mock_course = Mock()
        mock_get_course.return_value = mock_course
        
        mock_is_teaching.return_value = False
        
        response = instructor_session.get('/instructor/course/1', follow_redirects=True)
        assert b"You don't teach this course" in response.data
    
    @patch('models.instructor.Instructor.get_by_id')
    @patch('models.courses.Course.get_by_id')
    @patch('models.instructor.Instructor.is_teaching_course')
    @patch('models.courses.Course.add_assignment')
    def test_add_assignment(self, mock_add_assignment, mock_is_teaching, 
                           mock_get_course, mock_get_instructor, instructor_session):
        """Test adding assignment"""
        mock_instructor = Mock()
        mock_get_instructor.return_value = mock_instructor
        
        mock_course = Mock()
        mock_course.id = 1
        mock_get_course.return_value = mock_course
        
        mock_is_teaching.return_value = True
        mock_assignment = Mock()
        mock_add_assignment.return_value = mock_assignment
        
        response = instructor_session.post('/instructor/course/1/add_assignment', data={
            'title': 'Homework 1',
            'description': 'Complete exercises',
            'due_date': '2024-12-31'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Assignment added successfully' in response.data
        mock_add_assignment.assert_called_with('Homework 1', 'Complete exercises', '2024-12-31')
    
    @patch('models.instructor.Instructor.get_by_id')
    @patch('models.courses.Course.get_by_id')
    @patch('models.instructor.Instructor.is_teaching_course')
    @patch('models.courses.Course.add_announcement')
    def test_add_announcement(self, mock_add_announcement, mock_is_teaching, 
                            mock_get_course, mock_get_instructor, instructor_session):
        """Test adding announcement"""
        mock_instructor = Mock()
        mock_get_instructor.return_value = mock_instructor
        
        mock_course = Mock()
        mock_course.id = 1
        mock_get_course.return_value = mock_course
        
        mock_is_teaching.return_value = True
        
        with instructor_session.session_transaction() as session:
            session['user_id'] = 2
        
        response = instructor_session.post('/instructor/course/1/add_announcement', data={
            'title': 'Important Update',
            'content': 'Exam date changed'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Announcement added successfully' in response.data
        mock_add_announcement.assert_called_with('Important Update', 'Exam date changed', 2)