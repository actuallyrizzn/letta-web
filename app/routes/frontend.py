"""
Letta Chatbot - Frontend Routes
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
        
        # Validate that the agent exists (no access control - Letta handles it)
        agent = client.get_agent(agent_id)
        
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
        
        # Get all agents (no filtering - Letta handles access control)
        all_agents = client.list_agents()
        
        # Sort by updatedAt date (newest first)
        sorted_agents = sorted(all_agents, key=lambda x: x.get('updated_at', 0), reverse=True)
        
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
        
        # Get agent (no access control - Letta handles it)
        agent = client.get_agent(agent_id)
        
        return render_template('components/agent_details.html', agent=agent)
    except Exception as e:
        current_app.logger.error(f'Error fetching agent details: {e}')
        return render_template('components/agent_details.html', error=str(e))
