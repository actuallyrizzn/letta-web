# Contributing to Letta Chatbot

<!--
Letta Chatbot Contributing Guide
Copyright (C) 2025 Letta Chatbot Contributors
Licensed under CC-BY-SA 4.0
-->

Thank you for your interest in contributing to Letta Chatbot! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by our commitment to:

- **Be respectful**: Treat all contributors with respect and kindness
- **Be constructive**: Provide helpful feedback and criticism
- **Be collaborative**: Work together to improve the project
- **Be inclusive**: Welcome contributors of all backgrounds and skill levels

We will not tolerate harassment, discrimination, or toxic behavior of any kind.

## Getting Started

### Prerequisites

- **Python 3.8+** installed
- **Git** for version control
- **Basic Flask knowledge** (or willingness to learn)
- **Understanding of AI agents** (helpful but not required)

### Find Something to Work On

1. Check the [issue tracker](https://github.com/your-org/letta-chatbot-example/issues)
2. Look for issues labeled `good first issue` or `help wanted`
3. Read existing discussions and pull requests
4. Join our community channels (Discord, Discussions)

### Before Starting Work

1. **Comment on the issue** you want to work on
2. **Wait for approval** from a maintainer
3. **Fork the repository** and create a branch
4. **Communicate regularly** about your progress

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/letta-chatbot-example.git
cd letta-chatbot-example

# Add upstream remote
git remote add upstream https://github.com/original-org/letta-chatbot-example.git
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install all dependencies including development tools
pip install -r requirements.txt

# Install additional development tools
pip install pytest pytest-cov black flake8 mypy
```

### 4. Configure Environment

```bash
cp env.example .env
# Edit .env with your test Letta server details
```

### 5. Run Tests

```bash
# Run all tests
python run_tests.py --mode all

# Run quick tests
python run_tests.py --mode quick
```

### 6. Start Development Server

```bash
python wsgi.py
```

Visit `http://localhost:5000` to see your local instance.

## How to Contribute

### Types of Contributions

We welcome many types of contributions:

- **Bug fixes**: Fix issues in the codebase
- **New features**: Add new functionality
- **Documentation**: Improve or add documentation
- **Tests**: Add or improve test coverage
- **Performance**: Optimize existing code
- **UI/UX**: Improve the user interface
- **Examples**: Add examples or tutorials

### Contribution Workflow

1. **Create a branch** from `main`
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, readable code
   - Follow coding standards
   - Add tests for new functionality
   - Update documentation

3. **Test your changes**
   ```bash
   python run_tests.py --mode all
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: description of your changes"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill out the PR template

## Coding Standards

### Python Code Style

We follow **PEP 8** with some modifications:

- **Line length**: 120 characters maximum
- **Imports**: Organized using `isort`
- **Formatting**: Automated with `black`
- **Type hints**: Encouraged for public APIs

### Formatting Code

```bash
# Format all Python files
black app/ tests/ --line-length=120

# Check formatting
black --check app/ tests/ --line-length=120
```

### Linting

```bash
# Run flake8
flake8 app/ tests/ --max-line-length=120 --ignore=E203,W503

# Run mypy for type checking
mypy app/ --ignore-missing-imports
```

### Code Organization

```python
"""
Letta Chatbot - Module Name
Copyright (C) 2025 Letta Chatbot Contributors

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

# Standard library imports
import os
import sys

# Third-party imports
from flask import Flask, request

# Local imports
from app.utils import helper_function


class MyClass:
    """Docstring describing the class."""
    
    def public_method(self, param: str) -> str:
        """
        Docstring describing the method.
        
        Args:
            param: Description of parameter
            
        Returns:
            Description of return value
        """
        return self._private_method(param)
    
    def _private_method(self, param: str) -> str:
        """Private methods prefixed with underscore."""
        return param.upper()
```

### Naming Conventions

- **Variables**: `snake_case`
- **Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private members**: `_leading_underscore`

### Documentation Strings

All public functions, classes, and modules must have docstrings:

```python
def process_message(message: str, agent_id: str) -> dict:
    """
    Process a user message and generate agent response.
    
    This function handles the complete message processing pipeline including
    validation, context loading, agent invocation, and response formatting.
    
    Args:
        message: The user's message text
        agent_id: The ID of the agent to process the message
        
    Returns:
        A dictionary containing the processed message and response
        
    Raises:
        ValueError: If message is empty or agent_id is invalid
        LettaAPIError: If the Letta API call fails
        
    Example:
        >>> process_message("Hello!", "agent-123")
        {'user_message': 'Hello!', 'agent_response': 'Hi there!'}
    """
    pass
```

## Testing Guidelines

### Test Structure

```
tests/
├── conftest.py           # Shared fixtures
├── fixtures.py           # Test data
├── test_api_agents.py    # Agent API tests
├── test_api_messages.py  # Message API tests
├── test_utils.py         # Utility function tests
├── test_integration.py   # Integration tests
└── test_e2e.py          # End-to-end tests
```

### Writing Tests

```python
import pytest
from app import create_app

@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app('testing')
    return app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

def test_create_agent(client):
    """Test agent creation endpoint."""
    # Arrange
    data = {'name': 'Test Agent'}
    
    # Act
    response = client.post('/api/agents', json=data)
    
    # Assert
    assert response.status_code == 200
    assert 'id' in response.json
    assert response.json['name'] == 'Test Agent'
```

### Test Coverage

- Aim for **80%+ code coverage**
- Test all public APIs
- Test error conditions
- Test edge cases

```bash
# Run tests with coverage
pytest --cov=app --cov-report=html --cov-report=term-missing

# View HTML report
open htmlcov/index.html
```

### Integration Tests

Integration tests should test component interactions:

```python
def test_full_conversation_flow(client):
    """Test complete conversation flow."""
    # Create agent
    agent_response = client.post('/api/agents')
    agent_id = agent_response.json['id']
    
    # Send message
    message_response = client.post(
        f'/api/agents/{agent_id}/messages',
        json={'message': 'Hello!', 'role': 'user'}
    )
    
    # Verify response
    assert message_response.status_code == 200
    messages = message_response.json['messages']
    assert len(messages) >= 2  # User message + agent response
```

## Documentation

### Documentation Standards

- **Clear and concise**: Explain concepts clearly
- **Examples**: Provide code examples
- **Up-to-date**: Keep docs synchronized with code
- **Accessible**: Write for all skill levels

### Documentation Types

1. **Code Documentation**: Docstrings in code
2. **API Documentation**: `docs/API.md`
3. **User Documentation**: `README.md`
4. **Developer Documentation**: This file
5. **Deployment Documentation**: `docs/DEPLOYMENT.md`

### Writing Documentation

```markdown
# Feature Name

Brief description of the feature.

## Overview

Detailed explanation of what the feature does and why it's useful.

## Usage

### Basic Example

\`\`\`python
# Code example
result = function_call(parameters)
\`\`\`

### Advanced Example

\`\`\`python
# More complex example
\`\`\`

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `option_name` | `str` | `"default"` | What it does |

## API Reference

See [API.md](API.md#endpoint-name) for full API details.
```

### Documentation License

All documentation files must include the CC-BY-SA license header:

```markdown
<!--
Letta Chatbot Documentation Title
Copyright (C) 2025 Letta Chatbot Contributors
Licensed under CC-BY-SA 4.0
-->
```

## Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] Branch is up to date with main
- [ ] No merge conflicts

### PR Title Format

```
[Type] Brief description of changes

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- style: Code style changes (formatting, etc.)
- refactor: Code refactoring
- test: Adding or updating tests
- chore: Maintenance tasks
```

Examples:
- `feat: Add archival memory search endpoint`
- `fix: Resolve session timeout issue`
- `docs: Update API documentation for messages endpoint`

### PR Description Template

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Fixes #123
Related to #456

## Changes Made
- Changed X to Y
- Added Z functionality
- Refactored W component

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots (if applicable)
[Add screenshots here]

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No new warnings
```

### Review Process

1. **Automated checks** run on your PR
2. **Maintainer review** provides feedback
3. **Address feedback** and push updates
4. **Approval** from at least one maintainer
5. **Merge** into main branch

### After Merge

- Delete your feature branch
- Update your local repository
- Celebrate your contribution! 🎉

## Issue Guidelines

### Creating Issues

Use issue templates when available:

#### Bug Report

```markdown
**Describe the bug**
Clear description of the bug.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What should happen.

**Actual behavior**
What actually happens.

**Screenshots**
If applicable.

**Environment**
- OS: [e.g. Ubuntu 20.04]
- Python version: [e.g. 3.11]
- Flask version: [e.g. 3.0.0]

**Additional context**
Any other relevant information.
```

#### Feature Request

```markdown
**Is your feature request related to a problem?**
Description of the problem.

**Describe the solution you'd like**
What you want to happen.

**Describe alternatives you've considered**
Other solutions you've thought about.

**Additional context**
Any other relevant information.
```

### Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Documentation improvements
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention needed
- `question`: Further information requested
- `wontfix`: This will not be worked on

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and community discussion
- **Discord**: Real-time chat and support
- **Email**: maintainers@example.com

### Getting Help

- Check existing issues and documentation
- Search closed issues and PRs
- Ask in Discussions or Discord
- Be patient and respectful

### Recognition

Contributors are recognized in:
- `README.md` contributors section
- Release notes
- Project credits

## Development Tips

### Useful Commands

```bash
# Update from upstream
git fetch upstream
git merge upstream/main

# Run specific tests
pytest tests/test_api_agents.py -v

# Format and lint
black app/ tests/
flake8 app/ tests/

# Check types
mypy app/

# Profile performance
python -m cProfile wsgi.py

# Generate coverage report
pytest --cov=app --cov-report=html
```

### Debugging

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use Flask debugging
app.config['DEBUG'] = True  # Development only!

# Logging
current_app.logger.info('Debug message')
current_app.logger.error('Error message')
```

### Common Gotchas

- **Session handling**: Remember to test with and without cookies
- **Letta API**: Mock Letta API calls in tests
- **Rate limiting**: Disable in tests or use separate limits
- **Caching**: Clear cache between tests

## License

By contributing to Letta Chatbot, you agree that your contributions will be licensed under:

- **Code**: GNU Affero General Public License v3.0
- **Documentation**: Creative Commons Attribution-ShareAlike 4.0

All code files must include the AGPLv3 license header.
All documentation files must include the CC-BY-SA license header.

## Questions?

If you have questions about contributing, please:

1. Check this document
2. Search existing issues
3. Ask in GitHub Discussions
4. Join our Discord community

Thank you for contributing to Letta Chatbot! 🙏

---

**Happy coding! Let's build something amazing together.** ✨

