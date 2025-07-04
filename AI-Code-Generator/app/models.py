from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.db import Base

class CodingApproachSample(Base):
    __tablename__ = "coding_approach_samples"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=True, index=True)
    title = Column(String, nullable=False)
    code_sample = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 