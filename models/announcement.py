from extensions import db

class Announcement(db.Model):
    __tablename__ = 'announcements'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Foreign keys
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    
    # Relationship
    poster_user = db.relationship('User', backref='announcements')
    
    @staticmethod
    def get_by_course(course_id):
        """Get announcements for a course"""
        return Announcement.query.filter_by(course_id=course_id).order_by(
            Announcement.created_at.desc()
        ).all()