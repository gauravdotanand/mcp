"""
Multi-agent workflow designer UI for visual orchestration.
Provides drag-and-drop interface for creating agent workflows.
"""

import streamlit as st
import streamlit.components.v1 as components
import json
from typing import Dict, List
from workflows.engine import workflow_engine, WorkflowStepType
from integrations.crewai_adapter import crewai_adapter
from integrations.langgraph_adapter import langgraph_adapter
from agents.communication import agent_comm_manager

def workflow_designer_ui():
    st.header("Multi-Agent Workflow Designer")
    
    # Sidebar for workflow management
    with st.sidebar:
        st.subheader("Workflow Management")
        
        # Create new workflow
        workflow_name = st.text_input("New Workflow Name")
        if st.button("Create Workflow"):
            if workflow_name:
                workflow = workflow_engine.create_workflow(workflow_name)
                st.success(f"Created workflow: {workflow.workflow_id}")
                st.session_state.current_workflow = workflow.workflow_id
        
        # Select existing workflow
        existing_workflows = list(workflow_engine.workflows.keys())
        if existing_workflows:
            selected_workflow = st.selectbox(
                "Select Workflow",
                existing_workflows,
                format_func=lambda x: workflow_engine.workflows[x].name
            )
            if st.button("Load Workflow"):
                st.session_state.current_workflow = selected_workflow
    
    # Main workflow designer area
    if 'current_workflow' in st.session_state:
        workflow_id = st.session_state.current_workflow
        workflow = workflow_engine.workflows[workflow_id]
        
        st.subheader(f"Workflow: {workflow.name}")
        
        # Workflow status
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Status", workflow.status)
        with col2:
            st.metric("Steps", len(workflow.steps))
        with col3:
            if st.button("Execute Workflow"):
                try:
                    result = workflow_engine.execute_workflow(workflow_id)
                    st.success("Workflow executed successfully!")
                    st.json(result)
                except Exception as e:
                    st.error(f"Workflow execution failed: {str(e)}")
        
        # Step configuration
        st.subheader("Configure Steps")
        
        # Agent task step
        with st.expander("Add Agent Task"):
            col1, col2 = st.columns(2)
            with col1:
                agent_capability = st.text_input("Agent Capability")
                task_data = st.text_area("Task Data (JSON)")
            with col2:
                dependencies = st.multiselect(
                    "Dependencies",
                    [step.step_id for step in workflow.steps]
                )
            
            if st.button("Add Agent Task"):
                try:
                    task_json = json.loads(task_data) if task_data else {}
                    step_id = workflow.add_agent_task(
                        agent_capability=agent_capability,
                        task_data=task_json,
                        dependencies=dependencies
                    )
                    st.success(f"Added agent task: {step_id}")
                except Exception as e:
                    st.error(f"Failed to add agent task: {str(e)}")
        
        # Sequential steps
        with st.expander("Add Sequential Steps"):
            num_steps = st.number_input("Number of Steps", min_value=1, max_value=10, value=2)
            steps_config = []
            
            for i in range(num_steps):
                with st.container():
                    st.write(f"Step {i+1}")
                    col1, col2 = st.columns(2)
                    with col1:
                        step_type = st.selectbox(
                            f"Step {i+1} Type",
                            ["agent_task", "sequential", "parallel"],
                            key=f"step_type_{i}"
                        )
                    with col2:
                        step_config = st.text_area(
                            f"Step {i+1} Config (JSON)",
                            value="{}",
                            key=f"step_config_{i}"
                        )
                    steps_config.append({
                        "type": step_type,
                        "config": step_config
                    })
            
            if st.button("Add Sequential Steps"):
                try:
                    step_ids = workflow.add_sequential_steps(steps_config)
                    st.success(f"Added {len(step_ids)} sequential steps")
                except Exception as e:
                    st.error(f"Failed to add sequential steps: {str(e)}")
        
        # Parallel steps
        with st.expander("Add Parallel Steps"):
            num_parallel = st.number_input("Number of Parallel Steps", min_value=1, max_value=5, value=2)
            parallel_config = []
            
            for i in range(num_parallel):
                with st.container():
                    st.write(f"Parallel Step {i+1}")
                    col1, col2 = st.columns(2)
                    with col1:
                        step_type = st.selectbox(
                            f"Parallel Step {i+1} Type",
                            ["agent_task", "sequential", "parallel"],
                            key=f"parallel_type_{i}"
                        )
                    with col2:
                        step_config = st.text_area(
                            f"Parallel Step {i+1} Config (JSON)",
                            value="{}",
                            key=f"parallel_config_{i}"
                        )
                    parallel_config.append({
                        "type": step_type,
                        "config": step_config
                    })
            
            if st.button("Add Parallel Steps"):
                try:
                    step_ids = workflow.add_parallel_steps(parallel_config)
                    st.success(f"Added {len(step_ids)} parallel steps")
                except Exception as e:
                    st.error(f"Failed to add parallel steps: {str(e)}")
        
        # Workflow visualization
        st.subheader("Workflow Visualization")
        
        # Simple text-based visualization
        for i, step in enumerate(workflow.steps):
            with st.container():
                col1, col2, col3 = st.columns([1, 3, 1])
                with col1:
                    st.write(f"Step {i+1}")
                with col2:
                    st.write(f"**{step.step_type.value}** - {step.status}")
                    if step.dependencies:
                        st.caption(f"Dependencies: {', '.join(step.dependencies)}")
                with col3:
                    if step.status == "completed":
                        st.success("✓")
                    elif step.status == "failed":
                        st.error("✗")
                    else:
                        st.info("⏳")
        
        # Integration section
        st.subheader("External Integrations")
        
        # CrewAI integration
        with st.expander("CrewAI Integration"):
            if crewai_adapter.available:
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Registered CrewAI Agents:**")
                    crewai_agents = crewai_adapter.list_agents()
                    for agent in crewai_agents:
                        st.write(f"- {agent['name']} ({agent['agent_guid'][:8]}...)")
                
                with col2:
                    st.write("**Created Crews:**")
                    crews = crewai_adapter.list_crews()
                    for crew in crews:
                        st.write(f"- {crew['crew_id']} ({len(crew['agents'])} agents)")
            else:
                st.warning("CrewAI not available. Install with: `pip install crewai`")
        
        # LangGraph integration
        with st.expander("LangGraph Integration"):
            if langgraph_adapter.available:
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Registered LangGraph Agents:**")
                    langgraph_agents = list(langgraph_adapter.langgraph_agents.keys())
                    for agent_guid in langgraph_agents:
                        st.write(f"- {agent_guid[:8]}...")
                
                with col2:
                    st.write("**Created Workflows:**")
                    workflows = langgraph_adapter.list_workflows()
                    for workflow_info in workflows:
                        st.write(f"- {workflow_info['workflow_id']}")
            else:
                st.warning("LangGraph not available. Install with: `pip install langgraph langchain-core`")
        
        # Agent communication
        st.subheader("Agent Communication")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Registered Agents:**")
            for agent_guid, agent_info in agent_comm_manager.agent_registry.items():
                st.write(f"- {agent_guid[:8]}... ({agent_info['protocol']})")
        
        with col2:
            st.write("**Shared Contexts:**")
            for context_id, context in agent_comm_manager.shared_contexts.items():
                st.write(f"- {context_id} ({len(context.data)} items)")
        
        # Message queue
        if agent_comm_manager.message_queue:
            st.write("**Recent Messages:**")
            for message in agent_comm_manager.message_queue[-5:]:
                st.caption(f"{message.sender_guid[:8]} → {message.recipient_guid[:8]}: {message.message_type}")
    
    else:
        st.info("Create or select a workflow to start designing")
        
        # Show available integrations
        st.subheader("Available Integrations")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**CrewAI**")
            st.write("- Multi-agent collaboration")
            st.write("- Role-based agents")
            st.write("- Sequential task execution")
            if not crewai_adapter.available:
                st.warning("Not installed")
        
        with col2:
            st.write("**LangGraph**")
            st.write("- State-based workflows")
            st.write("- Conditional routing")
            st.write("- Complex agent interactions")
            if not langgraph_adapter.available:
                st.warning("Not installed") 