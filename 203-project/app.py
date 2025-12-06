from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User 

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scrs.db'

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from controllers.admin_controller import admin_bp
app.register_blueprint(admin_bp)
from controllers.instructor_controller import instructor_bp
from controllers.TA_controller import ta_bp

app.register_blueprint(instructor_bp)
app.register_blueprint(ta_bp) 
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.password == password:
            login_user(user)
            if user.role == 'instructor':
                return redirect(url_for('instructor.dashboard'))
            elif user.role == 'ta':
                return redirect(url_for('ta.dashboard'))
            elif user.role == 'student':
                return "Student Portal Coming Soon" 
            else:
                return redirect(url_for('home'))
        else:
            flash('Invalid Email or Password', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
