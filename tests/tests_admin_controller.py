import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import session, url_for

class TestAdminController:
    """Tests for admin_controller.py"""
    
    def test_dashboard_requires_login(self, client):
        """Test that dashboard redirects to login when not authenticated"""
        response = client.get('/admin/dashboard')
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_dashboard_requires_admin_role(self, client, auth_client):
        """Test that dashboard requires admin role"""
        # Login as student
        auth_client.login_as('student', 4)
        response = client.get('/admin/dashboard')
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_dashboard_success(self, client, auth_client):
        """Test successful access to admin dashboard"""
        auth_client.login_as('admin', 1)
        response = client.get('/admin/dashboard')
        assert response.status_code == 200
    
    @patch('controllers.admin_controller.Course')
    def test_searchcourse(self, mock_course, client, auth_client):
        """Test search course functionality"""
        auth_client.login_as('admin', 1)
        
        # Mock course search results
        mock_course.search_courses.return_value = [
            Mock(id=1, name="Test Course", code="CS101")
        ]
        
        response = client.get('/admin/searchcourse?search=test')
        assert response.status_code == 200
        mock_course.search_courses.assert_called_once_with('test')
    
    @patch('controllers.admin_controller.Course')
    @patch('controllers.admin_controller.User')
    def test_view_course(self, mock_user, mock_course, client, auth_client):
        """Test viewing a specific course"""
        auth_client.login_as('admin', 1)
        
        # Mock course
        mock_course_instance = Mock()
        mock_course_instance.get_enrolled_students.return_value = [
            Mock(id=1, name="Student 1")
        ]
        mock_course.query.get.return_value = mock_course_instance
        
        response = client.get('/admin/viewcourse/1')
        assert response.status_code == 200
    
    @patch('controllers.admin_controller.User')
    def test_searchpeople(self, mock_user, client, auth_client):
        """Test search people functionality"""
        auth_client.login_as('admin', 1)
        
        # Mock user search results
        mock_user.search_users.return_value = [
            Mock(id=1, name="Test User", email="test@test.com", role="student")
        ]
        
        response = client.get('/admin/searchpeople?search=test')
        assert response.status_code == 200
        mock_user.search_users.assert_called_once_with('test')
    
    def test_add_person_get(self, client, auth_client):
        """Test GET request to add person page"""
        auth_client.login_as('admin', 1)
        response = client.get('/admin/addperson')
        assert response.status_code == 200
    
    @patch('controllers.admin_controller.db')
    @patch('controllers.admin_controller.User')
    def test_add_person_post_success(self, mock_user, mock_db, client, auth_client):
        """Test successful POST to add person"""
        auth_client.login_as('admin', 1)
        
        # Mock user query
        mock_user.query.filter_by.return_value.first.return_value = None
        
        # Mock new user
        mock_new_user = Mock()
        mock_user.return_value = mock_new_user
        
        data = {
            'name': 'New User',
            'email': 'new@test.com',
            'password': 'password123',
            'role': 'student'
        }
        
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['role'] = 'admin'
        
        response = client.post('/admin/addperson', data=data, follow_redirects=False)
        assert response.status_code == 302  # Redirect after success
    
    @patch('controllers.admin_controller.User')
    def test_add_person_post_email_exists(self, mock_user, client, auth_client):
        """Test add person with existing email"""
        auth_client.login_as('admin', 1)
        
        # Mock existing user
        mock_existing_user = Mock()
        mock_user.query.filter_by.return_value.first.return_value = mock_existing_user
        
        data = {
            'name': 'New User',
            'email': 'existing@test.com',
            'password': 'password123',
            'role': 'student'
        }
        
        response = client.post('/admin/addperson', data=data, follow_redirects=False)
        assert response.status_code == 302
    
    @patch('controllers.admin_controller.User')
    def test_edit_person_get(self, mock_user, client, auth_client):
        """Test GET request to edit person"""
        auth_client.login_as('admin', 1)
        
        # Mock person to edit
        mock_person = Mock(id=1, name="Test User", email="test@test.com", role="student")
        mock_user.query.get.return_value = mock_person
        
        response = client.get('/admin/editperson/1')
        assert response.status_code == 200
    
    @patch('controllers.admin_controller.db')
    @patch('controllers.admin_controller.User')
    def test_edit_person_post_success(self, mock_user, mock_db, client, auth_client):
        """Test successful POST to edit person"""
        auth_client.login_as('admin', 1)
        
        # Mock person to edit
        mock_person = Mock()
        mock_person.email = "old@test.com"
        mock_user.query.get.return_value = mock_person
        
        # Mock email check
        mock_user.query.filter.return_value.first.return_value = None
        
        data = {
            'name': 'Updated User',
            'email': 'updated@test.com',
            'role': 'instructor',
            'password': 'newpassword123'
        }
        
        response = client.post('/admin/editperson/1', data=data, follow_redirects=False)
        assert response.status_code == 302
    
    @patch('controllers.admin_controller.Course')
    def test_edit_course_get(self, mock_course, client, auth_client):
        """Test GET request to edit course"""
        auth_client.login_as('admin', 1)
        
        # Mock course
        mock_course_instance = Mock(id=1, name="Test Course")
        mock_course.query.get.return_value = mock_course_instance
        
        # Mock user queries
        with patch('controllers.admin_controller.User') as mock_user:
            mock_user.query.filter_by.return_value.all.side_effect = [
                [Mock(id=2, name="Instructor")],  # instructors
                [Mock(id=3, name="TA")]  # TAs
            ]
            
            response = client.get('/admin/editcourse/1')
            assert response.status_code == 200
    
    @patch('controllers.admin_controller.db')
    @patch('controllers.admin_controller.Course')
    def test_delete_person(self, mock_course, mock_db, client, auth_client):
        """Test deleting a person"""
        auth_client.login_as('admin', 1)
        
        # Mock person
        mock_person = Mock()
        mock_person.role = 'student'
        
        with patch('controllers.admin_controller.User') as mock_user:
            mock_user.query.get.return_value = mock_person
            
            # Mock related deletions
            with patch('controllers.admin_controller.Enrollment') as mock_enrollment:
                with patch('controllers.admin_controller.Submission') as mock_submission:
                    response = client.get('/admin/deleteperson/1', follow_redirects=False)
                    assert response.status_code == 302
    
    @patch('controllers.admin_controller.db')
    @patch('controllers.admin_controller.Course')
    def test_delete_course(self, mock_course, mock_db, client, auth_client):
        """Test deleting a course"""
        auth_client.login_as('admin', 1)
        
        # Mock course
        mock_course_instance = Mock()
        mock_course.query.get.return_value = mock_course_instance
        
        response = client.get('/admin/deletecourse/1', follow_redirects=False)
        assert response.status_code == 302
    
    @patch('controllers.admin_controller.Course')
    def test_add_course_get(self, mock_course, client, auth_client):
        """Test GET request to add course"""
        auth_client.login_as('admin', 1)
        
        with patch('controllers.admin_controller.User') as mock_user:
            mock_user.query.filter_by.return_value.all.side_effect = [
                [Mock(id=2, name="Instructor")],  # instructors
                [Mock(id=3, name="TA")]  # TAs
            ]
            
            response = client.get('/admin/addcourse')
            assert response.status_code == 200
    
    @patch('controllers.admin_controller.db')
    @patch('controllers.admin_controller.Course')
    def test_add_course_post_success(self, mock_course, mock_db, client, auth_client):
        """Test successful POST to add course"""
        auth_client.login_as('admin', 1)
        
        # Mock course query for existence check
        mock_course.query.filter_by.return_value.first.return_value = None
        
        # Mock new course
        mock_new_course = Mock()
        mock_course.return_value = mock_new_course
        
        data = {
            'code': 'CS101',
            'name': 'Test Course',
            'description': 'Test Description',
            'instructor': '2',
            'ta': '3',
            'credits': '3',
            'seats': '30',
            'schedule': 'MWF 10:00',
            'department': 'Computer Science'
        }
        
        response = client.post('/admin/addcourse', data=data, follow_redirects=False)
        assert response.status_code == 302