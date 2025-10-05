import os
import pytest
from app import create_app
from app.config import config

@pytest.fixture(scope='session')
def app():
    """Create test application"""
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'LETTA_API_KEY': 'test-api-key',
        'LETTA_BASE_URL': 'http://test-letta-server:8283',
        'USE_COOKIE_BASED_AUTHENTICATION': True,
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
        'SECRET_KEY': 'test-secret-key'
    })
    return app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def client_with_session(app):
    """Create test client with session"""
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['letta_uid'] = 'test-user-123'
            sess['created_at'] = '2024-01-01T00:00:00'
        yield client

@pytest.fixture
def mock_letta_responses():
    """Mock Letta API responses"""
    return {
        'agents': [
            {
                'id': 'agent-1',
                'name': 'Test Agent 1',
                'model': 'letta/letta-free',
                'tags': ['user:test-user-123'],
                'updatedAt': 1640995200000,
                'memoryBlocks': [
                    {'label': 'persona', 'value': 'I am a test agent'}
                ]
            }
        ],
        'messages': [
            {
                'id': 'msg-1',
                'messageType': 'user_message',
                'content': 'Hello, test message',
                'date': 1640995200000
            },
            {
                'id': 'msg-2', 
                'messageType': 'assistant_message',
                'content': 'Hello! How can I help you?',
                'date': 1640995260000
            }
        ],
        'agent_details': {
            'id': 'agent-1',
            'name': 'Test Agent 1',
            'model': 'letta/letta-free',
            'tags': ['user:test-user-123'],
            'memoryBlocks': [
                {'label': 'persona', 'value': 'I am a test agent'},
                {'label': 'human', 'value': 'The human is a tester'}
            ]
        }
    }

@pytest.fixture
def sample_agent_data():
    """Sample agent data for testing"""
    return {
        'name': 'Test Agent',
        'model': 'letta/letta-free',
        'memoryBlocks': [
            {'label': 'persona', 'value': 'I am a helpful test agent'},
            {'label': 'human', 'value': 'The human is testing the system'}
        ]
    }

@pytest.fixture
def sample_message_data():
    """Sample message data for testing"""
    return {
        'messages': [
            {
                'role': 'user',
                'content': 'Hello, this is a test message'
            }
        ]
    }
