from extensions import db

class Submission(db.Model):
    __tablename__ = 'submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    submission_text = db.Column(db.Text, nullable=False)
    grade = db.Column(db.Float)
    feedback = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Foreign keys
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('assignment_id', 'student_id', name='unique_submission'),
    )