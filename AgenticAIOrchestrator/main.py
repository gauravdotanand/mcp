import streamlit as st
from ui import agents_ui, tools_ui, tasks_ui, logs_ui, dashboard_ui, inventory_ui, workflow_designer_ui
from signals.handlers import setup_signal_handlers

# Setup signal handlers for automatic logging
setup_signal_handlers()

st.set_page_config(
    page_title="Agentic AI Orchestrator",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Agentic AI Orchestrator")

# Sidebar navigation
page = st.sidebar.selectbox(
    "Navigation",
    ["Dashboard", "Agents", "Tools", "Tasks", "Logs", "Inventory", "Workflow Designer"]
)

# Page routing
if page == "Dashboard":
    dashboard_ui.dashboard_ui()
elif page == "Agents":
    agents_ui.agents_ui()
elif page == "Tools":
    tools_ui.tools_ui()
elif page == "Tasks":
    tasks_ui.tasks_ui()
elif page == "Logs":
    logs_ui.logs_ui()
elif page == "Inventory":
    inventory_ui.inventory_ui()
elif page == "Workflow Designer":
    workflow_designer_ui.workflow_designer_ui() 