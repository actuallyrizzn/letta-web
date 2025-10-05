import uuid
from flask import session, request, current_app
from datetime import datetime, timedelta

LETTA_UID = 'letta_uid'
SESSION_TIMEOUT = 24 * 60 * 60  # 24 hours in seconds

def get_user_id():
    """Get user ID from session or create new one"""
    if not current_app.config['USE_COOKIE_BASED_AUTHENTICATION']:
        return 'default'
    
    user_id = session.get(LETTA_UID)
    if not user_id:
        user_id = str(uuid.uuid4())
        session[LETTA_UID] = user_id
        session['created_at'] = datetime.utcnow().isoformat()
        session.permanent = True
    
    # Check session timeout
    if is_session_expired():
        # Regenerate session ID for security
        session.clear()
        user_id = str(uuid.uuid4())
        session[LETTA_UID] = user_id
        session['created_at'] = datetime.utcnow().isoformat()
        session.permanent = True
    
    return user_id

def is_session_expired():
    """Check if session has expired"""
    if not current_app.config['USE_COOKIE_BASED_AUTHENTICATION']:
        return False
    
    created_at = session.get('created_at')
    if not created_at:
        return True
    
    try:
        created_time = datetime.fromisoformat(created_at)
        return datetime.utcnow() - created_time > timedelta(seconds=SESSION_TIMEOUT)
    except (ValueError, TypeError):
        return True

def get_user_tag_id(user_id):
    """Get user tag for Letta API"""
    if not current_app.config['USE_COOKIE_BASED_AUTHENTICATION']:
        return []
    
    return [f'user:{user_id}']

def validate_agent_owner(agent_id, user_id):
    """Validate that user owns the agent"""
    if not current_app.config['USE_COOKIE_BASED_AUTHENTICATION']:
        return True
    
    from app.utils.letta_client import LettaClient
    client = LettaClient()
    
    try:
        agent = client.get_agent(agent_id)
        user_tag = f'user:{user_id}'
        return user_tag in agent.get('tags', [])
    except Exception:
        return False

def get_session_info():
    """Get current session information"""
    if not current_app.config['USE_COOKIE_BASED_AUTHENTICATION']:
        return {
            'user_id': 'default',
            'is_authenticated': True,
            'session_age': 0
        }
    
    user_id = session.get(LETTA_UID)
    created_at = session.get('created_at')
    
    session_age = 0
    if created_at:
        try:
            created_time = datetime.fromisoformat(created_at)
            session_age = (datetime.utcnow() - created_time).total_seconds()
        except (ValueError, TypeError):
            pass
    
    return {
        'user_id': user_id,
        'is_authenticated': bool(user_id),
        'session_age': session_age,
        'expires_in': SESSION_TIMEOUT - session_age if session_age < SESSION_TIMEOUT else 0
    }

def clear_session():
    """Clear current session"""
    session.clear()
