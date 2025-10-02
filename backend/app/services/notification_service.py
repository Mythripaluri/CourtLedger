from typing import List, Optional, Dict, Any
from datetime import datetime, date
import asyncio
import logging
from dataclasses import dataclass
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

from ..config import settings

logger = logging.getLogger(__name__)

@dataclass
class NotificationRecipient:
    """Notification recipient information"""
    email: Optional[str] = None
    phone: Optional[str] = None
    name: Optional[str] = None
    case_numbers: Optional[List[str]] = None

@dataclass
class NotificationTemplate:
    """Notification template"""
    template_id: str
    subject: str
    body: str
    notification_type: str  # 'email', 'sms', 'webhook'

class NotificationService:
    """
    Court Case Notification System
    
    Features:
    - Email notifications for case status changes
    - SMS notifications for urgent updates
    - Webhook notifications for integrations
    - Hearing reminders
    - Status change alerts
    - Scheduled notifications
    """
    
    def __init__(self):
        self.email_enabled = getattr(settings, 'email_enabled', False)
        self.sms_enabled = getattr(settings, 'sms_enabled', False)
        self.webhook_enabled = getattr(settings, 'webhook_enabled', False)
        
        # Email configuration
        self.smtp_server = getattr(settings, 'smtp_server', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'smtp_port', 587)
        self.email_username = getattr(settings, 'email_username', '')
        self.email_password = getattr(settings, 'email_password', '')
        self.from_email = getattr(settings, 'from_email', 'noreply@courttracker.com')
        
        # Notification templates
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, NotificationTemplate]:
        """Load notification templates"""
        return {
            "status_change": NotificationTemplate(
                template_id="status_change",
                subject="Case Status Update - {case_number}",
                body="""
Dear Subscriber,

Your case {case_number} has been updated:

Previous Status: {old_status}
New Status: {new_status}
Updated On: {updated_date}
Next Hearing: {next_hearing_date}

Please visit the court website or our platform for more details.

Best regards,
Court Case Tracker Team
                """.strip(),
                notification_type="email"
            ),
            
            "hearing_reminder": NotificationTemplate(
                template_id="hearing_reminder",
                subject="Hearing Reminder - {case_number}",
                body="""
Dear Subscriber,

This is a reminder for your upcoming court hearing:

Case Number: {case_number}
Parties: {parties}
Hearing Date: {hearing_date}
Hearing Time: {hearing_time}
Court Room: {court_room}
Judge: {judge}

Please ensure you arrive at least 30 minutes before the scheduled time.

Best regards,
Court Case Tracker Team
                """.strip(),
                notification_type="email"
            ),
            
            "daily_summary": NotificationTemplate(
                template_id="daily_summary",
                subject="Daily Case Summary - {date}",
                body="""
Dear Subscriber,

Here's your daily case summary for {date}:

Total Cases: {total_cases}
New Cases: {new_cases}
Status Changes: {status_changes}
Upcoming Hearings: {upcoming_hearings}

Visit our platform for detailed information.

Best regards,
Court Case Tracker Team
                """.strip(),
                notification_type="email"
            )
        }
    
    async def notify_status_change(
        self,
        case_number: str,
        old_status: str,
        new_status: str,
        next_hearing_date: Optional[date] = None,
        recipients: Optional[List[NotificationRecipient]] = None
    ) -> Dict[str, Any]:
        """
        Send notification for case status changes
        """
        try:
            template = self.templates["status_change"]
            
            # Format notification content
            subject = template.subject.format(case_number=case_number)
            body = template.body.format(
                case_number=case_number,
                old_status=old_status,
                new_status=new_status,
                updated_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                next_hearing_date=next_hearing_date.strftime("%Y-%m-%d") if next_hearing_date else "Not scheduled"
            )
            
            # Send notifications
            results = []
            
            if self.email_enabled and recipients:
                for recipient in recipients:
                    if recipient.email:
                        email_result = await self._send_email(
                            to_email=recipient.email,
                            subject=subject,
                            body=body,
                            recipient_name=recipient.name
                        )
                        results.append(email_result)
            
            # Log notification
            logger.info(f"Status change notification sent for case {case_number}: {old_status} -> {new_status}")
            
            return {
                "success": True,
                "case_number": case_number,
                "notification_type": "status_change",
                "recipients_notified": len(results),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Failed to send status change notification for {case_number}: {e}")
            return {
                "success": False,
                "error": str(e),
                "case_number": case_number
            }
    
    async def send_hearing_reminder(
        self,
        case_number: str,
        parties: str,
        hearing_date: date,
        hearing_time: Optional[str] = None,
        court_room: Optional[str] = None,
        judge: Optional[str] = None,
        recipients: Optional[List[NotificationRecipient]] = None
    ) -> Dict[str, Any]:
        """
        Send hearing reminder notifications
        """
        try:
            template = self.templates["hearing_reminder"]
            
            # Format notification content
            subject = template.subject.format(case_number=case_number)
            body = template.body.format(
                case_number=case_number,
                parties=parties,
                hearing_date=hearing_date.strftime("%Y-%m-%d"),
                hearing_time=hearing_time or "Not specified",
                court_room=court_room or "Not specified",
                judge=judge or "Not specified"
            )
            
            # Send notifications
            results = []
            
            if self.email_enabled and recipients:
                for recipient in recipients:
                    if recipient.email:
                        email_result = await self._send_email(
                            to_email=recipient.email,
                            subject=subject,
                            body=body,
                            recipient_name=recipient.name
                        )
                        results.append(email_result)
            
            # Log notification
            logger.info(f"Hearing reminder sent for case {case_number} on {hearing_date}")
            
            return {
                "success": True,
                "case_number": case_number,
                "notification_type": "hearing_reminder",
                "hearing_date": hearing_date.isoformat(),
                "recipients_notified": len(results),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Failed to send hearing reminder for {case_number}: {e}")
            return {
                "success": False,
                "error": str(e),
                "case_number": case_number
            }
    
    async def send_daily_summary(
        self,
        summary_date: date,
        total_cases: int,
        new_cases: int,
        status_changes: int,
        upcoming_hearings: int,
        recipients: List[NotificationRecipient]
    ) -> Dict[str, Any]:
        """
        Send daily case summary notifications
        """
        try:
            template = self.templates["daily_summary"]
            
            # Format notification content
            subject = template.subject.format(date=summary_date.strftime("%Y-%m-%d"))
            body = template.body.format(
                date=summary_date.strftime("%Y-%m-%d"),
                total_cases=total_cases,
                new_cases=new_cases,
                status_changes=status_changes,
                upcoming_hearings=upcoming_hearings
            )
            
            # Send notifications
            results = []
            
            if self.email_enabled:
                for recipient in recipients:
                    if recipient.email:
                        email_result = await self._send_email(
                            to_email=recipient.email,
                            subject=subject,
                            body=body,
                            recipient_name=recipient.name
                        )
                        results.append(email_result)
            
            # Log notification
            logger.info(f"Daily summary sent for {summary_date} to {len(recipients)} recipients")
            
            return {
                "success": True,
                "notification_type": "daily_summary",
                "summary_date": summary_date.isoformat(),
                "recipients_notified": len(results),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Failed to send daily summary for {summary_date}: {e}")
            return {
                "success": False,
                "error": str(e),
                "summary_date": summary_date.isoformat()
            }
    
    async def _send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        recipient_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send email notification
        """
        if not self.email_enabled:
            return {
                "success": False,
                "error": "Email notifications are disabled",
                "to_email": to_email
            }
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add greeting if recipient name is provided
            if recipient_name:
                body = f"Dear {recipient_name},\n\n" + body.lstrip("Dear Subscriber,").lstrip()
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_username, self.email_password)
            text = msg.as_string()
            server.sendmail(self.from_email, to_email, text)
            server.quit()
            
            return {
                "success": True,
                "to_email": to_email,
                "subject": subject,
                "sent_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return {
                "success": False,
                "error": str(e),
                "to_email": to_email
            }
    
    async def _send_sms(
        self,
        to_phone: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Send SMS notification (placeholder implementation)
        """
        if not self.sms_enabled:
            return {
                "success": False,
                "error": "SMS notifications are disabled",
                "to_phone": to_phone
            }
        
        # TODO: Implement SMS sending using Twilio, AWS SNS, or other service
        logger.info(f"SMS notification would be sent to {to_phone}: {message[:50]}...")
        
        return {
            "success": True,
            "to_phone": to_phone,
            "message": message,
            "sent_at": datetime.now().isoformat(),
            "note": "SMS sending not implemented yet"
        }
    
    async def _send_webhook(
        self,
        webhook_url: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send webhook notification (placeholder implementation)
        """
        if not self.webhook_enabled:
            return {
                "success": False,
                "error": "Webhook notifications are disabled",
                "webhook_url": webhook_url
            }
        
        # TODO: Implement webhook sending using aiohttp
        logger.info(f"Webhook notification would be sent to {webhook_url}")
        
        return {
            "success": True,
            "webhook_url": webhook_url,
            "payload": payload,
            "sent_at": datetime.now().isoformat(),
            "note": "Webhook sending not implemented yet"
        }
    
    async def schedule_notifications(
        self,
        notification_type: str,
        schedule_time: datetime,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Schedule future notifications (placeholder implementation)
        """
        # TODO: Implement with Celery, APScheduler, or similar task scheduler
        logger.info(f"Scheduled {notification_type} notification for {schedule_time}")
        
        return {
            "success": True,
            "notification_type": notification_type,
            "scheduled_for": schedule_time.isoformat(),
            "payload": payload,
            "note": "Notification scheduling not implemented yet"
        }
    
    def get_notification_preferences(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get user notification preferences (placeholder implementation)
        """
        # TODO: Implement user preference storage and retrieval
        return {
            "user_id": user_id,
            "email_enabled": True,
            "sms_enabled": False,
            "webhook_enabled": False,
            "status_change_notifications": True,
            "hearing_reminders": True,
            "daily_summaries": False
        }
    
    def update_notification_preferences(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update user notification preferences (placeholder implementation)
        """
        # TODO: Implement user preference storage
        logger.info(f"Updated notification preferences for user {user_id}")
        
        return {
            "success": True,
            "user_id": user_id,
            "updated_preferences": preferences,
            "updated_at": datetime.now().isoformat()
        }

    def get_email_templates(self) -> Dict[str, NotificationTemplate]:
        """
        Get all available email templates
        """
        return self.templates