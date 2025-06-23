import streamlit as st
from db import SessionLocal
from db.models import Agent, Tool, Task, Log

def dashboard_ui():
    st.header("Dashboard")
    session = SessionLocal()
    agent_count = session.query(Agent).count()
    tool_count = session.query(Tool).count()
    task_count = session.query(Task).count()
    log_count = session.query(Log).count()
    session.close()
    st.metric("Agents", agent_count)
    st.metric("Tools", tool_count)
    st.metric("Tasks", task_count)
    st.metric("Logs", log_count) 