"""
Custom dashboard widgets for analytics and system monitoring.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from db import SessionLocal
from db.models import Agent, Tool, Task, Log, User, AuditEntry, AgentStatus, ToolStatus, TaskStatus
import pandas as pd

class DashboardWidgets:
    def __init__(self):
        pass
    
    def agent_status_chart(self):
        """Display agent status distribution chart."""
        session = SessionLocal()
        try:
            agents = session.query(Agent).all()
            status_counts = {}
            for status in AgentStatus:
                status_counts[status.value] = 0
            
            for agent in agents:
                status_counts[agent.status.value] += 1
            
            # Create pie chart
            fig = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="Agent Status Distribution",
                color_discrete_map={
                    'online': '#00ff00',
                    'offline': '#ff0000',
                    'busy': '#ffff00',
                    'idle': '#0000ff'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        finally:
            session.close()
    
    def tool_status_chart(self):
        """Display tool status distribution chart."""
        session = SessionLocal()
        try:
            tools = session.query(Tool).all()
            status_counts = {}
            for status in ToolStatus:
                status_counts[status.value] = 0
            
            for tool in tools:
                status_counts[tool.status.value] += 1
            
            # Create bar chart
            fig = px.bar(
                x=list(status_counts.keys()),
                y=list(status_counts.values()),
                title="Tool Status Distribution",
                color=list(status_counts.values()),
                color_continuous_scale='viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
        finally:
            session.close()
    
    def task_status_chart(self):
        """Display task status distribution chart."""
        session = SessionLocal()
        try:
            tasks = session.query(Task).all()
            status_counts = {}
            for status in TaskStatus:
                status_counts[status.value] = 0
            
            for task in tasks:
                status_counts[task.status.value] += 1
            
            # Create donut chart
            fig = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="Task Status Distribution",
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
        finally:
            session.close()
    
    def log_activity_timeline(self, hours: int = 24):
        """Display log activity timeline."""
        session = SessionLocal()
        try:
            # Get logs from the last N hours
            start_time = datetime.utcnow() - timedelta(hours=hours)
            logs = session.query(Log).filter(
                Log.timestamp >= start_time
            ).order_by(Log.timestamp).all()
            
            # Group by hour
            log_data = []
            for log in logs:
                hour = log.timestamp.replace(minute=0, second=0, microsecond=0)
                log_data.append({
                    'hour': hour,
                    'level': log.level
                })
            
            df = pd.DataFrame(log_data)
            if not df.empty:
                hourly_counts = df.groupby(['hour', 'level']).size().reset_index(name='count')
                
                fig = px.line(
                    hourly_counts,
                    x='hour',
                    y='count',
                    color='level',
                    title=f"Log Activity (Last {hours} Hours)"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(f"No log activity in the last {hours} hours")
        finally:
            session.close()
    
    def system_metrics(self):
        """Display system metrics summary."""
        session = SessionLocal()
        try:
            # Count entities
            agent_count = session.query(Agent).count()
            tool_count = session.query(Tool).count()
            task_count = session.query(Task).count()
            user_count = session.query(User).count()
            
            # Count by status
            online_agents = session.query(Agent).filter(Agent.status == AgentStatus.ONLINE).count()
            available_tools = session.query(Tool).filter(Tool.status == ToolStatus.AVAILABLE).count()
            pending_tasks = session.query(Task).filter(Task.status == TaskStatus.PENDING).count()
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Agents", agent_count, f"{online_agents} online")
            
            with col2:
                st.metric("Total Tools", tool_count, f"{available_tools} available")
            
            with col3:
                st.metric("Total Tasks", task_count, f"{pending_tasks} pending")
            
            with col4:
                st.metric("Total Users", user_count)
        finally:
            session.close()
    
    def recent_activity(self, limit: int = 10):
        """Display recent system activity."""
        session = SessionLocal()
        try:
            # Get recent audit entries
            audit_entries = session.query(AuditEntry).order_by(
                AuditEntry.timestamp.desc()
            ).limit(limit).all()
            
            st.subheader("Recent Activity")
            
            for entry in audit_entries:
                user = session.query(User).filter(User.id == entry.user_id).first()
                with st.container():
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.write(f"**{user.username if user else 'Unknown'}**")
                    
                    with col2:
                        st.write(f"{entry.action} {entry.resource_type}")
                    
                    with col3:
                        st.caption(entry.timestamp.strftime('%H:%M:%S'))
                    
                    if entry.details:
                        st.caption(f"Details: {entry.details}")
                    
                    st.divider()
        finally:
            session.close()
    
    def performance_metrics(self):
        """Display performance metrics."""
        session = SessionLocal()
        try:
            # Calculate task completion rate
            total_tasks = session.query(Task).count()
            completed_tasks = session.query(Task).filter(Task.status == TaskStatus.COMPLETED).count()
            failed_tasks = session.query(Task).filter(Task.status == TaskStatus.FAILED).count()
            
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            failure_rate = (failed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # Display metrics
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Task Completion Rate", f"{completion_rate:.1f}%")
            
            with col2:
                st.metric("Task Failure Rate", f"{failure_rate:.1f}%")
            
            # Progress bar for completion rate
            st.progress(completion_rate / 100)
        finally:
            session.close()

# Global widgets instance
dashboard_widgets = DashboardWidgets() 