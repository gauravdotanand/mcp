import streamlit as st
import pandas as pd
from tools.manager import register_tool, update_tool_status
from db import SessionLocal
from db.models import Tool, ToolStatus
import requests

API_BASE_URL = "http://localhost:8000/tools"

def tools_ui():
    st.header("Tools Management")
    session = SessionLocal()
    tools = session.query(Tool).all()
    session.close()

    st.subheader("Add New Tool")
    with st.form("add_tool_form"):
        name = st.text_input("Tool Name")
        submitted = st.form_submit_button("Add Tool")
        if submitted and name:
            register_tool(name)
            st.success(f"Tool '{name}' added.")
            st.rerun()

    st.subheader("Import Tools (Bulk)")
    col_import1, col_import2 = st.columns(2)
    with col_import1:
        csv_file = st.file_uploader("Import Tools from CSV", type=["csv"], key="import_tools_csv")
        if csv_file and st.button("Upload CSV"):
            files = {"file": (csv_file.name, csv_file.getvalue())}
            response = requests.post(f"{API_BASE_URL}/import/csv", files=files)
            if response.ok:
                st.success(f"Imported: {response.json().get('created')}")
                st.rerun()
            else:
                st.error("Import failed.")
    with col_import2:
        json_file = st.file_uploader("Import Tools from JSON", type=["json"], key="import_tools_json")
        if json_file and st.button("Upload JSON"):
            files = {"file": (json_file.name, json_file.getvalue())}
            response = requests.post(f"{API_BASE_URL}/import/json", files=files)
            if response.ok:
                st.success(f"Imported: {response.json().get('created')}")
                st.rerun()
            else:
                st.error("Import failed.")

    st.subheader("Existing Tools")
    
    # Export buttons
    col_export1, col_export2 = st.columns(2)
    with col_export1:
        if st.button("Export Tools as CSV"):
            response = requests.get(f"{API_BASE_URL}/export/csv")
            st.download_button("Download CSV", response.content, file_name="tools.csv")
    with col_export2:
        if st.button("Export Tools as JSON"):
            response = requests.get(f"{API_BASE_URL}/export/json")
            st.download_button("Download JSON", response.content, file_name="tools.json")
    
    # Pagination
    items_per_page = st.selectbox("Items per page", [5, 10, 20, 50], index=1)
    total_tools = len(tools)
    total_pages = (total_tools + items_per_page - 1) // items_per_page
    
    if total_pages > 1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            current_page = st.selectbox("Page", range(1, total_pages + 1), key="tools_page")
    else:
        current_page = 1
    
    # Calculate start and end indices
    start_idx = (current_page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_tools)
    current_tools = tools[start_idx:end_idx]
    
    # Create a proper table display using pandas DataFrame
    if current_tools:
        # Prepare data for the table
        tools_data = []
        for tool in current_tools:
            tools_data.append({
                "Name": tool.name,
                "GUID": tool.guid,
                "Status": tool.status.value,
                "ID": tool.id
            })
        
        # Create DataFrame
        df = pd.DataFrame(tools_data)
        
        # Display the table with proper formatting
        st.dataframe(
            df[["Name", "GUID", "Status"]], 
            use_container_width=True,
            hide_index=True
        )
        
        # Pagination info
        st.caption(f"Showing {start_idx + 1}-{end_idx} of {total_tools} tools")
        
        # Action buttons for each tool
        st.subheader("Tool Actions")
        for tool in current_tools:
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                
                with col1:
                    st.write(f"**{tool.name}**")
                    st.caption(f"GUID: {tool.guid[:8]}...")
                
                with col2:
                    # Edit button
                    if st.button("✏️ Edit", key=f"edit_tool_{tool.id}"):
                        st.session_state[f"editing_tool_{tool.id}"] = True
                
                with col3:
                    # Delete button
                    if st.button("🗑️ Delete", key=f"delete_tool_{tool.id}"):
                        st.session_state[f"confirm_delete_tool_{tool.id}"] = True
                
                with col4:
                    # Status change button
                    if st.button("🔄 Status", key=f"status_tool_{tool.id}"):
                        st.session_state[f"changing_status_tool_{tool.id}"] = True
                
                with col5:
                    # Current status display
                    if tool.status == ToolStatus.AVAILABLE:
                        st.success(tool.status.value)
                    elif tool.status == ToolStatus.IN_USE:
                        st.warning(tool.status.value)
                    else:
                        st.error(tool.status.value)
                
                # Edit form
                if st.session_state.get(f"editing_tool_{tool.id}", False):
                    with st.form(f"edit_tool_{tool.id}"):
                        new_name = st.text_input("New Name", value=tool.name, key=f"edit_name_tool_{tool.id}")
                        col_submit, col_cancel = st.columns(2)
                        with col_submit:
                            if st.form_submit_button("Save"):
                                # Update tool name via API
                                response = requests.put(f"{API_BASE_URL}/{tool.id}", json={"name": new_name})
                                if response.ok:
                                    st.success(f"Updated tool name to '{new_name}'")
                                    st.session_state[f"editing_tool_{tool.id}"] = False
                                    st.rerun()
                                else:
                                    st.error("Failed to update tool")
                        with col_cancel:
                            if st.form_submit_button("Cancel"):
                                st.session_state[f"editing_tool_{tool.id}"] = False
                                st.rerun()
                
                # Delete confirmation
                if st.session_state.get(f"confirm_delete_tool_{tool.id}", False):
                    st.warning(f"Are you sure you want to delete tool '{tool.name}'?")
                    col_confirm, col_cancel = st.columns(2)
                    with col_confirm:
                        if st.button("Yes, Delete", key=f"confirm_delete_yes_tool_{tool.id}"):
                            # Delete tool via API
                            response = requests.delete(f"{API_BASE_URL}/{tool.id}")
                            if response.ok:
                                st.success(f"Deleted tool '{tool.name}'")
                                st.session_state[f"confirm_delete_tool_{tool.id}"] = False
                                st.rerun()
                            else:
                                st.error("Failed to delete tool")
                    with col_cancel:
                        if st.button("Cancel", key=f"cancel_delete_tool_{tool.id}"):
                            st.session_state[f"confirm_delete_tool_{tool.id}"] = False
                            st.rerun()
                
                # Status change form
                if st.session_state.get(f"changing_status_tool_{tool.id}", False):
                    with st.form(f"change_status_tool_{tool.id}"):
                        new_status = st.selectbox(
                            "New Status",
                            [status.value for status in ToolStatus],
                            index=[status.value for status in ToolStatus].index(tool.status.value),
                            key=f"new_status_tool_{tool.id}"
                        )
                        col_submit, col_cancel = st.columns(2)
                        with col_submit:
                            if st.form_submit_button("Update Status"):
                                if new_status != tool.status.value:
                                    update_tool_status(tool.id, ToolStatus(new_status))
                                    st.success(f"Updated {tool.name} status to {new_status}")
                                    st.session_state[f"changing_status_tool_{tool.id}"] = False
                                    st.rerun()
                        with col_cancel:
                            if st.form_submit_button("Cancel"):
                                st.session_state[f"changing_status_tool_{tool.id}"] = False
                                st.rerun()
                
                st.divider()
    else:
        st.info("No tools found. Add some tools to get started!") 