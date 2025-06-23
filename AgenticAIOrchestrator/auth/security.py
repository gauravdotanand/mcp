"""
Security utilities for authentication and authorization.
"""

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Union
from db.models import User, ApiKey
from db import SessionLocal
import secrets
import hashlib

# Security configuration
SECRET_KEY = "your-secret-key-here"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def generate_api_key() -> str:
    """Generate a new API key."""
    return secrets.token_urlsafe(32)

def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()

def verify_api_key(api_key: str) -> Optional[ApiKey]:
    """Verify an API key and return the associated key object."""
    session = SessionLocal()
    try:
        key_hash = hash_api_key(api_key)
        api_key_obj = session.query(ApiKey).filter(
            ApiKey.key_hash == key_hash,
            ApiKey.is_active == True
        ).first()
        
        if api_key_obj:
            # Update last used timestamp
            api_key_obj.last_used = datetime.utcnow()
            session.commit()
            return api_key_obj
        return None
    finally:
        session.close()

def get_user_by_username(username: str) -> Optional[User]:
    """Get a user by username."""
    session = SessionLocal()
    try:
        return session.query(User).filter(User.username == username).first()
    finally:
        session.close()

def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate a user with username and password."""
    user = get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_user(username: str, email: str, password: str, role: str = "viewer") -> User:
    """Create a new user."""
    session = SessionLocal()
    try:
        hashed_password = get_password_hash(password)
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=role
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    finally:
        session.close()

def create_api_key(user_id: int, name: str, permissions: str = None) -> tuple[str, ApiKey]:
    """Create a new API key for a user."""
    session = SessionLocal()
    try:
        api_key = generate_api_key()
        key_hash = hash_api_key(api_key)
        
        api_key_obj = ApiKey(
            name=name,
            key_hash=key_hash,
            user_id=user_id,
            permissions=permissions
        )
        session.add(api_key_obj)
        session.commit()
        session.refresh(api_key_obj)
        
        return api_key, api_key_obj
    finally:
        session.close() 