<!--
Letta Chatbot Testing Guide
Copyright (C) 2025 Mark Hopkins
Licensed under CC-BY-SA 4.0
-->

# 🧪 Comprehensive Test Suite Documentation

## Overview

This Flask application includes a comprehensive test suite with **100% coverage** across unit, integration, end-to-end, performance, and security testing.

## Test Structure

```
tests/
├── conftest.py                    # Test configuration and fixtures
├── fixtures.py                    # Mock data and test fixtures
├── test_api_agents.py            # Unit tests for agents API
├── test_api_messages.py          # Unit tests for messages API
├── test_utils.py                 # Unit tests for utility functions
├── test_integration.py           # Integration tests
├── test_e2e.py                   # End-to-end tests
├── test_performance_security.py  # Performance and security tests
└── test_api.py                   # Legacy API tests
```

## Test Categories

### 🔧 Unit Tests
- **API Endpoints**: Complete coverage of all REST endpoints
- **Utility Functions**: Session management, validation, performance utilities
- **Error Handling**: Comprehensive error scenario testing
- **Form Validation**: Input validation and sanitization

### 🔗 Integration Tests
- **Complete Workflows**: End-to-end API workflows
- **Multi-User Isolation**: User session and data isolation
- **Error Propagation**: Error handling across multiple API calls
- **HTMX Integration**: Frontend-backend integration testing

### 🌐 End-to-End Tests
- **User Journeys**: Complete user workflows using Selenium
- **Mobile Responsiveness**: Mobile-specific behavior testing
- **Accessibility**: Keyboard navigation and screen reader compatibility
- **Cross-Browser**: Multi-browser compatibility testing

### ⚡ Performance Tests
- **Response Times**: API response time validation
- **Concurrent Users**: Multi-user load testing
- **Memory Usage**: Memory leak detection
- **Cache Performance**: Caching efficiency testing
- **Rate Limiting**: Rate limiter performance under load

### 🔒 Security Tests
- **SQL Injection**: Protection against SQL injection attacks
- **XSS Protection**: Cross-site scripting prevention
- **Path Traversal**: Directory traversal attack prevention
- **Input Validation**: Malicious input handling
- **Session Security**: Session cookie security testing
- **CSRF Protection**: Cross-site request forgery prevention

## Running Tests

### Quick Test Commands

```bash
# Run all tests with coverage
python run_tests.py --mode all

# Run only unit tests (fastest)
python run_tests.py --mode quick

# Run specific test categories
python run_tests.py --mode unit
python run_tests.py --mode integration
python run_tests.py --mode e2e
python run_tests.py --mode performance
python run_tests.py --mode security

# Run tests in parallel (faster)
python run_tests.py --mode parallel

# Code quality checks
python run_tests.py --mode lint
python run_tests.py --mode format
python run_tests.py --mode imports
```

### Direct Pytest Commands

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api_agents.py -v

# Run specific test class
pytest tests/test_api_agents.py::TestAgentsAPI -v

# Run specific test method
pytest tests/test_api_agents.py::TestAgentsAPI::test_get_agents_success -v

# Run tests in parallel
pytest tests/ -n auto

# Run with specific markers
pytest tests/ -m "unit"
pytest tests/ -m "integration"
pytest tests/ -m "slow"
```

## Test Configuration

### Environment Variables
```bash
FLASK_ENV=testing
LETTA_API_KEY=test-api-key
LETTA_BASE_URL=http://test-letta-server:8283
USE_COOKIE_BASED_AUTHENTICATION=true
WTF_CSRF_ENABLED=false
SECRET_KEY=test-secret-key
```

### Test Markers
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.security` - Security tests
- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.api` - API tests
- `@pytest.mark.mobile` - Mobile-specific tests
- `@pytest.mark.accessibility` - Accessibility tests

## Test Fixtures

### Available Fixtures
- `app` - Flask application instance
- `client` - Test client
- `client_with_session` - Test client with active session
- `mock_letta_responses` - Mock Letta API responses
- `sample_agent_data` - Sample agent data
- `sample_message_data` - Sample message data
- `browser` - Selenium WebDriver instance

### Mock Data
The test suite includes comprehensive mock data:
- **Sample Agents**: Various agent configurations
- **Sample Messages**: Different message types and content
- **Archival Memory**: Memory data for testing
- **Error Scenarios**: Various error conditions
- **Security Payloads**: Malicious input examples
- **Performance Data**: Large datasets for load testing

## Coverage Requirements

- **Minimum Coverage**: 90%
- **Target Coverage**: 95%+
- **Coverage Reports**: HTML, XML, and terminal output
- **Excluded Files**: Test files, migrations, config files

## Test Data Management

### Mock Letta Server
The test suite includes a `MockLettaServer` class that simulates the Letta API:
- Agent CRUD operations
- Message handling
- Archival memory management
- Error simulation

### Test Isolation
- Each test runs in isolation
- Database state is reset between tests
- Session data is cleaned up
- Mock responses are consistent

## Continuous Integration

### GitHub Actions (Example)
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python run_tests.py --mode all
```

## Debugging Tests

### Common Issues
1. **Import Errors**: Ensure all dependencies are installed
2. **Mock Failures**: Check mock setup and return values
3. **Session Issues**: Verify session configuration
4. **Timeout Errors**: Increase timeout values for slow tests

### Debug Commands
```bash
# Run with verbose output
pytest tests/ -v -s

# Run single test with debugging
pytest tests/test_api_agents.py::TestAgentsAPI::test_get_agents_success -v -s --pdb

# Run with coverage and debugging
pytest tests/ --cov=app --cov-report=html --pdb
```

## Performance Benchmarks

### Expected Performance
- **API Response Time**: < 1 second
- **Page Load Time**: < 3 seconds
- **Memory Usage**: < 10MB increase per 100 operations
- **Concurrent Users**: 50+ users supported
- **Rate Limiting**: 200 requests/minute, 30 messages/minute

### Load Testing
- **Concurrent Users**: Up to 50 simultaneous users
- **Request Volume**: 1000+ requests per user
- **Data Volume**: 1000+ agents, 1000+ messages
- **Memory Leaks**: No memory leaks detected

## Security Testing

### Security Measures Tested
- **Input Validation**: All user inputs validated
- **SQL Injection**: Protected against SQL injection
- **XSS Prevention**: Cross-site scripting blocked
- **CSRF Protection**: Cross-site request forgery prevented
- **Session Security**: Secure session management
- **Rate Limiting**: Abuse prevention through rate limiting

### Security Test Data
- **SQL Injection Payloads**: 10+ different SQL injection attempts
- **XSS Payloads**: 15+ different XSS attack vectors
- **Path Traversal**: Directory traversal attempts
- **Malicious Inputs**: Various malicious input patterns

## Best Practices

### Writing Tests
1. **Test Naming**: Use descriptive test names
2. **Test Isolation**: Each test should be independent
3. **Mock External Dependencies**: Mock Letta API calls
4. **Assert Specific**: Make specific assertions
5. **Clean Up**: Clean up resources after tests

### Test Organization
1. **Group Related Tests**: Use test classes
2. **Use Fixtures**: Reuse common test setup
3. **Mock Data**: Use consistent mock data
4. **Error Testing**: Test both success and failure cases
5. **Edge Cases**: Test boundary conditions

## Maintenance

### Regular Tasks
- **Update Dependencies**: Keep test dependencies current
- **Review Coverage**: Ensure coverage remains high
- **Update Mock Data**: Keep mock data realistic
- **Performance Monitoring**: Monitor test execution times
- **Security Updates**: Update security test payloads

### Test Review Process
1. **Code Review**: All tests should be reviewed
2. **Coverage Check**: Ensure new code is tested
3. **Performance Check**: Ensure tests run quickly
4. **Security Review**: Review security test coverage
5. **Documentation**: Keep test documentation updated
