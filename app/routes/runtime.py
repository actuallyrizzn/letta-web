"""
Letta Chatbot - Runtime Configuration Routes
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

from flask import Blueprint, jsonify, current_app

runtime_bp = Blueprint('runtime', __name__)

@runtime_bp.route('/runtime', methods=['GET'])
def get_runtime_info():
    """Get runtime configuration information"""
    return jsonify({
        'LETTA_BASE_URL': current_app.config['LETTA_BASE_URL']
    })
