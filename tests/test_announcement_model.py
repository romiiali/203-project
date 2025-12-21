# tests/test_announcement.py
import pytest
from datetime import datetime
from models.announcement import Announcement
from models.user import User
from models.courses import Course
from extensions import db

class TestAnnouncement:
    """Test cases for Announcement model"""
    
    def test_announcement_creation(self, init_database, test_user, test_course):
        """Test creating an announcement"""
        announcement = Announcement(
            title="Test Announcement",
            content="This is a test announcement",
            poster_id=test_user.id,
            course_id=test_course.id
        )
        
        db.session.add(announcement)
        db.session.commit()
        
        assert announcement.id is not None
        assert announcement.title == "Test Announcement"
        assert announcement.content == "This is a test announcement"
        assert announcement.poster_id == test_user.id
        assert announcement.course_id == test_course.id
        assert isinstance(announcement.created_at, datetime)
    
    def test_announcement_relationships(self, init_database, test_announcement):
        """Test announcement relationships"""
        announcement = test_announcement
        
        # Test poster relationship
        assert announcement.poster is not None
        assert isinstance(announcement.poster, User)
        
        # Test course relationship (assuming Course model exists)
        assert announcement.course_id is not None
    
    def test_announcement_get_by_course(self, init_database, test_course):
        """Test getting announcements by course ID"""
        # Create multiple announcements
        for i in range(3):
            announcement = Announcement(
                title=f"Announcement {i}",
                content=f"Content {i}",
                poster_id=1,  # Assuming user with id=1 exists
                course_id=test_course.id
            )
            db.session.add(announcement)
        db.session.commit()
        
        # Get announcements for course
        announcements = Announcement.get_by_course(test_course.id)
        
        assert len(announcements) >= 3
        # Should be ordered by created_at descending
        for i in range(len(announcements) - 1):
            assert announcements[i].created_at >= announcements[i + 1].created_at
    
    def test_announcement_required_fields(self, init_database):
        """Test that required fields cannot be null"""
        announcement = Announcement()
        
        with pytest.raises(Exception):
            db.session.add(announcement)
            db.session.commit()
    
    def test_announcement_string_representation(self, test_announcement):
        """Test string representation of announcement"""
        announcement = test_announcement
        # Add __repr__ method to Announcement model for better testing
        assert announcement.title in str(announcement)