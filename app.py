from flask import Flask, session, redirect, url_for
from config import Config
from extensions import db

# Initialize app first
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# NOW import models (after db is initialized with app)
with app.app_context():
    # This ensures models are loaded in app context
    from models.user import User
    from models.courses import Course
    from models.enrollment import Enrollment
    from models.assignment import Assignment
    from models.announcement import Announcement
    from models.submission import Submission

# Now import blueprints
from controllers.auth_controller import auth_bp
from controllers.student_controller import student_bp
from controllers.TA_controller import ta_bp
from controllers.admin_controller import admin_bp
# from controllers.instructor_controller import instructor_bp

app.secret_key = 'dev-secret-key-change-this'

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)
app.register_blueprint(ta_bp)
app.register_blueprint(admin_bp)
# app.register_blueprint(instructor_bp)

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(debug=True, port=5000)
