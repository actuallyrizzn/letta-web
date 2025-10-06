#!/usr/bin/env python3
"""
Letta Chatbot - WSGI Entry Point
Copyright (C) 2025 Mark Hopkins

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
import sys
from app import create_app

# Add the project root to Python path (helpful for some deployment scenarios)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Get environment from FLASK_ENV variable (defaults to production for safety)
flask_env = os.environ.get('FLASK_ENV', 'production')

# Create Flask application with the specified environment
app = create_app(flask_env)

if __name__ == '__main__':
    # This is only used when running directly (not via gunicorn/uwsgi)
    # For development: FLASK_ENV=development python wsgi.py
    # For production: gunicorn wsgi:app
    
    is_development = flask_env == 'development'
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Starting Flask app in {flask_env} mode on port {port}")
    print(f"Debug mode: {is_development}")
    
    app.run(
        debug=is_development,
        host='0.0.0.0',
        port=port
    )
