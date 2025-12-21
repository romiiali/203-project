# tests/test_student_controller.py
import pytest
from unittest.mock import Mock, patch
from flask import session

class TestStudentController:
    """Test cases for student controller"""
    
    @pytest.fixture
    def student_session(self, client):
        """Set up student session for testing"""
        with client.session_transaction() as session:
            session['user_id'] = 1
            session['role'] = 'student'
        return client
    
    def test_dashboard_requires_login(self, client):
        """Test dashboard redirects when not logged in"""
        response = client.get('/student/dashboard', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_dashboard_requires_student_role(self, client):
        """Test dashboard redirects when wrong role"""
        # Set up non-student session
        with client.session_transaction() as session:
            session['user_id'] = 1
            session['role'] = 'instructor'
        
        response = client.get('/student/dashboard', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location
    
    @patch('models.student.Student.get_by_id')
    def test_dashboard_success(self, mock_get_student, student_session):
        """Test student dashboard loads successfully"""
        # Mock student object
        mock_student = Mock()
        mock_student.get_enrolled_courses.return_value = []
        mock_get_student.return_value = mock_student
        
        response = student_session.get('/student/dashboard')
        assert response.status_code == 200
        assert b'Dashboard' in response.data
    
    @patch('models.student.Student.get_by_id')
    def test_dashboard_student_not_found(self, mock_get_student, student_session):
        """Test dashboard when student not found"""
        mock_get_student.return_value = None
        
        response = student_session.get('/student/dashboard', follow_redirects=True)
        assert b'Student not found' in response.data
        assert b'Login' in response.data
    
    @patch('models.student.Student.get_by_id')
    def test_view_courses(self, mock_get_student, student_session):
        """Test view enrolled courses"""
        mock_student = Mock()
        mock_course = Mock()
        mock_course.name = "Test Course"
        mock_course.code = "TEST101"
        mock_student.get_enrolled_courses.return_value = [mock_course]
        mock_get_student.return_value = mock_student
        
        response = student_session.get('/student/courses')
        assert response.status_code == 200
        assert b'Test Course' in response.data
        assert b'TEST101' in response.data
    
    @patch('models.student.Student.get_by_id')
    @patch('models.courses.Course.search_courses')
    def test_search_courses(self, mock_search, mock_get_student, student_session):
        """Test course search"""
        mock_student = Mock()
        mock_student.get_enrolled_courses.return_value = []
        mock_get_student.return_value = mock_student
        
        mock_course = Mock()
        mock_course.id = 1
        mock_course.name = "Advanced Python"
        mock_course.code = "CS501"
        mock_search.return_value = [mock_course]
        
        response = student_session.get('/student/search?keyword=Python')
        assert response.status_code == 200
        assert b'Advanced Python' in response.data
        assert b'CS501' in response.data
    
    @patch('models.student.Student.get_by_id')
    @patch('models.student.Student.enroll_course')
    def test_enroll_course(self, mock_enroll, mock_get_student, student_session):
        """Test course enrollment"""
        mock_student = Mock()
        mock_get_student.return_value = mock_student
        mock_enroll.return_value = (True, "Enrolled successfully")
        
        response = student_session.get('/student/enroll/1', follow_redirects=True)
        assert response.status_code == 200
        assert b'Enrolled successfully' in response.data
        mock_enroll.assert_called_with(1)
    
    @patch('models.student.Student.get_by_id')
    @patch('models.student.Student.drop_course')
    def test_drop_course(self, mock_drop, mock_get_student, student_session):
        """Test course drop"""
        mock_student = Mock()
        mock_get_student.return_value = mock_student
        mock_drop.return_value = (True, "Course dropped successfully")
        
        response = student_session.get('/student/drop/1', follow_redirects=True)
        assert response.status_code == 200
        assert b'Course dropped successfully' in response.data
        mock_drop.assert_called_with(1)
    
    @patch('models.student.Student.get_by_id')
    @patch('models.courses.Course.get_by_id')
    @patch('models.student.Student.is_enrolled_in_course')
    def test_view_course_details(self, mock_is_enrolled, mock_get_course, mock_get_student, student_session):
        """Test viewing course details"""
        mock_student = Mock()
        mock_student.id = 1
        mock_get_student.return_value = mock_student
        
        mock_course = Mock()
        mock_course.id = 1
        mock_course.name = "Test Course"
        mock_course.get_announcements.return_value = []
        mock_course.get_assignments.return_value = []
        mock_get_course.return_value = mock_course
        
        mock_is_enrolled.return_value = True
        
        response = student_session.get('/student/course/1')
        assert response.status_code == 200
        assert b'Test Course' in response.data
    
    @patch('models.student.Student.get_by_id')
    @patch('models.courses.Course.get_by_id')
    @patch('models.student.Student.is_enrolled_in_course')
    def test_view_course_not_enrolled(self, mock_is_enrolled, mock_get_course, mock_get_student, student_session):
        """Test viewing course when not enrolled"""
        mock_student = Mock()
        mock_get_student.return_value = mock_student
        
        mock_course = Mock()
        mock_get_course.return_value = mock_course
        
        mock_is_enrolled.return_value = False
        
        response = student_session.get('/student/course/1', follow_redirects=True)
        assert b'Course not found or not enrolled' in response.data
    
    @patch('models.student.Student.get_by_id')
    @patch('models.assignment.Assignment.get_by_id')
    @patch('models.courses.Course.get_by_id')
    @patch('models.student.Student.is_enrolled_in_course')
    @patch('models.assignment.Assignment.add_submission')
    def test_submit_assignment_post(self, mock_add_submission, mock_is_enrolled, 
                                  mock_get_course, mock_get_assignment, mock_get_student, student_session):
        """Test submitting assignment via POST"""
        mock_student = Mock()
        mock_student.id = 1
        mock_get_student.return_value = mock_student
        
        mock_assignment = Mock()
        mock_assignment.id = 1
        mock_assignment.course_id = 1
        mock_get_assignment.return_value = mock_assignment
        
        mock_course = Mock()
        mock_course.id = 1
        mock_get_course.return_value = mock_course
        
        mock_is_enrolled.return_value = True
        mock_add_submission.return_value = (True, "Submission added successfully")
        
        response = student_session.post('/student/assignment/1/submit', data={
            'submission_text': 'This is my submission'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Submission added successfully' in response.data
        mock_add_submission.assert_called_with(1, 'This is my submission')
    
    @patch('models.student.Student.get_by_id')
    @patch('models.assignment.Assignment.get_by_id')
    @patch('models.courses.Course.get_by_id')
    @patch('models.student.Student.is_enrolled_in_course')
    def test_submit_assignment_get(self, mock_is_enrolled, mock_get_course, 
                                 mock_get_assignment, mock_get_student, student_session):
        """Test assignment submission form"""
        mock_student = Mock()
        mock_get_student.return_value = mock_student
        
        mock_assignment = Mock()
        mock_assignment.title = "Test Assignment"
        mock_get_assignment.return_value = mock_assignment
        
        mock_course = Mock()
        mock_course.name = "Test Course"
        mock_get_course.return_value = mock_course
        
        mock_is_enrolled.return_value = True
        
        response = student_session.get('/student/assignment/1/submit')
        assert response.status_code == 200
        assert b'Test Assignment' in response.data
        assert b'Test Course' in response.data
        assert b'submission_text' in response.data
    
    @patch('models.student.Student.get_by_id')
    def test_view_grades(self, mock_get_student, student_session):
        """Test viewing grades"""
        mock_student = Mock()
        mock_course = Mock()
        mock_course.name = "Math 101"
        mock_student.get_enrolled_courses.return_value = [mock_course]
        mock_get_student.return_value = mock_student
        
        response = student_session.get('/student/grades')
        assert response.status_code == 200
        assert b'Grades' in response.data