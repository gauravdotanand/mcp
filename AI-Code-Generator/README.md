# AI Code Generator (Phase 4 - Streamlit UI)

## Overview
A complete AI code generation system with FastAPI backend and Streamlit web interface, supporting custom coding approaches, multi-user authentication, and mainframe context.

## Features
- **Multi-user Support**: API key-based authentication with data isolation
- **Token Optimization**: Automatic truncation, coding style summaries, and smart sample selection
- **Embedding-Based Similarity Search**: Uses semantic similarity to find relevant code samples
- **Mainframe Context**: Specialized for mainframe data extraction and string manipulation
- **Beautiful Web UI**: Streamlit interface for easy interaction

## Quick Start

### 1. Setup Backend
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export AZURE_OPENAI_API_KEY="your_azure_openai_key"
export AZURE_OPENAI_ENDPOINT="your_azure_openai_endpoint"

# Initialize database
python -c "from app.db import Base, engine; Base.metadata.create_all(bind=engine)"

# Start FastAPI server
uvicorn app.main:app --reload
```

### 2. Setup Frontend
```bash
# In a new terminal, start Streamlit
streamlit run streamlit_app.py
```

### 3. Access the Application
- **Web UI**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │   FastAPI API   │    │  Azure OpenAI   │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (LLM)         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   SQLite DB     │
                       │   (Storage)     │
                       └─────────────────┘
```

## Web UI Features

### 🚀 Code Generation
- **Task Description**: Describe what code you want to generate
- **Mainframe Context**: Provide mainframe screen data
- **Extraction Requirements**: Specify data extraction needs
- **Model Selection**: Choose from GPT-4, GPT-4o, or GPT-3.5-turbo
- **Sample Selection**: Choose from your stored coding approach samples
- **Direct Samples**: Paste code samples directly
- **Download**: Download generated code as files

### 📚 Sample Management
- **Add Samples**: Create new coding approach samples
- **View Samples**: See all your samples with style analysis
- **Delete Samples**: Remove unwanted samples
- **Style Analysis**: Automatic detection of coding patterns

### 📊 System Status
- **API Status**: Check backend connectivity
- **User Info**: View account details
- **Sample Statistics**: See usage analytics
- **Usage Tips**: Helpful guidance

## API Usage (Programmatic Access)

### Authentication
All endpoints (except user creation) require an API key in the `X-API-Key` header.

### Create a User
```bash
curl -X POST "http://localhost:8000/users" \
     -H "Content-Type: application/json" \
     -d '{"username": "your_username", "email": "your_email@example.com"}'
```

### Generate Code
```bash
curl -X POST "http://localhost:8000/generate-code" \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your_api_key_here" \
     -d '{
       "prompt": "Create a function to extract data from mainframe screen",
       "context": "Mainframe screen data...",
       "extraction_requirements": "Extract account number from columns 10-20",
       "model": "gpt-4"
     }'
```

## Environment Variables
- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint
- `AZURE_OPENAI_API_VERSION`: API version (default: 2023-05-15)
- `DATABASE_URL`: Database URL (default: SQLite)

## Token Optimization Features
- **Automatic Truncation**: Code samples are automatically truncated to fit within token limits
- **Coding Style Summaries**: High-level coding patterns are extracted and included in prompts
- **Smart Sample Selection**: Only the most relevant samples are sent to the LLM (max 3)
- **Embedding-Based Similarity Search**: Uses semantic similarity to find the most relevant code samples
- **Token Monitoring**: Estimated token usage is logged for each request

## Dependencies
- **Backend**: FastAPI, SQLAlchemy, OpenAI, Sentence-Transformers
- **Frontend**: Streamlit, Requests
- **Embedding Model**: `all-MiniLM-L6-v2` (~80MB, downloaded automatically)

## Development

### Running in Development Mode
```bash
# Terminal 1: Backend
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
streamlit run streamlit_app.py --server.port 8501
```

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Production Deployment
For production deployment, consider:
- Using a production database (PostgreSQL, MySQL)
- Setting up proper SSL/TLS
- Implementing rate limiting
- Adding monitoring and logging
- Using a production WSGI server (Gunicorn)
- Setting up proper environment variables

## Troubleshooting

### Common Issues
1. **Connection Error**: Make sure both FastAPI and Streamlit servers are running
2. **API Key Issues**: Verify your Azure OpenAI credentials
3. **Database Errors**: Recreate the database if schema changes
4. **Embedding Model**: First run will download the model (~80MB)

### Logs
- **FastAPI**: Check terminal output for API errors
- **Streamlit**: Check browser console and terminal output
- **Database**: SQLite database file: `app.db`