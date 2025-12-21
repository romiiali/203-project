# tests/test_ta_controller.py
import pytest
from unittest.mock import Mock, patch

class TestTAController:
    """Test cases for TA controller"""
    
    @pytest.fixture
    def ta_session(self, client):
        """Set up TA session for testing"""
        with client.session_transaction() as session:
            session['user_id'] = 3
            session['role'] = 'ta'
        return client
    
    def test_dashboard_requires_login(self, client):
        """Test TA dashboard requires login"""
        response = client.get('/ta/dashboard', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location
    
    @patch('models.ta.TA.get_by_id')
    def test_dashboard_success(self, mock_get_ta, ta_session):
        """Test TA dashboard loads successfully"""
        mock_ta = Mock()
        mock_ta.get_assigned_courses.return_value = []
        mock_get_ta.return_value = mock_ta
        
        response = ta_session.get('/ta/dashboard')
        assert response.status_code == 200
        assert b'Dashboard' in response.data
    
    @patch('models.ta.TA.get_by_id')
    @patch('models.courses.Course.search_courses')
    def test_search_course_post(self, mock_search_courses, mock_get_ta, ta_session):
        """Test course search via POST"""
        mock_ta = Mock()
        mock_get_ta.return_value = mock_ta
        
        mock_course = Mock()
        mock_course.name = "Database Systems"
        mock_search_courses.return_value = [mock_course]
        
        response = ta_session.post('/ta/search_course', data={
            'query': 'Database'
        })
        
        assert response.status_code == 200
        assert b'Database Systems' in response.data
    
    @patch('models.ta.TA.get_by_id')
    @patch('models.user.User.search_users')
    def test_search_student(self, mock_search_users, mock_get_ta, ta_session):
        """Test student search"""
        mock_ta = Mock()
        mock_get_ta.return_value = mock_ta
        
        mock_student = Mock()
        mock_student.name = "John Doe"
        mock_student.role = "student"
        mock_search_users.return_value = [mock_student]
        
        response = ta_session.post('/ta/search_student', data={
            'query': 'John'
        })
        
        assert response.status_code == 200
        assert b'John Doe' in response.data
    
    @patch('models.ta.TA.get_by_id')
    @patch('models.courses.Course.get_by_id')
    @patch('models.ta.TA.is_assigned_to_course')
    def test_course_details(self, mock_is_assigned, mock_get_course, mock_get_ta, ta_session):
        """Test viewing course details as TA"""
        mock_ta = Mock()
        mock_get_ta.return_value = mock_ta
        
        mock_course = Mock()
        mock_course.name = "CS101"
        mock_course.get_enrolled_students.return_value = []
        mock_get_course.return_value = mock_course
        
        mock_is_assigned.return_value = True
        
        response = ta_session.get('/ta/course/1')
        assert response.status_code == 200
        assert b'CS101' in response.data
    
    @patch('models.ta.TA.get_by_id')
    @patch('models.assignment.Assignment.get_by_id')
    @patch('models.courses.Course.get_by_id')
    @patch('models.ta.TA.is_assigned_to_course')
    def test_view_submissions(self, mock_is_assigned, mock_get_course, 
                            mock_get_assignment, mock_get_ta, ta_session):
        """Test viewing assignment submissions"""
        mock_ta = Mock()
        mock_get_ta.return_value = mock_ta
        
        mock_assignment = Mock()
        mock_assignment.title = "Homework 1"
        mock_assignment.course_id = 1
        mock_assignment.get_all_submissions.return_value = []
        mock_get_assignment.return_value = mock_assignment
        
        mock_course = Mock()
        mock_course.id = 1
        mock_get_course.return_value = mock_course
        
        mock_is_assigned.return_value = True
        
        response = ta_session.get('/ta/assignment/1/submissions')
        assert response.status_code == 200
        assert b'Homework 1' in response.data
        assert b'Submissions' in response.data
    
    @patch('models.ta.TA.get_by_id')
    @patch('models.submission.Submission.query')
    @patch('models.assignment.Assignment.get_by_id')
    @patch('models.courses.Course.get_by_id')
    @patch('models.ta.TA.is_assigned_to_course')
    @patch('models.assignment.Assignment.grade_submission')
    def test_submit_grade(self, mock_grade_submission, mock_is_assigned, mock_get_course,
                         mock_get_assignment, mock_query, mock_get_ta, ta_session):
        """Test grading a submission"""
        mock_ta = Mock()
        mock_get_ta.return_value = mock_ta
        
        mock_submission = Mock()
        mock_submission.id = 1
        mock_submission.student_id = 5
        mock_submission.assignment_id = 1
        
        mock_filter = Mock()
        mock_filter.first.return_value = mock_submission
        mock_query.get.return_value = mock_submission
        
        mock_assignment = Mock()
        mock_assignment.course_id = 1
        mock_get_assignment.return_value = mock_assignment
        
        mock_course = Mock()
        mock_course.id = 1
        mock_get_course.return_value = mock_course
        
        mock_is_assigned.return_value = True
        mock_grade_submission.return_value = (True, "Grade submitted successfully")
        
        response = ta_session.post('/ta/submission/1/grade', data={
            'grade': '95',
            'feedback': 'Excellent work'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Grade submitted successfully' in response.data
        mock_grade_submission.assert_called_with(5, '95', 'Excellent work')