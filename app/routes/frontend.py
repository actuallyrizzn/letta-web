from flask import Blueprint, render_template, request, jsonify, current_app
from app.utils.session_manager import get_user_id

frontend_bp = Blueprint('frontend', __name__)

@frontend_bp.route('/')
def index():
    """Main chat page"""
    return render_template('index.html', agent_id='')

@frontend_bp.route('/<agent_id>')
def chat_with_agent(agent_id):
    """Chat page with specific agent"""
    return render_template('index.html', agent_id=agent_id)

@frontend_bp.route('/api/agents-list')
def agents_list():
    """Get agents list for HTMX"""
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    try:
        from app.utils.letta_client import LettaClient
        client = LettaClient()
        user_tags = [f'user:{user_id}'] if current_app.config['USE_COOKIE_BASED_AUTHENTICATION'] else []
        
        agents = client.list_agents(tags=user_tags, match_all_tags=True)
        
        # Sort by updatedAt date (newest first)
        sorted_agents = sorted(agents, key=lambda x: x.get('updatedAt', 0), reverse=True)
        
        # Render agents list template
        return render_template('components/agents_list.html', agents=sorted_agents)
    except Exception as e:
        current_app.logger.error(f'Error fetching agents: {e}')
        return render_template('components/agents_list.html', agents=[], error=str(e))

@frontend_bp.route('/api/agent-details/<agent_id>')
def agent_details(agent_id):
    """Get agent details for HTMX"""
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    try:
        from app.utils.letta_client import LettaClient
        client = LettaClient()
        
        # Validate ownership
        agent = client.get_agent(agent_id)
        user_tags = [f'user:{user_id}'] if current_app.config['USE_COOKIE_BASED_AUTHENTICATION'] else []
        
        if user_tags and not any(tag in agent.get('tags', []) for tag in user_tags):
            return render_template('components/agent_details.html', error='Agent not found')
        
        return render_template('components/agent_details.html', agent=agent)
    except Exception as e:
        current_app.logger.error(f'Error fetching agent details: {e}')
        return render_template('components/agent_details.html', error=str(e))
