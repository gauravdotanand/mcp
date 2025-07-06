from fastapi import HTTPException, Depends, Header
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import User
from typing import Optional
import secrets

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    x_api_key: str = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from API key"""
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required. Please provide X-API-Key header."
        )
    
    user = db.query(User).filter(
        User.api_key == x_api_key,
        User.is_active == 1
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid or inactive API key."
        )
    
    return user

def generate_api_key() -> str:
    """Generate a secure API key"""
    return secrets.token_urlsafe(32)

def create_user(db: Session, username: str, email: str) -> User:
    """Create a new user with a generated API key"""
    # Check if username or email already exists
    existing_user = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists."
        )
    
    api_key = generate_api_key()
    user = User(
        username=username,
        email=email,
        api_key=api_key
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user 