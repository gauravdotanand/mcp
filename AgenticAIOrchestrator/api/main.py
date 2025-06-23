from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import uvicorn
from db import engine, Base
from auth.dependencies import get_current_user
from api.routers import agents, tools, tasks, logs, auth, workflows
from signals.handlers import setup_signal_handlers, cleanup_signal_handlers

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_signal_handlers()
    yield
    # Shutdown
    cleanup_signal_handlers()

app = FastAPI(
    title="Agentic AI Orchestrator API",
    description="API for managing agents, tools, tasks, and workflows",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(agents.router, prefix="/api")
app.include_router(tools.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(logs.router, prefix="/api")
app.include_router(workflows.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Agentic AI Orchestrator API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 