from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from models.ta import TA
from models.courses import Course
from models.user import User
from models.student import Student
from models.assignment import Assignment
from models.announcement import Announcement
from models.submission import Submission
from extensions import db
import datetime

ta_bp = Blueprint('ta', __name__, url_prefix='/ta')

# Helper function to check TA authentication
def require_ta():
    """Check if user is authenticated as TA"""
    if 'user_id' not in session or session.get('role') != 'ta':
        flash('Please log in as TA to access this page', 'error')
        return False
    return True

@ta_bp.route('/')
def dashboard():
    """TA Dashboard - main page"""
    if not require_ta():
        return redirect('/login')
    
    # Get TA info
    ta = TA.get_by_id(session['user_id'])
    if not ta:
        flash("TA not found", "error")
        return redirect('/login')
    
    # Get assigned courses - assuming TA has at least one course
    # Modified to handle the database model structure
    courses = Course.get_courses_by_ta(ta.id) if hasattr(Course, 'get_courses_by_ta') else []
    
    # For now, take the first course or use a default
    course = courses[0] if courses else None
    
    return render_template('dashboard.html', course=course, user=ta)

@ta_bp.route('/student_list', methods=['GET', 'POST'])
def student_list():
    """Search for students in TA's courses"""
    if not require_ta():
        return redirect('/login')
    
    ta_id = session['user_id']
    results = []
    
    # Get courses where this user is TA
    ta_courses = Course.query.filter_by(ta_id=ta_id).all()
    
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        if query:
            # Search for students in TA's courses
            for course in ta_courses:
                # Get enrolled students for this course
                enrollments = db.session.query(User).join(
                    Submission, User.id == Submission.student_id
                ).filter(
                    User.role == 'student'
                ).all()
                
                for student in enrollments:
                    if (query.lower() in student.name.lower() or 
                        query.lower() in student.email.lower()):
                        # Add student info
                        student_data = {
                            'id': student.id,
                            'name': student.name,
                            'email': student.email,
                            'major': getattr(student, 'major', 'N/A'),
                            'level': getattr(student, 'level', 'N/A')
                        }
                        if student_data not in results:
                            results.append(student_data)
    
    return render_template('student_list.html', 
                         results=results, 
                         course=ta_courses[0] if ta_courses else None)

@ta_bp.route('/course/<int:course_id>/student/<int:student_id>')
def student_profile(course_id, student_id):
    """View student profile"""
    if not require_ta():
        return redirect('/login')
    
    # Check if TA is assigned to this course
    course = Course.query.get(course_id)
    if not course or course.ta_id != session['user_id']:
        flash('You are not the TA for this course', 'error')
        return redirect(url_for('ta.dashboard'))
    
    # Get student info
    student = User.query.get(student_id)
    if not student or student.role != 'student':
        flash('Student not found', 'error')
        return redirect(url_for('ta.student_list'))
    
    # Get courses this student is enrolled in
    from models.enrollment import Enrollment
    enrollments = Enrollment.query.filter_by(student_id=student_id).all()
    courses = []
    for enrollment in enrollments:
        course = Course.query.get(enrollment.course_id)
        if course:
            courses.append(course)
    
    return render_template('student_profile.html', 
                         student=student, 
                         courses=courses,
                         current_course_id=course_id)

@ta_bp.route('/post_assignment', methods=['GET', 'POST'])
def post_assignment():
    """Post a new assignment"""
    if not require_ta():
        return redirect('/login')
    
    ta_id = session['user_id']
    
    # Get courses where this user is TA
    ta_courses = Course.query.filter_by(ta_id=ta_id).all()
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        due_date_str = request.form.get('due_date')
        max_points = request.form.get('max_points', 100)
        course_id = request.form.get('course_id')
        
        if not all([title, description, due_date_str, course_id]):
            flash('All fields are required', 'error')
            return render_template('post_assignment.html', courses=ta_courses)
        
        try:
            # Parse due date
            due_date = datetime.datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
            
            # Create assignment
            assignment = Assignment(
                title=title,
                description=description,
                due_date=due_date,
                course_id=course_id
            )
            
            db.session.add(assignment)
            db.session.commit()
            
            flash('Assignment posted successfully!', 'success')
            return redirect(url_for('ta.dashboard'))
            
        except Exception as e:
            flash(f'Error creating assignment: {str(e)}', 'error')
            return render_template('post_assignment.html', courses=ta_courses)
    
    # GET request - show form
    return render_template('post_assignment.html', courses=ta_courses)

@ta_bp.route('/post_announcement', methods=['GET', 'POST'])
def post_announcement():
    """Post an announcement"""
    if not require_ta():
        return redirect('/login')
    
    ta_id = session['user_id']
    
    # Get courses where this user is TA
    ta_courses = Course.query.filter_by(ta_id=ta_id).all()
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        priority = request.form.get('priority', 'normal')
        course_id = request.form.get('course_id')
        
        if not all([title, content, course_id]):
            flash('All fields are required', 'error')
            return render_template('post_announcement.html', courses=ta_courses)
        
        try:
            # Create announcement
            announcement = Announcement(
                title=title,
                content=content,
                poster_id=ta_id,
                course_id=course_id
            )
            
            db.session.add(announcement)
            db.session.commit()
            
            flash('Announcement posted successfully!', 'success')
            return redirect(url_for('ta.dashboard'))
            
        except Exception as e:
            flash(f'Error creating announcement: {str(e)}', 'error')
            return render_template('post_announcement.html', courses=ta_courses)
    
    # GET request - show form
    return render_template('post_announcement.html', courses=ta_courses)

@ta_bp.route('/assignment/<int:assignment_id>/submissions')
def view_submissions(assignment_id):
    """View submissions for an assignment"""
    if not require_ta():
        return redirect('/login')
    
    ta_id = session['user_id']
    
    # Get assignment
    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        flash('Assignment not found', 'error')
        return redirect(url_for('ta.dashboard'))
    
    # Check if TA is assigned to this course
    course = Course.query.get(assignment.course_id)
    if not course or course.ta_id != ta_id:
        flash('You are not the TA for this course', 'error')
        return redirect(url_for('ta.dashboard'))
    
    # Get submissions with student info
    submissions = db.session.query(Submission, User).join(
        User, Submission.student_id == User.id
    ).filter(
        Submission.assignment_id == assignment_id
    ).all()
    
    # Format submissions data
    formatted_submissions = []
    for submission, student in submissions:
        formatted_submissions.append({
            'id': submission.id,
            'student': student,
            'submission_text': submission.submission_text,
            'grade': submission.grade,
            'feedback': submission.feedback,
            'submission_date': submission.submitted_at.strftime('%Y-%m-%d %H:%M') if submission.submitted_at else 'N/A'
        })
    
    return render_template('assignment_submissions.html',
                         assignment=assignment,
                         submissions=formatted_submissions)

@ta_bp.route('/submission/<int:submission_id>/grade', methods=['POST'])
def grade_submission(submission_id):
    """Grade a submission"""
    if not require_ta():
        return redirect('/login')
    
    ta_id = session['user_id']
    
    # Get submission
    submission = Submission.query.get(submission_id)
    if not submission:
        flash('Submission not found', 'error')
        return redirect(url_for('ta.dashboard'))
    
    # Get assignment
    assignment = Assignment.query.get(submission.assignment_id)
    if not assignment:
        flash('Assignment not found', 'error')
        return redirect(url_for('ta.dashboard'))
    
    # Check if TA is assigned to this course
    course = Course.query.get(assignment.course_id)
    if not course or course.ta_id != ta_id:
        flash('You are not the TA for this course', 'error')
        return redirect(url_for('ta.dashboard'))
    
    # Get grade and feedback
    grade = request.form.get('grade')
    feedback = request.form.get('feedback', '')
    
    if not grade:
        flash('Grade is required', 'error')
        return redirect(url_for('ta.view_submissions', assignment_id=assignment.id))
    
    try:
        grade_value = float(grade)
        if grade_value < 0 or grade_value > 100:
            flash('Grade must be between 0 and 100', 'error')
            return redirect(url_for('ta.view_submissions', assignment_id=assignment.id))
        
        # Update submission
        submission.grade = grade_value
        submission.feedback = feedback
        db.session.commit()
        
        flash('Grade saved successfully!', 'success')
        
    except ValueError:
        flash('Invalid grade format', 'error')
    
    return redirect(url_for('ta.view_submissions', assignment_id=assignment.id))

@ta_bp.route('/search_student')
def search_student():
    """Redirect to student_list for backward compatibility"""
    return redirect(url_for('ta.student_list'))

# Additional routes that might be needed based on your HTML templates

@ta_bp.route('/course/<int:course_id>')
def course_details(course_id):
    """View course details"""
    if not require_ta():
        return redirect('/login')
    
    ta_id = session['user_id']
    
    course = Course.query.get(course_id)
    if not course or course.ta_id != ta_id:
        flash('You are not the TA for this course', 'error')
        return redirect(url_for('ta.dashboard'))
    
    # Get assignments for this course
    assignments = Assignment.query.filter_by(course_id=course_id).all()
    
    # Get announcements for this course
    announcements = Announcement.query.filter_by(course_id=course_id).order_by(
        Announcement.created_at.desc()
    ).all()
    
    # Get enrolled students count
    from models.enrollment import Enrollment
    student_count = Enrollment.query.filter_by(course_id=course_id).count()
    
    return render_template('ta/course_details.html',
                         course=course,
                         assignments=assignments,
                         announcements=announcements,
                         student_count=student_count)