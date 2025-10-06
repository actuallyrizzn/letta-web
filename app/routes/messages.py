from flask import Blueprint, request, jsonify, Response, current_app, render_template
from app.utils.letta_client import LettaClient
from app.utils.session_manager import get_user_id, get_user_tag_id
from app.utils.validators import filter_messages, convert_to_ai_sdk_message
from app.utils.error_handler import handle_api_error, handle_htmx_error
from app.utils.performance import rate_limit, message_rate_limiter
from app.utils.forms import validate_message_data
import json

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/agents/<agent_id>/messages', methods=['GET'])
@handle_api_error
def get_agent_messages(agent_id):
    """Get messages for an agent"""
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    try:
        client = LettaClient()
        
        # Validate ownership first
        agent = client.get_agent(agent_id)
        user_tags = get_user_tag_id(user_id)
        
        # Check if user owns the agent (either has user tag OR has no tags for backward compatibility)
        user_tag = f'user:{user_id}'
        agent_tags = agent.get('tags', [])
        if user_tags and user_tag not in agent_tags and len(agent_tags) > 0:
            return jsonify({'error': 'Agent not found'}), 404
        
        # Get messages
        messages = client.list_messages(agent_id, limit=100)
        
        # Filter messages
        filtered_messages = filter_messages(messages)
        
        # Convert to AI SDK format
        converted_messages = convert_to_ai_sdk_message(filtered_messages)
        
        # Check if this is an HTMX request
        if request.headers.get('HX-Request'):
            return render_template('components/messages_list.html', messages=converted_messages)
        else:
            return jsonify(converted_messages)
    except Exception as e:
        current_app.logger.error(f'Error fetching messages: {e}')
        if request.headers.get('HX-Request'):
            return render_template('components/messages_list.html', messages=[], error=str(e))
        else:
            return jsonify({'error': 'Error fetching messages'}), 500

@messages_bp.route('/agents/<agent_id>/messages', methods=['POST'])
@handle_api_error
@rate_limit(message_rate_limiter)
def send_message(agent_id):
    """Send message to agent"""
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    try:
        # Validate request data
        data = request.get_json()
        validation_errors = validate_message_data(data)
        if validation_errors:
            return jsonify({'error': 'Validation failed', 'details': validation_errors}), 400
        
        client = LettaClient()
        
        # Validate ownership first
        agent = client.get_agent(agent_id)
        user_tags = get_user_tag_id(user_id)
        
        # Check if user owns the agent (either has user tag OR has no tags for backward compatibility)
        user_tag = f'user:{user_id}'
        agent_tags = agent.get('tags', [])
        if user_tags and user_tag not in agent_tags and len(agent_tags) > 0:
            return jsonify({'error': 'Agent not found'}), 404
        
        # Get messages from request
        messages = data.get('messages', [])
        
        # Send message to Letta
        response = client.send_message(agent_id, messages)
        
        return jsonify(response)
    except Exception as e:
        current_app.logger.error(f'Error sending message: {e}')
        return jsonify({'error': 'Error sending message'}), 500

@messages_bp.route('/agents/<agent_id>/archival_memory', methods=['GET'])
def get_agent_archival_memory(agent_id):
    """Get agent's archival memory"""
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    try:
        client = LettaClient()
        
        # Validate ownership first
        agent = client.get_agent(agent_id)
        user_tags = get_user_tag_id(user_id)
        
        # Check if user owns the agent (either has user tag OR has no tags for backward compatibility)
        user_tag = f'user:{user_id}'
        agent_tags = agent.get('tags', [])
        if user_tags and user_tag not in agent_tags and len(agent_tags) > 0:
            return jsonify({'error': 'Agent not found'}), 404
        
        # Get archival memory
        try:
            memory = client.get_archival_memory(agent_id)
            # Check if this is an HTMX request
            if request.headers.get('HX-Request'):
                return render_template('components/archival_memory.html', memory=memory)
            else:
                return jsonify(memory)
        except Exception as memory_error:
            # If archival memory doesn't exist, return empty result
            current_app.logger.info(f'No archival memory found for agent {agent_id}: {memory_error}')
            if request.headers.get('HX-Request'):
                return render_template('components/archival_memory.html', memory={'archival_memory': []})
            else:
                return jsonify({'archival_memory': []})
    except Exception as e:
        current_app.logger.error(f'Error fetching archival memory: {e}')
        return jsonify({'error': 'Error fetching archival memory'}), 500
