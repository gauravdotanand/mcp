"""
Audit manager for tracking user actions and system changes.
"""

from datetime import datetime
from db import SessionLocal
from db.models import AuditEntry, User
from typing import Optional, Dict, Any
import json

class AuditManager:
    def __init__(self):
        pass
    
    def log_action(self, user_id: int, action: str, resource_type: str, 
                   resource_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None,
                   ip_address: Optional[str] = None) -> AuditEntry:
        """Log an audit entry for a user action."""
        session = SessionLocal()
        try:
            audit_entry = AuditEntry(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=json.dumps(details) if details else None,
                ip_address=ip_address
            )
            session.add(audit_entry)
            session.commit()
            session.refresh(audit_entry)
            return audit_entry
        finally:
            session.close()
    
    def log_agent_action(self, user_id: int, action: str, agent_guid: str, 
                        details: Optional[Dict[str, Any]] = None, ip_address: Optional[str] = None):
        """Log an agent-related action."""
        return self.log_action(user_id, action, "agent", agent_guid, details, ip_address)
    
    def log_tool_action(self, user_id: int, action: str, tool_guid: str, 
                       details: Optional[Dict[str, Any]] = None, ip_address: Optional[str] = None):
        """Log a tool-related action."""
        return self.log_action(user_id, action, "tool", tool_guid, details, ip_address)
    
    def log_task_action(self, user_id: int, action: str, task_guid: str, 
                       details: Optional[Dict[str, Any]] = None, ip_address: Optional[str] = None):
        """Log a task-related action."""
        return self.log_action(user_id, action, "task", task_guid, details, ip_address)
    
    def log_user_action(self, user_id: int, action: str, target_user_id: Optional[int] = None,
                       details: Optional[Dict[str, Any]] = None, ip_address: Optional[str] = None):
        """Log a user-related action."""
        resource_id = str(target_user_id) if target_user_id else None
        return self.log_action(user_id, action, "user", resource_id, details, ip_address)
    
    def log_system_action(self, user_id: int, action: str, 
                         details: Optional[Dict[str, Any]] = None, ip_address: Optional[str] = None):
        """Log a system-related action."""
        return self.log_action(user_id, action, "system", None, details, ip_address)
    
    def get_audit_entries(self, user_id: Optional[int] = None, resource_type: Optional[str] = None,
                         action: Optional[str] = None, limit: int = 100) -> list[AuditEntry]:
        """Get audit entries with optional filtering."""
        session = SessionLocal()
        try:
            query = session.query(AuditEntry).order_by(AuditEntry.timestamp.desc())
            
            if user_id:
                query = query.filter(AuditEntry.user_id == user_id)
            if resource_type:
                query = query.filter(AuditEntry.resource_type == resource_type)
            if action:
                query = query.filter(AuditEntry.action == action)
            
            return query.limit(limit).all()
        finally:
            session.close()
    
    def get_user_audit_summary(self, user_id: int) -> Dict[str, Any]:
        """Get a summary of audit entries for a specific user."""
        session = SessionLocal()
        try:
            entries = session.query(AuditEntry).filter(AuditEntry.user_id == user_id).all()
            
            summary = {
                "total_actions": len(entries),
                "actions_by_type": {},
                "recent_actions": []
            }
            
            for entry in entries:
                # Count by action type
                if entry.action not in summary["actions_by_type"]:
                    summary["actions_by_type"][entry.action] = 0
                summary["actions_by_type"][entry.action] += 1
            
            # Get recent actions (last 10)
            recent_entries = session.query(AuditEntry).filter(
                AuditEntry.user_id == user_id
            ).order_by(AuditEntry.timestamp.desc()).limit(10).all()
            
            summary["recent_actions"] = [
                {
                    "action": entry.action,
                    "resource_type": entry.resource_type,
                    "timestamp": entry.timestamp.isoformat(),
                    "details": json.loads(entry.details) if entry.details else None
                }
                for entry in recent_entries
            ]
            
            return summary
        finally:
            session.close()

# Global audit manager instance
audit_manager = AuditManager() 