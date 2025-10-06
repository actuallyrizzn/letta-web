"""
Letta Chatbot - Configuration Module
Copyright (C) 2025 Letta Chatbot Contributors

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

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
