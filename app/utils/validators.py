import json

MESSAGE_TYPE = {
    'USER_MESSAGE': 'user_message',
    'ASSISTANT_MESSAGE': 'assistant_message', 
    'SYSTEM_MESSAGE': 'system_message',
    'TOOL_MESSAGE': 'tool_message'
}

def filter_messages(messages):
    """Filter messages to remove system messages and heartbeat messages"""
    MESSAGE_TYPES_TO_HIDE = [MESSAGE_TYPE['SYSTEM_MESSAGE']]
    
    filtered = []
    for message in messages:
        try:
            # Check for heartbeat messages
            if (message.get('messageType') == MESSAGE_TYPE['USER_MESSAGE'] and 
                isinstance(message.get('content'), str)):
                try:
                    parsed = json.loads(message['content'])
                    if parsed.get('type') == 'heartbeat':
                        continue  # Skip heartbeat messages
                except json.JSONDecodeError:
                    pass  # Not JSON, continue processing
            
            # Check for hidden message types
            if message.get('messageType') in MESSAGE_TYPES_TO_HIDE:
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
        message_type = message.get('messageType', '')
        
        # Skip standalone timestamps (they should be attached to previous messages)
        if isinstance(content, str) and content.count(':') == 1 and len(content) < 10 and content.replace(':', '').replace('.', '').isdigit():
            # This is a timestamp, skip it
            i += 1
            continue
        
        # Determine role and type based on content and messageType
        role = 'assistant'  # default
        
        # Check messageType first
        if message_type == MESSAGE_TYPE['USER_MESSAGE']:
            role = 'user'
        # Check if content contains username pattern (user messages)
        elif isinstance(content, str) and '[Username:' in content:
            role = 'user'
        # Check for system messages
        elif message_type == MESSAGE_TYPE['SYSTEM_MESSAGE']:
            role = 'system'
        # Check for tool messages
        elif message_type == MESSAGE_TYPE['TOOL_MESSAGE']:
            role = 'tool_call'
        # Check for JSON content that might be system messages
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
        # Check for reasoning/thinking content
        elif isinstance(content, str) and any(keyword in content.lower() for keyword in ['reasoning', 'thinking', 'analysis', 'considering']):
            role = 'reasoning'
        
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
