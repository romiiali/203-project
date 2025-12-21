# test_password.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from config import Config
from extensions import db
from werkzeug.security import check_password_hash

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

app = create_app()
with app.app_context():
    from models.user import User
    admin = User.query.filter_by(email='admin@university.edu').first()
    
    if admin:
        print(f"Admin found: {admin.name}")
        print(f"Email: {admin.email}")
        print(f"Password hash: {admin.password_hash}")
        print(f"Hash starts with: {admin.password_hash[:10]}")
        
        # Test the password
        test_password = 'password123'
        print(f"\nTesting password: {test_password}")
        
        # Try to verify
        try:
            result = check_password_hash(admin.password_hash, test_password)
            print(f"Password check result: {result}")
        except Exception as e:
            print(f"Error during password check: {e}")