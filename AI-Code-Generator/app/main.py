from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas import CodeGenerationRequest, CodeGenerationResponse, CodingApproachSampleCreate, CodingApproachSampleRead, UserCreate, UserResponse
from app.openai_client import AzureOpenAIClient
from app import config
from app.db import SessionLocal
from app.models import CodingApproachSample, User
from app.utils import truncate_code_sample, generate_coding_style_summary, get_most_relevant_samples, count_tokens
from app.embeddings import generate_embedding, create_search_text
from app.auth import get_current_user, create_user
from typing import List

app = FastAPI(title="AI Code Generator", description="Multi-user AI code generation with custom coding approaches")

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

# User Management Endpoints
@app.post("/users", response_model=UserResponse)
def create_new_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user and return their API key"""
    return create_user(db, user_data.username, user_data.email)

@app.get("/users/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

# Coding Approach Samples Endpoints (with authentication)
@app.post("/coding-approach-samples", response_model=CodingApproachSampleRead)
def create_coding_approach_sample(
    sample: CodingApproachSampleCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Generate truncated version and coding style summary
    truncated_code = truncate_code_sample(sample.code_sample, sample.max_sample_length)
    coding_summary = generate_coding_style_summary(sample.code_sample)
    
    # Generate embedding for similarity search
    search_text = create_search_text(sample.title, sample.code_sample, coding_summary)
    embedding = generate_embedding(search_text)
    
    db_sample = CodingApproachSample(
        user_id=current_user.id,
        title=sample.title,
        code_sample=sample.code_sample,
        max_sample_length=sample.max_sample_length,
        truncated_code_sample=truncated_code,
        coding_style_summary=coding_summary,
        embedding=embedding
    )
    db.add(db_sample)
    db.commit()
    db.refresh(db_sample)
    return db_sample

@app.get("/coding-approach-samples", response_model=List[CodingApproachSampleRead])
def list_coding_approach_samples(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all coding approach samples for the current user"""
    return db.query(CodingApproachSample).filter(CodingApproachSample.user_id == current_user.id).all()

@app.get("/coding-approach-samples/{sample_id}", response_model=CodingApproachSampleRead)
def get_coding_approach_sample(
    sample_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific coding approach sample (user can only access their own)"""
    sample = db.query(CodingApproachSample).filter(
        CodingApproachSample.id == sample_id,
        CodingApproachSample.user_id == current_user.id
    ).first()
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    return sample

@app.delete("/coding-approach-samples/{sample_id}")
def delete_coding_approach_sample(
    sample_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a coding approach sample (user can only delete their own)"""
    sample = db.query(CodingApproachSample).filter(
        CodingApproachSample.id == sample_id,
        CodingApproachSample.user_id == current_user.id
    ).first()
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    db.delete(sample)
    db.commit()
    return {"detail": "Sample deleted"}

# Code Generation Endpoint (with authentication)
@app.post("/generate-code", response_model=CodeGenerationResponse)
def generate_code(
    request: CodeGenerationRequest, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Gather code samples from IDs if provided (only user's own samples)
        samples = request.coding_approach_samples or []
        if request.coding_approach_sample_ids:
            db_samples = db.query(CodingApproachSample).filter(
                CodingApproachSample.id.in_(request.coding_approach_sample_ids),
                CodingApproachSample.user_id == current_user.id  # Only user's own samples
            ).all()
            # Use truncated samples and add coding style summaries
            for sample in db_samples:
                if sample.truncated_code_sample:
                    samples.append(f"Style: {sample.coding_style_summary}\nCode:\n{sample.truncated_code_sample}")
                else:
                    samples.append(sample.code_sample)
        
        # Smart selection: get most relevant samples using embedding-based similarity search
        if samples:
            samples = get_most_relevant_samples(samples, request.prompt, max_samples=3, db_session=db, user_id=current_user.id)
        
        # Count tokens for monitoring
        total_tokens = count_tokens(request.prompt + (request.context or "") + (request.extraction_requirements or ""))
        for sample in samples:
            total_tokens += count_tokens(sample)
        
        print(f"User {current_user.username}: Estimated tokens being sent to LLM: {total_tokens}")
        
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