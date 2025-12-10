from flask import Flask, session, redirect, url_for
from config import Config
from extensions import db  # Import from extensions

# Import blueprints
from controllers.auth_controller import auth_bp
from controllers.student_controller import student_bp
from controllers.TA_controller import ta_bp
from controllers.admin_controller import admin_bp
from controllers.instructor_controller import instructor_bp

app = Flask(__name__)

# Load configuration
app.config.from_object(Config)

# Initialize extensions with app
db.init_app(app)

app.secret_key = 'dev-secret-key-change-this'

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)
app.register_blueprint(ta_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(instructor_bp)

@app.route('/')
def index():
    # Redirect to login page by default
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    # Create tables if they don't exist (optional)
    with app.app_context():
        db.create_all()
    
    app.run(debug=True, port=5000)