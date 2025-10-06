"""
Letta Chatbot - Flask Application Factory
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

from flask import Flask
from app.config import config
from datetime import datetime
import markdown

def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config[config_name])
    
    # Add custom Jinja2 filters
    @app.template_filter('datetime')
    def datetime_filter(timestamp):
        if isinstance(timestamp, (int, float)):
            return datetime.fromtimestamp(timestamp / 1000).strftime('%H:%M')
        elif isinstance(timestamp, str):
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                return dt.strftime('%H:%M')
            except:
                return timestamp
        return timestamp
    
    @app.template_filter('markdown')
    def markdown_filter(text):
        """Convert markdown text to HTML"""
        if not text:
            return ''
        # Configure markdown with extensions for better formatting
        md = markdown.Markdown(extensions=['fenced_code', 'tables', 'nl2br'])
        return md.convert(text)
    
    # Register blueprints
    from app.routes.agents import agents_bp
    from app.routes.messages import messages_bp
    from app.routes.runtime import runtime_bp
    from app.routes.frontend import frontend_bp
    from app.utils.error_handler import error_bp
    
    app.register_blueprint(agents_bp, url_prefix='/api')
    app.register_blueprint(messages_bp, url_prefix='/api')
    app.register_blueprint(runtime_bp, url_prefix='/api')
    app.register_blueprint(frontend_bp)
    app.register_blueprint(error_bp)
    
    return app
