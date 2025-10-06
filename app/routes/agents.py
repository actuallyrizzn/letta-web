"""
Letta Chatbot - Agent Management Routes
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

from flask import Blueprint, request, jsonify, current_app, render_template
from app.utils.letta_client import LettaClient
from app.utils.session_manager import get_user_id, get_user_tag_id
from app.utils.error_handler import handle_api_error, handle_htmx_error, validate_request_data
from app.utils.performance import cache_result, rate_limit, api_rate_limiter
from app.utils.forms import validate_agent_data
import json

agents_bp = Blueprint('agents', __name__)

@agents_bp.route('/agents', methods=['GET'])
@handle_api_error
@rate_limit(api_rate_limiter)
@cache_result(ttl=60, key_prefix='agents_list')  # Cache for 1 minute
def get_agents():
    """Get list of agents for the current user"""
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    try:
        client = LettaClient()
        
        # Get all agents (no filtering - Letta handles access control)
        all_agents = client.list_agents()
        
        # Sort by updatedAt date (newest first)
        sorted_agents = sorted(all_agents, key=lambda x: x.get('updated_at', 0), reverse=True)
        
        # Debug logging
        current_app.logger.info(f'Found {len(all_agents)} total agents')
        
        # Check if this is an HTMX request
        if request.headers.get('HX-Request'):
            return render_template('components/agents_list.html', agents=sorted_agents)
        else:
            return jsonify(sorted_agents)
    except Exception as e:
        current_app.logger.error(f'Error fetching agents: {e}')
        if request.headers.get('HX-Request'):
            return render_template('components/agents_list.html', agents=[], error=str(e))
        else:
            return jsonify({'error': 'Error fetching agents'}), 500

@agents_bp.route('/agents', methods=['POST'])
def create_agent():
    """Create a new agent"""
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    try:
        # Load default agent configuration
        with open('default-agent.json', 'r') as f:
            default_agent = json.load(f)
        
        DEFAULT_MEMORY_BLOCKS = default_agent['DEFAULT_MEMORY_BLOCKS']
        DEFAULT_LLM = default_agent['DEFAULT_LLM']
        DEFAULT_EMBEDDING = default_agent['DEFAULT_EMBEDDING']
        
        client = LettaClient()
        user_tags = get_user_tag_id(user_id)
        
        new_agent = client.create_agent(
            memory_blocks=DEFAULT_MEMORY_BLOCKS,
            model=DEFAULT_LLM,
            embedding=DEFAULT_EMBEDDING,
            tags=user_tags
        )
        
        # Check if this is an HTMX request
        if request.headers.get('HX-Request'):
            # Return the updated agents list HTML
            return render_template('components/agents_list.html', agents=[new_agent])
        else:
            return jsonify(new_agent)
    except Exception as e:
        current_app.logger.error(f'Error creating agent: {e}')
        return jsonify({'error': 'Error creating agent'}), 500

@agents_bp.route('/agents/<agent_id>', methods=['GET'])
def get_agent(agent_id):
    """Get agent by ID"""
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    try:
        client = LettaClient()
        agent = client.get_agent(agent_id)
        
        # Validate ownership
        user_tags = get_user_tag_id(user_id)
        if user_tags and not any(tag in agent.get('tags', []) for tag in user_tags):
            return jsonify({'error': 'Agent not found'}), 404
        
        return jsonify(agent)
    except Exception as e:
        current_app.logger.error(f'Error fetching agent: {e}')
        return jsonify({'error': 'Agent not found'}), 404

@agents_bp.route('/agents/<agent_id>', methods=['PUT'])
def update_agent(agent_id):
    """Update agent"""
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    try:
        client = LettaClient()
        
        # Validate ownership first
        agent = client.get_agent(agent_id)
        user_tags = get_user_tag_id(user_id)
        if user_tags and not any(tag in agent.get('tags', []) for tag in user_tags):
            return jsonify({'error': 'Agent not found'}), 404
        
        # Update agent
        update_data = request.get_json()
        updated_agent = client.update_agent(agent_id, **update_data)
        
        return jsonify(updated_agent)
    except Exception as e:
        current_app.logger.error(f'Error updating agent: {e}')
        return jsonify({'error': 'Error updating agent'}), 500

@agents_bp.route('/agents/<agent_id>', methods=['DELETE'])
def delete_agent(agent_id):
    """Delete agent"""
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    try:
        client = LettaClient()
        
        # Validate ownership first
        agent = client.get_agent(agent_id)
        user_tags = get_user_tag_id(user_id)
        if user_tags and not any(tag in agent.get('tags', []) for tag in user_tags):
            return jsonify({'error': 'Agent not found'}), 404
        
        # Delete agent
        client.delete_agent(agent_id)
        
        return jsonify({'message': 'Agent deleted successfully'})
    except Exception as e:
        current_app.logger.error(f'Error deleting agent: {e}')
        return jsonify({'error': 'Error deleting agent'}), 500
