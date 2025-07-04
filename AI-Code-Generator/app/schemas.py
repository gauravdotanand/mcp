from pydantic import BaseModel
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

class CodingApproachSampleBase(BaseModel):
    title: str
    code_sample: str
    user_id: Optional[str] = None

class CodingApproachSampleCreate(CodingApproachSampleBase):
    pass

class CodingApproachSampleRead(CodingApproachSampleBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True 