"""
Letta Chatbot - Message Validators
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

import json

MESSAGE_TYPE = {
    'USER_MESSAGE': 'user_message',
    'ASSISTANT_MESSAGE': 'assistant_message', 
    'SYSTEM_MESSAGE': 'system_message',
    'TOOL_MESSAGE': 'tool_message',
    'REASONING_MESSAGE': 'reasoning_message'
}

def filter_messages(messages):
    """Filter messages to remove system messages and heartbeat messages"""
    MESSAGE_TYPES_TO_HIDE = [MESSAGE_TYPE['SYSTEM_MESSAGE']]
    
    filtered = []
    for message in messages:
        try:
            # Use 'message_type' (underscore) not 'messageType' (camelCase)
            msg_type = message.get('message_type', '')
            
            # Check for heartbeat messages
            if (msg_type == MESSAGE_TYPE['USER_MESSAGE'] and 
                isinstance(message.get('content'), str)):
                try:
                    parsed = json.loads(message['content'])
                    if parsed.get('type') == 'heartbeat':
                        continue  # Skip heartbeat messages
                except json.JSONDecodeError:
                    pass  # Not JSON, continue processing
            
            # Check for hidden message types
            if msg_type in MESSAGE_TYPES_TO_HIDE:
                continue
            
            filtered.append(message)
            
        except Exception:
            # If there's an error parsing, skip the message
            continue
    
    # Sort by date
    return sorted(filtered, key=lambda x: x.get('date', 0))

def convert_to_ai_sdk_message(messages):
    """Convert Letta messages to AI SDK format with proper message type detection and timestamp grouping"""
    converted = []
    i = 0
    
    while i < len(messages):
        message = messages[i]
        content = message.get('content', '')
        reasoning = message.get('reasoning', '')
        message_type = message.get('message_type', '')  # Use underscore not camelCase
        
        # Skip standalone timestamps (they should be attached to previous messages)
        if isinstance(content, str) and content.count(':') == 1 and len(content) < 10 and content.replace(':', '').replace('.', '').isdigit():
            # This is a timestamp, skip it
            i += 1
            continue
        
        # Skip very long system messages (likely system prompts/instructions)
        if len(content) > 5000 and ('You are' in content or 'Personality version' in content or 'memory_metadata' in content):
            i += 1
            continue
        
        # Determine role and type based on content and message_type
        role = 'assistant'  # default
        
        # Check message_type first
        if message_type == MESSAGE_TYPE['USER_MESSAGE']:
            role = 'user'
        elif message_type == MESSAGE_TYPE['ASSISTANT_MESSAGE']:
            role = 'assistant'
        elif message_type == MESSAGE_TYPE['SYSTEM_MESSAGE']:
            role = 'system'
        elif message_type == MESSAGE_TYPE['TOOL_MESSAGE']:
            role = 'tool_call'
        elif message_type == MESSAGE_TYPE['REASONING_MESSAGE']:
            role = 'reasoning'
        # Fallback checks if message_type is not set
        elif isinstance(content, str) and '[Username:' in content:
            role = 'user'
        elif isinstance(content, str) and content.startswith('{') and '}' in content:
            try:
                import json
                parsed = json.loads(content)
                if parsed.get('type') == 'heartbeat':
                    role = 'system'
                elif parsed.get('type') == 'system_alert':
                    role = 'system'
                elif parsed.get('type') == 'tool_call':
                    role = 'tool_call'
                else:
                    role = 'system'
            except json.JSONDecodeError:
                role = 'system'
        
        # Skip heartbeat and system messages that should be hidden
        if role == 'system' and isinstance(content, str):
            if 'heartbeat' in content.lower() or 'hidden from the user' in content.lower():
                i += 1
                continue
        
        # Look for timestamp in next message
        timestamp = message.get('date')
        if i + 1 < len(messages):
            next_message = messages[i + 1]
            next_content = next_message.get('content', '')
            if isinstance(next_content, str) and next_content.count(':') == 1 and len(next_content) < 10 and next_content.replace(':', '').replace('.', '').isdigit():
                # Next message is a timestamp, use it
                timestamp = next_content
                i += 1  # Skip the timestamp message
        
        converted.append({
            'id': message.get('id') or f'msg_{i}_{role}',
            'role': role,
            'content': content,
            'createdAt': timestamp
        })
        i += 1
    
    return converted
