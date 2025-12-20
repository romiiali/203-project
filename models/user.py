from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    
    # Role-specific fields (nullable)
    major = db.Column(db.String(100))
    level = db.Column(db.String(50))
    office = db.Column(db.String(100))
    office_hours = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationships
    courses_instructing = db.relationship('Course', backref='instructor', foreign_keys='Course.instructor_id')
    courses_ta = db.relationship('Course', backref='ta', foreign_keys='Course.ta_id')
    submissions = db.relationship('Submission', backref='student', lazy=True)
    announcements_posted = db.relationship('Announcement', backref='poster', lazy=True)
    enrolled_courses = db.relationship('Enrollment', backref='enrolled_student', lazy=True)
    
    # Single-table inheritance discriminator
    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': role
    }
    
    # In User.__init__ method:
    def __init__(self, name, email, role, password=None, **kwargs):
        self.name = name
        self.email = email
        self.role = role
        
        # ALWAYS set a password
        if password:
            self.set_password(password)
        else:
            # Set a default password if none provided
            self.set_password("default123")
        
        # Set role-specific fields
        if role == 'student':
            self.major = kwargs.get('major')
            self.level = kwargs.get('level')
        elif role in ['instructor', 'ta']:
            self.office = kwargs.get('office')
            self.office_hours = kwargs.get('office_hours')
        
    def set_password(self, password):
        """Hash the password before storing"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    # --- Authentication Methods (from old user.py) ---
    @staticmethod
    def login(email, password):
        if not email or not password:
            return None
        
        user = User.query.filter_by(email=email).first()
        if user and user.password_hash and user.check_password(password):
            return user
        return None

# Also fix the check_password method:
    def check_password(self, password):
        """Check if password matches hash with validation"""
        if not self.password_hash:
            return False
        
        try:
            return check_password_hash(self.password_hash, password)
        except Exception:
            # Handle invalid hash format
            return False
    

    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        return User.query.get(user_id)
    
    # --- People Model Replacement Methods ---
    def get_person(self, person_id):
        """Alias for get_by_id for compatibility"""
        return self.get_by_id(person_id)
    
    @staticmethod
    def get_all():
        """Get all users (replaces People.get_all_people())"""
        return User.query.all()
    
    @staticmethod
    def search_users_by_role(role):
        """Get users by role"""
        return User.query.filter_by(role=role).all()
    
    def get_person_by_role(self, role):
        """Get users by role (instance method version)"""
        return User.query.filter_by(role=role).all()
    
    @staticmethod
    def search_users(search_term=""):
        """Search users by name, email, or role (replaces both User.search_users() and People.search_people())"""
        if not search_term:
            return User.query.all()
        
        search = f"%{search_term}%"
        return User.query.filter(
            (User.name.ilike(search)) | 
            (User.email.ilike(search)) | 
            (User.role.ilike(search))
        ).all()
    
    # --- CRUD Operations (from People model) ---
    @staticmethod
    def add_person(name, email, role, password="default123"):
        """Add a new person/user"""
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return None
        
        new_user = User(name=name, email=email, role=role.lower())
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return new_user
    
    @staticmethod
    def edit_person(user_id, name=None, email=None, role=None, password=None):
        """Edit an existing person/user"""
        user = User.query.get(user_id)
        if not user:
            return None
        
        if name:
            user.name = name
        if email:
            # Check if email is taken by another user
            existing_user = User.query.filter(
                User.email == email,
                User.id != user_id
            ).first()
            if existing_user:
                return None
            user.email = email
        if role:
            user.role = role.lower()
        if password:
            user.set_password(password)
        
        db.session.commit()
        return user
    
    @staticmethod
    def delete_person(user_id):
        """Delete a person/user"""
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False
    
    def to_dict(self):
        base_dict = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role.capitalize(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        # Add role-specific fields
        if self.role == 'student':
            base_dict.update({
                'major': self.major,
                'level': self.level
            })
        elif self.role in ['instructor', 'ta']:
            base_dict.update({
                'office': self.office,
                'office_hours': self.office_hours
            })
        
        return base_dict
    
    def __repr__(self):
        return f'<User {self.name} ({self.role})>'