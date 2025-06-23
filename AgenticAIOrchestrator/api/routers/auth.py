"""
Authentication and authorization endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from db import SessionLocal
from db.models import User, UserRole, ApiKey
from auth.security import (
    authenticate_user, create_access_token, create_user, 
    create_api_key, verify_api_key, get_user_by_username
)
from auth.dependencies import get_current_user, require_admin
from pydantic import BaseModel
from typing import List, Optional
from datetime import timedelta

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "viewer"

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ApiKeyCreate(BaseModel):
    name: str
    permissions: Optional[str] = None

class ApiKeyOut(BaseModel):
    id: int
    name: str
    is_active: bool
    created_at: str
    last_used: Optional[str]

    class Config:
        orm_mode = True

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint to get access token."""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    session = SessionLocal()
    try:
        user.last_login = datetime.utcnow()
        session.commit()
    finally:
        session.close()
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserOut)
def register(user_data: UserCreate, current_user: User = Depends(require_admin)):
    """Register a new user (admin only)."""
    session = SessionLocal()
    try:
        # Check if username or email already exists
        existing_user = session.query(User).filter(
            (User.username == user_data.username) | (User.email == user_data.email)
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )
        
        user = create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            role=user_data.role
        )
        return user
    finally:
        session.close()

@router.get("/me", response_model=UserOut)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user

@router.get("/users", response_model=List[UserOut])
def list_users(current_user: User = Depends(require_admin)):
    """List all users (admin only)."""
    session = SessionLocal()
    try:
        users = session.query(User).all()
        return users
    finally:
        session.close()

@router.post("/api-keys", response_model=dict)
def create_api_key_endpoint(
    api_key_data: ApiKeyCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new API key for the current user."""
    api_key, api_key_obj = create_api_key(
        user_id=current_user.id,
        name=api_key_data.name,
        permissions=api_key_data.permissions
    )
    
    return {
        "api_key": api_key,
        "name": api_key_obj.name,
        "created_at": api_key_obj.created_at.isoformat(),
        "message": "Store this API key securely. It won't be shown again."
    }

@router.get("/api-keys", response_model=List[ApiKeyOut])
def list_api_keys(current_user: User = Depends(get_current_user)):
    """List API keys for the current user."""
    session = SessionLocal()
    try:
        api_keys = session.query(ApiKey).filter(ApiKey.user_id == current_user.id).all()
        return api_keys
    finally:
        session.close()

@router.delete("/api-keys/{api_key_id}")
def revoke_api_key(
    api_key_id: int,
    current_user: User = Depends(get_current_user)
):
    """Revoke an API key."""
    session = SessionLocal()
    try:
        api_key = session.query(ApiKey).filter(
            ApiKey.id == api_key_id,
            ApiKey.user_id == current_user.id
        ).first()
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        api_key.is_active = False
        session.commit()
        return {"message": "API key revoked successfully"}
    finally:
        session.close() 