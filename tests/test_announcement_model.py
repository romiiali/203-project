import pytest
from datetime import datetime
from models.announcement import Announcement
from models.courses import Course
from models.user import User
from extensions import db

class TestAnnouncementModel:
    """Tests for Announcement model"""
    
    def test_announcement_creation(self, session_db):
        """Test creating a new announcement"""
        # Create course and poster
        course = Course(code="CS101", name="CS 101")
        poster = User(
            name="Instructor",
            email="instructor@test.com",
            role="instructor",
            password="password123"
        )
        
        session_db.add(course)
        session_db.add(poster)
        session_db.commit()
        
        # Create announcement
        announcement = Announcement(
            title="Important Announcement",
            content="Class is cancelled tomorrow",
            poster_id=poster.id,
            course_id=course.id
        )
        
        session_db.add(announcement)
        session_db.commit()
        
        assert announcement.id is not None
        assert announcement.title == "Important Announcement"
        assert announcement.content == "Class is cancelled tomorrow"
        assert announcement.poster_id == poster.id
        assert announcement.course_id == course.id
        assert announcement.created_at is not None
    
    def test_created_at_default(self, session_db):
        """Test that created_at is set automatically"""
        course = Course(code="CS101", name="CS 101")
        poster = User(
            name="Instructor",
            email="instructor@test.com",
            role="instructor",
            password="password123"
        )
        
        session_db.add(course)
        session_db.add(poster)
        session_db.commit()
        
        announcement = Announcement(
            title="Test",
            content="Test content",
            poster_id=poster.id,
            course_id=course.id
        )
        session_db.add(announcement)
        session_db.commit()
        
        assert announcement.created_at is not None
    
    def test_get_by_course(self, session_db):
        """Test getting announcements by course"""
        # Create course
        course = Course(code="CS101", name="CS 101")
        session_db.add(course)
        session_db.commit()
        
        # Create multiple posters
        posters = []
        for i in range(2):
            poster = User(
                name=f"Instructor{i}",
                email=f"instructor{i}@test.com",
                role="instructor",
                password="password123"
            )
            posters.append(poster)
            session_db.add(poster)
        
        session_db.commit()
        
        # Create announcements for the course
        announcements = []
        for i, poster in enumerate(posters):
            announcement = Announcement(
                title=f"Announcement {i+1}",
                content=f"Content {i+1}",
                poster_id=poster.id,
                course_id=course.id
            )
            announcements.append(announcement)
            session_db.add(announcement)
        
        session_db.commit()
        
        # Get announcements for course
        course_announcements = Announcement.get_by_course(course.id)
        assert len(course_announcements) == 2
        assert all(announcement.course_id == course.id for announcement in course_announcements)
        
        # Should be ordered by created_at descending
        dates = [announcement.created_at for announcement in course_announcements]
        assert dates == sorted(dates, reverse=True)
    
    def test_get_by_course_empty(self, session_db):
        """Test getting announcements for course with none"""
        course = Course(code="CS101", name="CS 101")
        session_db.add(course)
        session_db.commit()
        
        announcements = Announcement.get_by_course(course.id)
        assert len(announcements) == 0
    
    def test_relationships(self, session_db):
        """Test announcement relationships"""
        course = Course(code="CS101", name="CS 101")
        poster = User(
            name="Instructor",
            email="instructor@test.com",
            role="instructor",
            password="password123"
        )
        
        session_db.add(course)
        session_db.add(poster)
        session_db.commit()
        
        announcement = Announcement(
            title="Test",
            content="Test",
            poster_id=poster.id,
            course_id=course.id
        )
        session_db.add(announcement)
        session_db.commit()
        
        # Test relationships exist
        assert hasattr(announcement, 'poster_user')  # Relationship to User
        assert hasattr(announcement, 'course')  # From backref
    
    def test_foreign_key_constraints(self, session_db):
        """Test that announcement requires valid poster and course"""
        # Test with non-existent poster
        course = Course(code="CS101", name="CS 101")
        session_db.add(course)
        session_db.commit()
        
        announcement1 = Announcement(
            title="Test",
            content="Test",
            poster_id=99999,  # Non-existent
            course_id=course.id
        )
        session_db.add(announcement1)
        with pytest.raises(Exception):
            session_db.commit()
        session_db.rollback()
        
        # Test with non-existent course
        poster = User(
            name="Instructor",
            email="instructor@test.com",
            role="instructor",
            password="password123"
        )
        session_db.add(poster)
        session_db.commit()
        
        announcement2 = Announcement(
            title="Test",
            content="Test",
            poster_id=poster.id,
            course_id=99999  # Non-existent
        )
        session_db.add(announcement2)
        with pytest.raises(Exception):
            session_db.commit()
        
        session_db.rollback()
    
    def test_poster_user_relationship(self, session_db):
        """Test accessing poster through relationship"""
        course = Course(code="CS101", name="CS 101")
        poster = User(
            name="Dr. Smith",
            email="smith@test.com",
            role="instructor",
            password="password123"
        )
        
        session_db.add(course)
        session_db.add(poster)
        session_db.commit()
        
        announcement = Announcement(
            title="Test",
            content="Test",
            poster_id=poster.id,
            course_id=course.id
        )
        session_db.add(announcement)
        session_db.commit()
        
        # Access poster through relationship
        assert announcement.poster_user is not None
        assert announcement.poster_user.name == "Dr. Smith"
        assert announcement.poster_user.email == "smith@test.com"