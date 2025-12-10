import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from config import Config
from extensions import db
from models.user import User
from models.courses import Course
from models.enrollment import Enrollment
from models.assignment import Assignment
from models.announcement import Announcement
from models.submission import Submission

def create_app():
    """Create Flask application for database initialization"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions with app
    db.init_app(app)
    
    return app

def init_database():
    """Initialize the database with default data using Windows Auth"""
    app = create_app()
    
    with app.app_context():
        print("="*60)
        print("DATABASE INITIALIZATION (Windows Authentication)")
        print("="*60)
        
        # Get current connection info
        from sqlalchemy import text
        try:
            result = db.session.execute(text("SELECT SUSER_NAME() as windows_user, DB_NAME() as current_db"))
            row = result.fetchone()
            print(f"Connected as Windows User: {row.windows_user}")
            print(f"Current Database: {row.current_db}")
        except Exception as e:
            print(f"⚠️ Could not get connection info: {e}")
        
        print("\nCreating database tables...")
        
        try:
            # Create all tables
            db.create_all()
            print("✅ Tables created successfully")
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            print("\nPossible solutions:")
            print("1. Check if your Windows user has CREATE TABLE permission")
            print("2. Check if database 'CourseManagement' exists")
            print("3. Try running SSMS as administrator and creating tables manually")
            return
        
        # ... rest of your initialization code (same as before) ...
        
        print("\n" + "="*60)
        print("DATABASE INITIALIZATION COMPLETE")
        print("="*60)

if __name__ == '__main__':
    print("Initializing database with Windows Authentication...")
    init_database()