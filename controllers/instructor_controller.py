from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from models.user import User
from models.courses import Course
from models.assignment import Assignment
from models.announcement import Announcement
from models.enrollment import Enrollment

instructor_bp = Blueprint('instructor', __name__, url_prefix='/instructor')

@instructor_bp.route('/')
def dashboard():
    if 'user_id' not in session or session.get('role') != 'instructor':
        return redirect('/login')
    
    instructor = User.get_by_id(session['user_id'])
    if not instructor:
        flash("Instructor not found", "error")
        return redirect('/login')
    
    # Get courses taught by this instructor
    my_courses = Course.get_courses_by_instructor(instructor.name)
    course_count = len(my_courses)
    
    return render_template('instructor/dashboard.html', 
                           instructor=instructor,
                           courses=my_courses,
                           course_count=course_count)

@instructor_bp.route('/course/<course_code>')
def open_course(course_code):
    if 'user_id' not in session or session.get('role') != 'instructor':
        return redirect('/login')
    
    course = Course.get_course_by_id(course_code)
    if not course:
        flash("Course not found", "error")
        return redirect(url_for('instructor.dashboard'))
    
    # Check if instructor teaches this course
    instructor = User.get_by_id(session['user_id'])
    if course.instructor_id != instructor.id:
        flash("You don't teach this course", "error")
        return redirect(url_for('instructor.dashboard'))
    
    assignments = Assignment.get_assignments_by_course(course_code)
    announcements = Announcement.get_announcements_by_course(course_code)
    
    return render_template('instructor/open_course.html', 
                           course=course, 
                           assignments=assignments, 
                           announcements=announcements)

@instructor_bp.route('/course/<course_code>/announce', methods=['GET', 'POST'])
def make_announcement(course_code):
    if 'user_id' not in session or session.get('role') != 'instructor':
        return redirect('/login')
    
    if request.method == 'POST':
        Announcement.add_announcement(
            course_code,
            request.form['title'],
            request.form['content'],
            session['user_id']  # Pass the instructor's user_id
        )
        flash('Announcement created successfully!', 'success')
        return redirect(url_for('instructor.open_course', course_code=course_code))
        
    return render_template('instructor/make_announcement.html', course_code=course_code)

@instructor_bp.route('/course/<course_code>/add_assignment', methods=['GET', 'POST'])
def send_assignment(course_code):
    if 'user_id' not in session or session.get('role') != 'instructor':
        return redirect('/login')
    
    if request.method == 'POST':
        Assignment.add_assignment(
            course_code,
            request.form['title'],
            request.form['description'],
            request.form['due_date']
        )
        flash('Assignment added successfully!', 'success')
        return redirect(url_for('instructor.open_course', course_code=course_code))
        
    return render_template('instructor/send_assignment.html', course_code=course_code)

@instructor_bp.route('/course/<course_code>/students')
def student_list(course_code):
    if 'user_id' not in session or session.get('role') != 'instructor':
        return redirect('/login')
    
    course = Course.get_course_by_id(course_code)
    if not course:
        flash("Course not found", "error")
        return redirect(url_for('instructor.dashboard'))
    
    # Use the course method to get enrolled students
    enrolled_students = course.get_enrolled_students()
                
    return render_template('instructor/student_list.html', 
                          course=course, 
                          students=enrolled_students)

@instructor_bp.route('/student/<int:student_id>')
def view_student(student_id):
    if 'user_id' not in session or session.get('role') != 'instructor':
        return redirect('/login')
    
    student = User.get_by_id(student_id)
    if not student or student.role != 'student':
        flash("Student not found", "error")
        return redirect(url_for('instructor.dashboard'))
    
    return render_template('instructor/view_student.html', student=student)

@instructor_bp.route('/course/<course_code>/edit', methods=['GET', 'POST'])
def edit_course(course_code):
    if 'user_id' not in session or session.get('role') != 'instructor':
        return redirect('/login')
    
    course = Course.get_course_by_id(course_code)
    if not course:
        flash("Course not found", "error")
        return redirect(url_for('instructor.dashboard'))
    
    # Check if instructor teaches this course
    instructor = User.get_by_id(session['user_id'])
    if course.instructor_id != instructor.id:
        flash("You don't teach this course", "error")
        return redirect(url_for('instructor.dashboard'))
    
    if request.method == 'POST':
        success = Course.edit_course(
            course_code, 
            request.form['name'], 
            request.form.get('ta', ''),  # Use .get() to avoid KeyError
            instructor.name,
            request.form['credits'], 
            request.form['seats']
        )
        if success:
            flash('Course updated successfully!', 'success')
        else:
            flash('Failed to update course', 'error')
        return redirect(url_for('instructor.open_course', course_code=course_code))
        
    return render_template('instructor/edit_course.html', course=course)

# Additional routes from instructor_controller.py
@instructor_bp.route('/assignment/<int:assignment_id>/submissions')
def view_submissions(assignment_id):
    if 'user_id' not in session or session.get('role') != 'instructor':
        return redirect('/login')
    
    assignment = Assignment.get_by_id(assignment_id)
    if not assignment:
        flash("Assignment not found", "error")
        return redirect(url_for('instructor.dashboard'))
    
    # Get course info
    course = Course.get_by_id(assignment.course_id)
    
    # Check if instructor teaches this course
    instructor = User.get_by_id(session['user_id'])
    if not course or course.instructor_id != instructor.id:
        flash("You don't teach this course", "error")
        return redirect(url_for('instructor.dashboard'))
    
    # Get submissions for this assignment
    submissions = assignment.get_submissions()
    
    return render_template('instructor/assignment_submissions.html', 
                         assignment=assignment, 
                         submissions=submissions,
                         course=course)