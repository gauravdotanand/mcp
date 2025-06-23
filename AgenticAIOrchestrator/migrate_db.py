#!/usr/bin/env python3
"""
Database migration script to add GUID columns to existing tables.
This script will:
1. Add GUID columns to agents, tools, and tasks tables
2. Generate new GUIDs for existing records
3. Add GUID reference columns to logs table
"""

import uuid
from sqlalchemy import create_engine, text, inspect
from db import SessionLocal
from db.models import Base, Agent, Tool, Task, Log

def migrate_database():
    """Perform database migration to add GUID support"""
    print("Starting database migration...")
    
    # Create engine and get connection
    engine = create_engine('sqlite:///agentic_ai_orchestrator.db')
    
    with engine.connect() as conn:
        # Check if GUID columns already exist
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if 'agents' in tables:
            agent_columns = [col['name'] for col in inspector.get_columns('agents')]
            if 'guid' not in agent_columns:
                print("Adding GUID column to agents table...")
                conn.execute(text("ALTER TABLE agents ADD COLUMN guid TEXT"))
                conn.commit()
                
                # Generate GUIDs for existing agents
                session = SessionLocal()
                agents = session.query(Agent).all()
                for agent in agents:
                    agent.guid = str(uuid.uuid4())
                session.commit()
                session.close()
                print(f"Generated GUIDs for {len(agents)} agents")
        
        if 'tools' in tables:
            tool_columns = [col['name'] for col in inspector.get_columns('tools')]
            if 'guid' not in tool_columns:
                print("Adding GUID column to tools table...")
                conn.execute(text("ALTER TABLE tools ADD COLUMN guid TEXT"))
                conn.commit()
                
                # Generate GUIDs for existing tools
                session = SessionLocal()
                tools = session.query(Tool).all()
                for tool in tools:
                    tool.guid = str(uuid.uuid4())
                session.commit()
                session.close()
                print(f"Generated GUIDs for {len(tools)} tools")
        
        if 'tasks' in tables:
            task_columns = [col['name'] for col in inspector.get_columns('tasks')]
            if 'guid' not in task_columns:
                print("Adding GUID column to tasks table...")
                conn.execute(text("ALTER TABLE tasks ADD COLUMN guid TEXT"))
                conn.commit()
                
                # Generate GUIDs for existing tasks
                session = SessionLocal()
                tasks = session.query(Task).all()
                for task in tasks:
                    task.guid = str(uuid.uuid4())
                session.commit()
                session.close()
                print(f"Generated GUIDs for {len(tasks)} tasks")
        
        if 'logs' in tables:
            log_columns = [col['name'] for col in inspector.get_columns('logs')]
            if 'agent_guid' not in log_columns:
                print("Adding agent_guid column to logs table...")
                conn.execute(text("ALTER TABLE logs ADD COLUMN agent_guid TEXT"))
                conn.commit()
            
            if 'tool_guid' not in log_columns:
                print("Adding tool_guid column to logs table...")
                conn.execute(text("ALTER TABLE logs ADD COLUMN tool_guid TEXT"))
                conn.commit()
            
            if 'task_guid' not in log_columns:
                print("Adding task_guid column to logs table...")
                conn.execute(text("ALTER TABLE logs ADD COLUMN task_guid TEXT"))
                conn.commit()
    
    print("Database migration completed successfully!")

if __name__ == "__main__":
    migrate_database() 