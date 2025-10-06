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
        
        # Get messages (no access control - Letta handles it)
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
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            message_content = data.get('messages', [])
            
            # Validate JSON messages
            if not message_content:
                return jsonify({'error': 'Messages field is required'}), 400
            if not isinstance(message_content, list):
                return jsonify({'error': 'Messages must be an array'}), 400
            if len(message_content) == 0:
                return jsonify({'error': 'Messages cannot be empty'}), 400
            
            # Validate message content
            for msg in message_content:
                if not isinstance(msg, dict):
                    return jsonify({'error': 'Each message must be an object'}), 400
                if 'role' not in msg or 'content' not in msg:
                    return jsonify({'error': 'Each message must have role and content'}), 400
                if msg['role'] not in ['user', 'assistant', 'system']:
                    return jsonify({'error': 'Invalid message role'}), 400
                if not isinstance(msg['content'], str):
                    return jsonify({'error': 'Message content must be a string'}), 400
                if len(msg['content']) > 4000:
                    return jsonify({'error': 'Message content too long (max 4000 characters)'}), 400
        else:
            # HTMX form submission
            message_content = request.form.get('message', '')
            if not message_content:
                return jsonify({'error': 'Message is required'}), 400
            # Convert to messages array format
            message_content = [{'role': 'user', 'content': message_content}]
        
        client = LettaClient()
        
        # Send message to Letta (no access control - Letta handles it)
        response = client.send_message(agent_id, message_content)
        
        # Fetch updated messages after sending
        updated_messages = client.list_messages(agent_id, limit=100)
        filtered_updated_messages = filter_messages(updated_messages)
        converted_updated_messages = convert_to_ai_sdk_message(filtered_updated_messages)
        
        # Return the updated messages list for HTMX swap
        if request.headers.get('HX-Request'):
            return render_template('components/messages_list.html', messages=converted_updated_messages)
        else:
            return jsonify(response)
    except Exception as e:
        current_app.logger.error(f'Error sending message: {e}')
        if request.headers.get('HX-Request'):
            return render_template('components/messages_list.html', messages=[], error=str(e))
        else:
            return jsonify({'error': 'Error sending message'}), 500

@messages_bp.route('/agents/<agent_id>/archival_memory', methods=['GET'])
def get_agent_archival_memory(agent_id):
    """Get agent's archival memory"""
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    try:
        client = LettaClient()
        
        # Get archival memory (passages) - no access control, Letta handles it
        try:
            memory = client.get_archival_memory(agent_id, limit=10)
            # Check if this is an HTMX request
            if request.headers.get('HX-Request'):
                return render_template('components/archival_memory.html', memory=memory)
            else:
                return jsonify(memory)
        except Exception as memory_error:
            # If archival memory doesn't exist, return empty result
            current_app.logger.info(f'No archival memory found for agent {agent_id}: {memory_error}')
            if request.headers.get('HX-Request'):
                return render_template('components/archival_memory.html', memory=[])
            else:
                return jsonify([])
    except Exception as e:
        current_app.logger.error(f'Error fetching archival memory: {e}')
        return jsonify({'error': 'Error fetching archival memory'}), 500
