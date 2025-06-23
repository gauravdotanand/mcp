from fastapi import APIRouter, HTTPException, Response, UploadFile, File
from db import SessionLocal
from db.models import Agent, AgentStatus
from agents.manager import register_agent, update_agent_status, get_agent_by_guid, get_all_agents
from pydantic import BaseModel
from typing import List, Optional
import csv
import io
import json

router = APIRouter()

class AgentCreate(BaseModel):
    name: str

class AgentOut(BaseModel):
    guid: str
    name: str
    status: str
    last_seen: str

    class Config:
        orm_mode = True

@router.get("/", response_model=List[AgentOut])
def list_agents():
    agents = get_all_agents()
    return agents

@router.post("/", response_model=AgentOut)
def create_agent(agent: AgentCreate):
    db_agent = register_agent(agent.name)
    return db_agent

@router.get("/{guid}", response_model=AgentOut)
def get_agent(guid: str):
    agent = get_agent_by_guid(guid)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

class AgentStatusUpdate(BaseModel):
    status: str

@router.patch("/{guid}/status", response_model=AgentOut)
def update_status(guid: str, status_update: AgentStatusUpdate):
    session = SessionLocal()
    agent = session.query(Agent).filter(Agent.guid == guid).first()
    if not agent:
        session.close()
        raise HTTPException(status_code=404, detail="Agent not found")
    try:
        update_agent_status(agent.id, AgentStatus(status_update.status))
        session.refresh(agent)
        return agent
    finally:
        session.close()

@router.get("/export/csv")
def export_agents_csv():
    session = SessionLocal()
    agents = session.query(Agent).all()
    session.close()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["guid", "name", "status", "last_seen"])
    for agent in agents:
        writer.writerow([agent.guid, agent.name, agent.status.value, agent.last_seen])
    return Response(content=output.getvalue(), media_type="text/csv")

@router.get("/export/json")
def export_agents_json():
    session = SessionLocal()
    agents = session.query(Agent).all()
    session.close()
    agents_json = [
        {
            "guid": agent.guid,
            "name": agent.name,
            "status": agent.status.value,
            "last_seen": str(agent.last_seen)
        }
        for agent in agents
    ]
    return Response(content=json.dumps(agents_json, indent=2), media_type="application/json")

@router.post("/import/csv")
def import_agents_csv(file: UploadFile = File(...)):
    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))
    created = []
    for row in reader:
        name = row.get("name")
        if name:
            agent = register_agent(name)
            created.append(agent.name)
    return {"created": created}

@router.post("/import/json")
def import_agents_json(file: UploadFile = File(...)):
    content = file.file.read().decode("utf-8")
    data = json.loads(content)
    created = []
    for entry in data:
        name = entry.get("name")
        if name:
            agent = register_agent(name)
            created.append(agent.name)
    return {"created": created} 