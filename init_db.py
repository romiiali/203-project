import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from config import Config
from extensions import db
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from sqlalchemy import text, exc

def create_app():
    """Create Flask application for database initialization"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions with app
    db.init_app(app)
    
    return app

def init_database():
    """Initialize the database with default data using Windows Auth"""
    app = create_app()
    
    with app.app_context():
        print("="*60)
        print("DATABASE INITIALIZATION (Windows Authentication)")
        print("="*60)
        
        # Get current connection info
        try:
            result = db.session.execute(text("SELECT SUSER_NAME() as windows_user, DB_NAME() as current_db"))
            row = result.fetchone()
            print(f"Connected as Windows User: {row.windows_user}")
            print(f"Current Database: {row.current_db}")
        except Exception as e:
            print(f"⚠️ Could not get connection info: {e}")
        
        print("\nCreating database tables...")
        
        try:
            # Create all tables
            db.create_all()
            print("✅ Tables created successfully")
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return
        
        # ============== ADD DUMMY DATA ==============
        print("\nAdding dummy data...")
        
        try:
            # Clear existing data in correct order (respecting foreign key constraints)
            print("Clearing existing data...")
            
            # Disable foreign key constraints temporarily
            db.session.execute(text("EXEC sp_MSforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT all'"))
            
            # Delete in reverse order of dependencies
            db.session.execute(text("DELETE FROM submissions"))
            db.session.execute(text("DELETE FROM announcements"))
            db.session.execute(text("DELETE FROM assignments"))
            db.session.execute(text("DELETE FROM enrollments"))
            db.session.execute(text("DELETE FROM courses"))
            db.session.execute(text("DELETE FROM users"))
            
            # Re-enable foreign key constraints
            db.session.execute(text("EXEC sp_MSforeachtable 'ALTER TABLE ? WITH CHECK CHECK CONSTRAINT all'"))
            
            db.session.commit()
            print("✅ Cleared existing data")
            
            # Now import models after clearing data
            from models.user import User
            from models.courses import Course
            from models.enrollment import Enrollment
            from models.assignment import Assignment
            from models.announcement import Announcement
            from models.submission import Submission
            
            # 1. Add Users (must be first because other tables reference users)
            print("Adding users...")
            
            users = [
                # Admins
                User(
                    name='Admin User',
                    email='admin@university.edu',
                    role='admin',
                    password='admin123'
                ),
                User(
                    name='System Admin',
                    email='sysadmin@university.edu',
                    role='admin',
                    password='admin123'
                ),
                
                # Instructors
                User(
                    name='Dr. Sarah Johnson',
                    email='sarah@instructor.edu',
                    role='instructor',
                    password='prof123'
                ),
                User(
                    name='Prof. Robert Smith',
                    email='robert@instructor.edu',
                    role='instructor',
                    password='prof123'
                ),
                User(
                    name='Dr. Jennifer Lee',
                    email='jennifer@instructor.edu',
                    role='instructor',
                    password='prof123'
                ),
                
                # TAs
                User(
                    name='Alex Chen',
                    email='alex@ta.edu',
                    role='ta',
                    password='ta123'
                ),
                User(
                    name='Lisa Wang',
                    email='lisa@ta.edu',
                    role='ta',
                    password='ta123'
                ),
                
                # Students
                User(
                    name='John Doe',
                    email='john@student.edu',
                    role='student',
                    password='student123'
                ),
                User(
                    name='Jane Smith',
                    email='jane@student.edu',
                    role='student',
                    password='student123'
                ),
                User(
                    name='Mike Johnson',
                    email='mike@student.edu',
                    role='student',
                    password='student123'
                ),
                User(
                    name='Emily Davis',
                    email='emily@student.edu',
                    role='student',
                    password='student123'
                ),
                User(
                    name='David Wilson',
                    email='david@student.edu',
                    role='student',
                    password='student123'
                ),
            ]
            
            for user in users:
                db.session.add(user)
            
            db.session.commit()
            print(f"✅ Added {len(users)} users")
            
            # Get user IDs after commit (auto-generated)
            # Users: 1-2: admin, 3-5: instructors, 6-7: TAs, 8-12: students
            
            # 2. Add Courses (requires instructor users to exist)
            print("Adding courses...")
            
            courses = [
                Course(
                    code='CS101',
                    name='Introduction to Programming',
                    description='Learn basic programming concepts using Python',
                    instructor_id=3,  # Dr. Sarah Johnson
                    ta_id=6,          # Alex Chen
                    credits=3,
                    max_seats=30,
                    schedule='Mon/Wed 10:00-11:30 AM',
                    department='Computer Science'
                ),
                Course(
                    code='CS201',
                    name='Data Structures and Algorithms',
                    description='Study of fundamental data structures and algorithms',
                    instructor_id=3,  # Dr. Sarah Johnson
                    ta_id=6,          # Alex Chen
                    credits=4,
                    max_seats=25,
                    schedule='Tue/Thu 1:00-2:30 PM',
                    department='Computer Science'
                ),
                Course(
                    code='CS301',
                    name='Database Systems',
                    description='Introduction to database design and SQL',
                    instructor_id=4,  # Prof. Robert Smith
                    ta_id=7,          # Lisa Wang
                    credits=3,
                    max_seats=28,
                    schedule='Mon/Wed 2:00-3:30 PM',
                    department='Computer Science'
                ),
                Course(
                    code='MATH101',
                    name='Calculus I',
                    description='Introduction to differential and integral calculus',
                    instructor_id=5,  # Dr. Jennifer Lee
                    credits=4,
                    max_seats=35,
                    schedule='Tue/Thu/Fri 9:00-10:00 AM',
                    department='Mathematics'
                ),
                Course(
                    code='MATH201',
                    name='Linear Algebra',
                    description='Vectors, matrices, and linear transformations',
                    instructor_id=5,  # Dr. Jennifer Lee
                    credits=3,
                    max_seats=30,
                    schedule='Mon/Wed/Fri 11:00-12:00 PM',
                    department='Mathematics'
                ),
            ]
            
            for course in courses:
                db.session.add(course)
            
            db.session.commit()
            print(f"✅ Added {len(courses)} courses")
            
            # 3. Add Enrollments (requires both users and courses to exist)
            print("Adding enrollments...")
            
            enrollments = [
                # CS101 enrollments
                Enrollment(student_id=8, course_id=1),  # John in CS101
                Enrollment(student_id=9, course_id=1),  # Jane in CS101
                Enrollment(student_id=10, course_id=1), # Mike in CS101
                Enrollment(student_id=11, course_id=1), # Emily in CS101
                
                # CS201 enrollments
                Enrollment(student_id=8, course_id=2),  # John in CS201
                Enrollment(student_id=10, course_id=2), # Mike in CS201
                Enrollment(student_id=12, course_id=2), # David in CS201
                
                # CS301 enrollments
                Enrollment(student_id=9, course_id=3),  # Jane in CS301
                Enrollment(student_id=11, course_id=3), # Emily in CS301
                Enrollment(student_id=12, course_id=3), # David in CS301
                
                # MATH101 enrollments
                Enrollment(student_id=8, course_id=4),  # John in MATH101
                Enrollment(student_id=9, course_id=4),  # Jane in MATH101
                Enrollment(student_id=10, course_id=4), # Mike in MATH101
                
                # MATH201 enrollments
                Enrollment(student_id=11, course_id=5), # Emily in MATH201
                Enrollment(student_id=12, course_id=5), # David in MATH201
            ]
            
            for enrollment in enrollments:
                db.session.add(enrollment)
            
            db.session.commit()
            print(f"✅ Added {len(enrollments)} enrollments")
            
            # Update course seat counts
            print("Updating course seat counts...")
            for course in courses:
                # Count enrollments for each course
                count = len([e for e in enrollments if e.course_id == course.id])
                course.seats_left = course.max_seats - count
            db.session.commit()
            print("✅ Updated seat counts")
            
            # 4. Add Assignments (requires courses to exist)
            print("Adding assignments...")
            
            # Create datetime objects for due dates
            due_date1 = datetime.now() + timedelta(days=14)  # 2 weeks from now
            due_date2 = datetime.now() + timedelta(days=21)  # 3 weeks from now
            due_date3 = datetime.now() + timedelta(days=7)   # 1 week from now
            
            assignments = [
                Assignment(
                    title='Python Basics Assignment',
                    description='Write a Python program that calculates the factorial of a number',
                    due_date=due_date1,
                    course_id=1  # CS101
                ),
                Assignment(
                    title='Midterm Exam',
                    description='Covers chapters 1-5: Variables, Loops, Functions, Lists, and Dictionaries',
                    due_date=due_date2,
                    course_id=1  # CS101
                ),
                Assignment(
                    title='Linked List Implementation',
                    description='Implement a singly linked list with insert, delete, and search operations',
                    due_date=due_date1,
                    course_id=2  # CS201
                ),
                Assignment(
                    title='Database Design Project',
                    description='Design a database schema for a library management system',
                    due_date=due_date3,
                    course_id=3  # CS301
                ),
                Assignment(
                    title='Calculus Problem Set 1',
                    description='Solve derivatives and integrals problems from chapter 2',
                    due_date=due_date3,
                    course_id=4  # MATH101
                ),
                Assignment(
                    title='Matrix Operations',
                    description='Implement matrix multiplication and determinant calculation',
                    due_date=due_date2,
                    course_id=5  # MATH201
                ),
            ]
            
            for assignment in assignments:
                db.session.add(assignment)
            
            db.session.commit()
            print(f"✅ Added {len(assignments)} assignments")
            
            # 5. Add Announcements (requires courses and users to exist)
            print("Adding announcements...")
            
            announcements = [
                Announcement(
                    title='Welcome to CS101!',
                    content='Welcome to Introduction to Programming. Please check the syllabus on the course page.',
                    poster_id=3,  # Dr. Sarah Johnson
                    course_id=1   # CS101
                ),
                Announcement(
                    title='Office Hours Change',
                    content='My office hours have changed to Tuesdays 2-4 PM instead of Thursdays.',
                    poster_id=3,  # Dr. Sarah Johnson
                    course_id=1   # CS101
                ),
                Announcement(
                    title='Important: Textbook Update',
                    content='The required textbook has been updated. Please check the resources page.',
                    poster_id=4,  # Prof. Robert Smith
                    course_id=3   # CS301
                ),
                Announcement(
                    title='Midterm Exam Schedule',
                    content='The midterm exam will be held in the main lecture hall on November 20th.',
                    poster_id=5,  # Dr. Jennifer Lee
                    course_id=4   # MATH101
                ),
            ]
            
            for announcement in announcements:
                db.session.add(announcement)
            
            db.session.commit()
            print(f"✅ Added {len(announcements)} announcements")
            
            # 6. Add Submissions (requires assignments and users to exist)
            print("Adding submissions...")
            
            submissions = [
                Submission(
                    assignment_id=1,  # Python Basics Assignment
                    student_id=8,     # John Doe
                    submission_text='def factorial(n):\n    if n == 0:\n        return 1\n    return n * factorial(n-1)',
                    grade=95.0,
                    feedback='Excellent implementation! Good use of recursion.'
                ),
                Submission(
                    assignment_id=1,  # Python Basics Assignment
                    student_id=9,     # Jane Smith
                    submission_text='def factorial(num):\n    result = 1\n    for i in range(1, num+1):\n        result *= i\n    return result',
                    grade=88.5,
                    feedback='Good iterative solution. Consider adding input validation.'
                ),
                Submission(
                    assignment_id=3,  # Linked List Implementation
                    student_id=8,     # John Doe
                    submission_text='class Node:\n    def __init__(self, data):\n        self.data = data\n        self.next = None',
                    grade=92.0,
                    feedback='Good start. Please complete the linked list operations.'
                ),
                Submission(
                    assignment_id=4,  # Database Design Project
                    student_id=9,     # Jane Smith
                    submission_text='CREATE TABLE books (id INT PRIMARY KEY, title VARCHAR(255), author VARCHAR(255));',
                    grade=None,  # Not graded yet
                    feedback=None
                ),
                Submission(
                    assignment_id=5,  # Calculus Problem Set 1
                    student_id=10,    # Mike Johnson
                    submission_text='∫ x² dx = (1/3)x³ + C',
                    grade=85.0,
                    feedback='Correct integration. Remember to include the constant of integration.'
                ),
            ]
            
            for submission in submissions:
                db.session.add(submission)
            
            db.session.commit()
            print(f"✅ Added {len(submissions)} submissions")
            
            print("\n" + "="*60)
            print("DUMMY DATA ADDED SUCCESSFULLY!")
            print("="*60)
            
            print("\n🔑 TEST CREDENTIALS:")
            print("   Admin:      admin@university.edu / admin123")
            print("   Instructor: sarah@instructor.edu / prof123")
            print("   TA:         alex@ta.edu / ta123")
            print("   Student:    john@student.edu / student123")
            
            print("\n📊 DATABASE SUMMARY:")
            print(f"   Users: {len(users)} (2 admin, 3 instructors, 2 TAs, 5 students)")
            print(f"   Courses: {len(courses)}")
            print(f"   Enrollments: {len(enrollments)}")
            print(f"   Assignments: {len(assignments)}")
            print(f"   Announcements: {len(announcements)}")
            print(f"   Submissions: {len(submissions)}")
            
            print("\n📚 COURSE ENROLLMENTS:")
            course_info = [
                ("CS101", 4, 30, "Dr. Sarah Johnson", "Alex Chen"),
                ("CS201", 3, 25, "Dr. Sarah Johnson", "Alex Chen"),
                ("CS301", 3, 28, "Prof. Robert Smith", "Lisa Wang"),
                ("MATH101", 3, 35, "Dr. Jennifer Lee", "None"),
                ("MATH201", 2, 30, "Dr. Jennifer Lee", "None"),
            ]
            for code, enrolled, max_seats, instructor, ta in course_info:
                print(f"   {code}: {enrolled}/{max_seats} students, Instructor: {instructor}, TA: {ta}")
            
        except exc.IntegrityError as e:
            print(f"❌ Integrity Error (constraint violation): {e}")
            db.session.rollback()
        except Exception as e:
            print(f"❌ Error adding dummy data: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
        
        print("\n" + "="*60)
        print("DATABASE INITIALIZATION COMPLETE")
        print("="*60)

if __name__ == '__main__':
    print("Initializing database with Windows Authentication...")
    init_database()