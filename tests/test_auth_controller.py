import pytest
from unittest.mock import Mock, patch
from flask import session

class TestAuthController:
    """Tests for auth_controller.py"""
    
    def test_login_get(self, client):
        """Test GET request to login page"""
        response = client.get('/login')
        assert response.status_code == 200
    
    @patch('controllers.auth_controller.User')
    def test_login_post_success_student(self, mock_user, client):
        """Test successful student login"""
        # Mock user
        mock_user_instance = Mock()
        mock_user_instance.id = 4
        mock_user_instance.role = 'student'
        mock_user.login.return_value = mock_user_instance
        
        data = {
            'email': 'student@test.com',
            'password': 'password123'
        }
        
        response = client.post('/login', data=data, follow_redirects=False)
        assert response.status_code == 302
        assert '/student/dashboard' in response.location
        
        # Check session
        with client.session_transaction() as sess:
            assert sess['user_id'] == 4
            assert sess['role'] == 'student'
    
    @patch('controllers.auth_controller.User')
    def test_login_post_success_instructor(self, mock_user, client):
        """Test successful instructor login"""
        mock_user_instance = Mock()
        mock_user_instance.id = 2
        mock_user_instance.role = 'instructor'
        mock_user.login.return_value = mock_user_instance
        
        data = {
            'email': 'instructor@test.com',
            'password': 'password123'
        }
        
        response = client.post('/login', data=data, follow_redirects=False)
        assert response.status_code == 302
        assert '/instructor/dashboard' in response.location
    
    @patch('controllers.auth_controller.User')
    def test_login_post_success_ta(self, mock_user, client):
        """Test successful TA login"""
        mock_user_instance = Mock()
        mock_user_instance.id = 3
        mock_user_instance.role = 'ta'
        mock_user.login.return_value = mock_user_instance
        
        data = {
            'email': 'ta@test.com',
            'password': 'password123'
        }
        
        response = client.post('/login', data=data, follow_redirects=False)
        assert response.status_code == 302
        assert '/ta/dashboard' in response.location
    
    @patch('controllers.auth_controller.User')
    def test_login_post_success_admin(self, mock_user, client):
        """Test successful admin login"""
        mock_user_instance = Mock()
        mock_user_instance.id = 1
        mock_user_instance.role = 'admin'
        mock_user.login.return_value = mock_user_instance
        
        data = {
            'email': 'admin@test.com',
            'password': 'password123'
        }
        
        response = client.post('/login', data=data, follow_redirects=False)
        assert response.status_code == 302
        assert '/admin/dashboard' in response.location
    
    @patch('controllers.auth_controller.User')
    def test_login_post_failure(self, mock_user, client):
        """Test failed login"""
        mock_user.login.return_value = None
        
        data = {
            'email': 'wrong@test.com',
            'password': 'wrongpassword'
        }
        
        response = client.post('/login', data=data, follow_redirects=True)
        assert response.status_code == 200  # Stays on login page
    
    def test_logout(self, client, auth_client):
        """Test logout functionality"""
        # Login first
        auth_client.login_as('student', 4)
        
        # Verify session exists
        with client.session_transaction() as sess:
            assert 'user_id' in sess
            assert 'role' in sess
        
        # Logout
        response = client.get('/logout', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location
        
        # Verify session cleared
        with client.session_transaction() as sess:
            assert 'user_id' not in sess
            assert 'role' not in sess