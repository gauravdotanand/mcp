"""
CrewAI integration adapter for multi-agent orchestration.
Provides seamless integration with CrewAI agents and crews.
"""

from typing import Dict, List, Any, Optional
import asyncio
from agents.communication import agent_comm_manager
from logs.logger import logger

# Try to import CrewAI, but make it optional
try:
    from crewai import Agent as CrewAIAgent, Task as CrewAITask, Crew
    CREWAI_AVAILABLE = True
except ImportError as e:
    print("CrewAI import error:", e)
    CREWAI_AVAILABLE = False
    # Create placeholder classes for when CrewAI is not available
    class CrewAIAgent:
        def __init__(self, name="", role="", goal="", backstory=""):
            self.name = name
            self.role = role
            self.goal = goal
            self.backstory = backstory
    
    class CrewAITask:
        def __init__(self, description="", agent=None, expected_output="", context=None):
            self.description = description
            self.agent = agent
            self.expected_output = expected_output
            self.context = context or []
    
    class Crew:
        def __init__(self, agents=None, tasks=None, verbose=True):
            self.agents = agents or []
            self.tasks = tasks or []
            self.verbose = verbose
        
        async def kickoff(self):
            return {"message": "CrewAI not available"}

class CrewAIAdapter:
    def __init__(self):
        self.crewai_agents = {}
        self.crews = {}
        self.available = CREWAI_AVAILABLE
    
    def register_crewai_agent(self, agent_guid: str, crewai_agent: CrewAIAgent, 
                             capabilities: List[str]) -> None:
        """Register a CrewAI agent with the communication manager."""
        if not self.available:
            logger.log(
                message="CrewAI not available - agent registration skipped",
                level="WARNING"
            )
            return
        
        self.crewai_agents[agent_guid] = crewai_agent
        
        # Register with communication manager
        agent_comm_manager.register_agent(
            agent_guid=agent_guid,
            capabilities=capabilities,
            communication_protocol="crewai"
        )
        
        logger.log_agent_event(
            agent_guid=agent_guid,
            message=f"Registered CrewAI agent: {crewai_agent.name}",
            level="INFO"
        )
    
    def create_crew(self, crew_id: str, agents: List[str], 
                   tasks: List[Dict]) -> Crew:
        """Create a CrewAI crew with specified agents and tasks."""
        if not self.available:
            logger.log(
                message="CrewAI not available - creating mock crew",
                level="WARNING"
            )
            return Crew()
        
        crewai_agents = []
        for agent_guid in agents:
            if agent_guid in self.crewai_agents:
                crewai_agents.append(self.crewai_agents[agent_guid])
        
        crewai_tasks = []
        for task_config in tasks:
            task = CrewAITask(
                description=task_config["description"],
                agent=crewai_agents[task_config.get("agent_index", 0)] if crewai_agents else None,
                expected_output=task_config.get("expected_output", ""),
                context=task_config.get("context", [])
            )
            crewai_tasks.append(task)
        
        crew = Crew(
            agents=crewai_agents,
            tasks=crewai_tasks,
            verbose=True
        )
        
        self.crews[crew_id] = crew
        
        logger.log(
            message=f"Created CrewAI crew: {crew_id} with {len(crewai_agents)} agents",
            level="INFO"
        )
        
        return crew
    
    async def execute_crew(self, crew_id: str, context: Dict = None) -> Dict:
        """Execute a CrewAI crew asynchronously."""
        if not self.available:
            return {
                "crew_id": crew_id,
                "result": "CrewAI not available",
                "status": "skipped"
            }
        
        if crew_id not in self.crews:
            raise ValueError(f"Crew {crew_id} not found")
        
        crew = self.crews[crew_id]
        
        try:
            # Execute crew
            result = await crew.kickoff()
            
            # Log execution
            logger.log(
                message=f"Executed CrewAI crew: {crew_id}",
                level="INFO"
            )
            
            return {
                "crew_id": crew_id,
                "result": result,
                "status": "completed"
            }
            
        except Exception as e:
            logger.log(
                message=f"Failed to execute CrewAI crew: {crew_id} - {str(e)}",
                level="ERROR"
            )
            raise
    
    def get_agent_info(self, agent_guid: str) -> Optional[Dict]:
        """Get information about a registered CrewAI agent."""
        if agent_guid not in self.crewai_agents:
            return None
        
        agent = self.crewai_agents[agent_guid]
        return {
            "agent_guid": agent_guid,
            "name": agent.name,
            "role": agent.role,
            "goal": agent.goal,
            "backstory": agent.backstory,
            "capabilities": agent_comm_manager.agent_registry.get(agent_guid, {}).get("capabilities", [])
        }
    
    def list_agents(self) -> List[Dict]:
        """List all registered CrewAI agents."""
        return [
            self.get_agent_info(agent_guid)
            for agent_guid in self.crewai_agents.keys()
        ]
    
    def list_crews(self) -> List[Dict]:
        """List all created crews."""
        return [
            {
                "crew_id": crew_id,
                "agents": [agent.name for agent in crew.agents],
                "tasks": [task.description for task in crew.tasks]
            }
            for crew_id, crew in self.crews.items()
        ]

# Global CrewAI adapter
crewai_adapter = CrewAIAdapter() 