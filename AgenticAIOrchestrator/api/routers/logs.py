from fastapi import APIRouter, Query, Response
from db import SessionLocal
from db.models import Log
from typing import List, Optional
from pydantic import BaseModel
import csv
import io
import json

router = APIRouter()

class LogOut(BaseModel):
    id: int
    message: str
    timestamp: str
    level: str
    agent_guid: Optional[str]
    tool_guid: Optional[str]
    task_guid: Optional[str]

    class Config:
        orm_mode = True

@router.get("/", response_model=List[LogOut])
def list_logs(
    level: Optional[str] = None,
    agent_guid: Optional[str] = None,
    tool_guid: Optional[str] = None,
    task_guid: Optional[str] = None,
    limit: int = 100
):
    session = SessionLocal()
    query = session.query(Log).order_by(Log.timestamp.desc())
    if level:
        query = query.filter(Log.level == level)
    if agent_guid:
        query = query.filter(Log.agent_guid == agent_guid)
    if tool_guid:
        query = query.filter(Log.tool_guid == tool_guid)
    if task_guid:
        query = query.filter(Log.task_guid == task_guid)
    logs = query.limit(limit).all()
    session.close()
    return logs

@router.get("/export/csv")
def export_logs_csv(
    level: Optional[str] = None,
    agent_guid: Optional[str] = None,
    tool_guid: Optional[str] = None,
    task_guid: Optional[str] = None,
    limit: int = 100
):
    session = SessionLocal()
    query = session.query(Log).order_by(Log.timestamp.desc())
    if level:
        query = query.filter(Log.level == level)
    if agent_guid:
        query = query.filter(Log.agent_guid == agent_guid)
    if tool_guid:
        query = query.filter(Log.tool_guid == tool_guid)
    if task_guid:
        query = query.filter(Log.task_guid == task_guid)
    logs = query.limit(limit).all()
    session.close()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "timestamp", "level", "message", "agent_guid", "tool_guid", "task_guid"])
    for log in logs:
        writer.writerow([
            log.id, log.timestamp, log.level, log.message, log.agent_guid, log.tool_guid, log.task_guid
        ])
    return Response(content=output.getvalue(), media_type="text/csv")

@router.get("/export/json")
def export_logs_json(
    level: Optional[str] = None,
    agent_guid: Optional[str] = None,
    tool_guid: Optional[str] = None,
    task_guid: Optional[str] = None,
    limit: int = 100
):
    session = SessionLocal()
    query = session.query(Log).order_by(Log.timestamp.desc())
    if level:
        query = query.filter(Log.level == level)
    if agent_guid:
        query = query.filter(Log.agent_guid == agent_guid)
    if tool_guid:
        query = query.filter(Log.tool_guid == tool_guid)
    if task_guid:
        query = query.filter(Log.task_guid == task_guid)
    logs = query.limit(limit).all()
    session.close()
    logs_json = [
        {
            "id": log.id,
            "timestamp": str(log.timestamp),
            "level": log.level,
            "message": log.message,
            "agent_guid": log.agent_guid,
            "tool_guid": log.tool_guid,
            "task_guid": log.task_guid
        }
        for log in logs
    ]
    return Response(content=json.dumps(logs_json, indent=2), media_type="application/json") 