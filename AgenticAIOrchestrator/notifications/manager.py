"""
Notification manager for handling email, Slack, and webhook notifications.
"""

import smtplib
import requests
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from db import SessionLocal
from db.models import Notification
from typing import Optional, Dict, Any
import os

class NotificationManager:
    def __init__(self):
        self.email_config = {
            "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            "smtp_port": int(os.getenv("SMTP_PORT", "587")),
            "username": os.getenv("EMAIL_USERNAME"),
            "password": os.getenv("EMAIL_PASSWORD"),
            "from_email": os.getenv("FROM_EMAIL")
        }
        self.slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    
    def send_email(self, to_email: str, subject: str, message: str) -> bool:
        """Send an email notification."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config["from_email"]
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(self.email_config["smtp_server"], self.email_config["smtp_port"])
            server.starttls()
            server.login(self.email_config["username"], self.email_config["password"])
            text = msg.as_string()
            server.sendmail(self.email_config["from_email"], to_email, text)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Email sending failed: {e}")
            return False
    
    def send_slack(self, channel: str, message: str, attachments: Optional[list] = None) -> bool:
        """Send a Slack notification."""
        try:
            if not self.slack_webhook_url:
                return False
            
            payload = {
                "channel": channel,
                "text": message,
                "attachments": attachments or []
            }
            
            response = requests.post(self.slack_webhook_url, json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"Slack notification failed: {e}")
            return False
    
    def send_webhook(self, webhook_url: str, payload: Dict[str, Any]) -> bool:
        """Send a webhook notification."""
        try:
            response = requests.post(webhook_url, json=payload)
            return response.status_code in [200, 201, 202]
        except Exception as e:
            print(f"Webhook notification failed: {e}")
            return False
    
    def create_notification(self, notification_type: str, recipient: str, 
                          subject: str, message: str) -> Notification:
        """Create a notification record in the database."""
        session = SessionLocal()
        try:
            notification = Notification(
                type=notification_type,
                recipient=recipient,
                subject=subject,
                message=message
            )
            session.add(notification)
            session.commit()
            session.refresh(notification)
            return notification
        finally:
            session.close()
    
    def send_notification(self, notification_type: str, recipient: str, 
                         subject: str, message: str) -> bool:
        """Send a notification and update the database record."""
        notification = self.create_notification(notification_type, recipient, subject, message)
        
        success = False
        if notification_type == "email":
            success = self.send_email(recipient, subject, message)
        elif notification_type == "slack":
            success = self.send_slack(recipient, message)
        elif notification_type == "webhook":
            success = self.send_webhook(recipient, {"subject": subject, "message": message})
        
        # Update notification status
        session = SessionLocal()
        try:
            notification.status = "sent" if success else "failed"
            notification.sent_at = datetime.utcnow() if success else None
            if not success:
                notification.error_message = "Failed to send notification"
            session.commit()
        finally:
            session.close()
        
        return success
    
    def notify_agent_status_change(self, agent_name: str, old_status: str, new_status: str):
        """Send notification for agent status change."""
        subject = f"Agent Status Change: {agent_name}"
        message = f"Agent '{agent_name}' status changed from {old_status} to {new_status}"
        
        # Send to admin users
        session = SessionLocal()
        try:
            from db.models import User, UserRole
            admin_users = session.query(User).filter(User.role == UserRole.ADMIN).all()
            for user in admin_users:
                self.send_notification("email", user.email, subject, message)
        finally:
            session.close()
    
    def notify_task_completion(self, task_description: str, status: str):
        """Send notification for task completion."""
        subject = f"Task {status.title()}: {task_description}"
        message = f"Task '{task_description}' has been {status}"
        
        # Send to operators and admins
        session = SessionLocal()
        try:
            from db.models import User, UserRole
            users = session.query(User).filter(
                User.role.in_([UserRole.OPERATOR, UserRole.ADMIN])
            ).all()
            for user in users:
                self.send_notification("email", user.email, subject, message)
        finally:
            session.close()

# Global notification manager instance
notification_manager = NotificationManager() 