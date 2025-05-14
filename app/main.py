# Import config first to set up environment variables
from app.config import *

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel
from typing import List, Optional
from crewai import Agent, Task, Crew, Process
from langchain.tools import tool
from datetime import timedelta

from app.auth.models import User, UserCreate, Token
from app.auth.auth_utils import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

app = FastAPI(title="CrewAI Multi-Agent API")

# Initialize MCP
mcp = FastApiMCP(app)

# Mount MCP server
mcp.mount()

# Define request models
class AgentRequest(BaseModel):
    role: str
    goal: str
    backstory: Optional[str] = None

class TaskRequest(BaseModel):
    description: str
    agent_role: str
    expected_output: str

class CrewRequest(BaseModel):
    agents: List[AgentRequest]
    tasks: List[TaskRequest]

# Custom tools
@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    # Implement web search functionality here
    return f"Search results for: {query}"

@tool
def analyze_data(data: str) -> str:
    """Analyze the provided data."""
    # Implement data analysis functionality here
    return f"Analysis of: {data}"

# Authentication endpoints
@app.post("/register", response_model=User)
async def register_user(user: UserCreate):
    from app.auth.models import users_db
    if user.username in users_db:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    hashed_password = get_password_hash(user.password)
    db_user = User(
        id=len(users_db) + 1,
        email=user.email,
        username=user.username,
        is_active=True,
        created_at=datetime.utcnow()
    )
    users_db[user.username] = {
        "user": db_user,
        "hashed_password": hashed_password
    }
    return db_user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    from app.auth.models import users_db
    user_data = users_db.get(form_data.username)
    if not user_data or not verify_password(form_data.password, user_data["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Protected API endpoints
@app.post("/create_crew")
async def create_crew(
    request: CrewRequest,
    current_user: User = Depends(get_current_active_user)
):
    try:
        # Create agents
        agents = []
        for agent_req in request.agents:
            agent = Agent(
                role=agent_req.role,
                goal=agent_req.goal,
                backstory=agent_req.backstory,
                tools=[search_web, analyze_data],
                verbose=True
            )
            agents.append(agent)

        # Create tasks
        tasks = []
        for task_req in request.tasks:
            # Find the corresponding agent
            agent = next((a for a in agents if a.role == task_req.agent_role), None)
            if not agent:
                raise HTTPException(status_code=400, detail=f"Agent with role {task_req.agent_role} not found")
            
            task = Task(
                description=task_req.description,
                agent=agent,
                expected_output=task_req.expected_output
            )
            tasks.append(task)

        # Create and run crew
        crew = Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential
        )
        
        result = crew.kickoff()
        return {"result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to CrewAI Multi-Agent API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 