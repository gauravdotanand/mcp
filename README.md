# CrewAI Multi-Agent FastAPI MCP Server

This project implements a multi-agent solution using CrewAI and exposes it through FastAPI-MCP server.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

4. Run the server:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

- `/mcp` - MCP server endpoint
- `/docs` - Swagger documentation
- `/redoc` - ReDoc documentation

## Project Structure

- `app/` - Main application directory
  - `main.py` - FastAPI application and MCP server setup
  - `agents/` - CrewAI agent definitions
  - `tasks/` - Task definitions for agents
  - `tools/` - Custom tools for agents 