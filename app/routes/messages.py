from flask import Blueprint, request, jsonify, Response, current_app, render_template
from app.utils.letta_client import LettaClient
from app.utils.session_manager import get_user_id, get_user_tag_id
from app.utils.validators import filter_messages, convert_to_ai_sdk_message
import json

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/agents/<agent_id>/messages', methods=['GET'])
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
        if user_tags and not any(tag in agent.get('tags', []) for tag in user_tags):
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
def send_message(agent_id):
    """Send message to agent"""
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
        
        # Get messages from request
        data = request.get_json()
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
        if user_tags and not any(tag in agent.get('tags', []) for tag in user_tags):
            return jsonify({'error': 'Agent not found'}), 404
        
        # Get archival memory
        memory = client.get_archival_memory(agent_id)
        
        return jsonify(memory)
    except Exception as e:
        current_app.logger.error(f'Error fetching archival memory: {e}')
        return jsonify({'error': 'Error fetching archival memory'}), 500
