from typing import Dict, Any, Optional, List
import requests
import os
import sendgrid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from dotenv import load_dotenv
from models.notification import Notification
from repo.supa_notification_repo import SupabaseNotificationRepo

# Load environment variables from .env file
load_dotenv()

class NotificationService:
    def __init__(self, repo: Optional[SupabaseNotificationRepo] = None):
        self.repo = repo or SupabaseNotificationRepo()

    def create_notification(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new notification.
        Required fields: userid, notification
        Optional fields: notification_type, related_task_id
        """
        # Validate required fields
        if not payload.get("userid"):
            raise ValueError("userid is required")
        if not payload.get("notification"):
            raise ValueError("notification content is required")

        # Use the Notification.from_dict constructor for proper type handling
        notification = Notification.from_dict(payload)

        # Convert to dictionary for database insertion (excludes id=None)
        data = notification.to_dict()
        data.pop("id", None)

        # Insert into database
        created = self.repo.insert_notification(data)
        return {"status": 201, "message": f"Notification created! Notification ID: {created.get('id')}", "data": created}

    def get_notifications_by_user(self, user_id: int) -> Dict[str, Any]:
        """
        Get all notifications for a specific user.
        """
        notifications = self.repo.find_by_user(user_id)
        if not notifications:
            return {"status": 404, "message": f"No notifications found for user ID {user_id}"}
        return {"status": 200, "data": notifications}

    def get_notification_by_id(self, notification_id: int) -> Dict[str, Any]:
        """
        Get a single notification by its ID.
        """
        notification = self.repo.get_notification(notification_id)
        if not notification:
            return {"status": 404, "message": f"Notification with ID {notification_id} not found"}
        return {"status": 200, "data": notification}

    def mark_notification_as_read(self, notification_id: int) -> Dict[str, Any]:
        """
        Mark a notification as read.
        """
        try:
            # Check if notification exists
            existing_notification = self.repo.get_notification(notification_id)
            if not existing_notification:
                return {"status": 404, "message": f"Notification with ID {notification_id} not found"}
            
            updated_notification = self.repo.mark_as_read(notification_id)
            return {"status": 200, "message": f"Notification {notification_id} marked as read", "data": updated_notification}
        except Exception as e:
            return {"status": 500, "message": f"Failed to mark notification {notification_id} as read: {str(e)}"}

    def mark_notification_as_unread(self, notification_id: int) -> Dict[str, Any]:
        """
        Mark a notification as unread.
        """
        try:
            # Check if notification exists
            existing_notification = self.repo.get_notification(notification_id)
            if not existing_notification:
                return {"status": 404, "message": f"Notification with ID {notification_id} not found"}
            
            updated_notification = self.repo.mark_as_unread(notification_id)
            return {"status": 200, "message": f"Notification {notification_id} marked as unread", "data": updated_notification}
        except Exception as e:
            return {"status": 500, "message": f"Failed to mark notification {notification_id} as unread: {str(e)}"}

    def get_unread_count(self, user_id: int) -> Dict[str, Any]:
        """
        Get the count of unread notifications for a user.
        """
        try:
            count = self.repo.get_unread_count(user_id)
            return {"status": 200, "data": {"unread_count": count}}
        except Exception as e:
            return {"status": 500, "message": f"Failed to get unread count for user {user_id}: {str(e)}"}

    def get_unread_notifications(self, user_id: int) -> Dict[str, Any]:
        """
        Get all unread notifications for a specific user.
        """
        notifications = self.repo.find_unread_by_user(user_id)
        if not notifications:
            return {"status": 404, "message": f"No unread notifications found for user ID {user_id}"}
        return {"status": 200, "data": notifications}

    def delete_notification(self, notification_id: int) -> Dict[str, Any]:
        """
        Delete a notification by its ID.
        """
        try:
            # Check if notification exists
            existing_notification = self.repo.get_notification(notification_id)
            if not existing_notification:
                return {"status": 404, "message": f"Notification with ID {notification_id} not found"}
            
            success = self.repo.delete_notification(notification_id)
            if success:
                return {"status": 200, "message": f"Notification {notification_id} deleted successfully"}
            else:
                return {"status": 500, "message": f"Failed to delete notification {notification_id}"}
        except Exception as e:
            return {"status": 500, "message": f"Failed to delete notification {notification_id}: {str(e)}"}

    def send_email_notification(self, user_email: str, subject: str, message: str) -> Dict[str, Any]:
        """
        Send email notification using SendGrid API with proper integration.
        """
        try:
            # Get SendGrid API key from environment
            sendgrid_api_key = os.environ.get("SENDGRID_API_KEY")
            if not sendgrid_api_key:
                return {"status": 500, "message": "SendGrid API key not configured"}
            
            # Create SendGrid client
            sg = sendgrid.SendGridAPIClient(api_key=sendgrid_api_key)
            
            # Get sender email from environment
            from_email = os.environ.get("SENDGRID_FROM_EMAIL")
            if not from_email:
                return {"status": 500, "message": "SendGrid from email not configured"}
            
            # Create email components using proper SendGrid format
            from_email_obj = Email(from_email)
            to_email_obj = To(user_email)
            subject_obj = subject
            content_obj = Content("text/html", message)
            
            # Create mail object
            mail = Mail(from_email_obj, to_email_obj, subject_obj, content_obj)
            
            # Get mail as JSON
            mail_json = mail.get()
            
            # Send email
            response = sg.client.mail.send.post(request_body=mail_json)
            
            if response.status_code in [200, 201, 202]:
                return {"status": 200, "message": "Email notification sent successfully"}
            else:
                return {"status": 500, "message": f"Failed to send email: HTTP {response.status_code}"}
                
        except Exception as e:
            return {"status": 500, "message": f"Failed to send email notification: {str(e)}"}