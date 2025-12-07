from flask import Blueprint, render_template, request, redirect, session, flash
from models.student import Student
from models.courses import Course
from models.announcement import Announcement
from models.assignment import Assignment

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect('/login')
    
    student = Student.get_by_id(session['user_id'])
    if not student:
        flash("Student not found", "error")
        return redirect('/login')
    
    enrolled_courses = student.get_enrolled_courses()
    
    return render_template('student/student-dashboard.html', 
                         student=student, 
                         enrolled_courses=enrolled_courses)

@student_bp.route('/courses')
def view_courses():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect('/login')
    
    student = Student.get_by_id(session['user_id'])
    enrolled_courses = student.get_enrolled_courses()
    
    return render_template('student/student-enrolled-courses.html', 
                         student=student, 
                         courses=enrolled_courses)

@student_bp.route('/search')
def search_courses():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect('/login')
    
    keyword = request.args.get('keyword', '')
    student = Student.get_by_id(session['user_id'])
    courses = Course.search_courses(keyword)
    
    enrolled_course_ids = [course.id for course in student.get_enrolled_courses()]
    
    return render_template('student/student-search.html', 
                         student=student, 
                         courses=courses, 
                         enrolled_course_ids=enrolled_course_ids,
                         keyword=keyword)

@student_bp.route('/enroll/<int:course_id>')
def enroll_course(course_id):
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect('/login')
    
    student = Student.get_by_id(session['user_id'])
    success, message = student.enroll_course(course_id)
    
    flash(message, 'success' if success else 'error')
    return redirect('/student/courses')

@student_bp.route('/drop/<int:course_id>')
def drop_course(course_id):
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect('/login')
    
    student = Student.get_by_id(session['user_id'])
    success, message = student.drop_course(course_id)
    
    flash(message, 'success' if success else 'error')
    return redirect('/student/courses')

@student_bp.route('/course/<int:course_id>')
def view_course(course_id):
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect('/login')
    
    student = Student.get_by_id(session['user_id'])
    course = Course.get_by_id(course_id)
    
    if not course or not student.is_enrolled_in_course(course_id):
        flash("Course not found or not enrolled", "error")
        return redirect('/student/courses')
    
    announcements = course.get_announcements()
    assignments = course.get_assignments()
    
    # Add submission status to each assignment
    for assignment in assignments:
        status = student.get_assignment_status(assignment.id)
        assignment.submitted = status['submitted']
        assignment.grade = status['grade']
    
    return render_template('student/student-view-course.html', 
                         student=student, 
                         course=course,
                         announcements=announcements,
                         assignments=assignments)

@student_bp.route('/course/<int:course_id>/announcements')
def view_announcements(course_id):
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect('/login')
    
    student = Student.get_by_id(session['user_id'])
    course = Course.get_by_id(course_id)
    
    if not course or not student.is_enrolled_in_course(course_id):
        flash("Course not found or not enrolled", "error")
        return redirect('/student/courses')
    
    announcements = course.get_announcements()
    
    return render_template('student/student-announcements.html', 
                         student=student, 
                         course=course,
                         announcements=announcements)

@student_bp.route('/course/<int:course_id>/assignments')
def view_assignments(course_id):
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect('/login')
    
    student = Student.get_by_id(session['user_id'])
    course = Course.get_by_id(course_id)
    
    if not course or not student.is_enrolled_in_course(course_id):
        flash("Course not found or not enrolled", "error")
        return redirect('/student/courses')
    
    assignments = course.get_assignments()
    
    # Add submission status to each assignment
    for assignment in assignments:
        status = student.get_assignment_status(assignment.id)
        assignment.submitted = status['submitted']
        assignment.grade = status['grade']
        assignment.submission_timestamp = status['timestamp']
    
    return render_template('student/student-assignments.html', 
                         student=student, 
                         course=course,
                         assignments=assignments)

@student_bp.route('/assignment/<int:assignment_id>/submit', methods=['GET', 'POST'])
def submit_assignment(assignment_id):
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect('/login')
    
    student = Student.get_by_id(session['user_id'])
    assignment = Assignment.get_by_id(assignment_id)
    
    if not assignment:
        flash("Assignment not found", "error")
        return redirect('/student/dashboard')
    
    # Check if student is enrolled in the course
    course = Course.get_by_id(assignment.course_id)
    if not course or not student.is_enrolled_in_course(course.id):
        flash("You are not enrolled in this course", "error")
        return redirect('/student/courses')
    
    if request.method == 'POST':
        submission_text = request.form.get('submission_text', '')
        
        if submission_text:
            success, message = assignment.add_submission(student.id, submission_text)
            flash(message, 'success' if success else 'error')
            
            if success:
                return redirect(f'/student/course/{course.id}/assignments')
        else:
            flash("Submission cannot be empty", "error")
    
    return render_template('student/student-submit-assignment.html', 
                         student=student, 
                         assignment=assignment,
                         course=course)

@student_bp.route('/grades')
def view_grades():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect('/login')
    
    student = Student.get_by_id(session['user_id'])
    
    grades = {}
    for course in student.get_enrolled_courses():
        assignments = course.get_assignments()
        course_grades = []
        for assignment in assignments:
            status = student.get_assignment_status(assignment.id)
            if status['submitted'] and status['grade'] is not None:
                course_grades.append({
                    'assignment': assignment.title,
                    'grade': status['grade'],
                    'max_grade': 10,
                    'feedback': assignment.get_submission(student.id).get('feedback') if assignment.get_submission(student.id) else None
                })
        if course_grades:
            grades[course.name] = course_grades
    
    return render_template('student/grades.html', 
                         student=student, 
                         grades=grades)

@student_bp.route('/schedule')
def view_schedule():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect('/login')
    
    student = Student.get_by_id(session['user_id'])
    enrolled_courses = student.get_enrolled_courses()
    
    return render_template('student/schedule.html', 
                         student=student, 
                         courses=enrolled_courses)