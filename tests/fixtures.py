import json
from datetime import datetime, timedelta

class TestFixtures:
    """Test fixtures and mock data for comprehensive testing"""
    
    @staticmethod
    def get_sample_agents():
        """Get sample agent data for testing"""
        return [
            {
                'id': 'agent-1',
                'name': 'Customer Support Agent',
                'model': 'letta/letta-free',
                'tags': ['user:test-user-123'],
                'updatedAt': 1640995200000,
                'createdAt': 1640908800000,
                'memoryBlocks': [
                    {
                        'label': 'persona',
                        'value': 'I am a helpful customer support agent. I provide friendly and efficient assistance.'
                    },
                    {
                        'label': 'human',
                        'value': 'The human is a customer seeking help with their account or services.'
                    }
                ]
            },
            {
                'id': 'agent-2',
                'name': 'Technical Assistant',
                'model': 'letta/letta-pro',
                'tags': ['user:test-user-123'],
                'updatedAt': 1640995100000,
                'createdAt': 1640908700000,
                'memoryBlocks': [
                    {
                        'label': 'persona',
                        'value': 'I am a technical assistant specializing in troubleshooting and technical guidance.'
                    },
                    {
                        'label': 'human',
                        'value': 'The human is a developer or technical user seeking assistance with technical issues.'
                    }
                ]
            },
            {
                'id': 'agent-3',
                'name': 'Creative Writer',
                'model': 'openai/gpt-4',
                'tags': ['user:test-user-456'],
                'updatedAt': 1640995000000,
                'createdAt': 1640908600000,
                'memoryBlocks': [
                    {
                        'label': 'persona',
                        'value': 'I am a creative writing assistant who helps with storytelling, content creation, and creative projects.'
                    },
                    {
                        'label': 'human',
                        'value': 'The human is a writer or creative professional seeking inspiration and assistance.'
                    }
                ]
            }
        ]
    
    @staticmethod
    def get_sample_messages():
        """Get sample message data for testing"""
        return [
            {
                'id': 'msg-1',
                'message_type': 'user_message',
                'content': 'Hello, I need help with my account',
                'date': 1640995200000,
                'agentId': 'agent-1'
            },
            {
                'id': 'msg-2',
                'message_type': 'assistant_message',
                'content': 'Hello! I\'d be happy to help you with your account. What specific issue are you experiencing?',
                'date': 1640995260000,
                'agentId': 'agent-1'
            },
            {
                'id': 'msg-3',
                'message_type': 'user_message',
                'content': 'I can\'t log in to my account',
                'date': 1640995320000,
                'agentId': 'agent-1'
            },
            {
                'id': 'msg-4',
                'message_type': 'assistant_message',
                'content': 'I understand you\'re having trouble logging in. Let me help you troubleshoot this. Have you tried resetting your password?',
                'date': 1640995380000,
                'agentId': 'agent-1'
            },
            {
                'id': 'msg-5',
                'message_type': 'system_message',
                'content': 'System: Agent memory updated with login troubleshooting context',
                'date': 1640995400000,
                'agentId': 'agent-1'
            }
        ]
    
    @staticmethod
    def get_sample_archival_memory():
        """Get sample archival memory data for testing"""
        return {
            'agentId': 'agent-1',
            'memories': [
                {
                    'id': 'memory-1',
                    'content': 'User frequently has login issues with their account',
                    'timestamp': 1640995200000,
                    'type': 'user_preference'
                },
                {
                    'id': 'memory-2',
                    'content': 'Customer prefers email communication over phone calls',
                    'timestamp': 1640995100000,
                    'type': 'user_preference'
                },
                {
                    'id': 'memory-3',
                    'content': 'Account was created on 2023-12-01',
                    'timestamp': 1640995000000,
                    'type': 'account_info'
                }
            ],
            'totalMemories': 3,
            'lastUpdated': 1640995400000
        }
    
    @staticmethod
    def get_sample_users():
        """Get sample user data for testing"""
        return [
            {
                'id': 'test-user-123',
                'sessionId': 'session-123',
                'createdAt': '2024-01-01T00:00:00Z',
                'lastActive': '2024-01-01T12:00:00Z',
                'agentCount': 2
            },
            {
                'id': 'test-user-456',
                'sessionId': 'session-456',
                'createdAt': '2024-01-01T01:00:00Z',
                'lastActive': '2024-01-01T11:00:00Z',
                'agentCount': 1
            }
        ]
    
    @staticmethod
    def get_error_scenarios():
        """Get various error scenarios for testing"""
        return {
            'connection_error': {
                'type': 'ConnectionError',
                'message': 'Failed to connect to Letta server',
                'status_code': 503
            },
            'authentication_error': {
                'type': 'AuthenticationError',
                'message': 'Invalid API key',
                'status_code': 401
            },
            'not_found_error': {
                'type': 'NotFoundError',
                'message': 'Agent not found',
                'status_code': 404
            },
            'validation_error': {
                'type': 'ValidationError',
                'message': 'Invalid input data',
                'status_code': 400
            },
            'rate_limit_error': {
                'type': 'RateLimitError',
                'message': 'Rate limit exceeded',
                'status_code': 429
            },
            'server_error': {
                'type': 'ServerError',
                'message': 'Internal server error',
                'status_code': 500
            }
        }
    
    @staticmethod
    def get_performance_test_data():
        """Get data for performance testing"""
        return {
            'large_agent_list': [
                {
                    'id': f'agent-{i}',
                    'name': f'Test Agent {i}',
                    'model': 'letta/letta-free',
                    'tags': ['user:test-user-123'],
                    'updatedAt': 1640995200000 + (i * 1000)
                }
                for i in range(100)
            ],
            'large_message_list': [
                {
                    'id': f'msg-{i}',
                    'message_type': 'user_message' if i % 2 == 0 else 'assistant_message',
                    'content': f'Test message {i}',
                    'date': 1640995200000 + (i * 1000)
                }
                for i in range(1000)
            ],
            'stress_test_requests': {
                'concurrent_users': 50,
                'requests_per_user': 100,
                'timeout_seconds': 30
            }
        }
    
    @staticmethod
    def get_security_test_data():
        """Get data for security testing"""
        return {
            'malicious_inputs': [
                '<script>alert("xss")</script>',
                '"; DROP TABLE users; --',
                '../../../etc/passwd',
                '${7*7}',
                '{{7*7}}',
                'javascript:alert(1)',
                'data:text/html,<script>alert(1)</script>'
            ],
            'sql_injection_payloads': [
                "' OR '1'='1",
                "'; DROP TABLE agents; --",
                "' UNION SELECT * FROM users --",
                "1' OR '1'='1' --"
            ],
            'xss_payloads': [
                "<img src=x onerror=alert(1)>",
                "<svg onload=alert(1)>",
                "<iframe src=javascript:alert(1)>",
                "<script>fetch('/api/agents').then(r=>r.text()).then(d=>console.log(d))</script>"
            ]
        }
    
    @staticmethod
    def get_mobile_test_scenarios():
        """Get mobile-specific test scenarios"""
        return {
            'viewport_sizes': [
                {'width': 375, 'height': 667, 'name': 'iPhone SE'},
                {'width': 414, 'height': 896, 'name': 'iPhone 11'},
                {'width': 768, 'height': 1024, 'name': 'iPad'},
                {'width': 360, 'height': 640, 'name': 'Android Small'},
                {'width': 412, 'height': 915, 'name': 'Android Large'}
            ],
            'touch_scenarios': [
                'swipe_left_to_close_sidebar',
                'swipe_right_to_open_sidebar',
                'pinch_to_zoom',
                'long_press_context_menu',
                'double_tap_to_select'
            ],
            'orientation_tests': [
                'portrait_to_landscape',
                'landscape_to_portrait',
                'orientation_change_with_sidebar_open'
            ]
        }
    
    @staticmethod
    def get_accessibility_test_data():
        """Get data for accessibility testing"""
        return {
            'aria_labels': [
                'Create new agent',
                'Delete agent',
                'Edit agent',
                'Send message',
                'Toggle sidebar',
                'Close modal'
            ],
            'keyboard_shortcuts': [
                {'key': 'Tab', 'action': 'Navigate to next element'},
                {'key': 'Shift+Tab', 'action': 'Navigate to previous element'},
                {'key': 'Enter', 'action': 'Activate focused element'},
                {'key': 'Escape', 'action': 'Close modal or sidebar'},
                {'key': 'Space', 'action': 'Activate button'}
            ],
            'screen_reader_text': [
                'Agent list with 2 agents',
                'Message input field',
                'Send button',
                'Agent details panel',
                'Loading indicator'
            ]
        }

class MockLettaServer:
    """Mock Letta server for testing"""
    
    def __init__(self):
        self.agents = TestFixtures.get_sample_agents()
        self.messages = TestFixtures.get_sample_messages()
        self.archival_memory = TestFixtures.get_sample_archival_memory()
    
    def list_agents(self, tags=None, match_all_tags=True):
        """Mock list agents endpoint"""
        if tags:
            filtered_agents = []
            for agent in self.agents:
                if match_all_tags:
                    if all(tag in agent['tags'] for tag in tags):
                        filtered_agents.append(agent)
                else:
                    if any(tag in agent['tags'] for tag in tags):
                        filtered_agents.append(agent)
            return filtered_agents
        return self.agents
    
    def get_agent(self, agent_id):
        """Mock get agent endpoint"""
        for agent in self.agents:
            if agent['id'] == agent_id:
                return agent
        raise Exception('Agent not found')
    
    def create_agent(self, memory_blocks, model, embedding, tags=None):
        """Mock create agent endpoint"""
        new_agent = {
            'id': f'agent-{len(self.agents) + 1}',
            'name': 'New Agent',
            'model': model,
            'tags': tags or [],
            'updatedAt': int(datetime.now().timestamp() * 1000),
            'createdAt': int(datetime.now().timestamp() * 1000),
            'memoryBlocks': memory_blocks
        }
        self.agents.append(new_agent)
        return new_agent
    
    def update_agent(self, agent_id, **kwargs):
        """Mock update agent endpoint"""
        for agent in self.agents:
            if agent['id'] == agent_id:
                agent.update(kwargs)
                agent['updatedAt'] = int(datetime.now().timestamp() * 1000)
                return agent
        raise Exception('Agent not found')
    
    def delete_agent(self, agent_id):
        """Mock delete agent endpoint"""
        for i, agent in enumerate(self.agents):
            if agent['id'] == agent_id:
                del self.agents[i]
                return {'deleted': True}
        raise Exception('Agent not found')
    
    def list_messages(self, agent_id, limit=100):
        """Mock list messages endpoint"""
        agent_messages = [msg for msg in self.messages if msg['agentId'] == agent_id]
        return agent_messages[-limit:]
    
    def send_message(self, agent_id, messages):
        """Mock send message endpoint"""
        # Add user message
        user_message = messages[-1]
        new_message = {
            'id': f'msg-{len(self.messages) + 1}',
            'message_type': 'user_message',
            'content': user_message['content'],
            'date': int(datetime.now().timestamp() * 1000),
            'agentId': agent_id
        }
        self.messages.append(new_message)
        
        # Generate AI response
        ai_response = {
            'id': f'msg-{len(self.messages) + 1}',
            'message_type': 'assistant_message',
            'content': f"AI response to: {user_message['content']}",
            'date': int(datetime.now().timestamp() * 1000),
            'agentId': agent_id
        }
        self.messages.append(ai_response)
        
        return ai_response
    
    def get_archival_memory(self, agent_id):
        """Mock get archival memory endpoint"""
        return self.archival_memory
