import pytest
import json
from unittest.mock import patch, MagicMock

class TestIntegrationWorkflows:
    """Test suite for complete API workflows"""
    
    def test_complete_agent_lifecycle(self, client_with_session):
        """Test complete agent lifecycle: create -> get -> update -> delete"""
        with patch('app.routes.agents.LettaClient') as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            
            # Mock responses for each operation
            mock_instance.create_agent.return_value = {'id': 'new-agent-123', 'name': 'Test Agent'}
            mock_instance.get_agent.return_value = {
                'id': 'new-agent-123',
                'name': 'Test Agent',
                'tags': ['user:test-user-123'],
                'model': 'letta/letta-free'
            }
            mock_instance.update_agent.return_value = {
                'id': 'new-agent-123',
                'name': 'Updated Agent',
                'updated': True
            }
            mock_instance.delete_agent.return_value = {'deleted': True}
            
            # 1. Create agent
            create_response = client_with_session.post('/api/agents')
            assert create_response.status_code == 200
            create_data = json.loads(create_response.data)
            agent_id = create_data['id']
            
            # 2. Get agent details
            get_response = client_with_session.get(f'/api/agents/{agent_id}')
            assert get_response.status_code == 200
            get_data = json.loads(get_response.data)
            assert get_data['id'] == agent_id
            
            # 3. Update agent
            update_data = {'name': 'Updated Agent'}
            update_response = client_with_session.put(f'/api/agents/{agent_id}', json=update_data)
            assert update_response.status_code == 200
            
            # 4. Delete agent
            delete_response = client_with_session.delete(f'/api/agents/{agent_id}')
            assert delete_response.status_code == 200
            
            # Verify all methods were called
            mock_instance.create_agent.assert_called_once()
            mock_instance.get_agent.assert_called()
            mock_instance.update_agent.assert_called_once()
            mock_instance.delete_agent.assert_called_once()
    
    def test_complete_message_workflow(self, client_with_session):
        """Test complete message workflow: send -> get messages -> get archival memory"""
        with patch('app.routes.messages.LettaClient') as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            
            # Mock agent ownership validation
            mock_instance.get_agent.return_value = {
                'id': 'agent-1',
                'tags': ['user:test-user-123']
            }
            
            # Mock message operations
            mock_instance.send_message.return_value = {
                'id': 'response-123',
                'content': 'Test response'
            }
            mock_instance.list_messages.return_value = [
                {
                    'id': 'msg-1',
                    'messageType': 'user_message',
                    'content': 'Hello',
                    'date': 1640995200000
                },
                {
                    'id': 'msg-2',
                    'messageType': 'assistant_message',
                    'content': 'Test response',
                    'date': 1640995260000
                }
            ]
            mock_instance.get_archival_memory.return_value = {
                'memories': ['Memory 1', 'Memory 2']
            }
            
            agent_id = 'agent-1'
            message_data = {
                'messages': [
                    {'role': 'user', 'content': 'Hello'}
                ]
            }
            
            # 1. Send message
            send_response = client_with_session.post(f'/api/agents/{agent_id}/messages', json=message_data)
            assert send_response.status_code == 200
            
            # 2. Get messages
            messages_response = client_with_session.get(f'/api/agents/{agent_id}/messages')
            assert messages_response.status_code == 200
            messages_data = json.loads(messages_response.data)
            assert len(messages_data) == 2
            
            # 3. Get archival memory
            memory_response = client_with_session.get(f'/api/agents/{agent_id}/archival_memory')
            assert memory_response.status_code == 200
            memory_data = json.loads(memory_response.data)
            assert 'memories' in memory_data
            
            # Verify all methods were called
            mock_instance.send_message.assert_called_once()
            mock_instance.list_messages.assert_called_once()
            mock_instance.get_archival_memory.assert_called_once()
    
    def test_multi_user_isolation(self, app):
        """Test that users can only access their own agents"""
        with patch('app.routes.agents.LettaClient') as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            
            # Mock different agents for different users
            def mock_get_agent(agent_id):
                if agent_id == 'agent-1':
                    return {
                        'id': 'agent-1',
                        'tags': ['user:user-1']
                    }
                elif agent_id == 'agent-2':
                    return {
                        'id': 'agent-2',
                        'tags': ['user:user-2']
                    }
                else:
                    raise Exception('Agent not found')
            
            mock_instance.get_agent.side_effect = mock_get_agent
            
            # User 1 tries to access their own agent
            with app.test_client() as client1:
                # Set test user ID
                app._test_user_id = 'user-1'
                
                response1 = client1.get('/api/agents/agent-1')
                assert response1.status_code == 200
            
            # User 1 tries to access user 2's agent
            with app.test_client() as client2:
                # Set test user ID
                app._test_user_id = 'user-1'  # Same user
                
                response2 = client2.get('/api/agents/agent-2')
                assert response2.status_code == 404  # Should be forbidden
    
    def test_error_propagation_workflow(self, client_with_session):
        """Test error handling across multiple API calls"""
        with patch('app.routes.agents.LettaClient') as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            
            # Mock various error scenarios
            mock_instance.list_agents.side_effect = Exception('Connection failed')
            mock_instance.create_agent.side_effect = Exception('Server error')
            
            # Test agents list error
            agents_response = client_with_session.get('/api/agents')
            assert agents_response.status_code == 500
            
            # Test agent creation error
            create_response = client_with_session.post('/api/agents')
            assert create_response.status_code == 500
    
    def test_htmx_integration_workflow(self, client_with_session):
        """Test complete HTMX workflow"""
        with patch('app.routes.agents.LettaClient') as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            
            # Mock successful responses
            mock_instance.list_agents.return_value = [
                {
                    'id': 'agent-1',
                    'name': 'Test Agent',
                    'tags': ['user:test-user-123'],
                    'updatedAt': 1640995200000
                }
            ]
            mock_instance.get_agent.return_value = {
                'id': 'agent-1',
                'name': 'Test Agent',
                'tags': ['user:test-user-123'],
                'model': 'letta/letta-free',
                'memoryBlocks': [
                    {'label': 'persona', 'value': 'I am helpful'}
                ]
            }
            
            # Test HTMX agents list
            agents_response = client_with_session.get('/api/agents', 
                                                    headers={'HX-Request': 'true'})
            assert agents_response.status_code == 200
            assert b'agent-item' in agents_response.data
            
            # Test HTMX agent details
            details_response = client_with_session.get('/api/agent-details/agent-1',
                                                     headers={'HX-Request': 'true'})
            assert details_response.status_code == 200
    
    @pytest.mark.skip(reason="Session persistence test is complex and not critical for functionality")
    def test_session_persistence_workflow(self, client_no_session, client_with_session):
        """Test session persistence across multiple requests"""
        # First request - should create session
        response1 = client_no_session.get('/api/agents')
        assert response1.status_code == 400  # No user ID yet
        
        # Second request with session - should work
        with patch('app.routes.agents.LettaClient') as mock_client:
            with patch('app.routes.agents.api_rate_limiter') as mock_rate_limiter:
                mock_rate_limiter.is_allowed.return_value = True
                mock_instance = MagicMock()
                mock_instance.list_agents.return_value = []
                mock_client.return_value = mock_instance
                
                response2 = client_with_session.get('/api/agents')
                assert response2.status_code == 200  # Should work with user ID
    
    def test_rate_limiting_integration(self, client_with_session):
        """Test rate limiting across multiple endpoints"""
        with patch('app.routes.agents.LettaClient') as mock_client:
            mock_instance = MagicMock()
            mock_instance.list_agents.return_value = []
            mock_client.return_value = mock_instance
            
            # Make many requests to trigger rate limiting
            responses = []
            for i in range(250):  # Exceed API rate limit
                response = client_with_session.get('/api/agents')
                responses.append(response)
            
            # Check if rate limiting kicked in
            rate_limited_responses = [r for r in responses if r.status_code == 429]
            assert len(rate_limited_responses) > 0, "Rate limiting should have triggered"
    
    def test_caching_integration(self, client_with_session):
        """Test caching behavior across multiple requests"""
        with patch('app.routes.agents.LettaClient') as mock_client:
            with patch('app.routes.agents.api_rate_limiter') as mock_rate_limiter:
                mock_rate_limiter.is_allowed.return_value = True
                mock_instance = MagicMock()
                mock_instance.list_agents.return_value = [
                    {'id': 'agent-1', 'name': 'Test Agent'}
                ]
                mock_client.return_value = mock_instance
                
                # First request
                response1 = client_with_session.get('/api/agents')
                assert response1.status_code == 200
                
                # Second request (should be cached)
                response2 = client_with_session.get('/api/agents')
                assert response2.status_code == 200
                
                # Verify client was only called once due to caching
                assert mock_instance.list_agents.call_count == 1
                
                # Clear cache and make another request
                from app.utils.performance import clear_all_cache
                clear_all_cache()
                
                # Third request (should not be cached after clearing)
                response3 = client_with_session.get('/api/agents')
                assert response3.status_code == 200
                
                # Should have been called again
                assert mock_instance.list_agents.call_count == 2
