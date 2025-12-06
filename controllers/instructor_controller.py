from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, Course, Assignment, Announcement

instructor_bp = Blueprint('instructor', __name__)

@instructor_bp.route('/instructor/dashboard')
@login_required
def dashboard():    
    courses = Course.query.filter_by(instructor_id=current_user.id).all()
    return render_template('instructor/dashboard.html', courses=courses)

@instructor_bp.route('/course/<int:course_id>')
@login_required
def course_details(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('instructor/course_details.html', course=course)

@instructor_bp.route('/course/<int:course_id>/add_assignment', methods=['POST'])
@login_required
def add_assignment(course_id):
    title = request.form.get('title')
    content = request.form.get('content')
    
    new_assign = Assignment(title=title, content=content, course_id=course_id)
    db.session.add(new_assign)
    db.session.commit()
    
    flash('Assignment posted successfully!', 'success')
    return redirect(url_for('instructor.course_details', course_id=course_id))

@instructor_bp.route('/course/<int:course_id>/add_announcement', methods=['POST'])
@login_required
def add_announcement(course_id):
    title = request.form.get('title')
    body = request.form.get('body')
    
    new_announce = Announcement(title=title, body=body, course_id=course_id)
    db.session.add(new_announce)
    db.session.commit()
    
    flash('Announcement posted successfully!', 'success')
    return redirect(url_for('instructor.course_details', course_id=course_id))