#!/usr/bin/env python3
"""
Production WSGI entry point for Letta Chatbot Flask application
"""

import os
import sys
from app import create_app

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create Flask application
app = create_app(os.environ.get('FLASK_ENV', 'production'))

if __name__ == '__main__':
    # This is only used for development
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
