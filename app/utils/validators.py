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
    """Convert Letta messages to AI SDK format"""
    converted = []
    for message in messages:
        converted.append({
            'id': message.get('id'),
            'role': 'user' if message.get('messageType') == MESSAGE_TYPE['USER_MESSAGE'] else 'assistant',
            'content': message.get('content', ''),
            'createdAt': message.get('date')
        })
    return converted
