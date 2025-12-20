# from flask import Blueprint, render_template, redirect, url_for, request, flash, session
# from models.instructor import Instructor
# from models.courses import Course
# from models.assignment import Assignment
# from models.announcement import Announcement

# instructor_bp = Blueprint('instructor', __name__, url_prefix='/instructor')

# @instructor_bp.route('/dashboard')
# def dashboard():
#     if 'user_id' not in session or session.get('role') != 'instructor':
#         return redirect('/login')
    
#     instructor = Instructor.get_by_id(session['user_id'])
#     if not instructor:
#         flash("Instructor not found", "error")
#         return redirect('/login')
    
#     courses = instructor.get_teaching_courses()
    
#     return render_template('instructor/dashboard.html', courses=courses)

# @instructor_bp.route('/course/<int:course_id>')
# def course_details(course_id):
#     if 'user_id' not in session or session.get('role') != 'instructor':
#         return redirect('/login')
    
#     course = Course.get_by_id(course_id)
#     if not course:
#         flash("Course not found", "error")
#         return redirect(url_for('instructor.dashboard'))
    
#     # Check if instructor teaches this course
#     instructor = Instructor.get_by_id(session['user_id'])
#     if course_id not in instructor.teaching_courses:
#         flash("You don't teach this course", "error")
#         return redirect(url_for('instructor.dashboard'))
    
#     announcements = course.get_announcements()
#     assignments = course.get_assignments()
#     students = course.get_enrolled_students()
    
#     return render_template('instructor/course_details.html', 
#                          course=course, 
#                          announcements=announcements,
#                          assignments=assignments,
#                          students=students)

# @instructor_bp.route('/course/<int:course_id>/add_assignment', methods=['POST'])
# def add_assignment(course_id):
#     if 'user_id' not in session or session.get('role') != 'instructor':
#         return redirect('/login')
    
#     course = Course.get_by_id(course_id)
#     if not course:
#         flash("Course not found", "error")
#         return redirect(url_for('instructor.dashboard'))
    
#     title = request.form.get('title')
#     description = request.form.get('description')
#     due_date = request.form.get('due_date')
    
#     if title and description and due_date:
#         assignment = course.add_assignment(title, description, due_date)
#         flash('Assignment added successfully!', 'success')
#     else:
#         flash('Please fill all fields', 'error')
    
#     return redirect(url_for('instructor.course_details', course_id=course_id))

# @instructor_bp.route('/course/<int:course_id>/add_announcement', methods=['POST'])
# def add_announcement(course_id):
#     if 'user_id' not in session or session.get('role') != 'instructor':
#         return redirect('/login')
    
#     course = Course.get_by_id(course_id)
#     if not course:
#         flash("Course not found", "error")
#         return redirect(url_for('instructor.dashboard'))
    
#     title = request.form.get('title')
#     content = request.form.get('content')
    
#     if title and content:
#         announcement = course.add_announcement(title, content, session['user_id'])
#         flash('Announcement added successfully!', 'success')
#     else:
#         flash('Please fill all fields', 'error')
    
#     return redirect(url_for('instructor.course_details', course_id=course_id))

# @instructor_bp.route('/assignment/<int:assignment_id>/submissions')
# def view_submissions(assignment_id):
#     if 'user_id' not in session or session.get('role') != 'instructor':
#         return redirect('/login')
    
#     assignment = Assignment.get_by_id(assignment_id)
#     if not assignment:
#         flash("Assignment not found", "error")
#         return redirect(url_for('instructor.dashboard'))
    
#     # Get all submissions
#     submissions_data = assignment.get_all_submissions()
    
#     # Convert to list of submission objects with student info
#     from models.student import Student
#     submissions = []
#     for student_id, submission_info in submissions_data.items():
#         student = Student.get_by_id(student_id)
#         if student:
#             submissions.append({
#                 'student': student,
#                 'grade': submission_info.get('grade'),
#                 'feedback': submission_info.get('feedback'),
#                 'timestamp': submission_info.get('timestamp'),
#                 'text': submission_info.get('text'),
#                 'id': student_id
#             })
    
#     # Get course info
#     course = Course.get_by_id(assignment.course_id)
    
#     return render_template('instructor/assignment_submissions.html', 
#                          assignment=assignment, 
#                          submissions=submissions,
#                          course=course)