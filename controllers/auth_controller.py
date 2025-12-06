from flask import Blueprint, render_template, request, redirect, session, flash
from models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        selected_role = request.form.get('role', 'student')
        
        user = User.login(email, password)
        
        if user and user.role == selected_role:
            session['user_id'] = user.id
            session['role'] = user.role
            session['user_name'] = user.name
            
            if user.role == 'student':
                return redirect('/student/dashboard')
            elif user.role == 'instructor':
                return redirect('/instructor/dashboard')
            elif user.role == 'ta':
                return redirect('/ta/dashboard')
            elif user.role == 'admin':
                return redirect('/admin/dashboard')
        else:
            if user:
                flash(f"Please select '{user.role}' role to login", "error")
            else:
                flash("Invalid email or password", "error")
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully", "success")
    return redirect('/login')