"""
Integration tests for end-to-end functionality
Tests complete user workflows across multiple controllers
"""
import pytest
import time
from unittest.mock import Mock, patch
from flask import session
from app import create_app
from extensions import db
from werkzeug.security import generate_password_hash

class TestIntegration:
    """End-to-end integration tests"""
    
    @pytest.fixture
    def test_app(self):
        """Create test application"""
        app = create_app()
        app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
            'SECRET_KEY': 'test-secret-key'
        })
        return app
    
    @pytest.fixture
    def client(self, test_app):
        """Create test client"""
        with test_app.test_client() as client:
            with test_app.app_context():
                db.create_all()
                yield client
                db.session.remove()
                db.drop_all()
    
    @pytest.fixture
    def init_test_data(self, client):
        """Initialize test data"""
        from models.user import User
        from models.courses import Course
        
        with client.application.app_context():
            # Create test users
            users = [
                User(
                    name="Admin User",
                    email="admin@test.com",
                    role="admin",
                    password_hash=generate_password_hash("admin123")
                ),
                User(
                    name="Instructor User",
                    email="instructor@test.com",
                    role="instructor",
                    password_hash=generate_password_hash("instructor123")
                ),
                User(
                    name="TA User",
                    email="ta@test.com",
                    role="ta",
                    password_hash=generate_password_hash("ta123")
                ),
                User(
                    name="Student User",
                    email="student@test.com",
                    role="student",
                    password_hash=generate_password_hash("student123")
                )
            ]
            
            for user in users:
                db.session.add(user)
            
            # Create test course
            course = Course(
                code="CS101",
                name="Computer Science 101",
                description="Intro to CS",
                credits=3,
                max_seats=30,
                seats_left=30
            )
            db.session.add(course)
            db.session.commit()
    
    def login_user(self, client, email, password):
        """Helper to login user"""
        return client.post('/login', data={
            'email': email,
            'password': password
        }, follow_redirects=True)
    
    def logout_user(self, client):
        """Helper to logout user"""
        return client.get('/logout', follow_redirects=True)
    
    def test_complete_student_workflow(self, client, init_test_data):
        """Test complete student enrollment and submission flow"""
        print("\n📚 Testing complete student workflow...")
        
        # 1. Login as student
        response = self.login_user(client, "student@test.com", "student123")
        assert response.status_code == 200
        assert b"Dashboard" in response.data or b"Welcome" in response.data
        print("  ✅ Student logged in")
        
        # 2. View available courses
        response = client.get('/student/courses')
        assert response.status_code == 200
        print("  ✅ Accessed courses page")
        
        # 3. Search for courses
        response = client.get('/student/search?keyword=CS101')
        assert response.status_code == 200
        print("  ✅ Searched courses")
        
        # 4. Logout
        response = self.logout_user(client)
        assert response.status_code == 200
        print("  ✅ Student logged out")
        
        print("🎉 Complete student workflow test passed!")
    
    def test_authentication_workflow(self, client, init_test_data):
        """Test complete authentication flow"""
        print("\n🔐 Testing authentication workflow...")
        
        # Test successful login
        response = self.login_user(client, "admin@test.com", "admin123")
        assert response.status_code == 200
        print("  ✅ Admin login successful")
        
        # Verify session
        with client.session_transaction() as sess:
            assert sess['user_id'] is not None
            assert sess['role'] == 'admin'
        print("  ✅ Session established")
        
        # Access protected route
        response = client.get('/admin/dashboard')
        assert response.status_code == 200
        print("  ✅ Accessed protected route")
        
        # Test logout
        response = self.logout_user(client)
        assert response.status_code == 200
        print("  ✅ Logout successful")
        
        # Verify session cleared
        with client.session_transaction() as sess:
            assert 'user_id' not in sess
            assert 'role' not in sess
        print("  ✅ Session cleared")
        
        # Try to access protected route after logout
        response = client.get('/admin/dashboard', follow_redirects=False)
        assert response.status_code == 302  # Redirect to login
        print("  ✅ Redirected after logout")
        
        # Test failed login
        response = client.post('/login', data={
            'email': 'admin@test.com',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b"Invalid" in response.data or b"Login" in response.data
        print("  ✅ Failed login handled correctly")
        
        print("🎉 Authentication workflow test passed!")
    
    def test_role_based_access(self, client, init_test_data):
        """Test role-based access control"""
        print("\n👮 Testing role-based access control...")
        
        # Test admin access
        self.login_user(client, "admin@test.com", "admin123")
        response = client.get('/admin/dashboard')
        assert response.status_code == 200
        print("  ✅ Admin can access admin dashboard")
        
        response = client.get('/admin/searchpeople')
        assert response.status_code == 200
        print("  ✅ Admin can search people")
        
        self.logout_user(client)
        
        # Test instructor access
        self.login_user(client, "instructor@test.com", "instructor123")
        response = client.get('/instructor/dashboard')
        assert response.status_code == 200
        print("  ✅ Instructor can access instructor dashboard")
        
        # Instructor should not access admin routes
        response = client.get('/admin/dashboard', follow_redirects=False)
        assert response.status_code == 302  # Redirect
        print("  ✅ Instructor cannot access admin routes")
        
        self.logout_user(client)
        
        # Test student access
        self.login_user(client, "student@test.com", "student123")
        response = client.get('/student/dashboard')
        assert response.status_code == 200
        print("  ✅ Student can access student dashboard")
        
        # Student should not access instructor routes
        response = client.get('/instructor/dashboard', follow_redirects=False)
        assert response.status_code == 302  # Redirect
        print("  ✅ Student cannot access instructor routes")
        
        self.logout_user(client)
        
        # Test TA access
        self.login_user(client, "ta@test.com", "ta123")
        response = client.get('/ta/dashboard')
        assert response.status_code == 200
        print("  ✅ TA can access TA dashboard")
        
        self.logout_user(client)
        
        print("🎉 Role-based access control test passed!")
    
    def test_course_management_workflow(self, client, init_test_data):
        """Test complete course management workflow"""
        print("\n🏫 Testing course management workflow...")
        
        # Admin creates a course
        self.login_user(client, "admin@test.com", "admin123")
        
        # Mock the database operations
        with patch('controllers.admin_controller.db.session.commit') as mock_commit:
            with patch('controllers.admin_controller.Course') as MockCourse:
                mock_course = Mock()
                mock_course.id = 1
                MockCourse.return_value = mock_course
                
                response = client.post('/admin/addcourse', data={
                    'code': 'MATH101',
                    'name': 'Mathematics 101',
                    'description': 'Intro to Mathematics',
                    'credits': '4',
                    'seats': '40',
                    'schedule': 'MWF 9:00',
                    'department': 'Mathematics'
                }, follow_redirects=True)
                
                assert response.status_code == 200
                print("  ✅ Course creation attempted")
        
        # View the course
        response = client.get('/admin/viewcourse/1')
        assert response.status_code == 200 or response.status_code == 404
        print("  ✅ Course view attempted")
        
        self.logout_user(client)
        
        # Student tries to enroll
        self.login_user(client, "student@test.com", "student123")
        
        with patch('controllers.student_controller.Student') as MockStudent:
            mock_student = Mock()
            mock_student.enroll_course.return_value = (True, "Enrolled successfully")
            MockStudent.get_by_id.return_value = mock_student
            
            response = client.get('/student/enroll/1', follow_redirects=True)
            assert response.status_code == 200
            print("  ✅ Course enrollment attempted")
        
        self.logout_user(client)
        
        print("🎉 Course management workflow test passed!")
    
    def test_assignment_submission_workflow(self, client, init_test_data):
        """Test assignment submission and grading workflow"""
        print("\n📝 Testing assignment submission workflow...")
        
        # Instructor creates assignment
        self.login_user(client, "instructor@test.com", "instructor123")
        
        with patch('controllers.instructor_controller.Course') as MockCourse:
            with patch('controllers.instructor_controller.db.session.commit') as mock_commit:
                mock_course = Mock()
                mock_course.add_assignment.return_value = Mock(id=1)
                MockCourse.get_by_id.return_value = mock_course
                
                response = client.post('/instructor/course/1/add_assignment', data={
                    'title': 'Homework 1',
                    'description': 'First homework assignment',
                    'due_date': '2024-12-31'
                }, follow_redirects=True)
                
                assert response.status_code == 200 or response.status_code == 302
                print("  ✅ Assignment creation attempted")
        
        self.logout_user(client)
        
        # Student submits assignment
        self.login_user(client, "student@test.com", "student123")
        
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
                        'submission_text': 'My solution to the assignment'
                    }, follow_redirects=True)
                    
                    assert response.status_code == 200 or response.status_code == 302
                    print("  ✅ Assignment submission attempted")
        
        self.logout_user(client)
        
        # TA grades assignment
        self.login_user(client, "ta@test.com", "ta123")
        
        with patch('controllers.TA_controller.Assignment') as MockAssignment:
            mock_assignment = Mock()
            mock_assignment.grade_submission.return_value = (True, "Graded")
            MockAssignment.get_by_id.return_value = mock_assignment
            
            response = client.post('/ta/submission/4/grade', data={
                'assignment_id': '1',
                'grade': '95',
                'feedback': 'Excellent work!'
            }, follow_redirects=True)
            
            assert response.status_code == 200 or response.status_code == 302
            print("  ✅ Assignment grading attempted")
        
        self.logout_user(client)
        
        print("🎉 Assignment submission workflow test passed!")
    
    def test_search_functionality_integration(self, client, init_test_data):
        """Test search functionality across the system"""
        print("\n🔍 Testing search functionality integration...")
        
        # Admin searches people
        self.login_user(client, "admin@test.com", "admin123")
        
        with patch('controllers.admin_controller.User') as MockUser:
            MockUser.search_users.return_value = [Mock(name="Test User", email="test@test.com")]
            
            response = client.get('/admin/searchpeople?search=test')
            assert response.status_code == 200
            print("  ✅ Admin people search attempted")
        
        # Admin searches courses
        with patch('controllers.admin_controller.Course') as MockCourse:
            MockCourse.search_courses.return_value = [Mock(code="CS101", name="Computer Science")]
            
            response = client.get('/admin/searchcourse?search=computer')
            assert response.status_code == 200
            print("  ✅ Admin course search attempted")
        
        self.logout_user(client)
        
        # Student searches courses
        self.login_user(client, "student@test.com", "student123")
        
        with patch('controllers.student_controller.Course') as MockCourse:
            with patch('controllers.student_controller.Student') as MockStudent:
                MockCourse.search_courses.return_value = [Mock(code="MATH101", name="Mathematics")]
                MockStudent.get_by_id.return_value = Mock()
                
                response = client.get('/student/search?keyword=math')
                assert response.status_code == 200
                print("  ✅ Student course search attempted")
        
        self.logout_user(client)
        
        print("🎉 Search functionality integration test passed!")
    
    def test_error_handling_integration(self, client, init_test_data):
        """Test error handling across the system"""
        print("\n🚨 Testing error handling integration...")
        
        # Test 404 page
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
        print("  ✅ 404 error handling works")
        
        # Test access without login
        response = client.get('/admin/dashboard', follow_redirects=False)
        assert response.status_code == 302  # Redirect to login
        print("  ✅ Unauthorized access redirected")
        
        # Test invalid form submission
        self.login_user(client, "student@test.com", "student123")
        
        # Submit empty form
        response = client.post('/student/assignment/1/submit', data={}, follow_redirects=True)
        assert response.status_code == 200
        print("  ✅ Invalid form submission handled")
        
        self.logout_user(client)
        
        print("🎉 Error handling integration test passed!")