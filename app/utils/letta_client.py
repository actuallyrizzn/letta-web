"""
Letta Chatbot - Letta API Client
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

from flask import current_app
from letta_client import Letta, MessageCreate

class LettaClient:
    """Wrapper client for interacting with Letta API using official SDK"""
    
    def __init__(self):
        """Initialize the Letta client with configuration from Flask app"""
        self.base_url = current_app.config['LETTA_BASE_URL']
        self.api_key = current_app.config['LETTA_API_KEY']
        
        # Initialize the official Letta SDK client
        self.client = Letta(
            base_url=self.base_url,
            token=self.api_key
        )
    
    def list_agents(self, tags=None, match_all_tags=True):
        """List agents with optional tag filtering"""
        try:
            # The SDK returns an iterable/list of agents
            agents = self.client.agents.list()
            
            # Convert to list if not already
            agents_list = list(agents) if not isinstance(agents, list) else agents
            
            # Apply tag filtering if specified
            if tags:
                filtered_agents = []
                for agent in agents_list:
                    agent_tags = agent.get('tags', []) if isinstance(agent, dict) else getattr(agent, 'tags', [])
                    if match_all_tags:
                        if all(tag in agent_tags for tag in tags):
                            filtered_agents.append(agent)
                    else:
                        if any(tag in agent_tags for tag in tags):
                            filtered_agents.append(agent)
                agents_list = filtered_agents
            
            # Convert SDK objects to dicts for compatibility
            return [self._agent_to_dict(agent) for agent in agents_list]
        except Exception as e:
            current_app.logger.error(f"Letta API error in list_agents: {e}")
            raise
    
    def create_agent(self, memory_blocks, model, embedding, tags=None):
        """Create a new agent"""
        try:
            # Prepare the create request
            create_params = {
                'memory_blocks': memory_blocks,
                'llm_config': {'model': model},
                'embedding_config': {'embedding': embedding}
            }
            
            if tags:
                create_params['tags'] = tags
            
            agent = self.client.agents.create(**create_params)
            return self._agent_to_dict(agent)
        except Exception as e:
            current_app.logger.error(f"Letta API error in create_agent: {e}")
            raise
    
    def get_agent(self, agent_id):
        """Get agent by ID"""
        try:
            agent = self.client.agents.retrieve(agent_id=agent_id)
            return self._agent_to_dict(agent)
        except Exception as e:
            current_app.logger.error(f"Letta API error in get_agent: {e}")
            raise
    
    def update_agent(self, agent_id, **kwargs):
        """Update agent"""
        try:
            # The SDK's update method signature may vary
            agent = self.client.agents.update(agent_id=agent_id, **kwargs)
            return self._agent_to_dict(agent)
        except Exception as e:
            current_app.logger.error(f"Letta API error in update_agent: {e}")
            raise
    
    def delete_agent(self, agent_id):
        """Delete agent"""
        try:
            result = self.client.agents.delete(agent_id=agent_id)
            return result if isinstance(result, dict) else {}
        except Exception as e:
            current_app.logger.error(f"Letta API error in delete_agent: {e}")
            raise
    
    def list_messages(self, agent_id, limit=100):
        """List messages for an agent"""
        try:
            messages = self.client.agents.messages.list(agent_id=agent_id, limit=limit)
            
            # Convert to list if not already
            messages_list = list(messages) if not isinstance(messages, list) else messages
            
            # Convert SDK objects to dicts for compatibility
            return [self._message_to_dict(msg) for msg in messages_list]
        except Exception as e:
            current_app.logger.error(f"Letta API error in list_messages: {e}")
            raise
    
    def send_message(self, agent_id, messages):
        """Send message to agent"""
        try:
            # Convert messages to MessageCreate objects
            message_objects = []
            for msg in messages:
                if isinstance(msg, dict):
                    message_objects.append(MessageCreate(
                        role=msg.get('role', 'user'),
                        content=msg.get('content', '')
                    ))
                else:
                    # Already a MessageCreate object
                    message_objects.append(msg)
            
            response = self.client.agents.messages.create(
                agent_id=agent_id,
                messages=message_objects
            )
            
            # The response might be a complex object, convert to dict
            if isinstance(response, dict):
                return response
            else:
                return self._response_to_dict(response)
        except Exception as e:
            current_app.logger.error(f"Letta API error in send_message: {e}")
            raise
    
    def get_archival_memory(self, agent_id, limit=50, after=None, before=None):
        """Get agent's archival memory (passages)"""
        try:
            params = {'limit': limit}
            if after:
                params['after'] = after
            if before:
                params['before'] = before
            
            passages = self.client.agents.passages.list(agent_id=agent_id, **params)
            
            # Convert to list if not already
            passages_list = list(passages) if not isinstance(passages, list) else passages
            
            # Convert SDK objects to dicts for compatibility
            return [self._passage_to_dict(passage) for passage in passages_list]
        except Exception as e:
            current_app.logger.error(f"Letta API error in get_archival_memory: {e}")
            raise
    
    # Helper methods to convert SDK objects to dicts
    def _agent_to_dict(self, agent):
        """Convert agent object to dict"""
        if isinstance(agent, dict):
            return agent
        
        # Convert SDK object attributes to dict
        agent_dict = {}
        for attr in ['id', 'name', 'created_at', 'updated_at', 'tags', 'memory_blocks', 'llm_config', 'embedding_config', 'system_prompt']:
            if hasattr(agent, attr):
                agent_dict[attr] = getattr(agent, attr)
        
        return agent_dict
    
    def _message_to_dict(self, message):
        """Convert message object to dict"""
        if isinstance(message, dict):
            return message
        
        # Convert SDK object attributes to dict
        msg_dict = {}
        for attr in ['id', 'role', 'content', 'created_at', 'agent_id', 'type']:
            if hasattr(message, attr):
                msg_dict[attr] = getattr(message, attr)
        
        return msg_dict
    
    def _passage_to_dict(self, passage):
        """Convert passage object to dict"""
        if isinstance(passage, dict):
            return passage
        
        # Convert SDK object attributes to dict
        passage_dict = {}
        for attr in ['id', 'text', 'created_at', 'updated_at', 'tags', 'embedding', 'agent_id']:
            if hasattr(passage, attr):
                passage_dict[attr] = getattr(passage, attr)
        
        return passage_dict
    
    def _response_to_dict(self, response):
        """Convert response object to dict"""
        if isinstance(response, dict):
            return response
        
        # Try to convert to dict using common attributes
        response_dict = {}
        for attr in dir(response):
            if not attr.startswith('_'):
                try:
                    value = getattr(response, attr)
                    if not callable(value):
                        response_dict[attr] = value
                except:
                    pass
        
        return response_dict
