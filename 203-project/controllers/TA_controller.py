from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, Course, Assignment, Announcement, User, Submission
ta_bp = Blueprint('ta', __name__)

@ta_bp.route('/ta/dashboard')
@login_required
def dashboard():
    courses = Course.query.all()
    return render_template('ta/dashboard.html', courses=courses)

@ta_bp.route('/ta/search_course', methods=['GET', 'POST'])
@login_required
def search_course():
    results = []
    if request.method == 'POST':
        query = request.form.get('query')
        if query:
            results = Course.query.filter(
                (Course.name.contains(query)) | (Course.code.contains(query))
            ).all()
    return render_template('ta/search_course.html', results=results)

@ta_bp.route('/ta/search_student', methods=['GET', 'POST'])
@login_required
def search_student():
    results = []
    if request.method == 'POST':
        query = request.form.get('query')
        if query:
            results = User.query.filter(
                ((User.name.contains(query)) | (User.email.contains(query))) & (User.role == 'student')
            ).all()
    return render_template('ta/search_student.html', results=results)

@ta_bp.route('/ta/course/<int:course_id>')
@login_required
def course_details(course_id):
    course = Course.query.get_or_404(course_id)
    students = User.query.filter_by(role='student').all()
    return render_template('ta/course_details.html', course=course, students=students)

@ta_bp.route('/ta/course/<int:course_id>/add_assignment', methods=['POST'])
@login_required
def add_assignment(course_id):
    title = request.form.get('title')
    content = request.form.get('content')
    
    new_assign = Assignment(title=title, content=content, course_id=course_id)
    db.session.add(new_assign)
    db.session.commit()
    
    flash('Assignment posted successfully!', 'success')
    return redirect(url_for('ta.course_details', course_id=course_id))

@ta_bp.route('/ta/course/<int:course_id>/add_announcement', methods=['POST'])
@login_required
def add_announcement(course_id):
    title = request.form.get('title')
    body = request.form.get('body')
    
    new_announce = Announcement(title=title, body=body, course_id=course_id)
    db.session.add(new_announce)
    db.session.commit()
    
    flash('Announcement posted successfully!', 'success')
    return redirect(url_for('ta.course_details', course_id=course_id))
@ta_bp.route('/ta/course/<int:course_id>/attendance', methods=['GET', 'POST'])
@login_required
def attendance(course_id):
    course = Course.query.get_or_404(course_id)
    students = User.query.filter_by(role='student').all()
    
    if request.method == 'POST':
        flash('Attendance recorded successfully for today!', 'success')
        return redirect(url_for('ta.course_details', course_id=course_id))
        
    return render_template('ta/attendance.html', course=course, students=students)
@ta_bp.route('/ta/assignment/<int:assignment_id>/submissions')
@login_required
def view_submissions(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    submissions = Submission.query.filter_by(assignment_id=assignment_id).all()
    return render_template('ta/assignment_submissions.html', assignment=assignment, submissions=submissions)

@ta_bp.route('/ta/submission/<int:sub_id>/grade', methods=['POST'])
@login_required
def submit_grade(sub_id):
    sub = Submission.query.get_or_404(sub_id)
    sub.grade = request.form.get('grade')
    sub.feedback = request.form.get('feedback')
    db.session.commit()
    
    flash('Grade updated successfully!', 'success')
    return redirect(request.referrer) 
@ta_bp.route('/ta/student/<int:student_id>')
@login_required
def view_student(student_id):
    student = User.query.get_or_404(student_id)
    
    submissions = Submission.query.filter_by(student_id=student_id).all()
    
    courses = Course.query.all() 
    
    return render_template('ta/student_profile.html', 
                         student=student, 
                         submissions=submissions, 
                         courses=courses)