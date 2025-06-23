#!/usr/bin/env python3
"""
Test script to verify the GUID-based system is working correctly.
"""

import time
from agents.manager import register_agent, update_agent_status
from tools.manager import register_tool, update_tool_status
from tasks.manager import create_task, update_task_status
from logs.logger import logger
from db import SessionLocal
from db.models import Agent, Tool, Task, Log, AgentStatus, ToolStatus, TaskStatus

def test_guid_system():
    """Test the GUID-based system"""
    print("Testing GUID-based system...")
    
    # Use timestamp to make names unique
    timestamp = int(time.time())
    
    # Test agent creation
    print("\n1. Testing agent creation...")
    agent_name = f"Test Agent {timestamp}"
    agent = register_agent(agent_name)
    print(f"Agent created: {agent.name} with GUID: {agent.guid}")
    
    # Test tool creation
    print("\n2. Testing tool creation...")
    tool_name = f"Test Tool {timestamp}"
    tool = register_tool(tool_name)
    print(f"Tool created: {tool.name} with GUID: {tool.guid}")
    
    # Test task creation
    print("\n3. Testing task creation...")
    task_description = f"Test Task {timestamp}"
    task = create_task(task_description, agent_id=agent.id, tool_id=tool.id)
    print(f"Task created: {task.description} with GUID: {task.guid}")
    
    # Test status updates
    print("\n4. Testing status updates...")
    update_agent_status(agent.id, AgentStatus.BUSY)
    update_tool_status(tool.id, ToolStatus.IN_USE)
    update_task_status(task.id, TaskStatus.RUNNING)
    
    # Test manual logging
    print("\n5. Testing manual logging...")
    logger.log_agent_event(agent.guid, "Agent is working hard", "INFO")
    logger.log_tool_event(tool.guid, "Tool is being used", "INFO")
    logger.log_task_event(task.guid, "Task is in progress", "INFO")
    logger.log_full_event(agent.guid, tool.guid, task.guid, "Full workflow test", "INFO")
    
    # Verify logs were created
    print("\n6. Verifying logs...")
    session = SessionLocal()
    logs = session.query(Log).order_by(Log.timestamp.desc()).limit(10).all()
    print(f"Found {len(logs)} log entries:")
    for log in logs:
        print(f"  - [{log.timestamp}] [{log.level}] {log.message}")
        if log.agent_guid:
            print(f"    Agent GUID: {log.agent_guid}")
        if log.tool_guid:
            print(f"    Tool GUID: {log.tool_guid}")
        if log.task_guid:
            print(f"    Task GUID: {log.task_guid}")
    
    session.close()
    
    print("\n✅ GUID system test completed successfully!")

if __name__ == "__main__":
    test_guid_system() 