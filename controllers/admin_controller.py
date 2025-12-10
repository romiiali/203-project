from flask import Blueprint, render_template, redirect, request, session, flash
from models.courses import Course
from models.user import User  # Changed from People to User
from app import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/searchpeople')
def searchpeople():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    
    search_term = request.args.get('search', '')
    people = User.search_users(search_term)  # Changed from People().search_people()
    
    return render_template('admin/searchpeople.html', people=people, search_term=search_term)

@admin_bp.route('/addperson', methods=['GET', 'POST'])
def add_person():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    
    if request.method == 'GET':
        return render_template('admin/addperson.html')
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')  # Added email field
        password = request.form.get('password')  # Added password field
        role = request.form.get('role')
        
        if name and email and password and role:
            # Check if email already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Email already registered', 'error')
                return redirect('/admin/addperson')
            
            # Create new user
            new_user = User(name=name, email=email, role=role.lower())
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            flash('Person added successfully!', 'success')
            return redirect('/admin/searchpeople')
        else:
            flash('Please fill all fields', 'error')
        
        return redirect('/admin/addperson')

@admin_bp.route("/editperson/<int:person_id>", methods=['GET', 'POST'])
def edit_person(person_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    
    person = User.query.get(person_id)  # Changed from People().get_person()
    
    if not person:
        flash("Person not found", "error")
        return redirect('/admin/searchpeople')
    
    if request.method == 'GET':
        return render_template('admin/editperson.html', person=person)
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')  # Added email
        role = request.form.get('role')
        password = request.form.get('password')  # Optional password update
        
        if not name or not email or not role:
            flash('Please fill all required fields', 'error')
            return redirect(f'/admin/editperson/{person_id}')
        
        # Check if email is taken by another user
        existing_user = User.query.filter(
            User.email == email,
            User.id != person_id
        ).first()
        if existing_user:
            flash('Email already registered to another user', 'error')
            return redirect(f'/admin/editperson/{person_id}')
        
        # Update user
        person.name = name
        person.email = email
        person.role = role.lower()
        
        if password:
            person.set_password(password)
        
        db.session.commit()
        
        flash('Person updated successfully!', 'success')
        return redirect('/admin/searchpeople')

@admin_bp.route('/deleteperson/<int:person_id>')
def delete_person(person_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    
    person = User.query.get(person_id)
    
    if person:
        db.session.delete(person)
        db.session.commit()
        flash('Person deleted successfully!', 'success')
    else:
        flash('Person not found', 'error')
    
    return redirect('/admin/searchpeople')

# Update the add_course method
@admin_bp.route('/addcourse', methods=['GET', 'POST'])
def add_course():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    
    if request.method == 'GET':
        instructors = User.query.filter_by(role='instructor').all()
        tas = User.query.filter_by(role='ta').all()
        
        return render_template('admin/addcourse.html', 
                             instructors=instructors, 
                             tas=tas)
    
    if request.method == 'POST':
        # Get form data
        code = request.form.get('code', '').strip()
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        instructor_id = request.form.get('instructor', '')
        ta_id = request.form.get('ta', '')
        credits = request.form.get('credits', '')
        max_seats = request.form.get('seats', '')
        schedule = request.form.get('schedule', 'TBA').strip()
        department = request.form.get('department', 'General').strip()
        
        # Validate required fields
        if not code or not name or not credits or not max_seats:
            flash('Please fill all required fields (Name, Code, Credits, Seats)', 'error')
            return redirect('/admin/addcourse')
        
        if code and name and credits and max_seats:
            # Check if course code already exists
            existing_course = Course.query.filter_by(code=code).first()
            if existing_course:
                flash('Course code already exists', 'error')
                return redirect('/admin/addcourse')
            
            # Create new course
            new_course = Course(
                code=code,
                name=name,
                description=description if description else f"Course: {name}",
                instructor_id=int(instructor_id) if instructor_id else None,
                ta_id=int(ta_id) if ta_id else None,
                credits=credits_int,
                max_seats=max_seats_int,
                schedule=schedule,
                department=department
            )
            
            db.session.add(new_course)
            db.session.commit()
            
            flash('Course added successfully!', 'success')
            return redirect('/admin/searchcourse')
        else:
            flash('Please fill all required fields', 'error')
        
        return redirect('/admin/addcourse')
