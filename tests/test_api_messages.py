import pytest
import json
from unittest.mock import patch, MagicMock

class TestMessagesAPI:
    """Test suite for messages API endpoints"""
    
    def test_get_agent_messages_success(self, client_with_session, mock_letta_responses):
        """Test successful message retrieval"""
        with patch('app.routes.messages.LettaClient') as mock_client:
            mock_instance = MagicMock()
            mock_instance.get_agent.return_value = {
                'id': 'agent-1',
                'tags': ['user:test-user-123']
            }
            mock_instance.list_messages.return_value = mock_letta_responses['messages']
            mock_client.return_value = mock_instance
            
            response = client_with_session.get('/api/agents/agent-1/messages')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert isinstance(data, list)
            assert len(data) == 2
            assert data[0]['role'] == 'user'
            assert data[1]['role'] == 'assistant'
    
    def test_get_agent_messages_htmx_request(self, client_with_session, mock_letta_responses):
        """Test message retrieval with HTMX request"""
        with patch('app.routes.messages.LettaClient') as mock_client:
            mock_instance = MagicMock()
            mock_instance.get_agent.return_value = {
                'id': 'agent-1',
                'tags': ['user:test-user-123']
            }
            mock_instance.list_messages.return_value = mock_letta_responses['messages']
            mock_client.return_value = mock_instance
            
            response = client_with_session.get('/api/agents/agent-1/messages',
                                             headers={'HX-Request': 'true'})
            assert response.status_code == 200
            assert b'max-w-xs lg:max-w-md' in response.data  # Check for message styling
    
    def test_get_agent_messages_unauthorized(self, client_with_session):
        """Test message retrieval for unauthorized agent"""
        with patch('app.routes.messages.LettaClient') as mock_client:
            mock_instance = MagicMock()
            mock_instance.get_agent.return_value = {
                'id': 'agent-1',
                'tags': ['user:other-user']
            }
            mock_client.return_value = mock_instance
            
            response = client_with_session.get('/api/agents/agent-1/messages')
            assert response.status_code == 404
    
    def test_send_message_success(self, client_with_session, sample_message_data):
        """Test successful message sending"""
        with patch('app.routes.messages.LettaClient') as mock_client:
            mock_instance = MagicMock()
            mock_instance.get_agent.return_value = {
                'id': 'agent-1',
                'tags': ['user:test-user-123']
            }
            mock_instance.send_message.return_value = {
                'id': 'response-123',
                'content': 'Test response'
            }
            mock_client.return_value = mock_instance
            
            response = client_with_session.post('/api/agents/agent-1/messages',
                                              json=sample_message_data)
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['id'] == 'response-123'
    
    def test_send_message_invalid_data(self, client_with_session):
        """Test message sending with invalid data"""
        invalid_data = {
            'messages': [
                {'role': 'invalid_role', 'content': 'test'}
            ]
        }
        
        response = client_with_session.post('/api/agents/agent-1/messages',
                                          json=invalid_data)
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Validation failed' in data['error']
    
    def test_send_message_empty_messages(self, client_with_session):
        """Test message sending with empty messages"""
        invalid_data = {'messages': []}
        
        response = client_with_session.post('/api/agents/agent-1/messages',
                                          json=invalid_data)
        assert response.status_code == 400
    
    def test_send_message_missing_messages_field(self, client_with_session):
        """Test message sending without messages field"""
        invalid_data = {}
        
        response = client_with_session.post('/api/agents/agent-1/messages',
                                          json=invalid_data)
        assert response.status_code == 400
    
    def test_send_message_too_long(self, client_with_session):
        """Test message sending with content too long"""
        long_content = 'x' * 5000  # Exceeds 4000 character limit
        invalid_data = {
            'messages': [
                {'role': 'user', 'content': long_content}
            ]
        }
        
        response = client_with_session.post('/api/agents/agent-1/messages',
                                          json=invalid_data)
        assert response.status_code == 400
    
    def test_message_rate_limiting(self, client_with_session, sample_message_data):
        """Test message rate limiting"""
        with patch('app.routes.messages.LettaClient') as mock_client:
            mock_instance = MagicMock()
            mock_instance.get_agent.return_value = {
                'id': 'agent-1',
                'tags': ['user:test-user-123']
            }
            mock_instance.send_message.return_value = {'id': 'response'}
            mock_client.return_value = mock_instance
            
            # Send many messages quickly
            responses = []
            for i in range(35):  # Exceed the 30 messages/minute limit
                response = client_with_session.post('/api/agents/agent-1/messages',
                                                  json=sample_message_data)
                responses.append(response)
            
            # Check if any requests were rate limited
            rate_limited = any(r.status_code == 429 for r in responses)
            assert rate_limited, "Message rate limiting should trigger"
    
    def test_get_archival_memory_success(self, client_with_session):
        """Test successful archival memory retrieval"""
        with patch('app.routes.messages.LettaClient') as mock_client:
            mock_instance = MagicMock()
            mock_instance.get_agent.return_value = {
                'id': 'agent-1',
                'tags': ['user:test-user-123']
            }
            mock_instance.get_archival_memory.return_value = {
                'memories': ['Memory 1', 'Memory 2']
            }
            mock_client.return_value = mock_instance
            
            response = client_with_session.get('/api/agents/agent-1/archival_memory')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'memories' in data
            assert len(data['memories']) == 2
    
    def test_get_archival_memory_unauthorized(self, client_with_session):
        """Test archival memory retrieval for unauthorized agent"""
        with patch('app.routes.messages.LettaClient') as mock_client:
            mock_instance = MagicMock()
            mock_instance.get_agent.return_value = {
                'id': 'agent-1',
                'tags': ['user:other-user']
            }
            mock_client.return_value = mock_instance
            
            response = client_with_session.get('/api/agents/agent-1/archival_memory')
            assert response.status_code == 404
    
    def test_message_filtering(self, client_with_session):
        """Test message filtering removes system messages"""
        with patch('app.routes.messages.LettaClient') as mock_client:
            mock_instance = MagicMock()
            mock_instance.get_agent.return_value = {
                'id': 'agent-1',
                'tags': ['user:test-user-123']
            }
            
            # Include system messages that should be filtered
            raw_messages = [
                {
                    'id': 'msg-1',
                    'messageType': 'user_message',
                    'content': 'Hello',
                    'date': 1640995200000
                },
                {
                    'id': 'msg-2',
                    'messageType': 'system_message',  # Should be filtered
                    'content': 'System message',
                    'date': 1640995210000
                },
                {
                    'id': 'msg-3',
                    'messageType': 'assistant_message',
                    'content': 'Hi there!',
                    'date': 1640995220000
                }
            ]
            
            mock_instance.list_messages.return_value = raw_messages
            mock_client.return_value = mock_instance
            
            response = client_with_session.get('/api/agents/agent-1/messages')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            # Should only have 2 messages (system message filtered out)
            assert len(data) == 2
            assert all(msg['role'] in ['user', 'assistant'] for msg in data)
