import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Secret key for Flask sessions
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-this'
    
    # Windows Authentication Connection String
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mssql+pyodbc://@localhost/CourseManagement?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Optimized for SQL Server with Windows Authentication
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 299,
        'pool_pre_ping': True,
        'connect_args': {
            'timeout': 30,  # Connection timeout in seconds
            'autocommit': True,
        }
    }
    
    # Session configuration
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes