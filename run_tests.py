#!/usr/bin/env python3
"""
Letta Chatbot - Test Runner Script
Copyright (C) 2025 Mark Hopkins

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"FAILED: {description}")
        print(f"Error: {result.stderr}")
        return False
    else:
        print(f"PASSED: {description}")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True

def run_unit_tests():
    """Run unit tests only"""
    return run_command(
        "python -m pytest tests/test_api_*.py tests/test_utils.py -v --tb=short",
        "Unit Tests"
    )

def run_integration_tests():
    """Run integration tests"""
    return run_command(
        "python -m pytest tests/test_integration.py -v --tb=short",
        "Integration Tests"
    )

def run_e2e_tests():
    """Run end-to-end tests"""
    return run_command(
        "python -m pytest tests/test_e2e.py -v --tb=short",
        "End-to-End Tests"
    )

def run_performance_tests():
    """Run performance tests"""
    return run_command(
        "python -m pytest tests/test_performance_security.py::TestPerformanceTests -v --tb=short",
        "Performance Tests"
    )

def run_security_tests():
    """Run security tests"""
    return run_command(
        "python -m pytest tests/test_performance_security.py::TestSecurityTests -v --tb=short",
        "Security Tests"
    )

def run_all_tests():
    """Run all tests"""
    return run_command(
        "python -m pytest tests/ -v --tb=short --cov=app --cov-report=html:htmlcov --cov-report=term-missing",
        "All Tests with Coverage"
    )

def run_quick_tests():
    """Run quick tests (unit tests only)"""
    return run_command(
        "python -m pytest tests/test_api_*.py tests/test_utils.py -v --tb=short -x",
        "Quick Tests (Unit Only)"
    )

def run_parallel_tests():
    """Run tests in parallel"""
    return run_command(
        "python -m pytest tests/ -v --tb=short -n auto",
        "Parallel Tests"
    )

def lint_code():
    """Run code linting"""
    return run_command(
        "python -m flake8 app/ tests/ --max-line-length=120 --ignore=E203,W503",
        "Code Linting"
    )

def format_code():
    """Format code"""
    return run_command(
        "python -m black app/ tests/ --line-length=120",
        "Code Formatting"
    )

def check_imports():
    """Check for unused imports"""
    return run_command(
        "python -m autoflake --check --recursive app/ tests/",
        "Import Check"
    )

def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description='Test runner for Letta Chatbot Flask application')
    parser.add_argument('--mode', choices=[
        'unit', 'integration', 'e2e', 'performance', 'security', 
        'all', 'quick', 'parallel', 'lint', 'format', 'imports'
    ], default='quick', help='Test mode to run')
    
    args = parser.parse_args()
    
    # Set up environment
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['LETTA_API_KEY'] = 'test-api-key'
    os.environ['LETTA_BASE_URL'] = 'http://test-letta-server:8283'
    
    print(f"Running tests in mode: {args.mode}")
    print(f"Working directory: {os.getcwd()}")
    
    success = True
    
    if args.mode == 'unit':
        success = run_unit_tests()
    elif args.mode == 'integration':
        success = run_integration_tests()
    elif args.mode == 'e2e':
        success = run_e2e_tests()
    elif args.mode == 'performance':
        success = run_performance_tests()
    elif args.mode == 'security':
        success = run_security_tests()
    elif args.mode == 'all':
        success = run_all_tests()
    elif args.mode == 'quick':
        success = run_quick_tests()
    elif args.mode == 'parallel':
        success = run_parallel_tests()
    elif args.mode == 'lint':
        success = lint_code()
    elif args.mode == 'format':
        success = format_code()
    elif args.mode == 'imports':
        success = check_imports()
    
    if success:
        print(f"\nSUCCESS: All {args.mode} tests passed!")
        sys.exit(0)
    else:
        print(f"\nFAILED: {args.mode} tests failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
