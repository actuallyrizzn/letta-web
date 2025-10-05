import uuid
from flask import session, request, current_app

LETTA_UID = 'letta_uid'

def get_user_id():
    """Get user ID from session or create new one"""
    if not current_app.config['USE_COOKIE_BASED_AUTHENTICATION']:
        return 'default'
    
    user_id = session.get(LETTA_UID)
    if not user_id:
        user_id = str(uuid.uuid4())
        session[LETTA_UID] = user_id
    
    return user_id

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
