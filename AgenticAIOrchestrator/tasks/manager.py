from db import SessionLocal
from db.models import Task, TaskStatus, Agent, Tool
from signals.events import task_status_changed
from logs.logger import logger

def create_task(description, agent_id=None, tool_id=None):
    session = SessionLocal()
    task = Task(description=description, agent_id=agent_id, tool_id=tool_id)
    session.add(task)
    session.commit()
    
    # Get agent and tool GUIDs for logging
    agent_guid = None
    tool_guid = None
    if agent_id:
        agent = session.query(Agent).filter(Agent.id == agent_id).first()
        agent_guid = agent.guid if agent else None
    if tool_id:
        tool = session.query(Tool).filter(Tool.id == tool_id).first()
        tool_guid = tool.guid if tool else None
    
    # Log the task creation
    if agent_guid and tool_guid:
        logger.log_full_event(
            agent_guid=agent_guid,
            tool_guid=tool_guid,
            task_guid=task.guid,
            message=f"Task created: {description}",
            level="INFO"
        )
    elif agent_guid:
        logger.log_agent_task_event(
            agent_guid=agent_guid,
            task_guid=task.guid,
            message=f"Task created: {description}",
            level="INFO"
        )
    elif tool_guid:
        logger.log_task_tool_event(
            task_guid=task.guid,
            tool_guid=tool_guid,
            message=f"Task created: {description}",
            level="INFO"
        )
    else:
        logger.log_task_event(
            task_guid=task.guid,
            message=f"Task created: {description}",
            level="INFO"
        )
    
    session.close()
    return task

def update_task_status(task_id, new_status):
    session = SessionLocal()
    task = session.query(Task).filter(Task.id == task_id).first()
    if task:
        old_status = task.status
        task.status = new_status
        session.commit()
        
        # Get agent and tool GUIDs for logging
        agent_guid = None
        tool_guid = None
        if task.agent:
            agent_guid = task.agent.guid
        if task.tool:
            tool_guid = task.tool.guid
        
        # Log the status change
        if agent_guid and tool_guid:
            logger.log_full_event(
                agent_guid=agent_guid,
                tool_guid=tool_guid,
                task_guid=task.guid,
                message=f"Task status changed from {old_status.value} to {new_status.value}",
                level="INFO"
            )
        elif agent_guid:
            logger.log_agent_task_event(
                agent_guid=agent_guid,
                task_guid=task.guid,
                message=f"Task status changed from {old_status.value} to {new_status.value}",
                level="INFO"
            )
        elif tool_guid:
            logger.log_task_tool_event(
                task_guid=task.guid,
                tool_guid=tool_guid,
                message=f"Task status changed from {old_status.value} to {new_status.value}",
                level="INFO"
            )
        else:
            logger.log_task_event(
                task_guid=task.guid,
                message=f"Task status changed from {old_status.value} to {new_status.value}",
                level="INFO"
            )
        
        # Emit signal with GUID
        task_status_changed.send(
            task_id=task_id,
            task_guid=task.guid,
            old_status=old_status,
            new_status=new_status
        )
    session.close()

def get_task_by_guid(task_guid):
    """Get task by GUID"""
    session = SessionLocal()
    task = session.query(Task).filter(Task.guid == task_guid).first()
    session.close()
    return task

def get_all_tasks():
    """Get all tasks with their GUIDs"""
    session = SessionLocal()
    tasks = session.query(Task).all()
    session.close()
    return tasks 