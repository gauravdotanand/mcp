"""
Utility functions for GUID-based operations.
This module provides helper functions for working with GUIDs across the system.
"""

from db import SessionLocal
from db.models import Agent, Tool, Task

def get_entity_by_guid(entity_type, guid):
    """
    Get an entity by its GUID.
    
    Args:
        entity_type (str): Type of entity ('agent', 'tool', 'task')
        guid (str): The GUID to look up
    
    Returns:
        The entity object or None if not found
    """
    session = SessionLocal()
    
    try:
        if entity_type.lower() == 'agent':
            return session.query(Agent).filter(Agent.guid == guid).first()
        elif entity_type.lower() == 'tool':
            return session.query(Tool).filter(Tool.guid == guid).first()
        elif entity_type.lower() == 'task':
            return session.query(Task).filter(Task.guid == guid).first()
        else:
            raise ValueError(f"Unknown entity type: {entity_type}")
    finally:
        session.close()

def get_entity_name_by_guid(entity_type, guid):
    """
    Get the name/description of an entity by its GUID.
    
    Args:
        entity_type (str): Type of entity ('agent', 'tool', 'task')
        guid (str): The GUID to look up
    
    Returns:
        The name/description or None if not found
    """
    entity = get_entity_by_guid(entity_type, guid)
    if entity:
        if entity_type.lower() == 'agent':
            return entity.name
        elif entity_type.lower() == 'tool':
            return entity.name
        elif entity_type.lower() == 'task':
            return entity.description
    return None

def get_all_guids():
    """
    Get all GUIDs from the system.
    
    Returns:
        dict: Dictionary with entity types as keys and lists of GUIDs as values
    """
    session = SessionLocal()
    
    try:
        return {
            'agents': [agent.guid for agent in session.query(Agent).all()],
            'tools': [tool.guid for tool in session.query(Tool).all()],
            'tasks': [task.guid for task in session.query(Task).all()]
        }
    finally:
        session.close()

def validate_guid(guid):
    """
    Validate if a string is a valid UUID/GUID format.
    
    Args:
        guid (str): The GUID to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    import uuid
    try:
        uuid.UUID(guid)
        return True
    except (ValueError, TypeError):
        return False

def format_guid_for_display(guid, max_length=8):
    """
    Format a GUID for display purposes.
    
    Args:
        guid (str): The GUID to format
        max_length (int): Maximum length of the displayed GUID
    
    Returns:
        str: Formatted GUID string
    """
    if not guid:
        return "N/A"
    
    if len(guid) <= max_length:
        return guid
    
    return f"{guid[:max_length]}..." 