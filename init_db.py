import sys
import os
from models.user import User

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from config import Config
from extensions import db
from sqlalchemy import text
from werkzeug.security import generate_password_hash

def create_app():
    """Create Flask application for database verification"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def update_password_hashes():
    """Update all password hashes to use scrypt method"""
    print("Updating password hashes to scrypt format...")
    
    users = User.query.all()
    updated_count = 0
    
    for user in users:
        # Generate new scrypt hash for password 'password123'
        new_hash = generate_password_hash('password123')
        user.password_hash = new_hash
        updated_count += 1
    
    db.session.commit()
    print(f"✅ Updated {updated_count} user passwords to scrypt format")
    return updated_count

def verify_database():
    """Verify the database is properly set up and update passwords if needed"""
    app = create_app()
    
    with app.app_context():
        print("="*60)
        print("DATABASE VERIFICATION & PASSWORD MIGRATION")
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
            
            # UPDATE ALL PASSWORD HASHES FIRST
            updated_count = update_password_hashes()
            
            # Now test authentication
            user = User.query.filter_by(email='admin@university.edu').first()
            if user:
                print(f"\n🔧 Testing authentication with updated password hash...")
                print(f"   Admin user: {user.name}")
                print(f"   New hash format: {user.password_hash[:20]}...")
                
                if user.check_password('password123'):
                    print(f"✅ Authentication test: Admin user password works!")
                else:
                    print(f"❌ Authentication test: Password verification still failing")
                    # Show more debug info
                    print(f"   Hash sample: {user.password_hash[:50]}...")
            else:
                print(f"❌ Authentication test: Admin user not found")
            
            print("\n" + "="*60)
            print("VERIFICATION COMPLETE")
            print("="*60)
            print(f"All {updated_count} users now have password: 'password123'")
            print("(Users should be prompted to change password on first login)")
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print("\nPlease run the SQL script in SQL Server Management Studio first!")
            return False
    
    return True

if __name__ == '__main__':
    print("Verifying database setup and migrating passwords...")
    verify_database()