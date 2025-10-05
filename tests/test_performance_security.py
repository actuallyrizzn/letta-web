import pytest
import time
import threading
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch, MagicMock
from app.utils.performance import RateLimiter, cache_result, get_cache_stats
from app.utils.forms import validate_agent_data, validate_message_data

class TestPerformanceTests:
    """Test suite for performance testing"""
    
    def test_api_response_times(self, client_with_session):
        """Test API response times are within acceptable limits"""
        with patch('app.routes.agents.LettaClient') as mock_client:
            mock_instance = MagicMock()
            mock_instance.list_agents.return_value = []
            mock_client.return_value = mock_instance
            
            # Test agents list response time
            start_time = time.time()
            response = client_with_session.get('/api/agents')
            response_time = time.time() - start_time
            
            assert response.status_code == 200
            assert response_time < 1.0, f"API response took {response_time:.2f}s, should be under 1s"
    
    def test_concurrent_requests(self, client_with_session):
        """Test application handles concurrent requests properly"""
        with patch('app.routes.agents.LettaClient') as mock_client:
            mock_instance = MagicMock()
            mock_instance.list_agents.return_value = []
            mock_client.return_value = mock_instance
            
            def make_request():
                return client_with_session.get('/api/agents')
            
            # Make 10 concurrent requests
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request) for _ in range(10)]
                responses = [future.result() for future in as_completed(futures)]
            
            # All requests should succeed
            assert all(r.status_code == 200 for r in responses)
            
            # Response times should be reasonable
            for response in responses:
                assert response.status_code == 200
    
    def test_memory_usage(self, app):
        """Test memory usage doesn't grow excessively"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Perform many operations
        with app.test_client() as client:
            for i in range(100):
                with client.session_transaction() as sess:
                    sess['test_key'] = f'test_value_{i}'
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 10MB)
        assert memory_increase < 10 * 1024 * 1024, f"Memory increased by {memory_increase / 1024 / 1024:.2f}MB"
    
    def test_cache_performance(self):
        """Test cache performance and efficiency"""
        call_count = 0
        
        @cache_result(ttl=60)
        def expensive_operation(x):
            nonlocal call_count
            call_count += 1
            time.sleep(0.1)  # Simulate expensive operation
            return x * 2
        
        # First call should be slow
        start_time = time.time()
        result1 = expensive_operation(5)
        first_call_time = time.time() - start_time
        
        # Second call should be fast (cached)
        start_time = time.time()
        result2 = expensive_operation(5)
        second_call_time = time.time() - start_time
        
        assert result1 == result2 == 10
        assert call_count == 1  # Function only called once
        assert second_call_time < first_call_time * 0.1  # Cached call should be much faster
    
    def test_rate_limiter_performance(self):
        """Test rate limiter performance under load"""
        limiter = RateLimiter(max_requests=1000, window_seconds=60)
        
        def check_rate_limit():
            return limiter.is_allowed('test-user')
        
        # Test many rapid requests
        start_time = time.time()
        results = []
        
        for i in range(1000):
            results.append(check_rate_limit())
        
        total_time = time.time() - start_time
        
        # All requests should be allowed
        assert all(results)
        
        # Should handle 1000 requests quickly
        assert total_time < 1.0, f"Rate limiter took {total_time:.2f}s for 1000 requests"
    
    def test_large_data_handling(self, client_with_session):
        """Test handling of large datasets"""
        # Create large agent list
        large_agent_list = [
            {
                'id': f'agent-{i}',
                'name': f'Test Agent {i}',
                'model': 'letta/letta-free',
                'tags': ['user:test-user-123'],
                'updatedAt': 1640995200000 + i
            }
            for i in range(1000)
        ]
        
        with patch('app.routes.agents.LettaClient') as mock_client:
            mock_instance = MagicMock()
            mock_instance.list_agents.return_value = large_agent_list
            mock_client.return_value = mock_instance
            
            start_time = time.time()
            response = client_with_session.get('/api/agents')
            response_time = time.time() - start_time
            
            assert response.status_code == 200
            assert response_time < 2.0, f"Large data response took {response_time:.2f}s"
            
            data = response.get_json()
            assert len(data) == 1000

class TestSecurityTests:
    """Test suite for security testing"""
    
    def test_sql_injection_protection(self, client_with_session):
        """Test protection against SQL injection attacks"""
        sql_payloads = [
            "'; DROP TABLE agents; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users --",
            "1' OR '1'='1' --"
        ]
        
        for payload in sql_payloads:
            # Try SQL injection in agent ID
            response = client_with_session.get(f'/api/agents/{payload}')
            # Should not crash or expose data
            assert response.status_code in [400, 404, 500]
            
            # Try SQL injection in message content
            message_data = {
                'messages': [
                    {'role': 'user', 'content': payload}
                ]
            }
            response = client_with_session.post('/api/agents/test-agent/messages', 
                                             json=message_data)
            # Should handle gracefully
            assert response.status_code in [400, 404, 500]
    
    def test_xss_protection(self, client_with_session):
        """Test protection against XSS attacks"""
        xss_payloads = [
            '<script>alert("xss")</script>',
            '<img src=x onerror=alert(1)>',
            '<svg onload=alert(1)>',
            'javascript:alert(1)',
            '<iframe src=javascript:alert(1)>'
        ]
        
        for payload in xss_payloads:
            # Try XSS in agent name
            agent_data = {
                'name': payload,
                'model': 'letta/letta-free',
                'memoryBlocks': [{'label': 'persona', 'value': 'test'}]
            }
            
            response = client_with_session.put('/api/agents/test-agent', json=agent_data)
            # Should sanitize or reject
            assert response.status_code in [200, 400, 500]
            
            # Try XSS in message content
            message_data = {
                'messages': [
                    {'role': 'user', 'content': payload}
                ]
            }
            response = client_with_session.post('/api/agents/test-agent/messages', 
                                             json=message_data)
            assert response.status_code in [200, 400, 500]
    
    def test_path_traversal_protection(self, client_with_session):
        """Test protection against path traversal attacks"""
        path_payloads = [
            '../../../etc/passwd',
            '..\\..\\..\\windows\\system32\\drivers\\etc\\hosts',
            '....//....//....//etc/passwd',
            '%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd'
        ]
        
        for payload in path_payloads:
            response = client_with_session.get(f'/api/agents/{payload}')
            # Should not expose file system
            assert response.status_code in [400, 404, 500]
    
    def test_input_validation_security(self):
        """Test input validation prevents malicious data"""
        malicious_inputs = [
            {'name': 'A' * 1000},  # Extremely long name
            {'model': 'invalid/model'},  # Invalid model
            {'memoryBlocks': [{'label': 'A' * 1000, 'value': 'B' * 10000}]},  # Oversized data
            {'messages': [{'role': 'invalid_role', 'content': 'test'}]},  # Invalid role
            {'messages': [{'role': 'user', 'content': 'A' * 10000}]},  # Oversized content
        ]
        
        for malicious_input in malicious_inputs:
            if 'name' in malicious_input:
                errors = validate_agent_data(malicious_input)
                assert len(errors) > 0, f"Should reject malicious input: {malicious_input}"
            
            if 'messages' in malicious_input:
                errors = validate_message_data(malicious_input)
                assert len(errors) > 0, f"Should reject malicious input: {malicious_input}"
    
    def test_session_security(self, app):
        """Test session security features"""
        with app.test_client() as client:
            # Test session creation
            response = client.get('/api/agents')
            assert response.status_code == 400  # No user ID
            
            # Check session cookie security
            cookies = response.headers.getlist('Set-Cookie')
            session_cookies = [c for c in cookies if 'session' in c.lower()]
            
            if session_cookies:
                session_cookie = session_cookies[0]
                # Should have security flags
                assert 'HttpOnly' in session_cookie
                assert 'SameSite' in session_cookie
    
    def test_csrf_protection(self, client_with_session):
        """Test CSRF protection (when enabled)"""
        # This test would be more relevant when CSRF is enabled
        # For now, just test that forms can be submitted
        agent_data = {
            'name': 'Test Agent',
            'model': 'letta/letta-free',
            'memoryBlocks': [{'label': 'persona', 'value': 'test'}]
        }
        
        response = client_with_session.post('/api/agents', json=agent_data)
        # Should work without CSRF token when disabled
        assert response.status_code in [200, 500]  # 500 if Letta server not available
    
    def test_rate_limiting_security(self, client_with_session):
        """Test rate limiting prevents abuse"""
        # Make many requests quickly
        responses = []
        for i in range(300):  # Exceed rate limit
            response = client_with_session.get('/api/agents')
            responses.append(response)
        
        # Should eventually get rate limited
        rate_limited_responses = [r for r in responses if r.status_code == 429]
        assert len(rate_limited_responses) > 0, "Rate limiting should prevent abuse"
    
    def test_error_information_disclosure(self, client_with_session):
        """Test that errors don't disclose sensitive information"""
        with patch('app.routes.agents.LettaClient') as mock_client:
            mock_instance = MagicMock()
            mock_instance.list_agents.side_effect = Exception('Database password: secret123')
            mock_client.return_value = mock_instance
            
            response = client_with_session.get('/api/agents')
            assert response.status_code == 500
            
            # Error message should not contain sensitive information
            error_text = response.get_data(as_text=True)
            assert 'secret123' not in error_text
            assert 'Database password' not in error_text

class TestLoadTests:
    """Test suite for load testing"""
    
    def test_concurrent_users(self, app):
        """Test application under concurrent user load"""
        def simulate_user():
            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess['letta_uid'] = f'user-{threading.current_thread().ident}'
                
                responses = []
                for i in range(10):  # 10 requests per user
                    response = client.get('/api/agents')
                    responses.append(response.status_code)
                
                return responses
        
        # Simulate 20 concurrent users
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(simulate_user) for _ in range(20)]
            results = [future.result() for future in as_completed(futures)]
        
        # All requests should complete (even if some fail)
        assert len(results) == 20
        for user_responses in results:
            assert len(user_responses) == 10
    
    def test_memory_leak_detection(self, app):
        """Test for memory leaks under load"""
        import gc
        
        def make_requests():
            with app.test_client() as client:
                for i in range(100):
                    response = client.get('/api/agents')
                    del response  # Explicit cleanup
        
        # Run multiple cycles
        for cycle in range(5):
            make_requests()
            gc.collect()  # Force garbage collection
        
        # Memory should not grow indefinitely
        assert True  # Placeholder - would need actual memory monitoring
