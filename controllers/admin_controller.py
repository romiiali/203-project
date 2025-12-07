from flask import Blueprint, render_template, redirect, request, session, flash
from models.courses import Course
from models.user import User

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    
    # Get statistics
    total_courses = len(Course.get_all())
    total_students = len([u for u in User.get_all() if u.role == 'student'])
    total_instructors = len([u for u in User.get_all() if u.role == 'instructor'])
    total_tas = len([u for u in User.get_all() if u.role == 'ta'])
    
    return render_template('admin/dashboard.html', 
                         total_courses=total_courses,
                         total_students=total_students,
                         total_instructors=total_instructors,
                         total_tas=total_tas)

@admin_bp.route('/searchcourse')
def search_courses():  # Renamed for consistency
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    
    search_term = request.args.get('search', '')
    courses = Course.search_courses(search_term)
    
    return render_template('admin/searchcourse.html', 
                         courses=courses, 
                         search_query=search_term)  # Changed from search_term to search_query

@admin_bp.route('/viewcourse/<int:course_id>')
def view_course(course_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    
    course = Course.get_by_id(course_id)
    if not course:
        flash("Course not found", "error")
        return redirect('/admin/searchcourse')
    
    instructor = course.get_instructor()
    ta = course.get_ta()
    
    students = course.get_enrolled_students()
    
    return render_template('admin/viewcourse.html', 
                         course=course, 
                         instructor=instructor,
                         ta=ta,
                         students=students)

@admin_bp.route('/editcourse/<int:course_id>', methods=['GET', 'POST'])
def edit_course(course_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    
    course = Course.get_by_id(course_id)
    if not course:
        flash("Course not found", "error")
        return redirect('/admin/searchcourse')
    
    if request.method == 'GET':
        # Get all users for instructor/TA selection
        all_users = User.get_all()
        instructors = [u for u in all_users if u.role == 'instructor']
        tas = [u for u in all_users if u.role == 'ta']
        
        return render_template('admin/editcourse.html', 
                             course=course, 
                             instructors=instructors, 
                             tas=tas)
    
    if request.method == 'POST':
        # Update course
        code = request.form.get('code')
        name = request.form.get('name')
        description = request.form.get('description', course.description)
        instructor_id = request.form.get('instructor')
        ta_id = request.form.get('ta')
        credits = request.form.get('credits')
        max_seats = request.form.get('seats')
        schedule = request.form.get('schedule', course.schedule)
        department = request.form.get('department', course.department)
        
        updated_course = Course.edit_course(
            course_id=course_id,
            code=code if code else course.code,
            name=name if name else course.name,
            description=description,
            instructor_id=int(instructor_id) if instructor_id else course.instructor_id,
            ta_id=int(ta_id) if ta_id else course.ta_id,
            credits=int(credits) if credits else course.credits,
            max_seats=int(max_seats) if max_seats else course.max_seats,
            schedule=schedule,
            department=department
        )
        
        if updated_course:
            flash('Course updated successfully!', 'success')
        else:
            flash('Failed to update course', 'error')
        
        return redirect(f'/admin/viewcourse/{course_id}')

@admin_bp.route('/addcourse', methods=['GET', 'POST'])
def add_course():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    
    if request.method == 'GET':
        all_users = User.get_all()
        instructors = [u for u in all_users if getattr(u, 'role', '').lower() == 'instructor']
        tas = [u for u in all_users if getattr(u, 'role', '').lower() == 'ta']
        
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
        
        try:
            # Convert to proper types
            credits_int = int(credits)
            max_seats_int = int(max_seats)
            
            # Create the course
            new_course = Course.add_course(
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
            
            if new_course:
                flash(f'Course "{name}" added successfully!', 'success')
                # REDIRECT TO DASHBOARD AFTER SUCCESS
                return redirect('/admin/dashboard')
            else:
                flash('Failed to add course', 'error')
                
        except ValueError:
            flash('Please enter valid numbers for Credits and Seats', 'error')
        
        except Exception as e:
            flash(f'Error adding course: {str(e)}', 'error')
        
        # If there's an error, stay on the add course page
        return redirect('/admin/addcourse')

@admin_bp.route('/deletecourse/<int:course_id>')
def delete_course(course_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    
    success = Course.delete_course(course_id)
    
    if success:
        flash('Course deleted successfully!', 'success')
    else:
        flash('Failed to delete course', 'error')
    
    return redirect('/admin/searchcourse')

@admin_bp.route('/searchpeople')
def search_people():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    
    search_term = request.args.get('search', '')
    
    # Try to get all users
    try:
        all_users = User.get_all()
    except AttributeError:
        # Fallback if User.get_all() doesn't exist
        all_users = []
    
    # Filter if search term exists
    if search_term:
        search_lower = search_term.lower()
        filtered = []
        for user in all_users:
            if (search_lower in user.name.lower() or 
                search_lower in getattr(user, 'role', '').lower() or
                search_lower in str(getattr(user, 'id', '')).lower()):
                filtered.append(user)
        people = filtered
    else:
        people = all_users
    
    return render_template('admin/searchpeople.html', 
                         people=people, 
                         search_query=search_term)

@admin_bp.route('/addperson', methods=['GET', 'POST'])
def add_person():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    
    if request.method == 'GET':
        return render_template('admin/addperson.html', 
                             roles=['student', 'instructor', 'ta', 'admin'])
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        person_id = request.form.get('id', '').strip()
        role = request.form.get('role', '').strip().lower()
        email = request.form.get('email', '').strip()
        password = request.form.get('pass', '').strip()
        
        # Validate required fields
        if not all([name, person_id, role, email, password]):
            flash('Please fill all required fields', 'error')
            return redirect('/admin/addperson')  # Redirect back to form
        
        # Validate role
        if role not in ['student', 'instructor', 'ta', 'admin']:
            flash('Please select a valid role', 'error')
            return redirect('/admin/addperson')
        
        # Success - in real system, save to database
        # For demo, just show success message
        
        flash(f'✅ Person "{name}" (ID: {person_id}) added as {role}!', 'success')
        return redirect('/admin/dashboard')  # Always redirect to dashboard after POST

@admin_bp.route("/editperson/<string:person_id>", methods=['GET', 'POST'])
def edit_person(person_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    
    # Try to find user
    user = None
    for u in User.get_all():
        if str(u.id) == person_id:
            user = u
            break
    
    if not user:
        flash("Person not found", "error")
        return redirect('/admin/searchpeople')
    
    if request.method == 'GET':
        return render_template('admin/editperson.html', person=user)
    
    if request.method == 'POST':
        name = request.form.get('name')
        new_id = request.form.get('ID')
        role = request.form.get('role')
        
        if name:
            user.name = name
        if new_id:
            user.id = int(new_id)
        if role:
            user.role = role.lower()
        
        flash('Person updated successfully! (Demo mode - not saved to DB)', 'success')
        return redirect('/admin/searchpeople')

@admin_bp.route('/deleteperson/<string:person_id>')
def delete_person(person_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    
    flash(f'Person {person_id} deleted! (Demo mode - not actually deleted)', 'success')
    return redirect('/admin/searchpeople')