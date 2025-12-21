from models.instructor import Instructor
from models.user import User
from extensions import db
from models.student import Student
from models.ta import TA    
class Admin(User):
    
    def __init__(self, name, email, password=None):
        super().__init__(name=name, email=email, role='admin', password=password)
    
    def get_all_users(self):
        """Get all users in the system"""
        return User.query.all()
    
    def create_user(self, name, email, role, password="password123", **kwargs):
        """Create a new user with password validation"""
        # Ensure password is not empty
        if not password or password.strip() == "":
            password = "password123"
        
        user_class = {
            'student': Student,
            'instructor': Instructor,
            'ta': TA,
            'admin': Admin
        }.get(role.lower(), User)
        
        user = user_class(name=name, email=email, password=password, **kwargs)
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def get_all():
        return Admin.query.filter_by(role='admin').all()
    
    @staticmethod
    def get_by_id(admin_id):
        return Admin.query.filter_by(id=admin_id, role='admin').first()