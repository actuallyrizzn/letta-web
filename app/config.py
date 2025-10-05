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

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
