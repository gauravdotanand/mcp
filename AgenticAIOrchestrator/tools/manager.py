from db import SessionLocal
from db.models import Tool, ToolStatus
from signals.events import tool_status_changed
from logs.logger import logger

def register_tool(name):
    session = SessionLocal()
    tool = Tool(name=name)
    session.add(tool)
    session.commit()
    
    # Log the tool registration
    logger.log_tool_event(
        tool_guid=tool.guid,
        message=f"Tool '{name}' registered successfully",
        level="INFO"
    )
    
    session.close()
    return tool

def update_tool_status(tool_id, new_status):
    session = SessionLocal()
    tool = session.query(Tool).filter(Tool.id == tool_id).first()
    if tool:
        old_status = tool.status
        tool.status = new_status
        session.commit()
        
        # Log the status change
        logger.log_tool_event(
            tool_guid=tool.guid,
            message=f"Tool '{tool.name}' status changed from {old_status.value} to {new_status.value}",
            level="INFO"
        )
        
        # Emit signal with GUID
        tool_status_changed.send(
            tool_id=tool_id,
            tool_guid=tool.guid,
            old_status=old_status,
            new_status=new_status
        )
    session.close()

def get_tool_by_guid(tool_guid):
    """Get tool by GUID"""
    session = SessionLocal()
    tool = session.query(Tool).filter(Tool.guid == tool_guid).first()
    session.close()
    return tool

def get_all_tools():
    """Get all tools with their GUIDs"""
    session = SessionLocal()
    tools = session.query(Tool).all()
    session.close()
    return tools 