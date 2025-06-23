from db import SessionLocal
from db.models import Agent, AgentStatus
from signals.events import agent_status_changed
from logs.logger import logger

def register_agent(name):
    session = SessionLocal()
    agent = Agent(name=name)
    session.add(agent)
    session.commit()
    
    # Log the agent registration
    logger.log_agent_event(
        agent_guid=agent.guid,
        message=f"Agent '{name}' registered successfully",
        level="INFO"
    )
    
    session.close()
    return agent

def update_agent_status(agent_id, new_status):
    session = SessionLocal()
    agent = session.query(Agent).filter(Agent.id == agent_id).first()
    if agent:
        old_status = agent.status
        agent.status = new_status
        session.commit()
        
        # Log the status change
        logger.log_agent_event(
            agent_guid=agent.guid,
            message=f"Agent '{agent.name}' status changed from {old_status.value} to {new_status.value}",
            level="INFO"
        )
        
        # Emit signal with GUID
        agent_status_changed.send(
            agent_id=agent_id,
            agent_guid=agent.guid,
            old_status=old_status,
            new_status=new_status
        )
    session.close()

def get_agent_by_guid(agent_guid):
    """Get agent by GUID"""
    session = SessionLocal()
    agent = session.query(Agent).filter(Agent.guid == agent_guid).first()
    session.close()
    return agent

def get_all_agents():
    """Get all agents with their GUIDs"""
    session = SessionLocal()
    agents = session.query(Agent).all()
    session.close()
    return agents 