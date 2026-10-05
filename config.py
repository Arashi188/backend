import os
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database configuration with proper URL handling
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///ecommerce.db')
    
    # Handle Render's PostgreSQL URLs (they use postgres:// not postgresql://)
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
    
    # Admin configuration
    ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN', 'admin-secret-token-change-this-in-production')
    
    # WhatsApp configuration
    WHATSAPP_NUMBER = os.environ.get('WHATSAPP_NUMBER', '2347088028747')

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'