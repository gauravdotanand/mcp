from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, create_engine, Boolean, Text, JSON
from sqlalchemy.orm import declarative_base, relationship
import enum
import datetime
import uuid

Base = declarative_base()

class AgentStatus(enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    IDLE = "idle"

class ToolStatus(enum.Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"

class TaskStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"

class NotificationType(enum.Enum):
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"

class Agent(Base):
    __tablename__ = 'agents'
    id = Column(Integer, primary_key=True)
    guid = Column(String, unique=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True)
    status = Column(Enum(AgentStatus), default=AgentStatus.IDLE)
    last_seen = Column(DateTime, default=datetime.datetime.utcnow)
    tasks = relationship("Task", back_populates="agent")

class Tool(Base):
    __tablename__ = 'tools'
    id = Column(Integer, primary_key=True)
    guid = Column(String, unique=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True)
    status = Column(Enum(ToolStatus), default=ToolStatus.AVAILABLE)

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    guid = Column(String, unique=True, default=lambda: str(uuid.uuid4()))
    description = Column(String)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    agent_id = Column(Integer, ForeignKey('agents.id'))
    agent = relationship("Agent", back_populates="tasks")
    tool_id = Column(Integer, ForeignKey('tools.id'))
    tool = relationship("Tool")

class Log(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    message = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    level = Column(String)
    agent_guid = Column(String, nullable=True)
    tool_guid = Column(String, nullable=True)
    task_guid = Column(String, nullable=True)

# Authentication and User Management Models
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

class ApiKey(Base):
    __tablename__ = 'api_keys'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    key_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_used = Column(DateTime, nullable=True)
    user = relationship("User")

# Notification System Models
class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    config = Column(JSON, nullable=True)  # For webhook URLs, Slack channels, etc.
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship("User")

# Audit Trail Models
class AuditEntry(Base):
    __tablename__ = 'audit_entries'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship("User") 