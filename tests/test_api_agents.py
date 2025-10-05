import pytest
import json
from unittest.mock import patch, MagicMock
from app.utils.session_manager import get_user_id, get_user_tag_id, validate_agent_owner

class TestAgentsAPI:
    """Test suite for agents API endpoints"""
    
    def test_get_agents_success(self, client_with_session, mock_letta_responses):
        """Test successful agents list retrieval"""
        with patch('app.routes.agents.LettaClient') as mock_client:
            mock_instance = MagicMock()
            mock_instance.list_agents.return_value = mock_letta_responses['agents']
            mock_client.return_value = mock_instance
            
            response = client_with_session.get('/api/agents')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]['id'] == 'agent-1'
    
    def test_get_agents_htmx_request(self, client_with_session, mock_letta_responses):
        """Test agents list with HTMX request"""
        with patch('app.routes.agents.LettaClient') as mock_client:
            mock_instance = MagicMock()
            mock_instance.list_agents.return_value = mock_letta_responses['agents']
            mock_client.return_value = mock_instance
            
            response = client_with_session.get('/api/agents', 
                                             headers={'HX-Request': 'true'})
            assert response.status_code == 200
            assert b'agent-item' in response.data
    
    def test_get_agents_no_user_id(self, client):
        """Test agents list without user ID"""
        response = client.get('/api/agents')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'User ID is required' in data['error']
    
    def test_get_agents_letta_error(self, client_with_session):
        """Test agents list with Letta server error"""
        with patch('app.routes.agents.LettaClient') as mock_client:
            mock_instance = MagicMock()
            mock_instance.list_agents.side_effect = Exception('Connection failed')
            mock_client.return_value = mock_instance
            
            response = client_with_session.get('/api/agents')
            assert response.status_code == 500
    
    def test_create_agent_success(self, client_with_session, sample_agent_data):
        """Test successful agent creation"""
        with patch('app.routes.agents.LettaClient') as mock_client:
            mock_instance = MagicMock()
            mock_instance.create_agent.return_value = {'id': 'new-agent-123'}
            mock_client.return_value = mock_instance
            
            response = client_with_session.post('/api/agents')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['id'] == 'new-agent-123'
    
    def test_create_agent_no_user_id(self, client):
        """Test agent creation without user ID"""
        response = client.post('/api/agents')
        assert response.status_code == 400
    
    def test_get_agent_by_id_success(self, client_with_session, mock_letta_responses):
        """Test successful agent retrieval by ID"""
        with patch('app.routes.agents.LettaClient') as mock_client:
            mock_instance = MagicMock()
            mock_instance.get_agent.return_value = mock_letta_responses['agent_details']
            mock_client.return_value = mock_instance
            
            response = client_with_session.get('/api/agents/agent-1')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['id'] == 'agent-1'
            assert data['name'] == 'Test Agent 1'
    
    def test_get_agent_not_found(self, client_with_session):
        """Test agent retrieval for non-existent agent"""
        with patch('app.routes.agents.LettaClient') as mock_client:
            mock_instance = MagicMock()
            mock_instance.get_agent.side_effect = Exception('Agent not found')
            mock_client.return_value = mock_instance
            
            response = client_with_session.get('/api/agents/nonexistent')
            assert response.status_code == 404
    
    def test_get_agent_unauthorized(self, client_with_session):
        """Test agent retrieval for agent user doesn't own"""
        with patch('app.routes.agents.LettaClient') as mock_client:
            mock_instance = MagicMock()
            mock_instance.get_agent.return_value = {
                'id': 'agent-1',
                'tags': ['user:other-user']
            }
            mock_client.return_value = mock_instance
            
            response = client_with_session.get('/api/agents/agent-1')
            assert response.status_code == 404
    
    def test_update_agent_success(self, client_with_session, sample_agent_data):
        """Test successful agent update"""
        with patch('app.routes.agents.LettaClient') as mock_client:
            mock_instance = MagicMock()
            mock_instance.get_agent.return_value = {
                'id': 'agent-1',
                'tags': ['user:test-user-123']
            }
            mock_instance.update_agent.return_value = {'id': 'agent-1', 'updated': True}
            mock_client.return_value = mock_instance
            
            response = client_with_session.put('/api/agents/agent-1', 
                                             json=sample_agent_data)
            assert response.status_code == 200
    
    def test_delete_agent_success(self, client_with_session):
        """Test successful agent deletion"""
        with patch('app.routes.agents.LettaClient') as mock_client:
            mock_instance = MagicMock()
            mock_instance.get_agent.return_value = {
                'id': 'agent-1',
                'tags': ['user:test-user-123']
            }
            mock_instance.delete_agent.return_value = {'deleted': True}
            mock_client.return_value = mock_instance
            
            response = client_with_session.delete('/api/agents/agent-1')
            assert response.status_code == 200
    
    def test_rate_limiting(self, client_with_session):
        """Test API rate limiting"""
        # Make many requests quickly
        responses = []
        for i in range(250):  # Exceed the 200 requests/minute limit
            response = client_with_session.get('/api/agents')
            responses.append(response)
        
        # Check if any requests were rate limited
        rate_limited = any(r.status_code == 429 for r in responses)
        assert rate_limited, "Rate limiting should trigger after exceeding limits"
    
    def test_caching(self, client_with_session, mock_letta_responses):
        """Test API response caching"""
        with patch('app.routes.agents.LettaClient') as mock_client:
            mock_instance = MagicMock()
            mock_instance.list_agents.return_value = mock_letta_responses['agents']
            mock_client.return_value = mock_instance
            
            # First request
            response1 = client_with_session.get('/api/agents')
            assert response1.status_code == 200
            
            # Second request (should be cached)
            response2 = client_with_session.get('/api/agents')
            assert response2.status_code == 200
            
            # Verify client was only called once due to caching
            assert mock_instance.list_agents.call_count == 1
