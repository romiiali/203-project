from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from models.ta import TA
from models.courses import Course
from models.user import User
from models.student import Student
from models.assignment import Assignment
from models.announcement import Announcement

ta_bp = Blueprint('ta', __name__, url_prefix='/ta')

@ta_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session or session.get('role') != 'ta':
        return redirect('/login')
    
    # Get TA info
    ta = TA.get_by_id(session['user_id'])
    if not ta:
        flash("TA not found", "error")
        return redirect('/login')
    
    # Get assigned courses
    courses = ta.get_assigned_courses()
    
    return render_template('ta/dashboard.html', courses=courses)

@ta_bp.route('/search_course', methods=['GET', 'POST'])
def search_course():
    if 'user_id' not in session or session.get('role') != 'ta':
        return redirect('/login')
    
    results = []
    if request.method == 'POST':
        query = request.form.get('query')
        if query:
            results = Course.search_courses(query)
    
    return render_template('ta/search_course.html', results=results)

@ta_bp.route('/search_student', methods=['GET', 'POST'])
def search_student():
    if 'user_id' not in session or session.get('role') != 'ta':
        return redirect('/login')
    
    results = []
    if request.method == 'POST':
        query = request.form.get('query')
        if query:
            results = User.search_users(query)
            # Filter for students only
            results = [user for user in results if user.role == 'student']
    
    return render_template('ta/search_student.html', results=results)

@ta_bp.route('/course/<int:course_id>')
def course_details(course_id):
    if 'user_id' not in session or session.get('role') != 'ta':
        return redirect('/login')
    
    course = Course.get_by_id(course_id)
    if not course:
        flash("Course not found", "error")
        return redirect(url_for('ta.dashboard'))
    
    # Get all students (for enrollment management)
    students = Student.get_all_students()
    
    return render_template('ta/course_details.html', course=course, students=students)

@ta_bp.route('/course/<int:course_id>/add_assignment', methods=['POST'])
def add_assignment(course_id):
    if 'user_id' not in session or session.get('role') != 'ta':
        return redirect('/login')
    
    course = Course.get_by_id(course_id)
    if not course:
        flash("Course not found", "error")
        return redirect(url_for('ta.dashboard'))
    
    title = request.form.get('title')
    description = request.form.get('description')
    due_date = request.form.get('due_date')
    
    if title and description and due_date:
        assignment = course.add_assignment(title, description, due_date)
        flash('Assignment added successfully!', 'success')
    else:
        flash('Please fill all fields', 'error')
    
    return redirect(url_for('ta.course_details', course_id=course_id))

@ta_bp.route('/course/<int:course_id>/add_announcement', methods=['POST'])
def add_announcement(course_id):
    if 'user_id' not in session or session.get('role') != 'ta':
        return redirect('/login')
    
    course = Course.get_by_id(course_id)
    if not course:
        flash("Course not found", "error")
        return redirect(url_for('ta.dashboard'))
    
    title = request.form.get('title')
    content = request.form.get('content')
    
    if title and content:
        announcement = course.add_announcement(title, content, session['user_id'])
        flash('Announcement added successfully!', 'success')
    else:
        flash('Please fill all fields', 'error')
    
    return redirect(url_for('ta.course_details', course_id=course_id))

@ta_bp.route('/course/<int:course_id>/attendance', methods=['GET', 'POST'])
def attendance(course_id):
    if 'user_id' not in session or session.get('role') != 'ta':
        return redirect('/login')
    
    course = Course.get_by_id(course_id)
    if not course:
        flash("Course not found", "error")
        return redirect(url_for('ta.dashboard'))
    
    students = course.get_enrolled_students()
    
    if request.method == 'POST':
        # Record attendance logic here
        flash('Attendance recorded successfully!', 'success')
        return redirect(url_for('ta.course_details', course_id=course_id))
        
    return render_template('ta/attendance.html', course=course, students=students)

@ta_bp.route('/assignment/<int:assignment_id>/submissions')
def view_submissions(assignment_id):
    if 'user_id' not in session or session.get('role') != 'ta':
        return redirect('/login')
    
    assignment = Assignment.get_by_id(assignment_id)
    if not assignment:
        flash("Assignment not found", "error")
        return redirect(url_for('ta.dashboard'))
    
    # Get all submissions
    submissions_data = assignment.get_all_submissions()
    
    # Convert to list of submission objects with student info
    submissions = []
    for student_id, submission_info in submissions_data.items():
        student = Student.get_by_id(student_id)
        if student:
            submissions.append({
                'student': student,
                'grade': submission_info.get('grade'),
                'feedback': submission_info.get('feedback'),
                'timestamp': submission_info.get('timestamp'),
                'text': submission_info.get('text'),
                'id': student_id  # Using student_id as submission id for now
            })
    
    return render_template('ta/assignment_submissions.html', 
                         assignment=assignment, 
                         submissions=submissions)

@ta_bp.route('/submission/<int:student_id>/grade', methods=['POST'])
def submit_grade(student_id):
    if 'user_id' not in session or session.get('role') != 'ta':
        return redirect('/login')
    
    assignment_id = request.form.get('assignment_id')
    grade = request.form.get('grade')
    feedback = request.form.get('feedback')
    
    assignment = Assignment.get_by_id(int(assignment_id)) if assignment_id else None
    
    if assignment and grade:
        success, message = assignment.grade_submission(student_id, grade, feedback)
        flash(message, 'success' if success else 'error')
    else:
        flash('Assignment not found or grade missing', 'error')
    
    return redirect(request.referrer or url_for('ta.dashboard'))

@ta_bp.route('/student/<int:student_id>')
def view_student(student_id):
    if 'user_id' not in session or session.get('role') != 'ta':
        return redirect('/login')
    
    student = Student.get_by_id(student_id)
    if not student:
        flash("Student not found", "error")
        return redirect(url_for('ta.search_student'))
    
    # Get courses the student is enrolled in
    enrolled_courses = student.get_enrolled_courses()
    
    return render_template('ta/student_profile.html', 
                         student=student, 
                         courses=enrolled_courses)