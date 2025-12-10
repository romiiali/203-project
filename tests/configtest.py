import pytest
from app import create_app
from extensions import db

@pytest.fixture
def app():
    """Create and configure a Flask app for testing models"""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-secret-key'
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def session_db(app):
    """Database session for model tests"""
    with app.app_context():
        yield db.session