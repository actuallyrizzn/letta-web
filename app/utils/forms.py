"""
Letta Chatbot - Form Validation Classes
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

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FieldList, FormField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from wtforms.widgets import TextArea

class MemoryBlockForm(FlaskForm):
    """Form for individual memory block"""
    label = StringField('Label', validators=[DataRequired(), Length(max=50)])
    value = TextAreaField('Value', validators=[DataRequired(), Length(max=1000)], widget=TextArea())

class AgentForm(FlaskForm):
    """Form for creating/editing agents"""
    name = StringField('Agent Name', validators=[Optional(), Length(max=100)])
    model = SelectField('Model', 
                       choices=[
                           ('letta/letta-free', 'Letta Free'),
                           ('letta/letta-pro', 'Letta Pro'),
                           ('openai/gpt-4', 'GPT-4'),
                           ('openai/gpt-3.5-turbo', 'GPT-3.5 Turbo'),
                           ('anthropic/claude-3-sonnet', 'Claude 3 Sonnet'),
                           ('anthropic/claude-3-haiku', 'Claude 3 Haiku')
                       ],
                       validators=[DataRequired()])
    memory_blocks = FieldList(FormField(MemoryBlockForm), min_entries=1)
    submit = SubmitField('Save Agent')

class MessageForm(FlaskForm):
    """Form for sending messages"""
    message = TextAreaField('Message', 
                          validators=[DataRequired(), Length(min=1, max=4000)],
                          widget=TextArea(),
                          render_kw={'rows': 3, 'placeholder': 'Type your message...'})
    submit = SubmitField('Send')

def validate_agent_data(data):
    """Validate agent data from API requests"""
    errors = []
    
    # Validate name
    if 'name' in data:
        name = data['name']
        if not isinstance(name, str):
            errors.append('Name must be a string')
        elif len(name) > 100:
            errors.append('Name must be less than 100 characters')
    
    # Validate model
    if 'model' in data:
        model = data['model']
        valid_models = [
            'letta/letta-free', 'letta/letta-pro',
            'openai/gpt-4', 'openai/gpt-3.5-turbo',
            'anthropic/claude-3-sonnet', 'anthropic/claude-3-haiku'
        ]
        if model not in valid_models:
            errors.append(f'Invalid model: {model}')
    
    # Validate memory blocks
    if 'memoryBlocks' in data:
        memory_blocks = data['memoryBlocks']
        if not isinstance(memory_blocks, list):
            errors.append('Memory blocks must be a list')
        else:
            for i, block in enumerate(memory_blocks):
                if not isinstance(block, dict):
                    errors.append(f'Memory block {i} must be a dictionary')
                elif 'label' not in block or 'value' not in block:
                    errors.append(f'Memory block {i} must have label and value')
                elif not isinstance(block['label'], str) or len(block['label']) > 50:
                    errors.append(f'Memory block {i} label must be a string less than 50 characters')
                elif not isinstance(block['value'], str) or len(block['value']) > 1000:
                    errors.append(f'Memory block {i} value must be a string less than 1000 characters')
    
    return errors

def validate_message_data(data):
    """Validate message data from API requests"""
    errors = []
    
    if 'messages' not in data:
        errors.append('Messages field is required')
    else:
        messages = data['messages']
        if not isinstance(messages, list):
            errors.append('Messages must be a list')
        elif len(messages) == 0:
            errors.append('At least one message is required')
        else:
            for i, message in enumerate(messages):
                if not isinstance(message, dict):
                    errors.append(f'Message {i} must be a dictionary')
                elif 'role' not in message or 'content' not in message:
                    errors.append(f'Message {i} must have role and content')
                elif message['role'] not in ['user', 'assistant', 'system']:
                    errors.append(f'Message {i} has invalid role: {message["role"]}')
                elif not isinstance(message['content'], str):
                    errors.append(f'Message {i} content must be a string')
                elif len(message['content']) > 4000:
                    errors.append(f'Message {i} content must be less than 4000 characters')
    
    return errors
