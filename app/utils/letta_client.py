import requests
import json
from flask import current_app

class LettaClient:
    """Client for interacting with Letta API"""
    
    def __init__(self):
        self.base_url = current_app.config['LETTA_BASE_URL']
        self.api_key = current_app.config['LETTA_API_KEY']
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, method, endpoint, **kwargs):
        """Make HTTP request to Letta API"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Letta API error: {e}")
            raise
    
    def list_agents(self, tags=None, match_all_tags=True):
        """List agents with optional tag filtering"""
        params = {}
        if tags:
            params['tags'] = tags
            params['matchAllTags'] = match_all_tags
        
        return self._make_request('GET', '/agents', params=params)
    
    def create_agent(self, memory_blocks, model, embedding, tags=None):
        """Create a new agent"""
        data = {
            'memoryBlocks': memory_blocks,
            'model': model,
            'embedding': embedding
        }
        if tags:
            data['tags'] = tags
        
        return self._make_request('POST', '/agents', json=data)
    
    def get_agent(self, agent_id):
        """Get agent by ID"""
        return self._make_request('GET', f'/agents/{agent_id}')
    
    def update_agent(self, agent_id, **kwargs):
        """Update agent"""
        return self._make_request('PUT', f'/agents/{agent_id}', json=kwargs)
    
    def delete_agent(self, agent_id):
        """Delete agent"""
        return self._make_request('DELETE', f'/agents/{agent_id}')
    
    def list_messages(self, agent_id, limit=100):
        """List messages for an agent"""
        params = {'limit': limit}
        return self._make_request('GET', f'/agents/{agent_id}/messages', params=params)
    
    def send_message(self, agent_id, messages):
        """Send message to agent"""
        data = {'messages': messages}
        return self._make_request('POST', f'/agents/{agent_id}/messages', json=data)
    
    def get_archival_memory(self, agent_id):
        """Get agent's archival memory"""
        return self._make_request('GET', f'/agents/{agent_id}/archival_memory')
