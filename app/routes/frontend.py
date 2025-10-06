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
    user_id = get_user_id()
    if not user_id:
        return render_template('errors/404.html'), 404
    
    try:
        from app.utils.letta_client import LettaClient
        client = LettaClient()
        
        # Validate that the agent exists and user has access
        agent = client.get_agent(agent_id)
        user_tags = [f'user:{user_id}'] if current_app.config['USE_COOKIE_BASED_AUTHENTICATION'] else []
        
        # Check if user owns the agent (either has user tag OR has no tags for backward compatibility)
        user_tag = f'user:{user_id}'
        agent_tags = agent.get('tags', [])
        if user_tags and user_tag not in agent_tags and len(agent_tags) > 0:
            return render_template('errors/404.html'), 404
        
        return render_template('index.html', agent_id=agent_id, agent_name=agent.get('name', 'Unnamed Agent'), agent_status='Active')
    except Exception as e:
        current_app.logger.error(f'Error validating agent {agent_id}: {e}')
        return render_template('errors/404.html'), 404

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
        
        # Get agents with user tags
        tagged_agents = client.list_agents(tags=user_tags, match_all_tags=True)
        
        # Get all agents (for backward compatibility with untagged agents)
        all_agents = client.list_agents()
        
        # Filter to include only agents that either:
        # 1. Have the user's tag, OR
        # 2. Have no tags (backward compatibility)
        user_tag = f'user:{user_id}'
        filtered_agents = []
        for agent in all_agents:
            agent_tags = agent.get('tags', [])
            if user_tag in agent_tags or len(agent_tags) == 0:
                filtered_agents.append(agent)
        
        # Sort by updatedAt date (newest first)
        sorted_agents = sorted(filtered_agents, key=lambda x: x.get('updated_at', 0), reverse=True)
        
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
        
        # Check if user owns the agent (either has user tag OR has no tags for backward compatibility)
        user_tag = f'user:{user_id}'
        agent_tags = agent.get('tags', [])
        if user_tags and user_tag not in agent_tags and len(agent_tags) > 0:
            return render_template('components/agent_details.html', error='Agent not found')
        
        return render_template('components/agent_details.html', agent=agent)
    except Exception as e:
        current_app.logger.error(f'Error fetching agent details: {e}')
        return render_template('components/agent_details.html', error=str(e))
