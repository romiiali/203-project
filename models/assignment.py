from extensions import db

class Assignment(db.Model):
    __tablename__ = 'assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Foreign key
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    
    # Relationship
    submissions = db.relationship('Submission', backref='assignment', cascade='all, delete-orphan')
    
    @staticmethod
    def get_by_course(course_id):
        return Assignment.query.filter_by(course_id=course_id).all()
    
    @staticmethod
    def get_by_id(assignment_id):
        return Assignment.query.get(assignment_id)
    
    def add_submission(self, student_id, submission_text):
        """Add submission for this assignment"""
        from models.submission import Submission
        submission = Submission(
            assignment_id=self.id,
            student_id=student_id,
            submission_text=submission_text
        )
        db.session.add(submission)
        db.session.commit()
        return True
    
    def get_submission(self, student_id):
        """Get submission for a specific student"""
        from models.submission import Submission
        return Submission.query.filter_by(
            assignment_id=self.id,
            student_id=student_id
        ).first()
    
    def get_all_submissions(self):
        """Get all submissions for this assignment"""
        from models.submission import Submission
        return Submission.query.filter_by(assignment_id=self.id).all()