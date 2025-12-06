from flask import Blueprint, render_template,redirect, request
from models.courses import Course
from models.people import Person

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
def dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/searchcourse')
def searchcourses():
    courses=Course.get_all_courses()
    return render_template('admin/searchcourse.html', courses=courses)

@admin_bp.route('/viewcourse/<int:course_code>')
def view_course(course_code):
    course = Course.get_course_by_id(course_code)
    students=Person.get_person_by_role("Student")
    return render_template('admin/viewcourse.html', course=course,students=students)

@app.route('/admin/editcourse/<int:course_code>', methods=['GET', 'POST'])
def edit_course_simple(course_code):
    # Get the course
    course = Course.get_course(course_code)
    people = Person.get_all_people()
    if not course:
        return "Course not found", 404
    
    if request.method == 'GET':
        return render_template('editcourse.html', course=course, people=people)
    
    if request.method == 'POST':
        # Simple form processing
        name = request.form['name']
        code = request.form['code']
        instructor = request.form['instructor']
        ta = request.form['ta']
        credits = request.form['credits']
        seats = request.form['seats']
        # Update course
        Course.edit_course(code, name, ta, instructor, int(credits), int(seats))
        return redirect('/')  # Redirect to home or courses page

@app.route('/addperson', methods=['GET', 'POST'])
def add_person():
    if request.method == 'GET':
        return render_template('addperson.html')
    if request.method == 'POST':
        name = request.form['name']
        id = request.form['id']
        role = request.form['Role']
        Person.add_person(name, id, role)
        return redirect('/admin')
    
@admin_bp.route('/searchpearson')
def searchpeople():
    people=Person.get_all_people()
    return render_template('admin/searchpeople.html', people=people)

@admin_bp.route("/editperson/<int:person_id>", methods=['GET', 'POST'])
def edit_person(person_id):
    person = Person.get_person_by_id(person_id)
    if not person:
        return "Person not found", 404
    
    if request.method == 'GET':
        return render_template('admin/editperson.html', person=person)
    
    if request.method == 'POST':
        name = request.form['name']
        id = request.form['id']
        role = request.form['Role']
        Person.edit_person(person_id, name, id, role)
        return redirect('/admin/searchpearson')
    

@admin_bp.route('/addcourse', methods=['GET','POST'])
def add_course():
    people = Person.get_all_people()
    if request.method == 'GET':
        return render_template('admin/addcourse.html', people=people)
    if request.method == 'POST':
        name = request.form['name']
        code = request.form['code']
        instructor = request.form['Instructor']
        ta = request.form['TA']
        credits = request.form['credits']
        seats = request.form['seats']
        Course.add_course(code, name, ta, instructor, int(credits), int(seats))
        return redirect('/admin')