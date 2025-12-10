import pytest
from unittest.mock import Mock, patch
from models.student import Student
from models.courses import Course
from models.assignment import Assignment
from models.user import User

class TestStudentModel:
    """Tests for Student model (inherits from User)"""
    
    def test_student_creation(self):
        """Test creating a student instance"""
        student = Student(
            id=1,
            name="John Doe",
            email="john@student.edu",
            password="pass123",
            major="Computer Science",
            level="Sophomore"
        )
        
        assert student.id == 1
        assert student.name == "John Doe"
        assert student.email == "john@student.edu"
        assert student.role == "student"
        assert student.major == "Computer Science"
        assert student.level == "Sophomore"
        assert student.enrolled_courses == []
    
    def test_get_by_id_static(self):
        """Test getting student by ID using static method"""
        student = Student.get_by_id(1)
        assert student is not None
        assert student.id == 1
        assert student.name == "John Doe"
        assert student.email == "john@student.edu"
    
    def test_get_by_id_not_found(self):
        """Test getting non-existent student"""
        student = Student.get_by_id(999)
        assert student is None
    
    def test_get_all_students(self):
        """Test getting all students"""
        students = Student.get_all_students()
        assert len(students) == 3
        assert all(student.role == "student" for student in students)
    
    @patch('models.student.Course')
    def test_enroll_course_success(self, mock_course):
        """Test successful course enrollment"""
        # Mock course
        mock_course_instance = Mock()
        mock_course_instance.id = 101
        mock_course_instance.seats_left = 5
        mock_course_instance.enrolled_students = []
        mock_course.get_by_id.return_value = mock_course_instance
        
        # Create student
        student = Student(
            id=1,
            name="John Doe",
            email="john@student.edu",
            password="pass123",
            major="CS",
            level="Sophomore"
        )
        student.enrolled_courses = []
        
        # Enroll in course
        success, message = student.enroll_course(101)
        
        assert success is True
        assert "successfully" in message.lower()
        assert 101 in student.enrolled_courses
        assert student.id in mock_course_instance.enrolled_students
        assert mock_course_instance.seats_left == 4
    
    @patch('models.student.Course')
    def test_enroll_course_not_found(self, mock_course):
        """Test enrolling in non-existent course"""
        mock_course.get_by_id.return_value = None
        
        student = Student(1, "John", "john@test.com", "pass", "CS", "Soph")
        
        success, message = student.enroll_course(999)
        
        assert success is False
        assert "not found" in message.lower()
    
    @patch('models.student.Course')
    def test_enroll_course_no_seats(self, mock_course):
        """Test enrolling in course with no seats"""
        mock_course_instance = Mock()
        mock_course_instance.id = 101
        mock_course_instance.seats_left = 0
        mock_course_instance.enrolled_students = []
        mock_course.get_by_id.return_value = mock_course_instance
        
        student = Student(1, "John", "john@test.com", "pass", "CS", "Soph")
        
        success, message = student.enroll_course(101)
        
        assert success is False
        assert "no seats" in message.lower()
    
    @patch('models.student.Course')
    def test_enroll_course_already_enrolled(self, mock_course):
        """Test enrolling in course already enrolled"""
        mock_course_instance = Mock()
        mock_course_instance.id = 101
        mock_course_instance.seats_left = 5
        mock_course_instance.enrolled_students = [1]  # Student already enrolled
        mock_course.get_by_id.return_value = mock_course_instance
        
        student = Student(1, "John", "john@test.com", "pass", "CS", "Soph")
        student.enrolled_courses = [101]  # Already enrolled
        
        success, message = student.enroll_course(101)
        
        assert success is False
        assert "already" in message.lower()
    
    @patch('models.student.Course')
    def test_drop_course_success(self, mock_course):
        """Test successful course drop"""
        mock_course_instance = Mock()
        mock_course_instance.id = 101
        mock_course_instance.enrolled_students = [1, 2, 3]  # Multiple students
        mock_course_instance.seats_left = 2
        mock_course.get_by_id.return_value = mock_course_instance
        
        student = Student(1, "John", "john@test.com", "pass", "CS", "Soph")
        student.enrolled_courses = [101, 102]  # Enrolled in two courses
        
        success, message = student.drop_course(101)
        
        assert success is True
        assert "dropped" in message.lower()
        assert 101 not in student.enrolled_courses
        assert 1 not in mock_course_instance.enrolled_students
        assert mock_course_instance.seats_left == 3
    
    @patch('models.student.Course')
    def test_drop_course_not_enrolled(self, mock_course):
        """Test dropping course not enrolled in"""
        student = Student(1, "John", "john@test.com", "pass", "CS", "Soph")
        student.enrolled_courses = []  # Not enrolled in any courses
        
        success, message = student.drop_course(101)
        
        assert success is False
        assert "not enrolled" in message.lower()
    
    @patch('models.student.Course')
    def test_get_enrolled_courses(self, mock_course):
        """Test getting enrolled courses"""
        # Mock course instances
        course1 = Mock()
        course1.id = 101
        course1.name = "CS101"
        
        course2 = Mock()
        course2.id = 102
        course2.name = "MATH101"
        
        mock_course.get_by_id.side_effect = lambda course_id: {
            101: course1,
            102: course2
        }.get(course_id)
        
        student = Student(1, "John", "john@test.com", "pass", "CS", "Soph")
        student.enrolled_courses = [101, 102]
        
        courses = student.get_enrolled_courses()
        
        assert len(courses) == 2
        assert any(course.name == "CS101" for course in courses)
        assert any(course.name == "MATH101" for course in courses)
    
    def test_is_enrolled_in_course(self):
        """Test checking if enrolled in course"""
        student = Student(1, "John", "john@test.com", "pass", "CS", "Soph")
        student.enrolled_courses = [101, 102]
        
        assert student.is_enrolled_in_course(101) is True
        assert student.is_enrolled_in_course(102) is True
        assert student.is_enrolled_in_course(103) is False
    
    @patch('models.student.Assignment')
    def test_get_assignment_status(self, mock_assignment):
        """Test getting assignment status"""
        # Mock assignment
        mock_assignment_instance = Mock()
        mock_assignment_instance.get_submission_status.return_value = {
            'submitted': True,
            'grade': 85,
            'timestamp': '2024-01-01'
        }
        mock_assignment.get_by_id.return_value = mock_assignment_instance
        
        student = Student(1, "John", "john@test.com", "pass", "CS", "Soph")
        
        status = student.get_assignment_status(201)
        
        assert status['submitted'] is True
        assert status['grade'] == 85
        assert status['timestamp'] == '2024-01-01'
    
    @patch('models.student.Assignment')
    def test_get_assignment_status_not_found(self, mock_assignment):
        """Test getting status for non-existent assignment"""
        mock_assignment.get_by_id.return_value = None
        
        student = Student(1, "John", "john@test.com", "pass", "CS", "Soph")
        
        status = student.get_assignment_status(999)
        
        assert status['submitted'] is False
        assert status['grade'] is None
        assert status['timestamp'] is None