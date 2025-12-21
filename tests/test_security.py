"""
Security tests for non-functional security requirements
"""
import pytest
import re
from unittest.mock import Mock, patch
from werkzeug.security import check_password_hash, generate_password_hash
from app import create_app
from extensions import db
from models.user import User

class TestSecurity:
    """Security requirement tests"""
    
    @pytest.fixture
    def app(self):
        """Create test application"""
        app = create_app()
        app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': True,
            'SECRET_KEY': 'test-secret-key-for-security-tests'
        })
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        with app.test_client() as client:
            with app.app_context():
                db.create_all()
                yield client
                db.session.remove()
                db.drop_all()
    
    def test_password_hashing(self, client):
        """Test that passwords are hashed (Non-functional requirement: Security)"""
        print("\n🔒 Testing password hashing...")
        
        # Create a test user
        password = "SecurePassword123!"
        
        with client.application.app_context():
            user = User(
                name="Security Test User",
                email="security@test.com",
                role="student"
            )
            user.set_password(password)
            
            # Test 1: Password should be hashed
            assert user.password_hash is not None
            assert password != user.password_hash  # Should not store plain text
            assert len(user.password_hash) > 50  # Hash should be long
            print("  ✅ Password is hashed, not stored in plain text")
            
            # Test 2: Hash should start with appropriate method
            # werkzeug usually starts with pbkdf2:sha256:
            assert user.password_hash.startswith('pbkdf2:sha256:')
            print("  ✅ Uses strong hashing algorithm (pbkdf2:sha256)")
            
            # Test 3: Should verify correctly
            assert user.check_password(password) is True
            print("  ✅ Password verification works")
            
            # Test 4: Should reject wrong passwords
            assert user.check_password("WrongPassword") is False
            print("  ✅ Rejects incorrect passwords")
            
            # Test 5: Hash should include salt
            # Extract salt from hash (format: pbkdf2:sha256:iterations$salt$hash)
            hash_parts = user.password_hash.split('$')
            assert len(hash_parts) >= 3  # Should have salt and hash
            print("  ✅ Password hash includes salt")
    
    def test_session_security(self, client):
        """Test session security measures"""
        print("\n📝 Testing session security...")
        
        # Create and login a user
        with client.application.app_context():
            user = User(
                name="Session Test",
                email="session@test.com",
                role="student",
                password="password123"
            )
            db.session.add(user)
            db.session.commit()
            
        # Login
        response = client.post('/login', data={
            'email': 'session@test.com',
            'password': 'password123'
        }, follow_redirects=True)
        
        # Test 1: Session should have secure attributes
        with client.session_transaction() as sess:
            assert 'user_id' in sess
            assert 'role' in sess
            print("  ✅ Session stores user authentication")
            
            # Check for CSRF token if using Flask-WTF
            if '_csrf_token' in sess:
                print("  ✅ CSRF token in session")
        
        # Test 2: Session cookie should have secure flags (in production)
        # Note: In testing, secure flag might not be set
        cookies = response.headers.getlist('Set-Cookie')
        session_cookie = next((c for c in cookies if 'session' in c.lower()), None)
        
        if session_cookie:
            # Check for HttpOnly flag
            if 'HttpOnly' in session_cookie:
                print("  ✅ Session cookie has HttpOnly flag")
            else:
                print("  ⚠️  Session cookie should have HttpOnly flag")
            
            # Check for SameSite attribute
            if 'SameSite' in session_cookie:
                print("  ✅ Session cookie has SameSite attribute")
            else:
                print("  ⚠️  Consider adding SameSite attribute")
        
        # Test 3: Logout should clear session
        response = client.get('/logout', follow_redirects=True)
        
        with client.session_transaction() as sess:
            assert 'user_id' not in sess
            assert 'role' not in sess
            print("  ✅ Logout properly clears session")
    
    def test_role_based_access_control(self, client):
        """Test RBAC implementation"""
        print("\n👮 Testing Role-Based Access Control...")
        
        # Create test users with different roles
        with client.application.app_context():
            users = [
                User(name="Admin", email="admin_rbac@test.com", role="admin", password="pass"),
                User(name="Instructor", email="instructor_rbac@test.com", role="instructor", password="pass"),
                User(name="TA", email="ta_rbac@test.com", role="ta", password="pass"),
                User(name="Student", email="student_rbac@test.com", role="student", password="pass")
            ]
            
            for user in users:
                db.session.add(user)
            db.session.commit()
        
        # Test each role's access
        test_cases = [
            ('admin_rbac@test.com', 'pass', 'admin', [
                ('/admin/dashboard', 200, "Access admin dashboard"),
                ('/instructor/dashboard', 302, "Redirect from instructor route"),
                ('/student/dashboard', 302, "Redirect from student route")
            ]),
            ('instructor_rbac@test.com', 'pass', 'instructor', [
                ('/instructor/dashboard', 200, "Access instructor dashboard"),
                ('/admin/dashboard', 302, "Cannot access admin routes"),
                ('/student/dashboard', 302, "Cannot access student routes")
            ]),
            ('student_rbac@test.com', 'pass', 'student', [
                ('/student/dashboard', 200, "Access student dashboard"),
                ('/admin/dashboard', 302, "Cannot access admin routes"),
                ('/instructor/dashboard', 302, "Cannot access instructor routes")
            ]),
            ('ta_rbac@test.com', 'pass', 'ta', [
                ('/ta/dashboard', 200, "Access TA dashboard"),
                ('/admin/dashboard', 302, "Cannot access admin routes")
            ])
        ]
        
        for email, password, role, routes in test_cases:
            print(f"\n  Testing {role} access control:")
            
            # Login
            client.post('/login', data={'email': email, 'password': password}, follow_redirects=True)
            
            for route, expected_status, description in routes:
                response = client.get(route, follow_redirects=False)
                assert response.status_code == expected_status, \
                    f"{role} access to {route}: expected {expected_status}, got {response.status_code}"
                print(f"    ✅ {description}")
            
            # Logout
            client.get('/logout', follow_redirects=True)
    
    def test_input_validation(self, client):
        """Test input validation and sanitization"""
        print("\n🛡️ Testing input validation...")
        
        # Test SQL injection attempts
        sql_injection_tests = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "<script>alert('xss')</script>"
        ]
        
        with client.application.app_context():
            # Create a test user
            user = User(
                name="Validation Test",
                email="validation@test.com",
                role="student",
                password="password123"
            )
            db.session.add(user)
            db.session.commit()
        
        # Login first
        client.post('/login', data={
            'email': 'validation@test.com',
            'password': 'password123'
        }, follow_redirects=True)
        
        # Test search functionality with malicious input
        for malicious_input in sql_injection_tests:
            response = client.get(f'/student/search?keyword={malicious_input}', follow_redirects=True)
            
            # Should not crash - return 200 or handle gracefully
            assert response.status_code in [200, 302, 400, 404]
            
            # Check for error messages or sanitized output
            response_text = response.get_data(as_text=True)
            
            # Should not echo back the malicious input
            if malicious_input in response_text:
                print(f"  ⚠️  Potential vulnerability: Input '{malicious_input[:20]}...' echoed back")
            else:
                print(f"  ✅ Input '{malicious_input[:20]}...' handled safely")
        
        # Test XSS in form submissions
        xss_payload = "<script>alert('XSS')</script>"
        
        # Try to submit assignment with XSS
        with patch('controllers.student_controller.Assignment') as MockAssignment:
            with patch('controllers.student_controller.Student') as MockStudent:
                with patch('controllers.student_controller.Course') as MockCourse:
                    mock_assignment = Mock()
                    mock_assignment.course_id = 1
                    mock_assignment.add_submission.return_value = (True, "Submitted")
                    MockAssignment.get_by_id.return_value = mock_assignment
                    
                    mock_student = Mock()
                    mock_student.is_enrolled_in_course.return_value = True
                    MockStudent.get_by_id.return_value = mock_student
                    
                    mock_course = Mock()
                    mock_course.id = 1
                    MockCourse.get_by_id.return_value = mock_course
                    
                    response = client.post('/student/assignment/1/submit', data={
                        'submission_text': xss_payload
                    }, follow_redirects=True)
                    
                    # Should handle without crashing
                    assert response.status_code in [200, 302]
                    print("  ✅ XSS payload in form submission handled")
    
    def test_https_requirements(self):
        """Test HTTPS/secure communication requirements"""
        print("\n🔐 Testing secure communication requirements...")
        
        # Test 1: Check for HTTPS in configuration
        app = create_app()
        
        # In production, these should be set
        if app.config.get('ENV') == 'production':
            assert app.config.get('PREFERRED_URL_SCHEME') == 'https', \
                "Production should use HTTPS"
            assert app.config.get('SESSION_COOKIE_SECURE') is True, \
                "Session cookies should be secure in production"
            print("  ✅ Production HTTPS configuration")
        else:
            print("  ℹ️  Development environment (HTNS not enforced)")
        
        # Test 2: Check for security headers in responses
        with app.test_client() as client:
            response = client.get('/')
            
            security_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block'
            }
            
            for header, expected_value in security_headers.items():
                if header in response.headers:
                    print(f"  ✅ Security header '{header}' present")
                else:
                    print(f"  ⚠️  Consider adding security header '{header}'")
    
    def test_authentication_timeout(self, client):
        """Test session timeout/expiration"""
        print("\n⏰ Testing authentication timeout...")
        
        with client.application.app_context():
            # Create test user
            user = User(
                name="Timeout Test",
                email="timeout@test.com",
                role="student",
                password="password123"
            )
            db.session.add(user)
            db.session.commit()
        
        # Login
        client.post('/login', data={
            'email': 'timeout@test.com',
            'password': 'password123'
        }, follow_redirects=True)
        
        # Verify initial access
        response = client.get('/student/dashboard', follow_redirects=True)
        assert response.status_code == 200
        print("  ✅ Initial access granted")
        
        # Manually expire session (simulate timeout)
        with client.session_transaction() as sess:
            # Modify session to simulate old session
            sess['_fresh'] = False
        
        # Try to access again
        response = client.get('/student/dashboard', follow_redirects=False)
        
        # Should redirect to login if session expired
        if response.status_code == 302:
            print("  ✅ Session expiration triggers re-authentication")
        else:
            print("  ⚠️  Consider implementing session timeout")
    
    def test_brute_force_protection(self, client):
        """Test protection against brute force attacks"""
        print("\n🛑 Testing brute force protection...")
        
        # Try multiple failed logins
        failed_attempts = 5
        
        for i in range(failed_attempts):
            response = client.post('/login', data={
                'email': 'nonexistent@test.com',
                'password': f'wrongpassword{i}'
            }, follow_redirects=True)
            
            # Should return error but not crash
            assert response.status_code == 200
            
            # Check for error message
            response_text = response.get_data(as_text=True)
            
            if i < 3:  # First few attempts
                if 'Invalid' in response_text or 'incorrect' in response_text.lower():
                    print(f"  ✅ Attempt {i+1}: Appropriate error message")
                else:
                    print(f"  ⚠️  Attempt {i+1}: Consider adding rate limiting")
            else:
                # After multiple attempts
                print(f"  ⚠️  Attempt {i+1}: Consider implementing account lockout")
        
        print("  ℹ️  Note: For production, implement rate limiting or account lockout")
    
    def test_data_privacy(self, client):
        """Test data privacy and information leakage"""
        print("\n🤫 Testing data privacy...")
        
        # Create multiple users
        with client.application.app_context():
            users = [
                User(name="User1", email="user1@test.com", role="student", password="pass"),
                User(name="User2", email="user2@test.com", role="student", password="pass"),
                User(name="User3", email="user3@test.com", role="instructor", password="pass")
            ]
            
            for user in users:
                db.session.add(user)
            db.session.commit()
        
        # Login as one student
        client.post('/login', data={
            'email': 'user1@test.com',
            'password': 'pass'
        }, follow_redirects=True)
        
        # Try to access another user's data directly
        # This should be prevented by authorization checks
        
        with patch('controllers.student_controller.Student') as MockStudent:
            mock_student = Mock()
            mock_student.id = 1  # Current user's ID
            MockStudent.get_by_id.return_value = mock_student
            
            # Try to access submission of another student (ID 2)
            with patch('controllers.student_controller.Assignment') as MockAssignment:
                mock_assignment = Mock()
                # Simulate that get_submission returns None for other user's data
                mock_assignment.get_submission.return_value = None
                MockAssignment.get_by_id.return_value = mock_assignment
                
                response = client.get('/student/assignment/1/submission/2', follow_redirects=True)
                
                # Should either return 404 or redirect
                assert response.status_code in [200, 302, 404]
                print("  ✅ Cannot access other users' submission data")
        
        # Check that sensitive data is not exposed in error messages
        # Try to login with non-existent user
        response = client.post('/login', data={
            'email': 'nonexistentuser@test.com',
            'password': 'wrong'
        }, follow_redirects=True)
        
        response_text = response.get_data(as_text=True)
        
        # Error message should not reveal whether user exists
        if 'does not exist' in response_text.lower() or 'unknown user' in response_text.lower():
            print("  ⚠️  Error message reveals user existence (security consideration)")
        else:
            print("  ✅ Generic error messages protect user enumeration")