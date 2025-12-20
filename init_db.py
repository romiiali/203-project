import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from config import Config
from extensions import db
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from sqlalchemy import text, exc, inspect

def create_app():
    """Create Flask application for database initialization"""
    app = Flask(__name__)
    app.config.from_object(Config)
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
        
        print("\n📊 Checking existing database state...")
        
        # Check if tables exist
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        if existing_tables:
            print(f"Found {len(existing_tables)} existing tables:")
            for table in existing_tables:
                try:
                    count = db.session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                    print(f"  • {table}: {count} rows")
                except:
                    print(f"  • {table}: Could not count rows")
        
        print("\n🚨 WARNING: This will DELETE ALL EXISTING DATA!")
        response = input("Do you want to continue? (yes/no): ")
        
        if response.lower() != 'yes':
            print("Operation cancelled.")
            return
        
        print("\nCreating/Recreating database tables...")
        
        try:
            # Drop all tables first (in correct order to avoid foreign key issues)
            print("Dropping existing tables...")
            db.session.execute(text("EXEC sp_MSforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT all'"))
            db.session.execute(text("EXEC sp_MSforeachtable 'DROP TABLE ?'"))
            db.session.commit()
            print("✅ Dropped existing tables")
        except Exception as e:
            print(f"⚠️ Could not drop tables: {e}")
            print("Trying to continue with create_all...")
        
        try:
            # Create all tables fresh
            db.create_all()
            print("✅ Tables created successfully")
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return
        
        # ============== ADD DUMMY DATA ==============
        print("\nAdding dummy data...")
        
        try:
            # Import models AFTER creating tables
            from models.user import User
            from models.courses import Course
            from models.enrollment import Enrollment
            from models.assignment import Assignment
            from models.announcement import Announcement
            from models.submission import Submission
            
            # 1. Add Users - ONE BY ONE with commits
            print("Adding users one by one...")
            
            # Add users individually to ensure proper IDs
            admin1 = User(name='Admin User', email='admin@university.edu', role='admin', password='admin123')
            db.session.add(admin1)
            db.session.commit()
            
            admin2 = User(name='System Admin', email='sysadmin@university.edu', role='admin', password='admin123')
            db.session.add(admin2)
            db.session.commit()
            
            instructor1 = User(name='Dr. Sarah Johnson', email='sarah@instructor.edu', role='instructor', password='prof123')
            db.session.add(instructor1)
            db.session.commit()
            
            instructor2 = User(name='Prof. Robert Smith', email='robert@instructor.edu', role='instructor', password='prof123')
            db.session.add(instructor2)
            db.session.commit()
            
            instructor3 = User(name='Dr. Jennifer Lee', email='jennifer@instructor.edu', role='instructor', password='prof123')
            db.session.add(instructor3)
            db.session.commit()
            
            # TAs
            ta1 = User(name='Alex Chen', email='alex@ta.edu', role='ta', password='ta123')
            db.session.add(ta1)
            db.session.commit()
            
            ta2 = User(name='Lisa Wang', email='lisa@ta.edu', role='ta', password='ta123')
            db.session.add(ta2)
            db.session.commit()
            
            ta3 = User(name='Michael Brown', email='michael@ta.edu', role='ta', password='ta123')
            db.session.add(ta3)
            db.session.commit()
            
            ta4 = User(name='Sarah Davis', email='sarah@ta.edu', role='ta', password='ta123')
            db.session.add(ta4)
            db.session.commit()
            
            ta5 = User(name='David Wilson', email='david@ta.edu', role='ta', password='ta123')
            db.session.add(ta5)
            db.session.commit()
            
            # Students
            students = [
                ('John Doe', 'john@student.edu', 'student123'),
                ('Jane Smith', 'jane@student.edu', 'student123'),
                ('Mike Johnson', 'mike@student.edu', 'student123'),
                ('Emily Davis', 'emily@student.edu', 'student123'),
                ('Chris Wilson', 'chris@student.edu', 'student123'),
                ('Jessica Lee', 'jessica@student.edu', 'student123'),
                ('Daniel Kim', 'daniel@student.edu', 'student123'),
                ('Amanda Taylor', 'amanda@student.edu', 'student123'),
            ]
            
            for name, email, password in students:
                student = User(name=name, email=email, role='student', password=password)
                db.session.add(student)
                db.session.commit()
            
            print(f"✅ Added 18 users total")
            
            # Get user IDs
            dr_sarah = User.query.filter_by(email='sarah@instructor.edu').first()
            prof_robert = User.query.filter_by(email='robert@instructor.edu').first()
            dr_jennifer = User.query.filter_by(email='jennifer@instructor.edu').first()
            
            alex_ta = User.query.filter_by(email='alex@ta.edu').first()
            lisa_ta = User.query.filter_by(email='lisa@ta.edu').first()
            michael_ta = User.query.filter_by(email='michael@ta.edu').first()
            sarah_ta = User.query.filter_by(email='sarah@ta.edu').first()
            david_ta = User.query.filter_by(email='david@ta.edu').first()
            
            # 2. Add Courses
            print("\nAdding courses...")
            
            courses = [
                # CS101 - Alex Chen is the ONLY TA for this course
                Course(
                    code='CS101',
                    name='Introduction to Programming',
                    description='Learn basic programming concepts using Python',
                    instructor_id=dr_sarah.id,
                    ta_id=alex_ta.id,
                    credits=3,
                    max_seats=35,
                    seats_left=35,
                    schedule='Mon/Wed 10:00-11:30 AM',
                    department='Computer Science'
                ),
                # CS201 - Lisa Wang is the ONLY TA for this course
                Course(
                    code='CS201',
                    name='Data Structures and Algorithms',
                    description='Study of fundamental data structures and algorithms',
                    instructor_id=dr_sarah.id,
                    ta_id=lisa_ta.id,
                    credits=4,
                    max_seats=30,
                    seats_left=30,
                    schedule='Tue/Thu 1:00-2:30 PM',
                    department='Computer Science'
                ),
                # CS301 - Michael Brown is the ONLY TA for this course
                Course(
                    code='CS301',
                    name='Database Systems',
                    description='Introduction to database design and SQL',
                    instructor_id=prof_robert.id,
                    ta_id=michael_ta.id,
                    credits=3,
                    max_seats=28,
                    seats_left=28,
                    schedule='Mon/Wed 2:00-3:30 PM',
                    department='Computer Science'
                ),
                # MATH101 - Sarah Davis is the ONLY TA for this course
                Course(
                    code='MATH101',
                    name='Calculus I',
                    description='Introduction to differential and integral calculus',
                    instructor_id=dr_jennifer.id,
                    ta_id=sarah_ta.id,
                    credits=4,
                    max_seats=40,
                    seats_left=40,
                    schedule='Tue/Thu/Fri 9:00-10:00 AM',
                    department='Mathematics'
                ),
                # MATH201 - David Wilson is the ONLY TA for this course
                Course(
                    code='MATH201',
                    name='Linear Algebra',
                    description='Vectors, matrices, and linear transformations',
                    instructor_id=dr_jennifer.id,
                    ta_id=david_ta.id,
                    credits=3,
                    max_seats=35,
                    seats_left=35,
                    schedule='Mon/Wed/Fri 11:00-12:00 PM',
                    department='Mathematics'
                ),
            ]
            
            for course in courses:
                db.session.add(course)
                db.session.commit()
            
            print(f"✅ Added {len(courses)} courses")
            
            # Get course objects
            cs101 = Course.query.filter_by(code='CS101').first()
            cs201 = Course.query.filter_by(code='CS201').first()
            cs301 = Course.query.filter_by(code='CS301').first()
            math101 = Course.query.filter_by(code='MATH101').first()
            math201 = Course.query.filter_by(code='MATH201').first()
            
            # Get student objects
            john = User.query.filter_by(email='john@student.edu').first()
            jane = User.query.filter_by(email='jane@student.edu').first()
            mike = User.query.filter_by(email='mike@student.edu').first()
            emily = User.query.filter_by(email='emily@student.edu').first()
            chris = User.query.filter_by(email='chris@student.edu').first()
            jessica = User.query.filter_by(email='jessica@student.edu').first()
            daniel = User.query.filter_by(email='daniel@student.edu').first()
            amanda = User.query.filter_by(email='amanda@student.edu').first()
            
            # 3. Add Enrollments
            print("Adding enrollments...")
            
            enrollments = [
                # CS101 enrollments (Alex Chen's course)
                Enrollment(student_id=john.id, course_id=cs101.id),
                Enrollment(student_id=jane.id, course_id=cs101.id),
                Enrollment(student_id=mike.id, course_id=cs101.id),
                Enrollment(student_id=emily.id, course_id=cs101.id),
                Enrollment(student_id=chris.id, course_id=cs101.id),
                
                # CS201 enrollments (Lisa Wang's course)
                Enrollment(student_id=john.id, course_id=cs201.id),
                Enrollment(student_id=mike.id, course_id=cs201.id),
                Enrollment(student_id=chris.id, course_id=cs201.id),
                Enrollment(student_id=jessica.id, course_id=cs201.id),
                
                # CS301 enrollments (Michael Brown's course)
                Enrollment(student_id=jane.id, course_id=cs301.id),
                Enrollment(student_id=emily.id, course_id=cs301.id),
                Enrollment(student_id=jessica.id, course_id=cs301.id),
                Enrollment(student_id=daniel.id, course_id=cs301.id),
                
                # MATH101 enrollments (Sarah Davis's course)
                Enrollment(student_id=john.id, course_id=math101.id),
                Enrollment(student_id=jane.id, course_id=math101.id),
                Enrollment(student_id=mike.id, course_id=math101.id),
                Enrollment(student_id=daniel.id, course_id=math101.id),
                Enrollment(student_id=amanda.id, course_id=math101.id),
                
                # MATH201 enrollments (David Wilson's course)
                Enrollment(student_id=emily.id, course_id=math201.id),
                Enrollment(student_id=chris.id, course_id=math201.id),
                Enrollment(student_id=jessica.id, course_id=math201.id),
                Enrollment(student_id=amanda.id, course_id=math201.id),
            ]
            
            for enrollment in enrollments:
                db.session.add(enrollment)
            db.session.commit()
            
            print(f"✅ Added {len(enrollments)} enrollments")
            
            # Update course seat counts
            print("Updating course seat counts...")
            cs101.seats_left = cs101.max_seats - 5
            cs201.seats_left = cs201.max_seats - 4
            cs301.seats_left = cs301.max_seats - 4
            math101.seats_left = math101.max_seats - 5
            math201.seats_left = math201.max_seats - 4
            db.session.commit()
            print("✅ Updated seat counts")
            
            # 4. Add Assignments
            print("Adding assignments...")
            
            due_date1 = datetime.now() + timedelta(days=7)
            due_date2 = datetime.now() + timedelta(days=14)
            due_date3 = datetime.now() + timedelta(days=21)
            
            assignments = [
                # CS101 assignments
                Assignment(
                    title='Python Basics Quiz',
                    description='Complete the Python basics quiz on variables, data types, and loops',
                    due_date=due_date1,
                    course_id=cs101.id
                ),
                Assignment(
                    title='Functions Project',
                    description='Create a Python program with at least 3 custom functions',
                    due_date=due_date2,
                    course_id=cs101.id
                ),
                
                # CS201 assignments
                Assignment(
                    title='Linked List Implementation',
                    description='Implement a singly linked list with insert, delete, and search operations',
                    due_date=due_date1,
                    course_id=cs201.id
                ),
                
                # CS301 assignments
                Assignment(
                    title='SQL Queries Assignment',
                    description='Write SQL queries for the given database schema',
                    due_date=due_date2,
                    course_id=cs301.id
                ),
            ]
            
            for assignment in assignments:
                db.session.add(assignment)
            db.session.commit()
            
            print(f"✅ Added {len(assignments)} assignments")
            
            # Get assignment objects
            cs101_assignment1 = Assignment.query.filter_by(title='Python Basics Quiz').first()
            cs101_assignment2 = Assignment.query.filter_by(title='Functions Project').first()
            cs201_assignment1 = Assignment.query.filter_by(title='Linked List Implementation').first()
            cs301_assignment1 = Assignment.query.filter_by(title='SQL Queries Assignment').first()
            
            # 5. Add Submissions
            print("Adding submissions...")
            
            submissions = [
                # CS101 submissions (for Alex Chen to grade)
                Submission(
                    assignment_id=cs101_assignment1.id,
                    student_id=john.id,
                    submission_text='def factorial(n):\n    if n == 0:\n        return 1\n    return n * factorial(n-1)',
                    grade=95.0,
                    feedback='Excellent work! Perfect recursive implementation.'
                ),
                Submission(
                    assignment_id=cs101_assignment1.id,
                    student_id=jane.id,
                    submission_text='def calculate_average(numbers):\n    return sum(numbers) / len(numbers)',
                    grade=88.0,
                    feedback='Good implementation. Add input validation.'
                ),
                Submission(
                    assignment_id=cs101_assignment1.id,
                    student_id=mike.id,
                    submission_text='# Working on it',
                    grade=None,
                    feedback=None
                ),
                
                # CS201 submissions (for Lisa Wang to grade)
                Submission(
                    assignment_id=cs201_assignment1.id,
                    student_id=john.id,
                    submission_text='class Node:\n    def __init__(self, data):\n        self.data = data\n        self.next = None',
                    grade=92.0,
                    feedback='Good start. Complete the linked list operations.'
                ),
                
                # CS301 submissions (for Michael Brown to grade)
                Submission(
                    assignment_id=cs301_assignment1.id,
                    student_id=jane.id,
                    submission_text='SELECT * FROM students WHERE grade > 80',
                    grade=None,
                    feedback=None
                ),
            ]
            
            for submission in submissions:
                db.session.add(submission)
            db.session.commit()
            
            print(f"✅ Added {len(submissions)} submissions")
            
            # 6. Add Announcements
            print("Adding announcements...")
            
            announcements = [
                # Posted by Alex Chen (TA for CS101)
                Announcement(
                    title='Office Hours This Week',
                    content='My office hours will be extended on Wednesday 2-4 PM for assignment help.',
                    poster_id=alex_ta.id,
                    course_id=cs101.id
                ),
                Announcement(
                    title='Assignment 1 Graded',
                    content='Assignment 1 has been graded. Check your grades and feedback.',
                    poster_id=alex_ta.id,
                    course_id=cs101.id
                ),
                
                # Posted by instructor
                Announcement(
                    title='Welcome to CS101!',
                    content='Welcome to Introduction to Programming. Please check the syllabus.',
                    poster_id=dr_sarah.id,
                    course_id=cs101.id
                ),
            ]
            
            for announcement in announcements:
                db.session.add(announcement)
            db.session.commit()
            
            print(f"✅ Added {len(announcements)} announcements")
            
            print("\n" + "="*60)
            print("DUMMY DATA ADDED SUCCESSFULLY!")
            print("="*60)
            
            print("\n🔑 TEST CREDENTIALS:")
            print("   Admin:      admin@university.edu / admin123")
            print("   Instructor: sarah@instructor.edu / prof123")
            print("   TA:         alex@ta.edu / ta123 (CS101 TA)")
            print("   Student:    john@student.edu / student123")
            
            print("\n📊 DATABASE SUMMARY:")
            print(f"   Users: 18 total")
            print(f"   Courses: 5 (each with one TA)")
            print(f"   Enrollments: {len(enrollments)}")
            print(f"   Assignments: {len(assignments)}")
            print(f"   Submissions: {len(submissions)}")
            print(f"   Announcements: {len(announcements)}")
            
            print("\n📚 COURSE ASSIGNMENTS:")
            print("   CS101 (Alex Chen): 5 students, 2 assignments, 3 submissions")
            print("   CS201 (Lisa Wang): 4 students, 1 assignment, 1 submission")
            print("   CS301 (Michael Brown): 4 students, 1 assignment, 1 submission")
            print("   MATH101 (Sarah Davis): 5 students, 0 assignments")
            print("   MATH201 (David Wilson): 4 students, 0 assignments")
            
            print("\n🎯 TA GRADING READY:")
            print("   • Alex Chen can grade submissions in CS101")
            print("   • Lisa Wang can grade submissions in CS201")
            print("   • Michael Brown can grade submissions in CS301")
            
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