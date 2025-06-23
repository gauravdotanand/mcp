#!/usr/bin/env python3
"""
Database migration script for authentication and advanced features.
This script will add all the new tables for users, audit entries, API keys, and notifications.
"""

import uuid
from sqlalchemy import create_engine, text, inspect
from db import SessionLocal
from db.models import Base, User, AuditEntry, ApiKey, Notification, UserRole
from auth.security import get_password_hash

def migrate_auth_database():
    """Perform database migration for authentication and advanced features"""
    print("Starting authentication database migration...")
    
    # Create engine and get connection
    engine = create_engine('sqlite:///agentic_ai_orchestrator.db')
    
    with engine.connect() as conn:
        # Check if tables already exist
        inspector = engine.dialect.inspector(engine)
        tables = inspector.get_table_names()
        
        # Create users table
        if 'users' not in tables:
            print("Creating users table...")
            conn.execute(text("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    guid TEXT UNIQUE,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL,
                    role TEXT DEFAULT 'viewer',
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login DATETIME
                )
            """))
            conn.commit()
            
            # Create default admin user
            session = SessionLocal()
            try:
                admin_user = User(
                    username="admin",
                    email="admin@example.com",
                    hashed_password=get_password_hash("admin123"),
                    role=UserRole.ADMIN
                )
                session.add(admin_user)
                session.commit()
                print("Created default admin user (username: admin, password: admin123)")
            finally:
                session.close()
        
        # Create audit_entries table
        if 'audit_entries' not in tables:
            print("Creating audit_entries table...")
            conn.execute(text("""
                CREATE TABLE audit_entries (
                    id INTEGER PRIMARY KEY,
                    guid TEXT UNIQUE,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    resource_id TEXT,
                    details TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """))
            conn.commit()
        
        # Create api_keys table
        if 'api_keys' not in tables:
            print("Creating api_keys table...")
            conn.execute(text("""
                CREATE TABLE api_keys (
                    id INTEGER PRIMARY KEY,
                    guid TEXT UNIQUE,
                    name TEXT NOT NULL,
                    key_hash TEXT NOT NULL,
                    user_id INTEGER,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_used DATETIME,
                    permissions TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """))
            conn.commit()
        
        # Create notifications table
        if 'notifications' not in tables:
            print("Creating notifications table...")
            conn.execute(text("""
                CREATE TABLE notifications (
                    id INTEGER PRIMARY KEY,
                    guid TEXT UNIQUE,
                    type TEXT NOT NULL,
                    recipient TEXT NOT NULL,
                    subject TEXT,
                    message TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    sent_at DATETIME,
                    error_message TEXT
                )
            """))
            conn.commit()
    
    print("Authentication database migration completed successfully!")

if __name__ == "__main__":
    migrate_auth_database() 