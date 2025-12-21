from extensions import db
from datetime import datetime
from sqlalchemy import event

class Assignment(db.Model):
    __tablename__ = 'assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Foreign key
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    
    # Relationships
    submissions = db.relationship('Submission', backref='assignment', cascade='all, delete-orphan', lazy=True)
    
    def __repr__(self):
        return f'<Assignment {self.title}>'
    
    @staticmethod
    def get_by_course(course_id):
        """Get all assignments for a course"""
        return Assignment.query.filter_by(course_id=course_id).order_by(Assignment.due_date).all()
    
    @staticmethod
    def get_by_id(assignment_id):
        """Get assignment by ID"""
        return Assignment.query.get(assignment_id)
    
    @staticmethod
    def get_upcoming():
        """Get upcoming assignments"""
        return Assignment.query.filter(
            Assignment.due_date > datetime.now()
        ).order_by(Assignment.due_date).all()
    
    def add_submission(self, student_id, submission_text):
        """Add or update submission for this assignment"""
        from models.submission import Submission
        
        # Check if submission already exists
        existing = Submission.query.filter_by(
            assignment_id=self.id,
            student_id=student_id
        ).first()
        
        if existing:
            # Update existing submission
            existing.submission_text = submission_text
            existing.submitted_at = db.func.current_timestamp()
            db.session.commit()
            return True, "Submission updated successfully"
        else:
            # Create new submission
            submission = Submission(
                assignment_id=self.id,
                student_id=student_id,
                submission_text=submission_text
            )
            db.session.add(submission)
            db.session.commit()
            return True, "Submission added successfully"
    
    def get_submission(self, student_id):
        """Get submission for a specific student"""
        from models.submission import Submission
        return Submission.query.filter_by(
            assignment_id=self.id,
            student_id=student_id
        ).first()
    
    def grade_submission(self, student_id, grade, feedback=None):
        """Grade a submission"""
        submission = self.get_submission(student_id)
        if submission:
            try:
                # Validate grade
                grade_float = float(grade)
                if grade_float < 0 or grade_float > 100:
                    return False, "Grade must be between 0 and 100"
                    
                submission.grade = grade_float
                submission.feedback = feedback
                db.session.commit()
                return True, "Grade submitted successfully"
            except (ValueError, TypeError):
                return False, "Invalid grade format. Please enter a number."
        return False, "Submission not found"
    
    def get_all_submissions(self):
        """Get all submissions for this assignment with student information"""
        from models.submission import Submission
        from models.user import User
        
        # Query submissions with student info
        submissions = db.session.query(
            Submission,
            User
        ).join(
            User, Submission.student_id == User.id
        ).filter(
            Submission.assignment_id == self.id
        ).all()
        
        # Format the results
        result = []
        for submission, student in submissions:
            result.append({
                'submission': submission,
                'student': student,
                'id': submission.id,  # Use submission ID, not student ID
                'grade': submission.grade,
                'feedback': submission.feedback,
                'timestamp': submission.submitted_at,
                'text': submission.submission_text
            })
        
        return result
    
    def is_past_due(self):
        """Check if assignment is past due"""
        return datetime.now() > self.due_date
    
    def to_dict(self):
        """Convert assignment to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'course_id': self.course_id,
            'is_past_due': self.is_past_due(),
            'time_remaining': self.time_remaining(),
            'submission_count': self.get_submission_count(),
            'average_grade': self.get_average_grade()
        }


