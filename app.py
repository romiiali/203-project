from flask import Flask, session, redirect, url_for
from controllers.auth_controller import auth_bp
from controllers.student_controller import student_bp
from controllers.TA_controller import ta_bp
from controllers.admin_controller import admin_bp
from controllers.instructor_controller import instructor_bp

app = Flask(__name__)

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
    app.run(debug=True, port=5000)