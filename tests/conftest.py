# tests/conftest.py
import sys
import os
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

print(f"✅ Python path: {sys.path[0]}")
print(f"✅ Project root: {project_root}")

# Import Flask app and extensions
from app import create_app
from extensions import db

# ================ FIXTURES FOR MODELS ================

@pytest.fixture(scope='session')
def app():
    """Create test Flask application"""
    # Create app with testing configuration
    app = create_app()
    
    # Override config for testing
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',  # Use SQLite in-memory DB
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False  # Disable CSRF for testing
    })
    
    print(f"✅ App created with database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    return app

@pytest.fixture(scope='function')
def client(app):
    """Test client for the app"""
    return app.test_client()

@pytest.fixture(scope='function')
def init_database(app):
    """Initialize database for model tests"""
    with app.app_context():
        # Drop all tables and create fresh ones
        db.drop_all()
        db.create_all()
        
        print(f"✅ Database tables created for model tests")
        
        yield db
        
        # Clean up
        db.session.remove()
        db.drop_all()

@pytest.fixture
def db_session(init_database, app):
    """Database session for model tests"""
    with app.app_context():
        yield db.session
        db.session.rollback()

# ================ MODEL FIXTURES ================

@pytest.fixture
def test_user(init_database, app):
    """Create a test user for model tests"""
    from models.user import User
    
    with app.app_context():
        user = User(
            name="Test User",
            email="user@test.com",
            role="student"
        )
        user.set_password("password123")
        
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user

@pytest.fixture
def test_course(init_database, app):
    """Create a test course for model tests"""
    from models.courses import Course
    
    with app.app_context():
        course = Course(
            name="Test Course",
            code="TEST101",
            description="A test course",
            max_seats=30
        )
        
        db.session.add(course)
        db.session.commit()
        db.session.refresh(course)
        return course

@pytest.fixture
def test_instructor_user(init_database, app):
    """Create a test instructor user"""
    from models.user import User
    
    with app.app_context():
        instructor = User(
            name="Test Instructor",
            email="instructor@test.com",
            role="instructor"
        )
        instructor.set_password("password123")
        
        db.session.add(instructor)
        db.session.commit()
        db.session.refresh(instructor)
        return instructor

@pytest.fixture
def test_ta_user(init_database, app):
    """Create a test TA user"""
    from models.user import User
    
    with app.app_context():
        ta = User(
            name="Test TA",
            email="ta@test.com",
            role="ta"
        )
        ta.set_password("password123")
        
        db.session.add(ta)
        db.session.commit()
        db.session.refresh(ta)
        return ta

@pytest.fixture
def test_admin_user(init_database, app):
    """Create a test admin user"""
    from models.user import User
    
    with app.app_context():
        admin = User(
            name="Test Admin",
            email="admin@test.com",
            role="admin"
        )
        admin.set_password("password123")
        
        db.session.add(admin)
        db.session.commit()
        db.session.refresh(admin)
        return admin

# ================ FIXTURES FOR CONTROLLER TESTS ================

@pytest.fixture
def login_student(client):
    """Login as student for controller tests"""
    with client.session_transaction() as session:
        session['user_id'] = 1
        session['role'] = 'student'
    return client

@pytest.fixture
def login_instructor(client):
    """Login as instructor for controller tests"""
    with client.session_transaction() as session:
        session['user_id'] = 2
        session['role'] = 'instructor'
    return client

@pytest.fixture
def login_ta(client):
    """Login as TA for controller tests"""
    with client.session_transaction() as session:
        session['user_id'] = 3
        session['role'] = 'ta'
    return client

@pytest.fixture
def login_admin(client):
    """Login as admin for controller tests"""
    with client.session_transaction() as session:
        session['user_id'] = 4
        session['role'] = 'admin'
    return client

@pytest.fixture
def mock_user():
    """Mock user object for controller tests"""
    user = Mock()
    user.id = 1
    user.name = "Test User"
    user.email = "test@test.com"
    user.role = "student"
    user.login = Mock(return_value=user)
    return user

@pytest.fixture
def mock_student():
    """Mock student object for controller tests"""
    student = Mock()
    student.id = 1
    student.name = "Test Student"
    student.get_enrolled_courses = Mock(return_value=[])
    student.enroll_course = Mock(return_value=(True, "Success"))
    student.drop_course = Mock(return_value=(True, "Success"))
    student.is_enrolled_in_course = Mock(return_value=True)
    student.get_assignment_status = Mock(return_value={
        'submitted': False,
        'grade': None,
        'timestamp': None
    })
    return student

@pytest.fixture
def mock_instructor():
    """Mock instructor object for controller tests"""
    instructor = Mock()
    instructor.id = 2
    instructor.name = "Test Instructor"
    instructor.get_teaching_courses = Mock(return_value=[])
    instructor.is_teaching_course = Mock(return_value=True)
    return instructor

@pytest.fixture
def mock_ta():
    """Mock TA object for controller tests"""
    ta = Mock()
    ta.id = 3
    ta.name = "Test TA"
    ta.get_assigned_courses = Mock(return_value=[])
    ta.is_assigned_to_course = Mock(return_value=True)
    return ta

@pytest.fixture
def mock_course():
    """Mock course object for controller tests"""
    course = Mock()
    course.id = 1
    course.name = "Test Course"
    course.code = "TEST101"
    course.description = "A test course"
    course.get_announcements = Mock(return_value=[])
    course.get_assignments = Mock(return_value=[])
    course.get_enrolled_students = Mock(return_value=[])
    course.add_assignment = Mock(return_value=Mock())
    course.add_announcement = Mock(return_value=Mock())
    course.search_courses = Mock(return_value=[])
    course.enroll_student = Mock(return_value=True)
    course.drop_student = Mock(return_value=True)
    return course

@pytest.fixture
def mock_assignment():
    """Mock assignment object for controller tests"""
    assignment = Mock()
    assignment.id = 1
    assignment.title = "Test Assignment"
    assignment.description = "Complete this assignment"
    assignment.course_id = 1
    assignment.due_date = datetime.now() + timedelta(days=7)
    assignment.add_submission = Mock(return_value=(True, "Submission added"))
    assignment.get_all_submissions = Mock(return_value=[])
    assignment.grade_submission = Mock(return_value=(True, "Graded successfully"))
    assignment.get_submission = Mock(return_value=None)
    return assignment

@pytest.fixture
def mock_announcement():
    """Mock announcement object for controller tests"""
    announcement = Mock()
    announcement.id = 1
    announcement.title = "Test Announcement"
    announcement.content = "This is a test announcement"
    announcement.created_at = datetime.now()
    return announcement

@pytest.fixture
def mock_submission():
    """Mock submission object for controller tests"""
    submission = Mock()
    submission.id = 1
    submission.submission_text = "My submission"
    submission.grade = 85.0
    submission.feedback = "Good work"
    submission.assignment_id = 1
    submission.student_id = 1
    submission.submitted_at = datetime.now()
    return submission

# ================ HELPER FUNCTIONS ================

@pytest.fixture
def create_test_data(init_database, app):
    """Helper to create comprehensive test data"""
    def _create_data():
        from models.user import User
        from models.courses import Course
        from models.announcement import Announcement
        from models.assignment import Assignment
        from models.submission import Submission
        
        with app.app_context():
            # Create users
            student = User(name="John Student", email="student@test.com", role="student")
            student.set_password("password123")
            
            instructor = User(name="Dr. Instructor", email="instructor@test.com", role="instructor")
            instructor.set_password("password123")
            
            ta = User(name="TA Assistant", email="ta@test.com", role="ta")
            ta.set_password("password123")
            
            admin = User(name="Admin User", email="admin@test.com", role="admin")
            admin.set_password("password123")
            
            # Create course
            course = Course(
                name="Computer Science 101",
                code="CS101",
                description="Introduction to Computer Science",
                instructor_id=instructor.id,
                ta_id=ta.id,
                max_seats=30,
                credits=3
            )
            
            # Add all to session
            db.session.add_all([student, instructor, ta, admin, course])
            db.session.commit()
            
            # Create announcement
            announcement = Announcement(
                title="Welcome to CS101",
                content="Welcome to the course!",
                poster_id=instructor.id,
                course_id=course.id
            )
            
            # Create assignment
            assignment = Assignment(
                title="First Assignment",
                description="Complete the exercises",
                due_date=datetime.now() + timedelta(days=14),
                course_id=course.id
            )
            
            db.session.add_all([announcement, assignment])
            db.session.commit()
            
            return {
                'student': student,
                'instructor': instructor,
                'ta': ta,
                'admin': admin,
                'course': course,
                'announcement': announcement,
                'assignment': assignment
            }
    
    return _create_data

# ================ TEST SETUP AND TEARDOWN ================

def pytest_sessionstart(session):
    """Run before all tests"""
    print("\n" + "="*60)
    print("STARTING TEST SESSION")
    print("="*60)

def pytest_sessionfinish(session, exitstatus):
    """Run after all tests"""
    print("\n" + "="*60)
    print(f"TEST SESSION COMPLETE - Exit status: {exitstatus}")
    print("="*60)

@pytest.fixture(autouse=True)
def cleanup(request, app):
    """Auto-cleanup after each test"""
    yield
    
    # Optional: Print test result
    if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
        print(f"❌ Test failed: {request.node.name}")
    elif hasattr(request.node, 'rep_call'):
        print(f"✅ Test passed: {request.node.name}")