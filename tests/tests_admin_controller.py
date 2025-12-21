# tests/test_admin_controller.py
import pytest
from unittest.mock import Mock, patch
from models.user import User
from models.courses import Course

class TestAdminController:
    """Test cases for admin controller"""
    
    @pytest.fixture
    def admin_session(self, client):
        """Set up admin session for testing"""
        with client.session_transaction() as session:
            session['user_id'] = 4
            session['role'] = 'admin'
        return client
    
    def test_dashboard_requires_login(self, client):
        """Test admin dashboard requires login"""
        response = client.get('/admin/dashboard', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_dashboard_requires_admin_role(self, client):
        """Test dashboard redirects when wrong role"""
        with client.session_transaction() as session:
            session['user_id'] = 1
            session['role'] = 'student'
        
        response = client.get('/admin/dashboard', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_dashboard_success(self, admin_session):
        """Test admin dashboard loads successfully"""
        response = admin_session.get('/admin/dashboard')
        assert response.status_code == 200
        assert b'Admin Dashboard' in response.data or b'Dashboard' in response.data
    
    @patch('models.courses.Course.search_courses')
    def test_search_course(self, mock_search, admin_session):
        """Test course search"""
        mock_course = Mock()
        mock_course.name = "Advanced Algorithms"
        mock_course.code = "CS601"
        mock_search.return_value = [mock_course]
        
        response = admin_session.get('/admin/searchcourse?search=Algorithms')
        assert response.status_code == 200
        assert b'Advanced Algorithms' in response.data
        assert b'CS601' in response.data
    
    @patch('models.user.User.search_users')
    def test_search_people(self, mock_search, admin_session):
        """Test people search"""
        mock_user = Mock()
        mock_user.name = "Jane Smith"
        mock_user.email = "jane@test.com"
        mock_user.role = "instructor"
        mock_search.return_value = [mock_user]
        
        response = admin_session.get('/admin/searchpeople?search=Jane')
        assert response.status_code == 200
        assert b'Jane Smith' in response.data
        assert b'instructor' in response.data
    
    @patch('models.courses.Course.query')
    def test_view_course(self, mock_query, admin_session):
        """Test viewing course details"""
        mock_course = Mock()
        mock_course.id = 1
        mock_course.name = "CS101"
        mock_course.code = "CS101"
        mock_course.get_enrolled_students.return_value = []
        mock_query.get.return_value = mock_course
        
        response = admin_session.get('/admin/viewcourse/1')
        assert response.status_code == 200
        assert b'CS101' in response.data
    
    @patch('models.user.User.query')
    def test_view_course_not_found(self, mock_query, admin_session):
        """Test viewing non-existent course"""
        mock_query.get.return_value = None
        
        response = admin_session.get('/admin/viewcourse/999', follow_redirects=True)
        assert b'Course not found' in response.data
    
    def test_add_person_form(self, admin_session):
        """Test add person form loads"""
        response = admin_session.get('/admin/addperson')
        assert response.status_code == 200
        assert b'Add Person' in response.data
        assert b'name' in response.data
        assert b'email' in response.data
        assert b'password' in response.data
        assert b'role' in response.data
    
    @patch('models.user.User.query')
    def test_add_person_post_success(self, mock_query, admin_session, init_database):
        """Test adding a person successfully"""
        mock_filter = Mock()
        mock_filter.first.return_value = None  # Email not taken
        mock_query.filter_by.return_value = mock_filter
        
        with patch.object(User, 'set_password') as mock_set_password:
            with admin_session.application.app_context():
                response = admin_session.post('/admin/addperson', data={
                    'name': 'New User',
                    'email': 'new@test.com',
                    'password': 'password123',
                    'role': 'student'
                }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Person added successfully' in response.data
    
    @patch('models.user.User.query')
    def test_add_person_email_exists(self, mock_query, admin_session):
        """Test adding person with existing email"""
        mock_existing = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = mock_existing  # Email already exists
        mock_query.filter_by.return_value = mock_filter
        
        response = admin_session.post('/admin/addperson', data={
            'name': 'New User',
            'email': 'existing@test.com',
            'password': 'password123',
            'role': 'student'
        }, follow_redirects=True)
        
        assert b'Email already registered' in response.data
    
    def test_add_person_missing_fields(self, admin_session):
        """Test adding person with missing fields"""
        response = admin_session.post('/admin/addperson', data={
            'name': '',
            'email': '',
            'password': '',
            'role': ''
        }, follow_redirects=True)
        
        assert b'Please fill all fields' in response.data
    
    @patch('models.user.User.query')
    def test_edit_person_form(self, mock_query, admin_session):
        """Test edit person form loads"""
        mock_person = Mock()
        mock_person.id = 1
        mock_person.name = "John Doe"
        mock_person.email = "john@test.com"
        mock_person.role = "student"
        mock_query.get.return_value = mock_person
        
        response = admin_session.get('/admin/editperson/1')
        assert response.status_code == 200
        assert b'John Doe' in response.data
        assert b'john@test.com' in response.data
        assert b'student' in response.data
    
    @patch('models.user.User.query')
    def test_edit_person_post(self, mock_query, admin_session):
        """Test updating a person"""
        mock_person = Mock()
        mock_person.id = 1
        mock_person.name = "Old Name"
        mock_person.email = "old@test.com"
        mock_person.role = "student"
        
        mock_filter = Mock()
        mock_filter.first.return_value = None  # Email not taken by others
        mock_query.get.return_value = mock_person
        mock_query.filter.return_value = mock_filter
        
        with patch.object(mock_person, 'set_password'):
            response = admin_session.post('/admin/editperson/1', data={
                'name': 'Updated Name',
                'email': 'updated@test.com',
                'role': 'instructor',
                'password': 'newpassword123'
            }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Person updated successfully' in response.data
    
    @patch('models.user.User.query')
    def test_delete_person(self, mock_query, admin_session):
        """Test deleting a person"""
        mock_person = Mock()
        mock_person.id = 1
        mock_person.name = "To Delete"
        mock_person.role = "student"  # Not admin
        mock_query.get.return_value = mock_person
        
        # Mock related deletions
        with patch('models.enrollment.Enrollment.query') as mock_enrollment, \
             patch('models.submission.Submission.query') as mock_submission:
            
            mock_enrollment.filter_by.return_value.delete.return_value = None
            mock_submission.filter_by.return_value.delete.return_value = None
            
            response = admin_session.get('/admin/deleteperson/1', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Person deleted successfully' in response.data
    
    @patch('models.user.User.query')
    def test_delete_admin_person(self, mock_query, admin_session):
        """Test attempting to delete an admin"""
        mock_admin = Mock()
        mock_admin.role = "admin"
        mock_query.get.return_value = mock_admin
        
        response = admin_session.get('/admin/deleteperson/1', follow_redirects=True)
        assert b'Cannot delete an admin user' in response.data
    
    @patch('models.courses.Course.query')
    def test_add_course_form(self, mock_query, admin_session):
        """Test add course form loads"""
        mock_instructor = Mock()
        mock_instructor.id = 1
        mock_instructor.name = "Dr. Smith"
        
        mock_ta = Mock()
        mock_ta.id = 2
        mock_ta.name = "TA Jones"
        
        mock_query.filter_by.side_effect = [
            Mock(all=Mock(return_value=[mock_instructor])),
            Mock(all=Mock(return_value=[mock_ta]))
        ]
        
        response = admin_session.get('/admin/addcourse')
        assert response.status_code == 200
        assert b'Add Course' in response.data
        assert b'Dr. Smith' in response.data
        assert b'TA Jones' in response.data