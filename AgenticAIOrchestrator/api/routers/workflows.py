"""
API endpoints for multi-agent workflow management.
Provides REST API for creating, executing, and monitoring agent workflows.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime
from workflows.engine import workflow_engine, WorkflowStepType
from integrations.crewai_adapter import crewai_adapter
from integrations.langgraph_adapter import langgraph_adapter
from agents.communication import agent_comm_manager
from auth.dependencies import get_current_user
from db.models import User

router = APIRouter(prefix="/workflows", tags=["workflows"])

# Pydantic models
class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None

class WorkflowStepCreate(BaseModel):
    step_type: str
    config: Dict[str, Any]
    dependencies: Optional[List[str]] = None

class AgentTaskCreate(BaseModel):
    agent_capability: str
    task_data: Dict[str, Any]
    dependencies: Optional[List[str]] = None

class WorkflowExecute(BaseModel):
    initial_context: Optional[Dict[str, Any]] = None

class CrewAIAgentRegister(BaseModel):
    agent_guid: str
    name: str
    role: str
    goal: str
    backstory: str
    capabilities: List[str]

class CrewAICrewCreate(BaseModel):
    crew_id: str
    agents: List[str]
    tasks: List[Dict[str, Any]]

class LangGraphWorkflowCreate(BaseModel):
    workflow_id: str
    state_schema: Dict[str, Any]
    nodes: Dict[str, str]
    edges: List[tuple]

@router.post("/")
async def create_workflow(
    workflow_data: WorkflowCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new multi-agent workflow."""
    try:
        workflow = workflow_engine.create_workflow(workflow_data.name)
        return {
            "workflow_id": workflow.workflow_id,
            "name": workflow.name,
            "status": workflow.status,
            "created_at": workflow.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/")
async def list_workflows(current_user: User = Depends(get_current_user)):
    """List all workflows."""
    workflows = []
    for workflow_id, workflow in workflow_engine.workflows.items():
        workflows.append({
            "workflow_id": workflow_id,
            "name": workflow.name,
            "status": workflow.status,
            "steps_count": len(workflow.steps),
            "created_at": workflow.created_at.isoformat(),
            "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None
        })
    return workflows

@router.get("/{workflow_id}")
async def get_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get workflow details and status."""
    try:
        status = workflow_engine.get_workflow_status(workflow_id)
        return status
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{workflow_id}/steps")
async def add_workflow_step(
    workflow_id: str,
    step_data: WorkflowStepCreate,
    current_user: User = Depends(get_current_user)
):
    """Add a step to a workflow."""
    try:
        if workflow_id not in workflow_engine.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = workflow_engine.workflows[workflow_id]
        step_type = WorkflowStepType(step_data.step_type)
        
        step_id = workflow.add_step(step_type, step_data.config)
        
        return {
            "step_id": step_id,
            "workflow_id": workflow_id,
            "step_type": step_data.step_type,
            "status": "added"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{workflow_id}/agent-tasks")
async def add_agent_task(
    workflow_id: str,
    task_data: AgentTaskCreate,
    current_user: User = Depends(get_current_user)
):
    """Add an agent task to a workflow."""
    try:
        if workflow_id not in workflow_engine.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = workflow_engine.workflows[workflow_id]
        step_id = workflow.add_agent_task(
            agent_capability=task_data.agent_capability,
            task_data=task_data.task_data,
            dependencies=task_data.dependencies
        )
        
        return {
            "step_id": step_id,
            "workflow_id": workflow_id,
            "agent_capability": task_data.agent_capability,
            "status": "added"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: str,
    execute_data: WorkflowExecute,
    current_user: User = Depends(get_current_user)
):
    """Execute a workflow."""
    try:
        result = workflow_engine.execute_workflow(
            workflow_id, 
            execute_data.initial_context
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# CrewAI Integration Endpoints
@router.post("/crewai/agents")
async def register_crewai_agent(
    agent_data: CrewAIAgentRegister,
    current_user: User = Depends(get_current_user)
):
    """Register a CrewAI agent."""
    try:
        # This would create an actual CrewAI agent
        # For now, we'll just register it in the adapter
        crewai_adapter.register_langgraph_agent(
            agent_guid=agent_data.agent_guid,
            agent_function=lambda x: x,  # Placeholder
            capabilities=agent_data.capabilities
        )
        
        return {
            "agent_guid": agent_data.agent_guid,
            "name": agent_data.name,
            "status": "registered"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/crewai/crews")
async def create_crewai_crew(
    crew_data: CrewAICrewCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a CrewAI crew."""
    try:
        crew = crewai_adapter.create_crew(
            crew_id=crew_data.crew_id,
            agents=crew_data.agents,
            tasks=crew_data.tasks
        )
        
        return {
            "crew_id": crew_data.crew_id,
            "agents_count": len(crew_data.agents),
            "tasks_count": len(crew_data.tasks),
            "status": "created"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/crewai/crews/{crew_id}/execute")
async def execute_crewai_crew(
    crew_id: str,
    current_user: User = Depends(get_current_user)
):
    """Execute a CrewAI crew."""
    try:
        result = await crewai_adapter.execute_crew(crew_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/crewai/agents")
async def list_crewai_agents(current_user: User = Depends(get_current_user)):
    """List all registered CrewAI agents."""
    return crewai_adapter.list_agents()

@router.get("/crewai/crews")
async def list_crewai_crews(current_user: User = Depends(get_current_user)):
    """List all created CrewAI crews."""
    return crewai_adapter.list_crews()

# LangGraph Integration Endpoints
@router.post("/langgraph/workflows")
async def create_langgraph_workflow(
    workflow_data: LangGraphWorkflowCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a LangGraph workflow."""
    try:
        workflow = langgraph_adapter.create_workflow(
            workflow_id=workflow_data.workflow_id,
            state_schema=workflow_data.state_schema,
            nodes=workflow_data.nodes,
            edges=workflow_data.edges
        )
        
        return {
            "workflow_id": workflow_data.workflow_id,
            "nodes_count": len(workflow_data.nodes),
            "status": "created"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/langgraph/workflows/{workflow_id}/execute")
async def execute_langgraph_workflow(
    workflow_id: str,
    initial_state: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Execute a LangGraph workflow."""
    try:
        result = await langgraph_adapter.execute_workflow(workflow_id, initial_state)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/langgraph/workflows")
async def list_langgraph_workflows(current_user: User = Depends(get_current_user)):
    """List all LangGraph workflows."""
    return langgraph_adapter.list_workflows()

# Agent Communication Endpoints
@router.get("/communication/agents")
async def list_registered_agents(current_user: User = Depends(get_current_user)):
    """List all registered agents in the communication manager."""
    return {
        "agents": [
            {
                "agent_guid": agent_guid,
                "capabilities": info["capabilities"],
                "protocol": info["protocol"],
                "status": info["status"],
                "last_seen": info["last_seen"].isoformat()
            }
            for agent_guid, info in agent_comm_manager.agent_registry.items()
        ]
    }

@router.get("/communication/contexts")
async def list_shared_contexts(current_user: User = Depends(get_current_user)):
    """List all shared contexts."""
    return {
        "contexts": [
            context.to_dict()
            for context in agent_comm_manager.shared_contexts.values()
        ]
    }

@router.get("/communication/messages")
async def get_recent_messages(current_user: User = Depends(get_current_user)):
    """Get recent messages from the communication queue."""
    return {
        "messages": [
            {
                "message_id": message.message_id,
                "sender_guid": message.sender_guid,
                "recipient_guid": message.recipient_guid,
                "message_type": message.message_type,
                "timestamp": message.timestamp.isoformat(),
                "status": message.status
            }
            for message in agent_comm_manager.message_queue[-50:]  # Last 50 messages
        ]
    }

@router.post("/communication/messages")
async def send_message(
    sender_guid: str,
    recipient_guid: str,
    message_type: str,
    content: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Send a message between agents."""
    try:
        message = agent_comm_manager.send_message(
            sender_guid=sender_guid,
            recipient_guid=recipient_guid,
            message_type=message_type,
            content=content
        )
        
        return {
            "message_id": message.message_id,
            "status": "sent",
            "timestamp": message.timestamp.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 