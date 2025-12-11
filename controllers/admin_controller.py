from flask import Blueprint, render_template, redirect, request, session, flash
from models.courses import Course
from models.user import User  # Changed from People to User
from extensions import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    
    return render_template('admin/dashboard.html')

@admin_bp.route('/searchcourse')
def searchcourse():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    
    search_term = request.args.get('search', '')
    courses = Course.search_courses(search_term)
    
    return render_template('admin/searchcourse.html', courses=courses, search_term=search_term)

@admin_bp.route('/viewcourse/<int:course_id>')
def view_course(course_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    
    course = Course.query.get(course_id)
    students = course.get_enrolled_students()
    if not course:
        flash("Course not found", "error")
        return redirect('/admin/searchcourse')
    
    return render_template('admin/viewcourse.html', course=course, students=students)

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
        
        if name and email and password and role and id:
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
        
        return redirect('/admin/dashboard')

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
        
      
        
        # Check if email is taken by another user
        if email and email !=person.email:
            existing_user = User.query.filter(
                User.email == email,
                User.id != person_id
            ).first()
            if existing_user:
                flash('Email already registered to another user', 'error')
                return redirect(f'/admin/editperson/{person_id}')
        
        # Update user
        if name:
            person.name = name
        if email:
            person.email = email
        if role:
            person.role = role.lower()
        if password:
            person.set_password(password)
        
        db.session.commit()
        
        flash('Person updated successfully!', 'success')
        return redirect(f'/admin/searchpeople')

@admin_bp.route('/editcourse/<int:course_id>', methods=['GET', 'POST'])
def edit_course(course_id): 
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    
    course = Course.query.get(course_id)
    
    if not course:
        flash("Course not found", "error")
        return redirect('/admin/searchcourse')
    
    if request.method == 'GET':
        instructors = User.query.filter_by(role='instructor').all()
        tas = User.query.filter_by(role='ta').all()
        
        return render_template('admin/editcourse.html', 
                             course=course, 
                             instructors=instructors, 
                             tas=tas)
    
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        instructor_id = request.form.get('instructor', '')
        ta_id = request.form.get('ta', '')
        credits = request.form.get('credits', '')
        max_seats = request.form.get('seats', '')
        schedule = request.form.get('schedule', 'TBA').strip()
        department = request.form.get('department', 'General').strip()
        
        
        # Check if course code already exists for another course
        existing_course = Course.query.filter(
            Course.code == code,
            Course.id != course_id
        ).first()
        if existing_course:
            flash('Course code already exists', 'error')
            return redirect(f'/admin/editcourse/{course_id}')
        
        # Update course details
        if code:
            course.code = code
        if name:
            course.name = name
        if description:   
            course.description = description
        if instructor_id:  
            course.instructor_id = int(instructor_id) if instructor_id != 'None' else None
        if ta_id:  
            course.ta_id = int(ta_id) if ta_id != 'None' else None
        if credits: 
            course.credits = int(credits) if credits.isdigit() else course.credits
        if max_seats:  
            new_max_seats = int(max_seats) if max_seats.isdigit() else course.max_seats
            seat_difference = new_max_seats - course.max_seats
            course.max_seats = new_max_seats
            course.seats_left = max(0, course.seats_left + seat_difference)
        if schedule:  
            course.schedule = schedule
        if department:  
            course.department = department
        
        db.session.commit()
        
        flash('Course updated successfully!', 'success')
        return redirect(f'/admin/viewcourse/{course_id}')

@admin_bp.route('/deleteperson/<int:person_id>')
def delete_person(person_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    
    person = User.query.get(person_id)
    
    if person:
        if person.role == 'admin':
            flash('Cannot delete an admin user', 'error')
            return redirect('/admin/searchpeople')
        if person.role=='instructor':
            Course.query.filter_by(instructor_id=person_id).update({'instructor_id': None})
            from models.announcement import Announcement
            Announcement.query.filter_by(poster_id=person_id).update({'poster_id': None})
        if person.role=='ta':
            Course.query.filter_by(ta_id=person_id).update({'ta_id': None})
            from models.announcement import Announcement
            Announcement.query.filter_by(poster_id=person_id).update({'poster_id': None})
        if person.role=='student':
            from models.enrollment import Enrollment
            Enrollment.query.filter_by(student_id=person_id).delete()

            from models.submission import Submission
            Submission.query.filter_by(student_id=person_id).delete()

        db.session.delete(person)
        db.session.commit()
        flash('Person deleted successfully!', 'success')
    else:
        flash('Person not found', 'error')
    
    return redirect('/admin/searchpeople')

@admin_bp.route('/deletecourse/<int:course_id>')
def delete_course(course_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    
    course = Course.query.get(course_id)
    
    if course:
        db.session.delete(course)
        db.session.commit()
        flash('Course deleted successfully!', 'success')
    else:
        flash('Course not found', 'error')
    
    return redirect('/admin/searchcourse')

@admin_bp.route('/dropstudent/<int:course_id>/<int:student_id>')
def drop_student(course_id, student_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    
    course = Course.query.get(course_id)
    
    if course:
        success = course.drop_student(student_id)
        if success:
            flash('Student dropped successfully!', 'success')
        else:
            flash('Student not enrolled in this course', 'error')
    else:
        flash('Course not found', 'error')
    
    return redirect(f'/admin/viewcourse/{course_id}')

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
                credits=credits,
                max_seats=max_seats,
                schedule=schedule,
                department=department
            )
            
            db.session.add(new_course)
            db.session.commit()
            
            flash('Course added successfully!', 'success')
            return redirect('/admin/searchcourse')
        else:
            flash('Please fill all required fields', 'error')
        
        return redirect('/admin/searchcourse')
