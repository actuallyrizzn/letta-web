from flask import Flask
from flask_session import Session
from app.config import config
from datetime import datetime

def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config[config_name])
    
    # Initialize Flask-Session
    Session(app)
    
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
