# AgenticAIOrchestrator

A multi-agent orchestration platform for managing agents, tools, tasks, inventory, logs, and statuses, with a modern Streamlit UI and event-driven architecture using GUID-based tracking.

## Features
- **GUID-based Entity Tracking**: All agents, tools, and tasks have unique GUIDs for precise tracking
- **Agent Management**: Status tracking, registration, monitoring with GUID-based logging
- **Tool Management**: Registration, assignment, monitoring with GUID-based logging
- **Task Management**: Assignment, tracking, status with GUID-based logging
- **Inventory Management**: Track resources and assets
- **Centralized Logging**: Comprehensive logging system with GUID references
- **Real-time Status Updates**: Event-driven architecture using signals/events
- **Advanced Log Filtering**: Filter logs by agent, tool, task, and log level
- **Signal-based Event Handling**: Automatic logging of all system events

## Architecture

### GUID System
- **Agents**: Each agent has a unique GUID for tracking and logging
- **Tools**: Each tool has a unique GUID for tracking and logging  
- **Tasks**: Each task has a unique GUID for tracking and logging
- **Logs**: All log entries can reference agent, tool, and task GUIDs

### Signal System
- **agent_status_changed**: Triggered when agent status changes
- **tool_status_changed**: Triggered when tool status changes
- **task_status_changed**: Triggered when task status changes
- **log_created**: Triggered when new logs are created

### Logging System
- **Agent-specific logs**: Track all agent activities
- **Tool-specific logs**: Track all tool usage
- **Task-specific logs**: Track all task progress
- **Combined logs**: Track interactions between agents, tools, and tasks

## Tech Stack
- **Frontend**: Streamlit (UI)
- **Backend**: Python
- **Database**: SQLAlchemy (ORM) + SQLite
- **Events**: Blinker (signals/events)
- **GUIDs**: UUID4 for unique identification

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Database Migration (if upgrading from older version)
```bash
python migrate_db.py
```

### 3. Run the Application
```bash
streamlit run main.py
```

## Usage

### Creating Agents
- Navigate to the "Agents" page
- Enter agent name and click "Add Agent"
- Each agent gets a unique GUID automatically
- Monitor agent status and activities in real-time

### Creating Tools
- Navigate to the "Tools" page
- Enter tool name and click "Add Tool"
- Each tool gets a unique GUID automatically
- Track tool usage and status

### Creating Tasks
- Navigate to the "Tasks" page
- Enter task description and optionally assign to agent/tool
- Each task gets a unique GUID automatically
- Monitor task progress and completion

### Viewing Logs
- Navigate to the "Logs" page
- Filter logs by:
  - Log level (INFO, WARNING, ERROR, DEBUG)
  - Agent
  - Tool
  - Task
- View detailed log entries with GUID references

## Database Schema

### Agents Table
- `id`: Primary key
- `guid`: Unique GUID for tracking
- `name`: Agent name
- `status`: Current status (online, offline, busy, idle)
- `last_seen`: Last activity timestamp

### Tools Table
- `id`: Primary key
- `guid`: Unique GUID for tracking
- `name`: Tool name
- `status`: Current status (available, in_use, maintenance)

### Tasks Table
- `id`: Primary key
- `guid`: Unique GUID for tracking
- `description`: Task description
- `status`: Current status (pending, running, completed, failed)
- `agent_id`: Reference to assigned agent
- `tool_id`: Reference to assigned tool

### Logs Table
- `id`: Primary key
- `message`: Log message
- `timestamp`: Log timestamp
- `level`: Log level
- `agent_guid`: Reference to agent GUID (optional)
- `tool_guid`: Reference to tool GUID (optional)
- `task_guid`: Reference to task GUID (optional)

## API Reference

### Logger Class
```python
from logs.logger import logger

# Log agent event
logger.log_agent_event(agent_guid, "Agent started", "INFO")

# Log tool event
logger.log_tool_event(tool_guid, "Tool activated", "INFO")

# Log task event
logger.log_task_event(task_guid, "Task completed", "INFO")

# Log combined event
logger.log_full_event(agent_guid, tool_guid, task_guid, "Full workflow", "INFO")
```

### Signal Usage
```python
from signals.events import agent_status_changed

# Emit signal with GUID
agent_status_changed.send(
    agent_id=agent.id,
    agent_guid=agent.guid,
    old_status=old_status,
    new_status=new_status
)
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License
MIT License 