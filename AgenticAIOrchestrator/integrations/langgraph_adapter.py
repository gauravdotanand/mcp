"""
LangGraph integration adapter for multi-agent orchestration.
Provides seamless integration with LangGraph agents and workflows.
"""

from typing import Dict, List, Any, Optional, Callable
import asyncio
from agents.communication import agent_comm_manager
from logs.logger import logger

# Try to import LangGraph, but make it optional
try:
    from langchain_core.runnables import RunnableConfig
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError as e:
    print("LangGraph import error:", e)
    LANGGRAPH_AVAILABLE = False
    # Create placeholder classes for when LangGraph is not available
    class RunnableConfig:
        pass
    
    class StateGraph:
        def __init__(self, state_schema):
            self.state_schema = state_schema
        
        def add_node(self, name, func):
            pass
        
        def add_edge(self, from_node, to_node):
            pass
        
        def add_conditional_edges(self, from_node, condition_func, edge_map):
            pass
        
        def set_entry_point(self, node):
            pass
        
        def compile(self):
            return self
    
    END = "END"

class LangGraphAdapter:
    def __init__(self):
        self.langgraph_agents = {}
        self.workflows = {}
        self.state_schemas = {}
        self.available = LANGGRAPH_AVAILABLE
    
    def register_langgraph_agent(self, agent_guid: str, agent_function: Callable, 
                                capabilities: List[str]) -> None:
        """Register a LangGraph agent function with the communication manager."""
        if not self.available:
            logger.log(
                message="LangGraph not available - agent registration skipped",
                level="WARNING"
            )
            return
        
        self.langgraph_agents[agent_guid] = agent_function
        
        # Register with communication manager
        agent_comm_manager.register_agent(
            agent_guid=agent_guid,
            capabilities=capabilities,
            communication_protocol="langgraph"
        )
        
        logger.log_agent_event(
            agent_guid=agent_guid,
            message=f"Registered LangGraph agent function",
            level="INFO"
        )
    
    def create_workflow(self, workflow_id: str, state_schema: Dict, 
                       nodes: Dict[str, str], edges: List[tuple]) -> StateGraph:
        """Create a LangGraph workflow with specified nodes and edges."""
        if not self.available:
            logger.log(
                message="LangGraph not available - creating mock workflow",
                level="WARNING"
            )
            return StateGraph(state_schema)
        
        # Create state graph
        workflow = StateGraph(state_schema)
        
        # Add nodes
        for node_name, agent_guid in nodes.items():
            if agent_guid in self.langgraph_agents:
                workflow.add_node(node_name, self.langgraph_agents[agent_guid])
            else:
                # Add a placeholder node if agent not found
                workflow.add_node(node_name, lambda state: state)
        
        # Add edges
        for edge in edges:
            if len(edge) == 2:
                workflow.add_edge(edge[0], edge[1])
            elif len(edge) == 3:
                workflow.add_conditional_edges(edge[0], edge[1], edge[2])
        
        # Set entry point
        if nodes:
            first_node = list(nodes.keys())[0]
            workflow.set_entry_point(first_node)
        
        # Compile workflow
        compiled_workflow = workflow.compile()
        self.workflows[workflow_id] = compiled_workflow
        self.state_schemas[workflow_id] = state_schema
        
        logger.log(
            message=f"Created LangGraph workflow: {workflow_id}",
            level="INFO"
        )
        
        return compiled_workflow
    
    async def execute_workflow(self, workflow_id: str, initial_state: Dict, 
                             config: Optional[RunnableConfig] = None) -> Dict:
        """Execute a LangGraph workflow asynchronously."""
        if not self.available:
            return {
                "workflow_id": workflow_id,
                "result": "LangGraph not available",
                "status": "skipped"
            }
        
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        
        try:
            # Execute workflow
            result = await workflow.ainvoke(initial_state, config)
            
            # Log execution
            logger.log(
                message=f"Executed LangGraph workflow: {workflow_id}",
                level="INFO"
            )
            
            return {
                "workflow_id": workflow_id,
                "result": result,
                "status": "completed"
            }
            
        except Exception as e:
            logger.log(
                message=f"Failed to execute LangGraph workflow: {workflow_id} - {str(e)}",
                level="ERROR"
            )
            raise
    
    def add_agent_to_workflow(self, workflow_id: str, node_name: str, 
                             agent_guid: str) -> None:
        """Add an agent to an existing workflow."""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        if agent_guid not in self.langgraph_agents:
            raise ValueError(f"Agent {agent_guid} not found")
        
        # This would require recreating the workflow
        # For now, just log the request
        logger.log(
            message=f"Request to add agent {agent_guid} to workflow {workflow_id} as node {node_name}",
            level="INFO"
        )
    
    def get_workflow_info(self, workflow_id: str) -> Optional[Dict]:
        """Get information about a LangGraph workflow."""
        if workflow_id not in self.workflows:
            return None
        
        return {
            "workflow_id": workflow_id,
            "state_schema": self.state_schemas.get(workflow_id, {}),
            "nodes": list(self.langgraph_agents.keys()),
            "status": "compiled"
        }
    
    def list_workflows(self) -> List[Dict]:
        """List all created LangGraph workflows."""
        return [
            self.get_workflow_info(workflow_id)
            for workflow_id in self.workflows.keys()
        ]
    
    def create_agent_function(self, agent_guid: str, function_name: str, 
                             function_code: str) -> Callable:
        """Create a LangGraph agent function from code."""
        try:
            # Create a function from the provided code
            # This is a simplified version - in practice, you'd want more security
            namespace = {}
            exec(function_code, namespace)
            
            if function_name in namespace:
                agent_function = namespace[function_name]
                
                # Register the agent
                self.register_langgraph_agent(
                    agent_guid=agent_guid,
                    agent_function=agent_function,
                    capabilities=["custom_function"]
                )
                
                return agent_function
            else:
                raise ValueError(f"Function {function_name} not found in code")
                
        except Exception as e:
            logger.log(
                message=f"Failed to create agent function: {str(e)}",
                level="ERROR"
            )
            raise

# Global LangGraph adapter
langgraph_adapter = LangGraphAdapter() 