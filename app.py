from flask import Blueprint, render_template, request, redirect, url_for
from models.courses import Course
from models.people import Person
from models.registration import Registration
from models.assignment import Assignment

instructor_bp = Blueprint('instructor', __name__, url_prefix='/instructor')

CURRENT_INSTRUCTOR = "Dr. Alice Johnson"

@instructor_bp.route('/')
def dashboard():
    my_courses = Course.get_courses_by_instructor(CURRENT_INSTRUCTOR)
    return render_template('instructor/course_list.html', courses=my_courses, instructor_name=CURRENT_INSTRUCTOR)

@instructor_bp.route('/course/<course_code>')
def open_course(course_code):
    course = Course.get_course_by_id(course_code)
    assignments = Assignment.get_assignments_by_course(course_code)
    return render_template('instructor/open_course.html', course=course, assignments=assignments)

@instructor_bp.route('/course/<course_code>/edit', methods=['GET', 'POST'])
def edit_course(course_code):
    course = Course.get_course_by_id(course_code)
    if request.method == 'POST':
        Course.edit_course(
            course_code, 
            request.form['name'], 
            request.form['ta'], 
            CURRENT_INSTRUCTOR, 
            request.form['credits'], 
            request.form['seats']
        )
        return redirect(url_for('instructor.open_course', course_code=course_code))
    return render_template('instructor/edit_course.html', course=course)

@instructor_bp.route('/course/<course_code>/students')
def student_list(course_code):
    course = Course.get_course_by_id(course_code)
    all_people = Person.get_all_people()
    enrolled_students = []
    for person in all_people:
        if person.role == "Student":
            student_courses = Registration.get_student_courses(person.id)
            if course_code in student_courses:
                enrolled_students.append(person)
                
    return render_template('instructor/student_list.html', course=course, students=enrolled_students)

@instructor_bp.route('/student/<student_id>')
def view_student(student_id):
    student = Person.get_person_by_id(student_id)
    return render_template('instructor/view_student.html', student=student)

@instructor_bp.route('/course/<course_code>/add_assignment', methods=['GET', 'POST'])
def send_assignment(course_code):
    if request.method == 'POST':
        Assignment.add_assignment(
            course_code,
            request.form['title'],
            request.form['description'],
            request.form['due_date']
        )
        return redirect(url_for('instructor.open_course', course_code=course_code))
    return render_template('instructor/send_assignment.html', course_code=course_code)