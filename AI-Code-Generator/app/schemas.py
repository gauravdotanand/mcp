from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class CodeGenerationRequest(BaseModel):
    prompt: str
    context: Optional[str] = None
    coding_approach_samples: Optional[List[str]] = None
    coding_approach_sample_ids: Optional[List[int]] = None
    extraction_requirements: Optional[str] = None
    model: Optional[str] = "gpt-4"

class CodeGenerationResponse(BaseModel):
    generated_code: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    api_key: str
    is_active: int
    created_at: datetime

    class Config:
        orm_mode = True

class CodingApproachSampleBase(BaseModel):
    title: str
    code_sample: str
    max_sample_length: Optional[int] = 1000

class CodingApproachSampleCreate(CodingApproachSampleBase):
    pass

class CodingApproachSampleRead(CodingApproachSampleBase):
    id: int
    user_id: int
    truncated_code_sample: Optional[str] = None
    coding_style_summary: Optional[str] = None
    embedding: Optional[List[float]] = None
    created_at: datetime

    class Config:
        orm_mode = True 