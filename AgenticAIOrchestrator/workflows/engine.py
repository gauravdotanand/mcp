"""
Multi-agent workflow engine for orchestrating agent interactions.
Supports sequential, parallel, and hierarchical agent workflows.
"""

from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import json
import uuid
from enum import Enum
from agents.communication import agent_comm_manager, SharedContext
from logs.logger import logger

class WorkflowStepType(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    LOOP = "loop"
    AGENT_TASK = "agent_task"
    HUMAN_APPROVAL = "human_approval"

class WorkflowStep:
    def __init__(self, step_id: str, step_type: WorkflowStepType, config: Dict):
        self.step_id = step_id
        self.step_type = step_type
        self.config = config
        self.status = "pending"
        self.result = None
        self.error = None
        self.start_time = None
        self.end_time = None
        self.dependencies = config.get("dependencies", [])

class MultiAgentWorkflow:
    def __init__(self, workflow_id: str, name: str):
        self.workflow_id = workflow_id
        self.name = name
        self.steps = []
        self.shared_context = None
        self.status = "created"
        self.created_at = datetime.utcnow()
        self.started_at = None
        self.completed_at = None
    
    def add_step(self, step_type: WorkflowStepType, config: Dict) -> str:
        """Add a step to the workflow."""
        step_id = str(uuid.uuid4())
        step = WorkflowStep(step_id, step_type, config)
        self.steps.append(step)
        return step_id
    
    def add_agent_task(self, agent_capability: str, task_data: Dict, 
                      dependencies: List[str] = None) -> str:
        """Add an agent task step."""
        config = {
            "agent_capability": agent_capability,
            "task_data": task_data,
            "dependencies": dependencies or []
        }
        return self.add_step(WorkflowStepType.AGENT_TASK, config)
    
    def add_sequential_steps(self, steps_config: List[Dict]) -> List[str]:
        """Add multiple sequential steps."""
        step_ids = []
        for i, step_config in enumerate(steps_config):
            dependencies = [step_ids[i-1]] if i > 0 else []
            step_config["dependencies"] = dependencies
            step_id = self.add_step(WorkflowStepType.SEQUENTIAL, step_config)
            step_ids.append(step_id)
        return step_ids
    
    def add_parallel_steps(self, steps_config: List[Dict]) -> List[str]:
        """Add multiple parallel steps."""
        step_ids = []
        for step_config in steps_config:
            step_id = self.add_step(WorkflowStepType.PARALLEL, step_config)
            step_ids.append(step_id)
        return step_ids

class WorkflowEngine:
    def __init__(self):
        self.workflows = {}
        self.execution_queue = []
    
    def create_workflow(self, name: str) -> MultiAgentWorkflow:
        """Create a new multi-agent workflow."""
        workflow_id = str(uuid.uuid4())
        workflow = MultiAgentWorkflow(workflow_id, name)
        self.workflows[workflow_id] = workflow
        return workflow
    
    def execute_workflow(self, workflow_id: str, initial_context: Dict = None) -> Dict:
        """Execute a multi-agent workflow."""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        workflow.status = "running"
        workflow.started_at = datetime.utcnow()
        
        # Create shared context
        workflow.shared_context = agent_comm_manager.create_shared_context(
            f"workflow_{workflow_id}", initial_context
        )
        
        # Log workflow start
        logger.log(
            message=f"Started workflow: {workflow.name}",
            level="INFO"
        )
        
        try:
            # Execute steps in dependency order
            executed_steps = set()
            results = {}
            
            while len(executed_steps) < len(workflow.steps):
                for step in workflow.steps:
                    if step.step_id in executed_steps:
                        continue
                    
                    # Check dependencies
                    if all(dep in executed_steps for dep in step.dependencies):
                        step_result = self._execute_step(step, workflow.shared_context)
                        results[step.step_id] = step_result
                        executed_steps.add(step.step_id)
            
            workflow.status = "completed"
            workflow.completed_at = datetime.utcnow()
            
            # Log workflow completion
            logger.log(
                message=f"Completed workflow: {workflow.name}",
                level="INFO"
            )
            
            return {
                "workflow_id": workflow_id,
                "status": "completed",
                "results": results,
                "shared_context": workflow.shared_context.to_dict()
            }
            
        except Exception as e:
            workflow.status = "failed"
            workflow.completed_at = datetime.utcnow()
            
            # Log workflow failure
            logger.log(
                message=f"Failed workflow: {workflow.name} - {str(e)}",
                level="ERROR"
            )
            
            raise
    
    def _execute_step(self, step: WorkflowStep, shared_context: SharedContext) -> Any:
        """Execute a single workflow step."""
        step.status = "running"
        step.start_time = datetime.utcnow()
        
        try:
            if step.step_type == WorkflowStepType.AGENT_TASK:
                result = self._execute_agent_task(step, shared_context)
            elif step.step_type == WorkflowStepType.SEQUENTIAL:
                result = self._execute_sequential_step(step, shared_context)
            elif step.step_type == WorkflowStepType.PARALLEL:
                result = self._execute_parallel_step(step, shared_context)
            else:
                result = self._execute_generic_step(step, shared_context)
            
            step.status = "completed"
            step.result = result
            step.end_time = datetime.utcnow()
            
            return result
            
        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            step.end_time = datetime.utcnow()
            raise
    
    def _execute_agent_task(self, step: WorkflowStep, shared_context: SharedContext) -> Any:
        """Execute an agent task step."""
        agent_capability = step.config["agent_capability"]
        task_data = step.config["task_data"]
        
        # Route task to appropriate agent
        agent_guid = agent_comm_manager.route_task_to_agent(agent_capability, task_data)
        
        if not agent_guid:
            raise Exception(f"No available agent with capability: {agent_capability}")
        
        # Send task to agent
        message = agent_comm_manager.send_message(
            sender_guid="workflow_engine",
            recipient_guid=agent_guid,
            message_type="task_assignment",
            content={
                "task_data": task_data,
                "shared_context_id": shared_context.context_id
            }
        )
        
        # Update shared context with task assignment
        shared_context.set_data(f"task_{step.step_id}", {
            "assigned_to": agent_guid,
            "status": "assigned",
            "message_id": message.message_id
        })
        
        return {
            "agent_guid": agent_guid,
            "message_id": message.message_id,
            "status": "assigned"
        }
    
    def _execute_sequential_step(self, step: WorkflowStep, shared_context: SharedContext) -> Any:
        """Execute a sequential step."""
        # For now, just return the config
        return step.config
    
    def _execute_parallel_step(self, step: WorkflowStep, shared_context: SharedContext) -> Any:
        """Execute a parallel step."""
        # For now, just return the config
        return step.config
    
    def _execute_generic_step(self, step: WorkflowStep, shared_context: SharedContext) -> Any:
        """Execute a generic step."""
        return step.config
    
    def get_workflow_status(self, workflow_id: str) -> Dict:
        """Get the status of a workflow."""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        return {
            "workflow_id": workflow_id,
            "name": workflow.name,
            "status": workflow.status,
            "steps": [
                {
                    "step_id": step.step_id,
                    "type": step.step_type.value,
                    "status": step.status,
                    "result": step.result,
                    "error": step.error
                }
                for step in workflow.steps
            ],
            "shared_context": workflow.shared_context.to_dict() if workflow.shared_context else None
        }

# Global workflow engine
workflow_engine = WorkflowEngine() 