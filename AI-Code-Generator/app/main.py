from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas import CodeGenerationRequest, CodeGenerationResponse
from app.openai_client import AzureOpenAIClient
from app import config
from app.db import SessionLocal
from app.models import CodingApproachSample
from app.schemas import CodingApproachSampleCreate, CodingApproachSampleRead
from typing import List

app = FastAPI()

client = AzureOpenAIClient(
    api_key=config.AZURE_OPENAI_API_KEY,
    endpoint=config.AZURE_OPENAI_ENDPOINT,
    api_version=config.AZURE_OPENAI_API_VERSION
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/generate-code", response_model=CodeGenerationResponse)
def generate_code(request: CodeGenerationRequest, db: Session = Depends(get_db)):
    try:
        # Gather code samples from IDs if provided
        samples = request.coding_approach_samples or []
        if request.coding_approach_sample_ids:
            db_samples = db.query(CodingApproachSample).filter(CodingApproachSample.id.in_(request.coding_approach_sample_ids)).all()
            samples += [s.code_sample for s in db_samples]
        code = client.generate_code(
            prompt=request.prompt,
            context=request.context,
            coding_approach_samples=samples if samples else None,
            model=request.model,
            extraction_requirements=request.extraction_requirements
        )
        return CodeGenerationResponse(generated_code=code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/coding-approach-samples", response_model=CodingApproachSampleRead)
def create_coding_approach_sample(sample: CodingApproachSampleCreate, db: Session = Depends(get_db)):
    db_sample = CodingApproachSample(**sample.dict())
    db.add(db_sample)
    db.commit()
    db.refresh(db_sample)
    return db_sample

@app.get("/coding-approach-samples", response_model=List[CodingApproachSampleRead])
def list_coding_approach_samples(db: Session = Depends(get_db)):
    return db.query(CodingApproachSample).all()

@app.get("/coding-approach-samples/{sample_id}", response_model=CodingApproachSampleRead)
def get_coding_approach_sample(sample_id: int, db: Session = Depends(get_db)):
    sample = db.query(CodingApproachSample).filter(CodingApproachSample.id == sample_id).first()
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    return sample

@app.delete("/coding-approach-samples/{sample_id}")
def delete_coding_approach_sample(sample_id: int, db: Session = Depends(get_db)):
    sample = db.query(CodingApproachSample).filter(CodingApproachSample.id == sample_id).first()
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    db.delete(sample)
    db.commit()
    return {"detail": "Sample deleted"} 