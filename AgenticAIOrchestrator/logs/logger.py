from db import SessionLocal
from db.models import Log
from signals.events import log_created
import datetime

class Logger:
    def __init__(self):
        self.session = SessionLocal()
    
    def log(self, message, level="INFO", agent_guid=None, tool_guid=None, task_guid=None):
        """Create a log entry with optional GUID references"""
        log_entry = Log(
            message=message,
            level=level,
            agent_guid=agent_guid,
            tool_guid=tool_guid,
            task_guid=task_guid,
            timestamp=datetime.datetime.utcnow()
        )
        
        self.session.add(log_entry)
        self.session.commit()
        
        # Emit signal with log details
        log_created.send(
            log_id=log_entry.id,
            message=message,
            level=level,
            agent_guid=agent_guid,
            tool_guid=tool_guid,
            task_guid=task_guid,
            timestamp=log_entry.timestamp
        )
        
        return log_entry
    
    def log_agent_event(self, agent_guid, message, level="INFO"):
        """Log an agent-specific event"""
        return self.log(message, level, agent_guid=agent_guid)
    
    def log_tool_event(self, tool_guid, message, level="INFO"):
        """Log a tool-specific event"""
        return self.log(message, level, tool_guid=tool_guid)
    
    def log_task_event(self, task_guid, message, level="INFO"):
        """Log a task-specific event"""
        return self.log(message, level, task_guid=task_guid)
    
    def log_agent_tool_event(self, agent_guid, tool_guid, message, level="INFO"):
        """Log an event involving both agent and tool"""
        return self.log(message, level, agent_guid=agent_guid, tool_guid=tool_guid)
    
    def log_agent_task_event(self, agent_guid, task_guid, message, level="INFO"):
        """Log an event involving both agent and task"""
        return self.log(message, level, agent_guid=agent_guid, task_guid=task_guid)
    
    def log_task_tool_event(self, task_guid, tool_guid, message, level="INFO"):
        """Log an event involving both task and tool"""
        return self.log(message, level, task_guid=task_guid, tool_guid=tool_guid)
    
    def log_full_event(self, agent_guid, tool_guid, task_guid, message, level="INFO"):
        """Log an event involving agent, tool, and task"""
        return self.log(message, level, agent_guid=agent_guid, tool_guid=tool_guid, task_guid=task_guid)
    
    def close(self):
        """Close the database session"""
        self.session.close()

# Global logger instance
logger = Logger() 