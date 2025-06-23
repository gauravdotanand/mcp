"""
Signal handlers for automatic logging of events.
This module provides handlers that listen to various signals and automatically
log events to the database with appropriate GUID references.
"""

from signals.events import (
    agent_status_changed, 
    tool_status_changed, 
    task_status_changed,
    log_created
)
from logs.logger import logger

# Global handler functions
def handle_agent_status_change(sender, **kwargs):
    """Handle agent status change events"""
    agent_guid = kwargs.get('agent_guid')
    old_status = kwargs.get('old_status')
    new_status = kwargs.get('new_status')
    
    if agent_guid:
        logger.log_agent_event(
            agent_guid=agent_guid,
            message=f"Agent status changed from {old_status.value} to {new_status.value}",
            level="INFO"
        )

def handle_tool_status_change(sender, **kwargs):
    """Handle tool status change events"""
    tool_guid = kwargs.get('tool_guid')
    old_status = kwargs.get('old_status')
    new_status = kwargs.get('new_status')
    
    if tool_guid:
        logger.log_tool_event(
            tool_guid=tool_guid,
            message=f"Tool status changed from {old_status.value} to {new_status.value}",
            level="INFO"
        )

def handle_task_status_change(sender, **kwargs):
    """Handle task status change events"""
    task_guid = kwargs.get('task_guid')
    old_status = kwargs.get('old_status')
    new_status = kwargs.get('new_status')
    
    if task_guid:
        logger.log_task_event(
            task_guid=task_guid,
            message=f"Task status changed from {old_status.value} to {new_status.value}",
            level="INFO"
        )

def handle_log_created(sender, **kwargs):
    """Handle log creation events (for debugging/monitoring)"""
    # This handler can be used for additional processing when logs are created
    # For example, sending notifications, updating dashboards, etc.
    pass

def setup_signal_handlers():
    """Setup all signal handlers for automatic logging"""
    agent_status_changed.connect(handle_agent_status_change)
    tool_status_changed.connect(handle_tool_status_change)
    task_status_changed.connect(handle_task_status_change)
    log_created.connect(handle_log_created)

def cleanup_signal_handlers():
    """Cleanup signal handlers"""
    agent_status_changed.disconnect(handle_agent_status_change)
    tool_status_changed.disconnect(handle_tool_status_change)
    task_status_changed.disconnect(handle_task_status_change)
    log_created.disconnect(handle_log_created) 