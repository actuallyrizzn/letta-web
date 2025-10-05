import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'dev-secret-key-change-in-production'
    LETTA_API_KEY = os.environ.get('LETTA_API_KEY') or 'DEFAULT_TOKEN'
    LETTA_BASE_URL = os.environ.get('LETTA_BASE_URL') or 'http://localhost:8283'
    USE_COOKIE_BASED_AUTHENTICATION = os.environ.get('USE_COOKIE_BASED_AUTHENTICATION', 'true').lower() == 'true'
    CREATE_AGENTS_FROM_UI = os.environ.get('NEXT_PUBLIC_CREATE_AGENTS_FROM_UI', 'true').lower() == 'true'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = False
    FLASK_ENV = 'testing'
    WTF_CSRF_ENABLED = False
    LETTA_API_KEY = 'test-api-key'
    LETTA_BASE_URL = 'http://test-letta-server:8283'
    USE_COOKIE_BASED_AUTHENTICATION = True
    
    # Session configuration for testing
    SESSION_TYPE = 'null'  # Use null session for testing
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
