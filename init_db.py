import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from config import Config
from extensions import db
from sqlalchemy import text

def create_app():
    """Create Flask application for database verification"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def verify_database():
    """Verify the database is properly set up"""
    app = create_app()
    
    with app.app_context():
        print("="*60)
        print("DATABASE VERIFICATION")
        print("="*60)
        
        try:
            # Test connection
            result = db.session.execute(text("SELECT SUSER_NAME() as windows_user, DB_NAME() as current_db"))
            row = result.fetchone()
            print(f"✅ Connected as: {row.windows_user}")
            print(f"✅ Database: {row.current_db}")
            
            # Check table counts
            tables = ['users', 'courses', 'enrollments', 'assignments', 'announcements', 'submissions']
            
            for table in tables:
                try:
                    result = db.session.execute(text(f"SELECT COUNT(*) as count FROM {table}"))
                    count = result.fetchone().count
                    print(f"✅ {table}: {count} records")
                except Exception as e:
                    print(f"❌ {table}: Error - {e}")
            
            # Test login with dummy user
            from models.user import User
            user = User.query.filter_by(email='admin@university.edu').first()
            if user and user.check_password('password123'):
                print(f"✅ Authentication test: Admin user password works")
            else:
                print(f"❌ Authentication test: Password verification failed")
            
            print("\n" + "="*60)
            print("VERIFICATION COMPLETE")
            print("="*60)
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print("\nPlease run the SQL script in SQL Server Management Studio first!")
            return False
    
    return True

if __name__ == '__main__':
    print("Verifying database setup...")
    verify_database()