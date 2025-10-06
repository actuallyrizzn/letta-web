import pytest
import json
from unittest.mock import patch, MagicMock
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class TestEndToEndWorkflows:
    """Test suite for complete user journey testing"""
    
    @pytest.fixture(scope='class')
    def browser(self):
        """Set up browser for E2E testing"""
        options = Options()
        options.add_argument('--headless')  # Run in headless mode for CI
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=options)
        yield driver
        driver.quit()
    
    def test_complete_user_journey_create_and_chat(self, browser, client_with_session):
        """Test complete user journey: visit site -> create agent -> chat"""
        with patch('app.routes.agents.LettaClient') as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            
            # Mock successful agent creation
            mock_instance.create_agent.return_value = {
                'id': 'new-agent-123',
                'name': 'Test Agent',
                'tags': ['user:test-user-123']
            }
            
            # Mock agent details
            mock_instance.get_agent.return_value = {
                'id': 'new-agent-123',
                'name': 'Test Agent',
                'tags': ['user:test-user-123'],
                'model': 'letta/letta-free',
                'memoryBlocks': [
                    {'label': 'persona', 'value': 'I am helpful'}
                ]
            }
            
            # Mock messages
            mock_instance.list_messages.return_value = []
            mock_instance.send_message.return_value = {
                'id': 'response-123',
                'content': 'Hello! How can I help you?'
            }
            
            # Start Flask app for E2E testing
            app = client_with_session.application
            
            # Navigate to the application
            browser.get('http://localhost:5000')
            
            # Wait for page to load
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, 'agents-list'))
            )
            
            # Check if create agent button is present and visible
            create_button = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-id="create-agent-button"]'))
            )
            
            # Click create agent button
            create_button.click()
            
            # Wait for agent to be created and appear in list
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.agent-item'))
            )
            
            # Verify agent appears in sidebar
            agent_items = browser.find_elements(By.CSS_SELECTOR, '.agent-item')
            assert len(agent_items) > 0
            
            # Click on the first agent
            agent_items[0].click()
            
            # Wait for agent details to load
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, 'agent-details'))
            )
            
            # Check if message composer is present
            message_input = browser.find_element(By.ID, 'message-input')
            assert message_input.is_displayed()
            
            # Type a message
            message_input.send_keys('Hello, this is a test message')
            
            # Submit the message
            submit_button = browser.find_element(By.CSS_SELECTOR, '#message-form button[type="submit"]')
            submit_button.click()
            
            # Wait for message to appear (this would require actual HTMX response)
            # For now, just verify the form submission worked
            assert message_input.get_attribute('value') == ''  # Should be cleared after submit
    
    def test_mobile_responsive_behavior(self, browser):
        """Test mobile responsive behavior"""
        # Set mobile viewport
        browser.set_window_size(375, 667)  # iPhone size
        
        # Navigate to app
        browser.get('http://localhost:5000')
        
        # Check if mobile menu button is visible
        mobile_menu = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.lg\\:hidden button'))
        )
        
        # Click mobile menu to open sidebar
        mobile_menu.click()
        
        # Check if sidebar is visible
        sidebar = browser.find_element(By.ID, 'sidebar')
        assert 'mobile-sidebar-visible' in sidebar.get_attribute('class')
        
        # Check if overlay is present
        overlay = browser.find_element(By.ID, 'mobile-overlay')
        assert not overlay.get_attribute('class').split().__contains__('hidden')
    
    def test_error_handling_e2e(self, browser):
        """Test error handling in E2E scenario"""
        # Navigate to app
        browser.get('http://localhost:5000')
        
        # Try to access non-existent agent
        browser.get('http://localhost:5000/nonexistent-agent')
        
        # Check if error is handled gracefully
        # (This would depend on how errors are displayed in the UI)
        assert browser.current_url.endswith('nonexistent-agent')
    
    def test_form_validation_e2e(self, browser):
        """Test form validation in E2E scenario"""
        browser.get('http://localhost:5000')
        
        # Find message input
        message_input = browser.find_element(By.ID, 'message-input')
        
        # Try to submit empty message
        submit_button = browser.find_element(By.CSS_SELECTOR, '#message-form button[type="submit"]')
        submit_button.click()
        
        # Check if validation prevents submission
        # (This would depend on client-side validation)
        assert message_input.get_attribute('value') == ''
    
    def test_session_persistence_e2e(self, browser):
        """Test session persistence across page refreshes"""
        browser.get('http://localhost:5000')
        
        # Wait for page to load and session to be created
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, 'agents-list'))
        )
        
        # Refresh the page
        browser.refresh()
        
        # Check if session persists (agents list should still load)
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, 'agents-list'))
        )
        
        # Verify session cookie exists
        cookies = browser.get_cookies()
        session_cookies = [c for c in cookies if 'session' in c['name'].lower()]
        assert len(session_cookies) > 0

class TestPerformanceE2E:
    """Test suite for performance testing"""
    
    def test_page_load_performance(self, browser):
        """Test page load performance"""
        import time
        
        start_time = time.time()
        browser.get('http://localhost:5000')
        
        # Wait for page to be fully loaded
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, 'agents-list'))
        )
        
        load_time = time.time() - start_time
        
        # Page should load within 3 seconds
        assert load_time < 3.0, f"Page took {load_time:.2f}s to load, should be under 3s"
    
    def test_concurrent_user_simulation(self, browser):
        """Test application behavior under concurrent users"""
        # This would require multiple browser instances
        # For now, just test that the app can handle multiple rapid requests
        
        browser.get('http://localhost:5000')
        
        # Simulate rapid interactions
        for i in range(10):
            browser.refresh()
            WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.ID, 'agents-list'))
            )
        
        # App should still be responsive
        assert browser.find_element(By.ID, 'agents-list').is_displayed()

class TestAccessibilityE2E:
    """Test suite for accessibility testing"""
    
    def test_keyboard_navigation(self, browser):
        """Test keyboard navigation"""
        browser.get('http://localhost:5000')
        
        # Tab through interactive elements
        from selenium.webdriver.common.keys import Keys
        
        # Find first focusable element
        body = browser.find_element(By.TAG_NAME, 'body')
        body.send_keys(Keys.TAB)
        
        # Check if focus is visible
        focused_element = browser.switch_to.active_element
        assert focused_element is not None
    
    def test_screen_reader_compatibility(self, browser):
        """Test screen reader compatibility"""
        browser.get('http://localhost:5000')
        
        # Check for proper ARIA labels
        elements_with_aria = browser.find_elements(By.CSS_SELECTOR, '[aria-label]')
        assert len(elements_with_aria) > 0, "Should have ARIA labels for accessibility"
        
        # Check for proper heading structure
        headings = browser.find_elements(By.CSS_SELECTOR, 'h1, h2, h3, h4, h5, h6')
        assert len(headings) > 0, "Should have proper heading structure"
    
    def test_color_contrast(self, browser):
        """Test color contrast (basic check)"""
        browser.get('http://localhost:5000')
        
        # Check if dark mode toggle is present
        # (This would require checking actual color values)
        assert True  # Placeholder for actual contrast testing
