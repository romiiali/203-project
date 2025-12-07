from flask import Blueprint, render_template, redirect, request, session, flash
from models.courses import Course
from models.people import People
from models.user import User

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
def dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    
    # Get statistics
    total_courses = len(Course.get_all())
    total_students = len(User.search_users_by_role('student'))
    total_instructors = len(User.search_users_by_role('instructor'))
    total_tas = len(User.search_users_by_role('ta'))
    
    return render_template('admin/dashboard.html', 
                         total_courses=total_courses,
                         total_students=total_students,
                         total_instructors=total_instructors,
                         total_tas=total_tas)

@admin_bp.route('/searchcourse')
def searchcourses():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    
    search_term = request.args.get('search', '')
    courses = Course.search_courses(search_term)
    
    return render_template('admin/searchcourse.html', courses=courses, search_term=search_term)

@admin_bp.route('/viewcourse/<int:course_id>')
def view_course(course_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    
    course = Course.get_by_id(course_id)
    if not course:
        flash("Course not found", "error")
        return redirect('/admin/searchcourse')
    
    students = course.get_enrolled_students()
    
    return render_template('admin/viewcourse.html', course=course, students=students)

@admin_bp.route('/editcourse/<int:course_code>', methods=['GET', 'POST'])
def edit_course(course_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    
    course = Course.get_by_id(course_id)
    if not course:
        flash("Course not found", "error")
        return redirect('/admin/searchcourse')
    
    if request.method == 'GET':
        # Get all users for instructor/TA selection
        instructors = User.search_users_by_role('instructor')
        tas = User.search_users_by_role('ta')
        
        return render_template('admin/editcourse.html', 
                             course=course, 
                             instructors=instructors, 
                             tas=tas)
    
    if request.method == 'POST':
        # Update course
        code = request.form.get('code')
        name = request.form.get('name')
        description = request.form.get('description')
        instructor_id = request.form.get('instructor_id')
        ta_id = request.form.get('ta_id')
        credits = request.form.get('credits')
        max_seats = request.form.get('max_seats')
        schedule = request.form.get('schedule')
        department = request.form.get('department')
        
        updated_course = Course.edit_course(
            course_id=course_id,
            code=code,
            name=name,
            description=description,
            instructor_id=int(instructor_id) if instructor_id else None,
            ta_id=int(ta_id) if ta_id else None,
            credits=int(credits) if credits else None,
            max_seats=int(max_seats) if max_seats else None,
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
        instructors = User.search_users_by_role('instructor')
        tas = User.search_users_by_role('ta')
        
        return render_template('admin/addcourse.html', instructors=instructors, tas=tas)
    
    if request.method == 'POST':
        code = request.form.get('code')
        name = request.form.get('name')
        description = request.form.get('description')
        instructor_id = request.form.get('instructor_id')
        ta_id = request.form.get('ta_id')
        credits = request.form.get('credits')
        max_seats = request.form.get('max_seats')
        schedule = request.form.get('schedule')
        department = request.form.get('department')
        
        if code and name and credits and max_seats:
            new_course = Course.add_course(
                code=code,
                name=name,
                description=description,
                instructor_id=int(instructor_id) if instructor_id else None,
                ta_id=int(ta_id) if ta_id else None,
                credits=int(credits),
                max_seats=int(max_seats),
                schedule=schedule,
                department=department
            )
            
            if new_course:
                flash('Course added successfully!', 'success')
                return redirect('/admin/searchcourse')
            else:
                flash('Failed to add course', 'error')
        else:
            flash('Please fill all required fields', 'error')
        
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
def searchpeople():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    
    search_term = request.args.get('search', '')
    people = People().search_people(search_term)
    
    return render_template('admin/searchpeople.html', people=people, search_term=search_term)

@admin_bp.route('/addperson', methods=['GET', 'POST'])
def add_person():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    
    if request.method == 'GET':
        return render_template('admin/addperson.html')
    
    if request.method == 'POST':
        name = request.form.get('name')
        person_id = request.form.get('id')
        role = request.form.get('role')
        
        if name and person_id and role:
            people_obj = People()
            updated_people = people_obj.add_person(name, person_id, role)
            
            if updated_people:
                flash('Person added successfully!', 'success')
                return redirect('/admin/searchpeople')
            else:
                flash('Failed to add person', 'error')
        else:
            flash('Please fill all fields', 'error')
        
        return redirect('/admin/addperson')

@admin_bp.route("/editperson/<string:person_id>", methods=['GET', 'POST'])
def edit_person(person_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    
    people_obj = People()
    person = people_obj.get_person(person_id)
    
    if not person:
        flash("Person not found", "error")
        return redirect('/admin/searchpeople')
    
    if request.method == 'GET':
        return render_template('admin/editperson.html', person=person)
    
    if request.method == 'POST':
        name = request.form.get('name')
        new_id = request.form.get('id')
        role = request.form.get('role')
        
        updated_person = people_obj.edit_person(name, new_id, role)
        
        if updated_person:
            flash('Person updated successfully!', 'success')
            return redirect('/admin/searchpeople')
        else:
            flash('Failed to update person', 'error')
            return redirect(f'/admin/editperson/{person_id}')

@admin_bp.route('/deleteperson/<string:person_id>')
def delete_person(person_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    
    people_obj = People()
    updated_people = people_obj.delete_person(person_id)
    
    if updated_people:
        flash('Person deleted successfully!', 'success')
    else:
        flash('Failed to delete person', 'error')
    
    return redirect('/admin/searchpeople')