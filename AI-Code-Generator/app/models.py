from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.types import TypeDecorator, String as SQLString
import json
import secrets
from app.db import Base

class Vector(TypeDecorator):
    """Custom type for storing embeddings as JSON string"""
    impl = SQLString
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return None
    
    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return None

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    api_key = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Integer, default=1)  # 1 for active, 0 for inactive
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CodingApproachSample(Base):
    __tablename__ = "coding_approach_samples"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # Changed to Integer to reference User.id
    title = Column(String, nullable=False)
    code_sample = Column(Text, nullable=False)
    truncated_code_sample = Column(Text, nullable=True)  # Truncated version for LLM
    coding_style_summary = Column(Text, nullable=True)   # High-level coding approach
    max_sample_length = Column(Integer, default=1000)   # Max tokens for truncation
    embedding = Column(Vector, nullable=True)  # Vector representation for similarity search
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 