import os
import pytest
from unittest.mock import patch
from app import create_app
from app.config import config
from playwright.sync_api import sync_playwright

@pytest.fixture(autouse=True)
def clear_global_state():
    """Clear global state before each test"""
    from app.utils.performance import clear_all_cache, reset_rate_limiters
    clear_all_cache()
    reset_rate_limiters()
    yield
    # Clean up after test
    clear_all_cache()
    reset_rate_limiters()

@pytest.fixture
def app():
    """Create test application"""
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'LETTA_API_KEY': 'test-api-key',
        'LETTA_BASE_URL': 'http://test-letta-server:8283',
        'USE_COOKIE_BASED_AUTHENTICATION': True,
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
        'SECRET_KEY': 'test-secret-key',
        'SESSION_TYPE': 'null'  # Use null session for testing
    })
    return app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def client_with_session(app):
    """Create test client with session"""
    client = app.test_client()
    # Set the test user ID on the app
    app._test_user_id = 'test-user-123'
    yield client
    # Clean up
    if hasattr(app, '_test_user_id'):
        delattr(app, '_test_user_id')

@pytest.fixture
def client_no_session(app):
    """Create test client without session"""
    client = app.test_client()
    # Set the test user ID to None on the app
    app._test_user_id = None
    yield client
    # Clean up
    if hasattr(app, '_test_user_id'):
        delattr(app, '_test_user_id')

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
                'message_type': 'user_message',
                'content': 'Hello, test message',
                'date': 1640995200000
            },
            {
                'id': 'msg-2', 
                'message_type': 'assistant_message',
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

@pytest.fixture(scope="session")
def browser():
    """Browser fixture for E2E tests"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()
