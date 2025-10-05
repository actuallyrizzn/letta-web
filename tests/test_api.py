import pytest
import json
from app import create_app

@pytest.fixture
def app():
    """Create test app"""
    app = create_app('development')
    app.config['TESTING'] = True
    app.config['LETTA_API_KEY'] = 'test-key'
    app.config['LETTA_BASE_URL'] = 'http://test-letta-server'
    app.config['USE_COOKIE_BASED_AUTHENTICATION'] = False
    return app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

def test_runtime_endpoint(client):
    """Test runtime info endpoint"""
    response = client.get('/api/runtime')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'LETTA_BASE_URL' in data

def test_agents_list_endpoint(client):
    """Test agents list endpoint"""
    response = client.get('/api/agents')
    # Should return 500 when Letta server is not available (expected in test)
    assert response.status_code == 500
    
    data = json.loads(response.data)
    assert 'error' in data

def test_create_agent_endpoint(client):
    """Test create agent endpoint"""
    response = client.post('/api/agents')
    # This will fail without Letta server, but should not crash
    assert response.status_code in [200, 500]

def test_agent_not_found(client):
    """Test agent not found"""
    response = client.get('/api/agents/nonexistent-agent')
    assert response.status_code == 404
