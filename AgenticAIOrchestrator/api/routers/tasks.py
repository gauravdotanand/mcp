from fastapi import APIRouter, HTTPException, Response
from db import SessionLocal
from db.models import Task, TaskStatus
from tasks.manager import create_task, update_task_status, get_task_by_guid, get_all_tasks
from pydantic import BaseModel
from typing import List, Optional
import csv
import io
import json

router = APIRouter()

class TaskCreate(BaseModel):
    description: str
    agent_id: Optional[int] = None
    tool_id: Optional[int] = None

class TaskOut(BaseModel):
    guid: str
    description: str
    status: str
    agent_id: Optional[int]
    tool_id: Optional[int]

    class Config:
        orm_mode = True

@router.get("/", response_model=List[TaskOut])
def list_tasks():
    tasks = get_all_tasks()
    return tasks

@router.post("/", response_model=TaskOut)
def create_task_api(task: TaskCreate):
    db_task = create_task(task.description, agent_id=task.agent_id, tool_id=task.tool_id)
    return db_task

@router.get("/{guid}", response_model=TaskOut)
def get_task(guid: str):
    task = get_task_by_guid(guid)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

class TaskStatusUpdate(BaseModel):
    status: str

@router.patch("/{guid}/status", response_model=TaskOut)
def update_status(guid: str, status_update: TaskStatusUpdate):
    session = SessionLocal()
    task = session.query(Task).filter(Task.guid == guid).first()
    if not task:
        session.close()
        raise HTTPException(status_code=404, detail="Task not found")
    try:
        update_task_status(task.id, TaskStatus(status_update.status))
        session.refresh(task)
        return task
    finally:
        session.close()

@router.get("/export/csv")
def export_tasks_csv():
    session = SessionLocal()
    tasks = session.query(Task).all()
    session.close()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["guid", "description", "status", "agent_id", "tool_id"])
    for task in tasks:
        writer.writerow([task.guid, task.description, task.status.value, task.agent_id, task.tool_id])
    return Response(content=output.getvalue(), media_type="text/csv")

@router.get("/export/json")
def export_tasks_json():
    session = SessionLocal()
    tasks = session.query(Task).all()
    session.close()
    tasks_json = [
        {
            "guid": task.guid,
            "description": task.description,
            "status": task.status.value,
            "agent_id": task.agent_id,
            "tool_id": task.tool_id
        }
        for task in tasks
    ]
    return Response(content=json.dumps(tasks_json, indent=2), media_type="application/json") 