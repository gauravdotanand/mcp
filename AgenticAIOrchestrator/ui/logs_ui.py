import streamlit as st
from db import SessionLocal
from db.models import Log, Agent, Tool, Task
from datetime import datetime
import requests

API_BASE_URL = "http://localhost:8000/logs"

def logs_ui():
    st.header("Logs")
    
    # Add filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        level_filter = st.selectbox(
            "Filter by Level",
            ["All", "INFO", "WARNING", "ERROR", "DEBUG"]
        )
    
    with col2:
        agent_filter = st.selectbox(
            "Filter by Agent",
            ["All"] + [agent.name for agent in SessionLocal().query(Agent).all()]
        )
    
    with col3:
        tool_filter = st.selectbox(
            "Filter by Tool",
            ["All"] + [tool.name for tool in SessionLocal().query(Tool).all()]
        )
    
    with col4:
        task_filter = st.selectbox(
            "Filter by Task",
            ["All"] + [f"Task {task.id}: {task.description[:30]}..." for task in SessionLocal().query(Task).all()]
        )
    
    # Advanced filters
    with st.expander("Advanced Filters & Search"):
        col5, col6 = st.columns(2)
        with col5:
            search_text = st.text_input("Search in Message", "")
        with col6:
            date_range = st.date_input(
                "Date Range",
                [datetime.now().date(), datetime.now().date()]
            )
    
    # Export buttons
    col_export1, col_export2 = st.columns(2)
    with col_export1:
        if st.button("Export as CSV"):
            params = {}
            if level_filter != "All": params["level"] = level_filter
            if agent_filter != "All":
                agent = SessionLocal().query(Agent).filter(Agent.name == agent_filter).first()
                if agent: params["agent_guid"] = agent.guid
            if tool_filter != "All":
                tool = SessionLocal().query(Tool).filter(Tool.name == tool_filter).first()
                if tool: params["tool_guid"] = tool.guid
            if task_filter != "All":
                task_id = int(task_filter.split(":")[0].split()[1])
                task = SessionLocal().query(Task).filter(Task.id == task_id).first()
                if task: params["task_guid"] = task.guid
            if search_text:
                params["search"] = search_text
            if date_range and len(date_range) == 2:
                params["start_date"] = str(date_range[0])
                params["end_date"] = str(date_range[1])
            response = requests.get(f"{API_BASE_URL}/export/csv", params=params)
            st.download_button("Download CSV", response.content, file_name="logs.csv")
    with col_export2:
        if st.button("Export as JSON"):
            params = {}
            if level_filter != "All": params["level"] = level_filter
            if agent_filter != "All":
                agent = SessionLocal().query(Agent).filter(Agent.name == agent_filter).first()
                if agent: params["agent_guid"] = agent.guid
            if tool_filter != "All":
                tool = SessionLocal().query(Tool).filter(Tool.name == tool_filter).first()
                if tool: params["tool_guid"] = tool.guid
            if task_filter != "All":
                task_id = int(task_filter.split(":")[0].split()[1])
                task = SessionLocal().query(Task).filter(Task.id == task_id).first()
                if task: params["task_guid"] = task.guid
            if search_text:
                params["search"] = search_text
            if date_range and len(date_range) == 2:
                params["start_date"] = str(date_range[0])
                params["end_date"] = str(date_range[1])
            response = requests.get(f"{API_BASE_URL}/export/json", params=params)
            st.download_button("Download JSON", response.content, file_name="logs.json")
    
    # Build query
    session = SessionLocal()
    query = session.query(Log).order_by(Log.timestamp.desc())
    
    if level_filter != "All":
        query = query.filter(Log.level == level_filter)
    
    if agent_filter != "All":
        agent = session.query(Agent).filter(Agent.name == agent_filter).first()
        if agent:
            query = query.filter(Log.agent_guid == agent.guid)
    
    if tool_filter != "All":
        tool = session.query(Tool).filter(Tool.name == tool_filter).first()
        if tool:
            query = query.filter(Log.tool_guid == tool.guid)
    
    if task_filter != "All":
        task_id = int(task_filter.split(":")[0].split()[1])
        task = session.query(Task).filter(Task.id == task_id).first()
        if task:
            query = query.filter(Log.task_guid == task.guid)
    
    # Full-text search
    if search_text:
        query = query.filter(Log.message.ilike(f"%{search_text}%"))
    
    # Date range filter
    if date_range and len(date_range) == 2:
        start_date = datetime.combine(date_range[0], datetime.min.time())
        end_date = datetime.combine(date_range[1], datetime.max.time())
        query = query.filter(Log.timestamp >= start_date, Log.timestamp <= end_date)
    
    logs = query.limit(100).all()
    session.close()
    
    # Display logs with enhanced information
    for log in logs:
        # Create a container for each log entry
        with st.container():
            col1, col2 = st.columns([1, 4])
            
            with col1:
                # Color-coded level indicator
                if log.level == "ERROR":
                    st.error(log.level)
                elif log.level == "WARNING":
                    st.warning(log.level)
                elif log.level == "INFO":
                    st.info(log.level)
                else:
                    st.text(log.level)
            
            with col2:
                # Main log message
                st.write(f"**{log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}** - {log.message}")
                
                # Show GUID references if available
                guid_info = []
                if log.agent_guid:
                    agent = session.query(Agent).filter(Agent.guid == log.agent_guid).first()
                    if agent:
                        guid_info.append(f"Agent: {agent.name} ({log.agent_guid[:8]}...)")
                
                if log.tool_guid:
                    tool = session.query(Tool).filter(Tool.guid == log.tool_guid).first()
                    if tool:
                        guid_info.append(f"Tool: {tool.name} ({log.tool_guid[:8]}...)")
                
                if log.task_guid:
                    task = session.query(Task).filter(Task.guid == log.task_guid).first()
                    if task:
                        guid_info.append(f"Task: {task.description[:30]}... ({log.task_guid[:8]}...)")
                
                if guid_info:
                    st.caption(" | ".join(guid_info))
        
        st.divider() 