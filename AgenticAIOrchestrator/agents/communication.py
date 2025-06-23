"""
Agent communication framework for multi-agent coordination.
Supports agent-to-agent messaging, shared context, and collaboration patterns.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import uuid
from db import SessionLocal
from db.models import Agent, Log
from logs.logger import logger

class AgentMessage:
    def __init__(self, sender_guid: str, recipient_guid: str, message_type: str, 
                 content: Any, metadata: Optional[Dict] = None):
        self.message_id = str(uuid.uuid4())
        self.sender_guid = sender_guid
        self.recipient_guid = recipient_guid
        self.message_type = message_type
        self.content = content
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()
        self.status = "sent"

class SharedContext:
    def __init__(self, context_id: str):
        self.context_id = context_id
        self.data = {}
        self.metadata = {}
        self.created_at = datetime.utcnow()
        self.last_updated = datetime.utcnow()
    
    def set_data(self, key: str, value: Any):
        self.data[key] = value
        self.last_updated = datetime.utcnow()
    
    def get_data(self, key: str, default=None):
        return self.data.get(key, default)
    
    def to_dict(self):
        return {
            "context_id": self.context_id,
            "data": self.data,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat()
        }

class AgentCommunicationManager:
    def __init__(self):
        self.message_queue = []
        self.shared_contexts = {}
        self.agent_registry = {}
    
    def register_agent(self, agent_guid: str, capabilities: List[str], 
                      communication_protocol: str = "http"):
        """Register an agent with its capabilities."""
        self.agent_registry[agent_guid] = {
            "capabilities": capabilities,
            "protocol": communication_protocol,
            "status": "available",
            "last_seen": datetime.utcnow()
        }
    
    def send_message(self, sender_guid: str, recipient_guid: str, 
                    message_type: str, content: Any, metadata: Optional[Dict] = None) -> AgentMessage:
        """Send a message between agents."""
        message = AgentMessage(sender_guid, recipient_guid, message_type, content, metadata)
        self.message_queue.append(message)
        
        # Log the message
        logger.log_agent_event(
            agent_guid=sender_guid,
            message=f"Sent {message_type} message to {recipient_guid}",
            level="INFO"
        )
        
        return message
    
    def broadcast_message(self, sender_guid: str, message_type: str, 
                         content: Any, metadata: Optional[Dict] = None) -> List[AgentMessage]:
        """Broadcast a message to all registered agents."""
        messages = []
        for agent_guid in self.agent_registry.keys():
            if agent_guid != sender_guid:
                message = self.send_message(sender_guid, agent_guid, message_type, content, metadata)
                messages.append(message)
        return messages
    
    def create_shared_context(self, context_id: str, initial_data: Optional[Dict] = None) -> SharedContext:
        """Create a shared context for agent collaboration."""
        context = SharedContext(context_id)
        if initial_data:
            context.data = initial_data
        self.shared_contexts[context_id] = context
        return context
    
    def update_shared_context(self, context_id: str, updates: Dict):
        """Update shared context data."""
        if context_id in self.shared_contexts:
            context = self.shared_contexts[context_id]
            for key, value in updates.items():
                context.set_data(key, value)
    
    def get_shared_context(self, context_id: str) -> Optional[SharedContext]:
        """Get a shared context by ID."""
        return self.shared_contexts.get(context_id)
    
    def find_agents_by_capability(self, capability: str) -> List[str]:
        """Find agents with specific capabilities."""
        matching_agents = []
        for agent_guid, agent_info in self.agent_registry.items():
            if capability in agent_info["capabilities"]:
                matching_agents.append(agent_guid)
        return matching_agents
    
    def route_task_to_agent(self, task_type: str, task_data: Dict) -> Optional[str]:
        """Route a task to the most appropriate agent."""
        # Find agents with matching capabilities
        capable_agents = self.find_agents_by_capability(task_type)
        
        if not capable_agents:
            return None
        
        # Simple routing: pick the first available agent
        # In a real system, you'd implement more sophisticated routing logic
        for agent_guid in capable_agents:
            if self.agent_registry[agent_guid]["status"] == "available":
                return agent_guid
        
        return None

# Global communication manager
agent_comm_manager = AgentCommunicationManager() 