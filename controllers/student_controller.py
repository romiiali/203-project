from flask import Blueprint, render_template, request, redirect, session, flash
from models.student import Student
from models.courses import Course, Announcement, Assignment

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect('/login')
    
    student = Student.get_by_id(session['user_id'])
    enrolled_courses = student.get_enrolled_courses()
    
    return render_template('student/dashboard.html', 
                         student=student, 
                         enrolled_count=len(enrolled_courses))

@student_bp.route('/courses')
def view_courses():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect('/login')
    
    student = Student.get_by_id(session['user_id'])
    enrolled_courses = student.get_enrolled_courses()
    
    return render_template('student/enrolled_courses.html', 
                         student=student, 
                         courses=enrolled_courses)

@student_bp.route('/search')
def search_courses():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect('/login')
    
    keyword = request.args.get('keyword', '')
    student = Student.get_by_id(session['user_id'])
    courses = Course.search_courses(keyword)
    
    enrolled_codes = student.enrolled_courses
    
    return render_template('student/search_courses.html', 
                         student=student, 
                         courses=courses, 
                         enrolled_codes=enrolled_codes,
                         keyword=keyword)

@student_bp.route('/enroll/<course_code>')
def enroll_course(course_code):
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect('/login')
    
    student = Student.get_by_id(session['user_id'])
    success, message = student.enroll_course(course_code)
    
    flash(message, 'success' if success else 'error')
    return redirect('/student/courses')

@student_bp.route('/drop/<course_code>')
def drop_course(course_code):
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect('/login')
    
    student = Student.get_by_id(session['user_id'])
    success, message = student.drop_course(course_code)
    
    flash(message, 'success' if success else 'error')
    return redirect('/student/courses')

@student_bp.route('/course/<course_code>')
def view_course(course_code):
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect('/login')
    
    student = Student.get_by_id(session['user_id'])
    course = Course.get_by_code(course_code)
    
    if not course or course_code not in student.enrolled_courses:
        flash("Course not found or not enrolled", "error")
        return redirect('/student/courses')
    
    announcements = Announcement.get_by_course(course.id)
    assignments = Assignment.get_by_course(course.id)
    
    for assignment in assignments:
        submission = assignment.get_submission(student.id)
        assignment.submitted = submission is not None
        assignment.grade = submission['grade'] if submission else None
    
    return render_template('student/view_course.html', 
                         student=student, 
                         course=course,
                         announcements=announcements,
                         assignments=assignments)

@student_bp.route('/course/<course_code>/announcements')
def view_announcements(course_code):
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect('/login')
    
    student = Student.get_by_id(session['user_id'])
    course = Course.get_by_code(course_code)
    
    if not course or course_code not in student.enrolled_courses:
        flash("Course not found or not enrolled", "error")
        return redirect('/student/courses')
    
    announcements = Announcement.get_by_course(course.id)
    
    return render_template('student/announcements.html', 
                         student=student, 
                         course=course,
                         announcements=announcements)

@student_bp.route('/course/<course_code>/assignments')
def view_assignments(course_code):
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect('/login')
    
    student = Student.get_by_id(session['user_id'])
    course = Course.get_by_code(course_code)
    
    if not course or course_code not in student.enrolled_courses:
        flash("Course not found or not enrolled", "error")
        return redirect('/student/courses')
    
    assignments = Assignment.get_by_course(course.id)
    
    for assignment in assignments:
        submission = assignment.get_submission(student.id)
        assignment.submitted = submission is not None
        assignment.grade = submission['grade'] if submission else None
    
    return render_template('student/assignments.html', 
                         student=student, 
                         course=course,
                         assignments=assignments)

@student_bp.route('/assignment/<int:assignment_id>/submit', methods=['GET', 'POST'])
def submit_assignment(assignment_id):
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect('/login')
    
    student = Student.get_by_id(session['user_id'])
    
    assignments = []
    for course_code in student.enrolled_courses:
        course = Course.get_by_code(course_code)
        if course:
            course_assignments = Assignment.get_by_course(course.id)
            assignments.extend(course_assignments)
    
    assignment = None
    for a in assignments:
        if a.id == assignment_id:
            assignment = a
            break
    
    if not assignment:
        flash("Assignment not found", "error")
        return redirect('/student/dashboard')
    
    if request.method == 'POST':
        submission_text = request.form.get('submission_text', '')
        
        success, message = assignment.add_submission(student.id, submission_text)
        flash(message, 'success' if success else 'error')
        
        if success:
            course_code = ""
            for c in Course.get_all():
                if c.id == assignment.course_id:
                    course_code = c.course_code
                    break
            return redirect(f'/student/course/{course_code}/assignments')
    
    return render_template('student/submit_assignment.html', 
                         student=student, 
                         assignment=assignment)

@student_bp.route('/grades')
def view_grades():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect('/login')
    
    student = Student.get_by_id(session['user_id'])
    
    grades = {}
    for course_code in student.enrolled_courses:
        course = Course.get_by_code(course_code)
        if course:
            assignments = Assignment.get_by_course(course.id)
            course_grades = []
            for assignment in assignments:
                submission = assignment.get_submission(student.id)
                if submission and submission['grade'] is not None:
                    course_grades.append({
                        'assignment': assignment.title,
                        'grade': submission['grade'],
                        'max_grade': 10
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