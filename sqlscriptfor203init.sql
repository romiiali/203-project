-- ============================================
-- Course Management System Database Script
-- Updated for Single Table Inheritance
-- ============================================

USE CourseManagement;
GO

-- ============================================
-- 1. DROP TABLES (if they exist)
-- ============================================
IF OBJECT_ID('submissions', 'U') IS NOT NULL DROP TABLE submissions;
IF OBJECT_ID('announcements', 'U') IS NOT NULL DROP TABLE announcements;
IF OBJECT_ID('assignments', 'U') IS NOT NULL DROP TABLE assignments;
IF OBJECT_ID('enrollments', 'U') IS NOT NULL DROP TABLE enrollments;
IF OBJECT_ID('courses', 'U') IS NOT NULL DROP TABLE courses;
IF OBJECT_ID('users', 'U') IS NOT NULL DROP TABLE users;
GO

-- ============================================
-- 2. CREATE TABLES with single users table
-- ============================================

-- Users table with ALL user types (single-table inheritance)
CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    email NVARCHAR(120) UNIQUE NOT NULL,
    password_hash NVARCHAR(256) NOT NULL,
    role NVARCHAR(50) NOT NULL CHECK (role IN ('student', 'instructor', 'ta', 'admin')),
    
    -- Student-specific fields (nullable for other roles)
    major NVARCHAR(100),
    level NVARCHAR(50),
    
    -- Instructor/TA-specific fields
    office NVARCHAR(100),
    office_hours NVARCHAR(100),
    
    created_at DATETIME DEFAULT GETDATE()
);
GO

CREATE INDEX idx_email ON users(email);
GO

-- Courses table
CREATE TABLE courses (
    id INT IDENTITY(1,1) PRIMARY KEY,
    code NVARCHAR(20) UNIQUE NOT NULL,
    name NVARCHAR(200) NOT NULL,
    description NVARCHAR(MAX),
    credits INT NOT NULL DEFAULT 3,
    max_seats INT NOT NULL DEFAULT 30,
    seats_left INT NOT NULL DEFAULT 30,
    schedule NVARCHAR(100),
    department NVARCHAR(100),
    
    instructor_id INT FOREIGN KEY REFERENCES users(id),
    ta_id INT FOREIGN KEY REFERENCES users(id)
);
GO

CREATE INDEX idx_code ON courses(code);
GO

-- Enrollments table
CREATE TABLE enrollments (
    id INT IDENTITY(1,1) PRIMARY KEY,
    student_id INT NOT NULL FOREIGN KEY REFERENCES users(id),
    course_id INT NOT NULL FOREIGN KEY REFERENCES courses(id),
    enrolled_at DATETIME DEFAULT GETDATE(),
    
    CONSTRAINT unique_enrollment UNIQUE (student_id, course_id)
);
GO

-- Assignments table
CREATE TABLE assignments (
    id INT IDENTITY(1,1) PRIMARY KEY,
    title NVARCHAR(200) NOT NULL,
    description NVARCHAR(MAX),
    due_date DATETIME NOT NULL,
    created_at DATETIME DEFAULT GETDATE(),
    course_id INT NOT NULL FOREIGN KEY REFERENCES courses(id)
);
GO

-- Announcements table
CREATE TABLE announcements (
    id INT IDENTITY(1,1) PRIMARY KEY,
    title NVARCHAR(200) NOT NULL,
    content NVARCHAR(MAX) NOT NULL,
    created_at DATETIME DEFAULT GETDATE(),
    poster_id INT NOT NULL FOREIGN KEY REFERENCES users(id),
    course_id INT NOT NULL FOREIGN KEY REFERENCES courses(id)
);
GO

-- Submissions table
CREATE TABLE submissions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    submission_text NVARCHAR(MAX) NOT NULL,
    grade FLOAT,
    feedback NVARCHAR(MAX),
    submitted_at DATETIME DEFAULT GETDATE(),
    assignment_id INT NOT NULL FOREIGN KEY REFERENCES assignments(id),
    student_id INT NOT NULL FOREIGN KEY REFERENCES users(id),
    
    CONSTRAINT unique_submission UNIQUE (assignment_id, student_id)
);
GO

-- ============================================
-- 3. INSERT DUMMY DATA with role-specific fields
-- ============================================

EXEC sp_MSforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT all';
GO

DELETE FROM submissions;
DELETE FROM announcements;
DELETE FROM assignments;
DELETE FROM enrollments;
DELETE FROM courses;
DELETE FROM users;
GO

DBCC CHECKIDENT ('users', RESEED, 0);
DBCC CHECKIDENT ('courses', RESEED, 0);
DBCC CHECKIDENT ('enrollments', RESEED, 0);
DBCC CHECKIDENT ('assignments', RESEED, 0);
DBCC CHECKIDENT ('announcements', RESEED, 0);
DBCC CHECKIDENT ('submissions', RESEED, 0);
GO

-- Insert Users with role-specific data
-- Password hash for 'password123'
INSERT INTO users (name, email, password_hash, role, major, level, office, office_hours) VALUES
-- Admins
('Admin User', 'admin@university.edu', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'admin', NULL, NULL, 'Admin Building 101', 'Mon-Fri 9-5'),
('System Admin', 'sysadmin@university.edu', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'admin', NULL, NULL, 'Admin Building 102', 'Mon-Fri 9-5'),

-- Instructors
('Dr. Sarah Johnson', 'sarah@instructor.edu', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'instructor', NULL, NULL, 'CS Building 301', 'Mon/Wed 2-4 PM'),
('Prof. Robert Smith', 'robert@instructor.edu', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'instructor', NULL, NULL, 'CS Building 302', 'Tue/Thu 1-3 PM'),
('Dr. Jennifer Lee', 'jennifer@instructor.edu', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'instructor', NULL, NULL, 'Math Building 201', 'Mon/Wed/Fri 10-12 PM'),

-- TAs
('Alex Chen', 'alex@ta.edu', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'ta', NULL, NULL, 'CS Building 105', 'Tue 3-5 PM'),
('Lisa Wang', 'lisa@ta.edu', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'ta', NULL, NULL, 'CS Building 106', 'Thu 3-5 PM'),

-- Students (with major and level)
('John Doe', 'john@student.edu', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'student', 'Computer Science', 'Sophomore', NULL, NULL),
('Jane Smith', 'jane@student.edu', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'student', 'Mathematics', 'Junior', NULL, NULL),
('Mike Johnson', 'mike@student.edu', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'student', 'Computer Science', 'Freshman', NULL, NULL),
('Emily Davis', 'emily@student.edu', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'student', 'Mathematics', 'Senior', NULL, NULL),
('David Wilson', 'david@student.edu', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'student', 'Physics', 'Sophomore', NULL, NULL);
GO

-- ... (rest of the SQL remains the same - courses, enrollments, assignments, etc.)
-- Insert Courses
INSERT INTO courses (code, name, description, instructor_id, ta_id, credits, max_seats, seats_left, schedule, department) VALUES
('CS101', 'Introduction to Programming', 'Learn basic programming concepts using Python', 3, 6, 3, 30, 26, 'Mon/Wed 10:00-11:30 AM', 'Computer Science'),
('CS201', 'Data Structures and Algorithms', 'Study of fundamental data structures and algorithms', 3, 6, 4, 25, 22, 'Tue/Thu 1:00-2:30 PM', 'Computer Science'),
('CS301', 'Database Systems', 'Introduction to database design and SQL', 4, 7, 3, 28, 25, 'Mon/Wed 2:00-3:30 PM', 'Computer Science'),
('MATH101', 'Calculus I', 'Introduction to differential and integral calculus', 5, NULL, 4, 35, 32, 'Tue/Thu/Fri 9:00-10:00 AM', 'Mathematics'),
('MATH201', 'Linear Algebra', 'Vectors, matrices, and linear transformations', 5, NULL, 3, 30, 28, 'Mon/Wed/Fri 11:00-12:00 PM', 'Mathematics');
GO

-- Insert Enrollments
INSERT INTO enrollments (student_id, course_id) VALUES
-- CS101 (id=1)
(8, 1), (9, 1), (10, 1), (11, 1),
-- CS201 (id=2)
(8, 2), (10, 2), (12, 2),
-- CS301 (id=3)
(9, 3), (11, 3), (12, 3),
-- MATH101 (id=4)
(8, 4), (9, 4), (10, 4),
-- MATH201 (id=5)
(11, 5), (12, 5);
GO

-- Update course seat counts
UPDATE courses 
SET seats_left = max_seats - (
    SELECT COUNT(*) 
    FROM enrollments 
    WHERE enrollments.course_id = courses.id
);
GO

-- Insert Assignments
INSERT INTO assignments (title, description, due_date, course_id) VALUES
('Python Basics Assignment', 'Write a Python program that calculates the factorial of a number', DATEADD(day, 14, GETDATE()), 1),
('Midterm Exam', 'Covers chapters 1-5: Variables, Loops, Functions, Lists, and Dictionaries', DATEADD(day, 21, GETDATE()), 1),
('Linked List Implementation', 'Implement a singly linked list with insert, delete, and search operations', DATEADD(day, 14, GETDATE()), 2),
('Database Design Project', 'Design a database schema for a library management system', DATEADD(day, 7, GETDATE()), 3),
('Calculus Problem Set 1', 'Solve derivatives and integrals problems from chapter 2', DATEADD(day, 7, GETDATE()), 4),
('Matrix Operations', 'Implement matrix multiplication and determinant calculation', DATEADD(day, 21, GETDATE()), 5);
GO

-- Insert Announcements
INSERT INTO announcements (title, content, poster_id, course_id) VALUES
('Welcome to CS101!', 'Welcome to Introduction to Programming. Please check the syllabus on the course page.', 3, 1),
('Office Hours Change', 'My office hours have changed to Tuesdays 2-4 PM instead of Thursdays.', 3, 1),
('Important: Textbook Update', 'The required textbook has been updated. Please check the resources page.', 4, 3),
('Midterm Exam Schedule', 'The midterm exam will be held in the main lecture hall on November 20th.', 5, 4);
GO

-- Insert Submissions
INSERT INTO submissions (assignment_id, student_id, submission_text, grade, feedback) VALUES
(1, 8, 'def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n-1)', 95.0, 'Excellent implementation! Good use of recursion.'),
(1, 9, 'def factorial(num):
    result = 1
    for i in range(1, num+1):
        result *= i
    return result', 88.5, 'Good iterative solution. Consider adding input validation.'),
(3, 8, 'class Node:
    def __init__(self, data):
        self.data = data
        self.next = None', 92.0, 'Good start. Please complete the linked list operations.'),
(4, 9, 'CREATE TABLE books (id INT PRIMARY KEY, title VARCHAR(255), author VARCHAR(255));', NULL, NULL),
(5, 10, '∫ x² dx = (1/3)x³ + C', 85.0, 'Correct integration. Remember to include the constant of integration.');
GO

EXEC sp_MSforeachtable 'ALTER TABLE ? WITH CHECK CHECK CONSTRAINT all';
GO

PRINT 'Database created with single-table inheritance!';
PRINT 'All users in one table with role-specific fields.';
GO