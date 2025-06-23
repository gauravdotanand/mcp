from fastapi import APIRouter, HTTPException, Response
from db import SessionLocal
from db.models import Tool, ToolStatus
from tools.manager import register_tool, update_tool_status, get_tool_by_guid, get_all_tools
from pydantic import BaseModel
from typing import List
import csv
import io
import json

router = APIRouter()

class ToolCreate(BaseModel):
    name: str

class ToolOut(BaseModel):
    guid: str
    name: str
    status: str

    class Config:
        orm_mode = True

@router.get("/", response_model=List[ToolOut])
def list_tools():
    tools = get_all_tools()
    return tools

@router.post("/", response_model=ToolOut)
def create_tool(tool: ToolCreate):
    db_tool = register_tool(tool.name)
    return db_tool

@router.get("/{guid}", response_model=ToolOut)
def get_tool(guid: str):
    tool = get_tool_by_guid(guid)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool

class ToolStatusUpdate(BaseModel):
    status: str

@router.patch("/{guid}/status", response_model=ToolOut)
def update_status(guid: str, status_update: ToolStatusUpdate):
    session = SessionLocal()
    tool = session.query(Tool).filter(Tool.guid == guid).first()
    if not tool:
        session.close()
        raise HTTPException(status_code=404, detail="Tool not found")
    try:
        update_tool_status(tool.id, ToolStatus(status_update.status))
        session.refresh(tool)
        return tool
    finally:
        session.close()

@router.get("/export/csv")
def export_tools_csv():
    session = SessionLocal()
    tools = session.query(Tool).all()
    session.close()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["guid", "name", "status"])
    for tool in tools:
        writer.writerow([tool.guid, tool.name, tool.status.value])
    return Response(content=output.getvalue(), media_type="text/csv")

@router.get("/export/json")
def export_tools_json():
    session = SessionLocal()
    tools = session.query(Tool).all()
    session.close()
    tools_json = [
        {
            "guid": tool.guid,
            "name": tool.name,
            "status": tool.status.value
        }
        for tool in tools
    ]
    return Response(content=json.dumps(tools_json, indent=2), media_type="application/json") 