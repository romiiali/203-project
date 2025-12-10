from flask import Blueprint, render_template, request, redirect, session, flash
from models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.login(email, password)
        if user:
            session['user_id'] = user.id
            
            if user.role == 'student':
                return redirect('/student/dashboard')
            elif user.role == 'instructor':
                return redirect('/instructor/dashboard')
            elif user.role == 'ta':
                return redirect('/ta/dashboard')
            elif user.role == 'admin':
                return redirect('/admin/dashboard')
            else:
                flash("Unknown user role", "error")
                session.pop('user_id', None)
                return redirect('/login')
    else:
        flash("Invalid email or password", "error")
    
    return render_template('/login')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully", "success")
    return redirect('/login')