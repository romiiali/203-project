import pytest
from unittest.mock import Mock, patch, MagicMock
from werkzeug.security import check_password_hash, generate_password_hash
from models.user import User
from extensions import db

class TestUserModel:
    """Tests for User model"""
    
    def test_user_creation(self, session_db):
        """Test creating a new user"""
        user = User(
            name="Test User",
            email="test@example.com",
            role="student",
            password="password123"
        )
        
        session_db.add(user)
        session_db.commit()
        
        assert user.id is not None
        assert user.name == "Test User"
        assert user.email == "test@example.com"
        assert user.role == "student"
        assert user.password_hash is not None
        assert check_password_hash(user.password_hash, "password123")
    
    def test_set_password(self, session_db):
        """Test password hashing"""
        user = User(name="Test", email="test@test.com", role="student")
        user.set_password("mypassword")
        
        assert user.password_hash is not None
        assert check_password_hash(user.password_hash, "mypassword")
        assert not check_password_hash(user.password_hash, "wrongpassword")
    
    def test_check_password(self, session_db):
        """Test password verification"""
        user = User(name="Test", email="test@test.com", role="student")
        user.set_password("secure123")
        
        assert user.check_password("secure123") is True
        assert user.check_password("wrong") is False
    
    def test_login_success(self, session_db):
        """Test successful login"""
        # Create a user first
        user = User(
            name="Test User",
            email="test@example.com",
            role="student",
            password="password123"
        )
        session_db.add(user)
        session_db.commit()
        
        # Test login
        result = User.login("test@example.com", "password123")
        assert result is not None
        assert result.email == "test@example.com"
        assert result.role == "student"
    
    def test_login_failure_wrong_password(self, session_db):
        """Test login with wrong password"""
        user = User(
            name="Test User",
            email="test@example.com",
            role="student",
            password="password123"
        )
        session_db.add(user)
        session_db.commit()
        
        result = User.login("test@example.com", "wrongpassword")
        assert result is None
    
    def test_login_failure_no_user(self):
        """Test login with non-existent email"""
        result = User.login("nonexistent@test.com", "password123")
        assert result is None
    
    def test_get_by_id(self, session_db):
        """Test retrieving user by ID"""
        user = User(
            name="Test User",
            email="test@example.com",
            role="student",
            password="password123"
        )
        session_db.add(user)
        session_db.commit()
        
        retrieved = User.get_by_id(user.id)
        assert retrieved is not None
        assert retrieved.id == user.id
        assert retrieved.email == user.email
    
    def test_get_all_people(self, session_db):
        """Test getting all users"""
        # Create multiple users
        users = [
            User(name="User1", email="user1@test.com", role="student", password="pass1"),
            User(name="User2", email="user2@test.com", role="instructor", password="pass2"),
            User(name="User3", email="user3@test.com", role="ta", password="pass3")
        ]
        
        for user in users:
            session_db.add(user)
        session_db.commit()
        
        all_users = User.get_all_people()
        assert len(all_users) >= 3
    
    def test_search_users_by_role(self, session_db):
        """Test searching users by role"""
        # Create users with different roles
        student = User(name="Student", email="student@test.com", role="student", password="pass")
        instructor = User(name="Instructor", email="instructor@test.com", role="instructor", password="pass")
        
        session_db.add(student)
        session_db.add(instructor)
        session_db.commit()
        
        students = User.search_users_by_role("student")
        assert len(students) >= 1
        assert all(user.role == "student" for user in students)
    
    def test_search_users_with_term(self, session_db):
        """Test searching users with search term"""
        users = [
            User(name="John Doe", email="john@test.com", role="student", password="pass"),
            User(name="Jane Smith", email="jane@test.com", role="instructor", password="pass")
        ]
        
        for user in users:
            session_db.add(user)
        session_db.commit()
        
        # Search by name
        results = User.search_users("John")
        assert len(results) >= 1
        assert any("John" in user.name for user in results)
        
        # Search by email
        results = User.search_users("jane@test.com")
        assert len(results) >= 1
        assert any(user.email == "jane@test.com" for user in results)
        
        # Search by role
        results = User.search_users("instructor")
        assert len(results) >= 1
        assert any(user.role == "instructor" for user in results)
    
    def test_search_users_empty_term(self, session_db):
        """Test searching users with empty term returns all"""
        users = [
            User(name="User1", email="user1@test.com", role="student", password="pass"),
            User(name="User2", email="user2@test.com", role="instructor", password="pass")
        ]
        
        for user in users:
            session_db.add(user)
        session_db.commit()
        
        results = User.search_users("")
        assert len(results) >= 2
    
    def test_add_person_success(self, session_db):
        """Test adding a new person successfully"""
        result = User.add_person(
            name="New User",
            email="new@test.com",
            role="student",
            password="password123"
        )
        
        assert result is not None
        assert result.name == "New User"
        assert result.email == "new@test.com"
        assert result.role == "student"
        
        # Verify it was saved
        user_in_db = session_db.query(User).filter_by(email="new@test.com").first()
        assert user_in_db is not None
    
    def test_add_person_duplicate_email(self, session_db):
        """Test adding person with existing email"""
        # Create existing user
        existing = User(
            name="Existing User",
            email="existing@test.com",
            role="student",
            password="password123"
        )
        session_db.add(existing)
        session_db.commit()
        
        # Try to add with same email
        result = User.add_person(
            name="New User",
            email="existing@test.com",
            role="student",
            password="password123"
        )
        
        assert result is None
    
    def test_edit_person_success(self, session_db):
        """Test editing a person successfully"""
        # Create a user to edit
        user = User(
            name="Original Name",
            email="original@test.com",
            role="student",
            password="original123"
        )
        session_db.add(user)
        session_db.commit()
        
        # Edit the user
        result = User.edit_person(
            user.id,
            name="Updated Name",
            email="updated@test.com",
            role="instructor",
            password="newpassword123"
        )
        
        assert result is not None
        assert result.name == "Updated Name"
        assert result.email == "updated@test.com"
        assert result.role == "instructor"
        assert result.check_password("newpassword123")
    
    def test_edit_person_email_taken(self, session_db):
        """Test editing person with email taken by another user"""
        # Create two users
        user1 = User(
            name="User1",
            email="user1@test.com",
            role="student",
            password="pass1"
        )
        user2 = User(
            name="User2",
            email="user2@test.com",
            role="instructor",
            password="pass2"
        )
        session_db.add(user1)
        session_db.add(user2)
        session_db.commit()
        
        # Try to change user1's email to user2's email
        result = User.edit_person(
            user1.id,
            email="user2@test.com"  # Already taken by user2
        )
        
        assert result is None
    
    def test_edit_person_partial_update(self, session_db):
        """Test editing person with partial data"""
        user = User(
            name="Original",
            email="original@test.com",
            role="student",
            password="original123"
        )
        session_db.add(user)
        session_db.commit()
        
        # Only update name
        result = User.edit_person(user.id, name="Updated Name")
        
        assert result is not None
        assert result.name == "Updated Name"
        assert result.email == "original@test.com"  # Unchanged
        assert result.role == "student"  # Unchanged
        assert result.check_password("original123")  # Unchanged
    
    def test_delete_person_success(self, session_db):
        """Test deleting a person successfully"""
        user = User(
            name="To Delete",
            email="delete@test.com",
            role="student",
            password="password123"
        )
        session_db.add(user)
        session_db.commit()
        
        user_id = user.id
        
        # Delete the user
        result = User.delete_person(user_id)
        assert result is True
        
        # Verify deletion
        deleted_user = session_db.query(User).get(user_id)
        assert deleted_user is None
    
    def test_delete_person_not_found(self):
        """Test deleting non-existent person"""
        result = User.delete_person(99999)  # Non-existent ID
        assert result is False
    
    def test_to_dict(self, session_db):
        """Test converting user to dictionary"""
        user = User(
            name="Test User",
            email="test@example.com",
            role="student",
            password="password123"
        )
        session_db.add(user)
        session_db.commit()
        
        user_dict = user.to_dict()
        
        assert user_dict['id'] == user.id
        assert user_dict['name'] == "Test User"
        assert user_dict['email'] == "test@example.com"
        assert user_dict['role'] == "Student"  # Capitalized in to_dict
        assert 'created_at' in user_dict
    
    def test_relationships(self, session_db):
        """Test user relationships"""
        user = User(
            name="Instructor User",
            email="instructor@test.com",
            role="instructor",
            password="password123"
        )
        session_db.add(user)
        session_db.commit()
        
        # Test relationships exist
        assert hasattr(user, 'courses_instructing')
        assert hasattr(user, 'courses_ta')
        assert hasattr(user, 'submissions')
        assert hasattr(user, 'announcements_posted')
    
    def test_unique_email_constraint(self, session_db):
        """Test that email must be unique"""
        user1 = User(
            name="User1",
            email="duplicate@test.com",
            role="student",
            password="pass1"
        )
        user2 = User(
            name="User2",
            email="duplicate@test.com",  # Same email
            role="instructor",
            password="pass2"
        )
        
        session_db.add(user1)
        session_db.commit()
        
        # Second user with same email should raise integrity error
        session_db.add(user2)
        with pytest.raises(Exception):
            session_db.commit()
        
        session_db.rollback()
    
    def test_get_person_alias(self, session_db):
        """Test get_person alias method"""
        user = User(
            name="Test User",
            email="test@example.com",
            role="student",
            password="password123"
        )
        session_db.add(user)
        session_db.commit()
        
        # Both methods should return the same
        by_id = User.get_by_id(user.id)
        by_person = user.get_person(user.id)
        
        assert by_id is not None
        assert by_person is not None
    
    def test_get_person_by_role_instance(self, session_db):
        """Test instance method get_person_by_role"""
        user = User(
            name="Test User",
            email="test@example.com",
            role="student",
            password="password123"
        )
        session_db.add(user)
        session_db.commit()
        
        # Also add an instructor
        instructor = User(
            name="Instructor",
            email="instructor@test.com",
            role="instructor",
            password="password123"
        )
        session_db.add(instructor)
        session_db.commit()
        
        # Get students using instance method
        students = user.get_person_by_role("student")
        assert len(students) >= 1
        assert all(u.role == "student" for u in students)