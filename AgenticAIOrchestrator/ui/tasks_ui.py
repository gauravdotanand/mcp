import streamlit as st
import pandas as pd
from tasks.manager import create_task, update_task_status
from db import SessionLocal
from db.models import Task, TaskStatus, Agent, Tool
import requests

API_BASE_URL = "http://localhost:8000/tasks"

def tasks_ui():
    st.header("Tasks Management")
    session = SessionLocal()
    tasks = session.query(Task).all()
    agents = session.query(Agent).all()
    tools = session.query(Tool).all()
    session.close()

    st.subheader("Create New Task")
    with st.form("add_task_form"):
        description = st.text_input("Task Description")
        agent_id = st.selectbox("Assign to Agent", [None] + [a.id for a in agents], format_func=lambda x: "None" if x is None else next((a.name for a in agents if a.id == x), str(x)))
        tool_id = st.selectbox("Assign Tool", [None] + [t.id for t in tools], format_func=lambda x: "None" if x is None else next((t.name for t in tools if t.id == x), str(x)))
        submitted = st.form_submit_button("Create Task")
        if submitted and description:
            create_task(description, agent_id=agent_id, tool_id=tool_id)
            st.success("Task created.")
            st.rerun()

    st.subheader("Import Tasks (Bulk)")
    col_import1, col_import2 = st.columns(2)
    with col_import1:
        csv_file = st.file_uploader("Import Tasks from CSV", type=["csv"], key="import_tasks_csv")
        if csv_file and st.button("Upload CSV"):
            files = {"file": (csv_file.name, csv_file.getvalue())}
            response = requests.post(f"{API_BASE_URL}/import/csv", files=files)
            if response.ok:
                st.success(f"Imported: {response.json().get('created')}")
                st.rerun()
            else:
                st.error("Import failed.")
    with col_import2:
        json_file = st.file_uploader("Import Tasks from JSON", type=["json"], key="import_tasks_json")
        if json_file and st.button("Upload JSON"):
            files = {"file": (json_file.name, json_file.getvalue())}
            response = requests.post(f"{API_BASE_URL}/import/json", files=files)
            if response.ok:
                st.success(f"Imported: {response.json().get('created')}")
                st.rerun()
            else:
                st.error("Import failed.")

    st.subheader("Existing Tasks")
    
    # Export buttons
    col_export1, col_export2 = st.columns(2)
    with col_export1:
        if st.button("Export Tasks as CSV"):
            response = requests.get(f"{API_BASE_URL}/export/csv")
            st.download_button("Download CSV", response.content, file_name="tasks.csv")
    with col_export2:
        if st.button("Export Tasks as JSON"):
            response = requests.get(f"{API_BASE_URL}/export/json")
            st.download_button("Download JSON", response.content, file_name="tasks.json")
    
    # Pagination
    items_per_page = st.selectbox("Items per page", [5, 10, 20, 50], index=1)
    total_tasks = len(tasks)
    total_pages = (total_tasks + items_per_page - 1) // items_per_page
    
    if total_pages > 1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            current_page = st.selectbox("Page", range(1, total_pages + 1), key="tasks_page")
    else:
        current_page = 1
    
    # Calculate start and end indices
    start_idx = (current_page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_tasks)
    current_tasks = tasks[start_idx:end_idx]
    
    # Create a proper table display using pandas DataFrame
    if current_tasks:
        # Prepare data for the table
        tasks_data = []
        for task in current_tasks:
            agent_name = task.agent.name if task.agent else "None"
            tool_name = task.tool.name if task.tool else "None"
            tasks_data.append({
                "Description": task.description,
                "GUID": task.guid,
                "Status": task.status.value,
                "Agent": agent_name,
                "Tool": tool_name,
                "ID": task.id
            })
        
        # Create DataFrame
        df = pd.DataFrame(tasks_data)
        
        # Display the table with proper formatting
        st.dataframe(
            df[["Description", "GUID", "Status", "Agent", "Tool"]], 
            use_container_width=True,
            hide_index=True
        )
        
        # Pagination info
        st.caption(f"Showing {start_idx + 1}-{end_idx} of {total_tasks} tasks")
        
        # Action buttons for each task
        st.subheader("Task Actions")
        for task in current_tasks:
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
                
                with col1:
                    st.write(f"**{task.description}**")
                    st.caption(f"GUID: {task.guid[:8]}...")
                    if task.agent or task.tool:
                        details = []
                        if task.agent:
                            details.append(f"Agent: {task.agent.name}")
                        if task.tool:
                            details.append(f"Tool: {task.tool.name}")
                        st.caption(" | ".join(details))
                
                with col2:
                    # Edit button
                    if st.button("✏️ Edit", key=f"edit_task_{task.id}"):
                        st.session_state[f"editing_task_{task.id}"] = True
                
                with col3:
                    # Delete button
                    if st.button("🗑️ Delete", key=f"delete_task_{task.id}"):
                        st.session_state[f"confirm_delete_task_{task.id}"] = True
                
                with col4:
                    # Status change button
                    if st.button("🔄 Status", key=f"status_task_{task.id}"):
                        st.session_state[f"changing_status_task_{task.id}"] = True
                
                with col5:
                    # Current status display
                    if task.status == TaskStatus.COMPLETED:
                        st.success(task.status.value)
                    elif task.status == TaskStatus.FAILED:
                        st.error(task.status.value)
                    elif task.status == TaskStatus.RUNNING:
                        st.warning(task.status.value)
                    else:
                        st.info(task.status.value)
                
                # Edit form
                if st.session_state.get(f"editing_task_{task.id}", False):
                    with st.form(f"edit_task_{task.id}"):
                        new_description = st.text_input("New Description", value=task.description, key=f"edit_desc_task_{task.id}")
                        new_agent_id = st.selectbox(
                            "Assign to Agent", 
                            [None] + [a.id for a in agents], 
                            index=0 if task.agent is None else [a.id for a in agents].index(task.agent.id) + 1,
                            format_func=lambda x: "None" if x is None else next((a.name for a in agents if a.id == x), str(x)),
                            key=f"edit_agent_task_{task.id}"
                        )
                        new_tool_id = st.selectbox(
                            "Assign Tool", 
                            [None] + [t.id for t in tools], 
                            index=0 if task.tool is None else [t.id for t in tools].index(task.tool.id) + 1,
                            format_func=lambda x: "None" if x is None else next((t.name for t in tools if t.id == x), str(x)),
                            key=f"edit_tool_task_{task.id}"
                        )
                        col_submit, col_cancel = st.columns(2)
                        with col_submit:
                            if st.form_submit_button("Save"):
                                # Update task via API
                                update_data = {
                                    "description": new_description,
                                    "agent_id": new_agent_id,
                                    "tool_id": new_tool_id
                                }
                                response = requests.put(f"{API_BASE_URL}/{task.id}", json=update_data)
                                if response.ok:
                                    st.success(f"Updated task description to '{new_description}'")
                                    st.session_state[f"editing_task_{task.id}"] = False
                                    st.rerun()
                                else:
                                    st.error("Failed to update task")
                        with col_cancel:
                            if st.form_submit_button("Cancel"):
                                st.session_state[f"editing_task_{task.id}"] = False
                                st.rerun()
                
                # Delete confirmation
                if st.session_state.get(f"confirm_delete_task_{task.id}", False):
                    st.warning(f"Are you sure you want to delete task '{task.description}'?")
                    col_confirm, col_cancel = st.columns(2)
                    with col_confirm:
                        if st.button("Yes, Delete", key=f"confirm_delete_yes_task_{task.id}"):
                            # Delete task via API
                            response = requests.delete(f"{API_BASE_URL}/{task.id}")
                            if response.ok:
                                st.success(f"Deleted task '{task.description}'")
                                st.session_state[f"confirm_delete_task_{task.id}"] = False
                                st.rerun()
                            else:
                                st.error("Failed to delete task")
                    with col_cancel:
                        if st.button("Cancel", key=f"cancel_delete_task_{task.id}"):
                            st.session_state[f"confirm_delete_task_{task.id}"] = False
                            st.rerun()
                
                # Status change form
                if st.session_state.get(f"changing_status_task_{task.id}", False):
                    with st.form(f"change_status_task_{task.id}"):
                        new_status = st.selectbox(
                            "New Status",
                            [status.value for status in TaskStatus],
                            index=[status.value for status in TaskStatus].index(task.status.value),
                            key=f"new_status_task_{task.id}"
                        )
                        col_submit, col_cancel = st.columns(2)
                        with col_submit:
                            if st.form_submit_button("Update Status"):
                                if new_status != task.status.value:
                                    update_task_status(task.id, TaskStatus(new_status))
                                    st.success(f"Updated task status to {new_status}")
                                    st.session_state[f"changing_status_task_{task.id}"] = False
                                    st.rerun()
                        with col_cancel:
                            if st.form_submit_button("Cancel"):
                                st.session_state[f"changing_status_task_{task.id}"] = False
                                st.rerun()
                
                st.divider()
    else:
        st.info("No tasks found. Create some tasks to get started!") 