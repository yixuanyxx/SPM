from typing import Dict, Any, List, Optional
import requests
from services.notification_service import NotificationService

class NotificationTriggerService:
    """
    Service to handle notification triggers for various events like task assignments and updates.
    """
    
    def __init__(self):
        self.notification_service = NotificationService()
    
    def get_user_details(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user details including notification preferences from user microservice.
        """
        try:
            response = requests.get(f"http://127.0.0.1:5003/users/{user_id}")
            if response.status_code == 200:
                user_data = response.json()
                return user_data.get("data")
            return None
        except requests.RequestException:
            return None
    
    def send_notification_based_on_preferences(self, user_id: int, notification_content: str, 
                                             notification_type: str = "general", 
                                             related_task_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Send notification based on user's preferences (in-app, email, or both).
        """
        # Get user details and preferences
        user_details = self.get_user_details(user_id)
        if not user_details:
            return {"status": 404, "message": f"User {user_id} not found"}
        
        preferences = user_details.get("notification_preferences", {"in_app": True, "email": True})
        user_email = user_details.get("email")
        user_name = user_details.get("name", "User")
        
        results = []
        
        # Send in-app notification if enabled
        if preferences.get("in_app", True):
            in_app_result = self.notification_service.create_notification({
                "userid": user_id,
                "notification": notification_content,
                "notification_type": notification_type,
                "related_task_id": related_task_id
            })
            results.append({"type": "in_app", "result": in_app_result})
        
        # Send email notification if enabled and email is available
        if preferences.get("email", True) and user_email:
            subject = f"SPM Notification: {notification_type.replace('_', ' ').title()}"
            email_result = self.notification_service.send_email_notification(
                user_email, subject, notification_content
            )
            results.append({"type": "email", "result": email_result})
        
        return {"status": 200, "message": "Notifications sent based on user preferences", "results": results}
    
    def notify_task_assignment(self, task_id: int, assigned_user_id: int, assigner_name: str = "System") -> Dict[str, Any]:
        """
        Send notification when a task is assigned to a user as a collaborator.
        """
        notification_content = f"You have been assigned to task (ID: {task_id}) as a collaborator by {assigner_name}."
        # Set related_task_id to None to avoid foreign key constraint issues
        # The task_id is still mentioned in the notification content for reference
        return self.send_notification_based_on_preferences(
            assigned_user_id, 
            notification_content, 
            "task_assigned", 
            None  # Set to None to avoid foreign key constraint
        )
    
    def notify_subtask_assignment(self, subtask_id: int, assigned_user_id: int, parent_task_id: int, assigner_name: str = "System") -> Dict[str, Any]:
        """
        Send notification when a subtask is assigned to a user as a collaborator.
        """
        notification_content = f"You have been assigned to subtask (ID: {subtask_id}) under task {parent_task_id} as a collaborator by {assigner_name}."
        return self.send_notification_based_on_preferences(
            assigned_user_id, 
            notification_content, 
            "task_assigned", 
            None  # Set to None to avoid foreign key constraint
        )
    
    def notify_task_status_change(self, task_id: int, user_ids: List[int], old_status: str, new_status: str, updater_name: str = "System") -> List[Dict[str, Any]]:
        """
        Send notification when task status changes to all collaborators.
        """
        notification_content = f"Task {task_id} status has been updated from '{old_status}' to '{new_status}' by {updater_name}."
        
        results = []
        for user_id in user_ids:
            result = self.send_notification_based_on_preferences(
                user_id, 
                notification_content, 
                "task_updated", 
                task_id
            )
            results.append({"user_id": user_id, "result": result})
        
        return results
    
    def notify_task_due_date_change(self, task_id: int, user_ids: List[int], old_due_date: str, new_due_date: str, updater_name: str = "System") -> List[Dict[str, Any]]:
        """
        Send notification when task due date changes to all collaborators.
        """
        notification_content = f"Task {task_id} due date has been updated from '{old_due_date}' to '{new_due_date}' by {updater_name}."
        
        results = []
        for user_id in user_ids:
            result = self.send_notification_based_on_preferences(
                user_id, 
                notification_content, 
                "task_updated", 
                task_id
            )
            results.append({"user_id": user_id, "result": result})
        
        return results
    
    def notify_task_description_change(self, task_id: int, user_ids: List[int], updater_name: str = "System") -> List[Dict[str, Any]]:
        """
        Send notification when task description changes to all collaborators.
        """
        notification_content = f"Task {task_id} description has been updated by {updater_name}."
        
        results = []
        for user_id in user_ids:
            result = self.send_notification_based_on_preferences(
                user_id, 
                notification_content, 
                "task_updated", 
                task_id
            )
            results.append({"user_id": user_id, "result": result})
        
        return results
    
    def notify_bulk_task_assignment(self, task_assignments: List[Dict[str, Any]], assigner_name: str = "System") -> List[Dict[str, Any]]:
        """
        Send notifications for multiple task assignments.
        
        task_assignments format: [{"task_id": int, "user_id": int, "is_subtask": bool, "parent_task_id": int}]
        """
        results = []
        for assignment in task_assignments:
            task_id = assignment.get("task_id")
            user_id = assignment.get("user_id")
            is_subtask = assignment.get("is_subtask", False)
            parent_task_id = assignment.get("parent_task_id")
            
            if is_subtask and parent_task_id:
                result = self.notify_subtask_assignment(task_id, user_id, parent_task_id, assigner_name)
            else:
                result = self.notify_task_assignment(task_id, user_id, assigner_name)
            
            results.append({"task_id": task_id, "user_id": user_id, "result": result})
        
        return results

