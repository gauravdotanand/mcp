import streamlit as st
import pandas as pd
from agents.manager import register_agent, update_agent_status
from db import SessionLocal
from db.models import Agent, AgentStatus
import requests

API_BASE_URL = "http://localhost:8000/agents"

def agents_ui():
    st.header("Agents Management")
    session = SessionLocal()
    agents = session.query(Agent).all()
    session.close()

    st.subheader("Add New Agent")
    with st.form("add_agent_form"):
        name = st.text_input("Agent Name")
        submitted = st.form_submit_button("Add Agent")
        if submitted and name:
            register_agent(name)
            st.success(f"Agent '{name}' added.")
            st.rerun()

    st.subheader("Import Agents (Bulk)")
    col_import1, col_import2 = st.columns(2)
    with col_import1:
        csv_file = st.file_uploader("Import Agents from CSV", type=["csv"], key="import_agents_csv")
        if csv_file and st.button("Upload CSV"):
            files = {"file": (csv_file.name, csv_file.getvalue())}
            response = requests.post(f"{API_BASE_URL}/import/csv", files=files)
            if response.ok:
                st.success(f"Imported: {response.json().get('created')}")
                st.rerun()
            else:
                st.error("Import failed.")
    with col_import2:
        json_file = st.file_uploader("Import Agents from JSON", type=["json"], key="import_agents_json")
        if json_file and st.button("Upload JSON"):
            files = {"file": (json_file.name, json_file.getvalue())}
            response = requests.post(f"{API_BASE_URL}/import/json", files=files)
            if response.ok:
                st.success(f"Imported: {response.json().get('created')}")
                st.rerun()
            else:
                st.error("Import failed.")

    st.subheader("Existing Agents")
    
    # Export buttons
    col_export1, col_export2 = st.columns(2)
    with col_export1:
        if st.button("Export Agents as CSV"):
            response = requests.get(f"{API_BASE_URL}/export/csv")
            st.download_button("Download CSV", response.content, file_name="agents.csv")
    with col_export2:
        if st.button("Export Agents as JSON"):
            response = requests.get(f"{API_BASE_URL}/export/json")
            st.download_button("Download JSON", response.content, file_name="agents.json")
    
    # Pagination
    items_per_page = st.selectbox("Items per page", [5, 10, 20, 50], index=1)
    total_agents = len(agents)
    total_pages = (total_agents + items_per_page - 1) // items_per_page
    
    if total_pages > 1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            current_page = st.selectbox("Page", range(1, total_pages + 1), key="agents_page")
    else:
        current_page = 1
    
    # Calculate start and end indices
    start_idx = (current_page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_agents)
    current_agents = agents[start_idx:end_idx]
    
    # Create a proper table display using pandas DataFrame
    if current_agents:
        # Prepare data for the table
        agents_data = []
        for agent in current_agents:
            agents_data.append({
                "Name": agent.name,
                "GUID": agent.guid,
                "Status": agent.status.value,
                "Last Seen": agent.last_seen.strftime('%Y-%m-%d %H:%M:%S'),
                "ID": agent.id
            })
        
        # Create DataFrame
        df = pd.DataFrame(agents_data)
        
        # Display the table with proper formatting
        st.dataframe(
            df[["Name", "GUID", "Status", "Last Seen"]], 
            use_container_width=True,
            hide_index=True
        )
        
        # Pagination info
        st.caption(f"Showing {start_idx + 1}-{end_idx} of {total_agents} agents")
        
        # Action buttons for each agent
        st.subheader("Agent Actions")
        for agent in current_agents:
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                
                with col1:
                    st.write(f"**{agent.name}**")
                    st.caption(f"GUID: {agent.guid[:8]}...")
                
                with col2:
                    # Edit button
                    if st.button("✏️ Edit", key=f"edit_{agent.id}"):
                        st.session_state[f"editing_agent_{agent.id}"] = True
                
                with col3:
                    # Delete button
                    if st.button("🗑️ Delete", key=f"delete_{agent.id}"):
                        st.session_state[f"confirm_delete_{agent.id}"] = True
                
                with col4:
                    # Status change button
                    if st.button("🔄 Status", key=f"status_{agent.id}"):
                        st.session_state[f"changing_status_{agent.id}"] = True
                
                with col5:
                    # Current status display
                    if agent.status == AgentStatus.ONLINE:
                        st.success(agent.status.value)
                    elif agent.status == AgentStatus.OFFLINE:
                        st.error(agent.status.value)
                    elif agent.status == AgentStatus.BUSY:
                        st.warning(agent.status.value)
                    else:
                        st.info(agent.status.value)
                
                # Edit form
                if st.session_state.get(f"editing_agent_{agent.id}", False):
                    with st.form(f"edit_agent_{agent.id}"):
                        new_name = st.text_input("New Name", value=agent.name, key=f"edit_name_{agent.id}")
                        col_submit, col_cancel = st.columns(2)
                        with col_submit:
                            if st.form_submit_button("Save"):
                                # Update agent name via API
                                response = requests.put(f"{API_BASE_URL}/{agent.id}", json={"name": new_name})
                                if response.ok:
                                    st.success(f"Updated agent name to '{new_name}'")
                                    st.session_state[f"editing_agent_{agent.id}"] = False
                                    st.rerun()
                                else:
                                    st.error("Failed to update agent")
                        with col_cancel:
                            if st.form_submit_button("Cancel"):
                                st.session_state[f"editing_agent_{agent.id}"] = False
                                st.rerun()
                
                # Delete confirmation
                if st.session_state.get(f"confirm_delete_{agent.id}", False):
                    st.warning(f"Are you sure you want to delete agent '{agent.name}'?")
                    col_confirm, col_cancel = st.columns(2)
                    with col_confirm:
                        if st.button("Yes, Delete", key=f"confirm_delete_yes_{agent.id}"):
                            # Delete agent via API
                            response = requests.delete(f"{API_BASE_URL}/{agent.id}")
                            if response.ok:
                                st.success(f"Deleted agent '{agent.name}'")
                                st.session_state[f"confirm_delete_{agent.id}"] = False
                                st.rerun()
                            else:
                                st.error("Failed to delete agent")
                    with col_cancel:
                        if st.button("Cancel", key=f"cancel_delete_{agent.id}"):
                            st.session_state[f"confirm_delete_{agent.id}"] = False
                            st.rerun()
                
                # Status change form
                if st.session_state.get(f"changing_status_{agent.id}", False):
                    with st.form(f"change_status_{agent.id}"):
                        new_status = st.selectbox(
                            "New Status",
                            [status.value for status in AgentStatus],
                            index=[status.value for status in AgentStatus].index(agent.status.value),
                            key=f"new_status_{agent.id}"
                        )
                        col_submit, col_cancel = st.columns(2)
                        with col_submit:
                            if st.form_submit_button("Update Status"):
                                if new_status != agent.status.value:
                                    update_agent_status(agent.id, AgentStatus(new_status))
                                    st.success(f"Updated {agent.name} status to {new_status}")
                                    st.session_state[f"changing_status_{agent.id}"] = False
                                    st.rerun()
                        with col_cancel:
                            if st.form_submit_button("Cancel"):
                                st.session_state[f"changing_status_{agent.id}"] = False
                                st.rerun()
                
                st.divider()
    else:
        st.info("No agents found. Add some agents to get started!") 