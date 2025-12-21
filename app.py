# app.py - REPLACE ENTIRE FILE WITH:
from flask import Flask, session, redirect, url_for
from config import Config
from extensions import db

def create_app(config_class=Config):
    """Create and configure the Flask application - FACTORY PATTERN"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    
    # Import all models
    with app.app_context():
        # Import models to register them with SQLAlchemy
        from models.user import User
        from models.student import Student
        from models.instructor import Instructor
        from models.ta import TA
        from models.admin import Admin
        from models.courses import Course
        from models.enrollment import Enrollment
        from models.assignment import Assignment
        from models.announcement import Announcement
        from models.submission import Submission
    
    # Import blueprints
    from controllers.auth_controller import auth_bp
    from controllers.student_controller import student_bp
    from controllers.TA_controller import ta_bp
    from controllers.admin_controller import admin_bp
    
    app.secret_key = app.config.get('SECRET_KEY', 'dev-secret-key-change-this')
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(ta_bp)
    app.register_blueprint(admin_bp)
    
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))
    
    return app

# Create app instance for running directly
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)