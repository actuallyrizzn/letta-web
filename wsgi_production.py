#!/usr/bin/env python3
"""
Letta Chatbot - Production WSGI Entry Point
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
import sys
from app import create_app

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create Flask application
app = create_app(os.environ.get('FLASK_ENV', 'production'))

if __name__ == '__main__':
    # This is only used for development
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
