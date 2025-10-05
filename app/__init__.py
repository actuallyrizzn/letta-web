from flask import Flask
from flask_session import Session
from app.config import config

def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize Flask-Session
    Session(app)
    
    # Register blueprints
    from app.routes.agents import agents_bp
    from app.routes.messages import messages_bp
    from app.routes.runtime import runtime_bp
    
    app.register_blueprint(agents_bp, url_prefix='/api')
    app.register_blueprint(messages_bp, url_prefix='/api')
    app.register_blueprint(runtime_bp, url_prefix='/api')
    
    return app
