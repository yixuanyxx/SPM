from typing import Dict, Any, List, Optional
import requests
from dotenv import load_dotenv
from services.notification_service import NotificationService

# Load environment variables from .env file
load_dotenv()

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
                                             related_task_id: Optional[int] = None,
                                             plain_text_content: str = None) -> Dict[str, Any]:
        """
        Send notification based on user's preferences (in-app, email, or both).
        
        Args:
            user_id: ID of the user to notify
            notification_content: HTML content for email notification
            notification_type: Type of notification
            related_task_id: ID of related task if applicable
            plain_text_content: Plain text content for in-app notification (if None, will strip HTML from notification_content)
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
            # Use plain text content for in-app notification
            in_app_text = plain_text_content if plain_text_content else self._strip_html(notification_content)
            in_app_result = self.notification_service.create_notification({
                "userid": user_id,
                "notification": in_app_text,
                "notification_type": notification_type,
                "related_task_id": related_task_id
            })
            results.append({"type": "in_app", "result": in_app_result})
        
        # Send email notification if enabled and email is available
        if preferences.get("email", True) and user_email:
            # Create proper email subject and content
            subject, email_content = self._create_email_content(
                notification_type, notification_content, user_name
            )
            email_result = self.notification_service.send_email_notification(
                user_email, subject, email_content
            )
            results.append({"type": "email", "result": email_result})
        
        return {"status": 200, "message": "Notifications sent based on user preferences", "results": results}
    
    def _strip_html(self, html_content: str) -> str:
        """
        Strip HTML tags and convert to plain text for in-app notifications.
        """
        import re
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html_content)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Decode HTML entities
        text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        return text.strip()
    
    def _create_email_content(self, notification_type: str, notification_content: str, user_name: str) -> tuple:
        """
        Create proper email subject and HTML content based on notification type.
        """
        # Create subject based on notification type
        subject_map = {
            "task_assigned": "New Task Assignmen",
            "task_ownership_transferred": "Task Ownership Transfer",
            "task_updated": "Task Update Notification",
            "project_collaborator_added": "Project Collaborator Addition",
            "general": "SPM Notification",
            "system": "SPM System Notification"
        }
        subject = subject_map.get(notification_type, "SPM Notification")
        
        # Create HTML email content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{subject}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f4f4f4;
                }}
                .email-container {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    border-bottom: 2px solid #3b82f6;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #3b82f6;
                    margin-bottom: 10px;
                }}
                .content {{
                    font-size: 16px;
                    line-height: 1.8;
                }}
                .notification-box {{
                    background-color: #f8fafc;
                    border-left: 4px solid #3b82f6;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e5e7eb;
                    color: #6b7280;
                    font-size: 14px;
                }}
                .button {{
                    display: inline-block;
                    background-color: #3b82f6;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <div class="logo">📋 SPM</div>
                    <h2>{subject}</h2>
                </div>
                
                <div class="content">
                    <p>Dear <strong>{user_name}</strong>,</p>
                    
                    <div class="notification-box">
                        {notification_content}
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return subject, html_content
    
    def _get_task_details(self, task_id: int) -> Optional[Dict[str, Any]]:
        """
        Get task details from the task microservice.
        """
        try:
            response = requests.get(f"http://127.0.0.1:5002/tasks/{task_id}")
            if response.status_code == 200:
                data = response.json()
                return data.get("task") or data
            return None
        except requests.RequestException:
            return None
    
    def _get_task_details_from_supabase(self, task_id: int) -> Optional[Dict[str, Any]]:
        """
        Get task details directly from Supabase task table.
        """
        try:
            # Import here to avoid circular imports
            from repo.supa_notification_repo import SupabaseNotificationRepo
            repo = SupabaseNotificationRepo()
            
            # Query the task table directly
            response = repo.client.table("task").select("*").eq("id", task_id).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error fetching task details from Supabase: {e}")
            return None
    
    def notify_task_assignment(self, task_id: int, assigned_user_id: int, assigner_name: str = "System") -> Dict[str, Any]:
        """
        Send notification when a task is assigned to a user as a collaborator.
        """
        # Get task details from Supabase for better notification content
        task_details = self._get_task_details_from_supabase(task_id)
        
        # Get task owner name for "Assigned by" field
        owner_name = assigner_name
        if task_details and task_details.get("owner_id"):
            owner_details = self.get_user_details(task_details.get("owner_id"))
            if owner_details:
                owner_name = owner_details.get("name", assigner_name)
        
        if task_details:
            task_name = task_details.get("task_name", f"Task {task_id}")
            description = task_details.get("description", "No description available")
            due_date = task_details.get("due_date", "No due date set")
            status = task_details.get("status", "Unknown")
            
            # Format due date for display
            if due_date != "No due date set":
                try:
                    from datetime import datetime
                    due_date_obj = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    due_date = due_date_obj.strftime('%Y-%m-%d')
                except:
                    pass
            
            # Get all collaborators for the task
            collaborators = task_details.get("collaborators", [])
            collaborators_info = []
            if collaborators:
                for collab_id in collaborators:
                    collab_details = self.get_user_details(collab_id)
                    if collab_details:
                        collaborators_info.append(collab_details.get("name", f"User {collab_id}"))
            
            collaborators_text = ", ".join(collaborators_info) if collaborators_info else "None"
            
            # HTML content for email - following the new format
            notification_content = f"""
            <h3 style="color: #1f2937; margin-bottom: 16px;"><strong>Task Assignment Summary</strong></h3>
            <p style="color: #374151; margin-bottom: 12px;">You have been added as a collaborator to:</p>
            <ul style="color: #374151; margin-bottom: 16px;">
                <li><strong>Task:</strong> {task_name}</li>
                <li><strong>Task ID:</strong> {task_id}</li>
                <li><strong>Description:</strong> {description}</li>
                <li><strong>Status:</strong> {status}</li>
                <li><strong>Due Date:</strong> {due_date}</li>
                <li><strong>Added by:</strong> {owner_name}</li>
                <li><strong>Your Role:</strong> Collaborator</li>
                <li><strong>All Collaborators:</strong> {collaborators_text}</li>
            </ul>
            <p style="color: #6b7280; font-size: 14px;">You can now view and collaborate on this task in your SPM dashboard.</p>
            """
            
            # Plain text content for in-app notification - following the new format
            plain_text = f"""**Task Assignment Summary**
You have been added as a collaborator to:

Task: {task_name}
Task ID: {task_id}
Description: {description}
Status: {status}
Due Date: {due_date}
Added by: {owner_name}
Your Role: Collaborator
All Collaborators: {collaborators_text}

You can now view and collaborate on this task in your SPM dashboard."""
        else:
            # HTML content for email
            notification_content = f"""
            <h3 style="color: #1f2937; margin-bottom: 16px;"><strong>Task Assignment Summary</strong></h3>
            <p style="color: #374151; margin-bottom: 12px;">You have been added as a collaborator to task (ID: {task_id}) by {owner_name}.</p>
            <p style="color: #6b7280; font-size: 14px;">You can now view and collaborate on this task in your SPM dashboard.</p>
            """
            
            # Plain text content for in-app notification
            plain_text = f"""**Task Assignment Summary**
You have been added as a collaborator to task (ID: {task_id}) by {owner_name}.

You can now view and collaborate on this task in your SPM dashboard."""
        
        return self.send_notification_based_on_preferences(
            assigned_user_id, 
            notification_content, 
            "task_assigned", 
            None,  # Set to None to avoid foreign key constraint
            plain_text
        )
    
    def notify_task_ownership_transfer(self, task_id: int, new_owner_id: int, previous_owner_name: str = "System") -> Dict[str, Any]:
        """
        Send notification when task ownership is transferred to a new user.
        """
        # Get task details from Supabase for better notification content
        task_details = self._get_task_details_from_supabase(task_id)
        
        if task_details:
            task_name = task_details.get("task_name", f"Task {task_id}")
            description = task_details.get("description", "No description available")
            due_date = task_details.get("due_date", "No due date set")
            status = task_details.get("status", "Unknown")
            
            # Format due date for display
            if due_date != "No due date set":
                try:
                    from datetime import datetime
                    due_date_obj = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    due_date = due_date_obj.strftime('%Y-%m-%d')
                except:
                    pass
            
            # HTML content for email - using the same format as task update notifications
            notification_content = f"""
            <h3 style="color: #1f2937; margin-bottom: 16px;"><strong>Task Assignment Summary</strong></h3>
            <p style="color: #374151; margin-bottom: 12px;">You have been assigned as the new owner of:</p>
            <ul style="color: #374151; margin-bottom: 16px;">
                <li><strong>Task:</strong> {task_name}</li>
                <li><strong>Task ID:</strong> {task_id}</li>
                <li><strong>Description:</strong> {description}</li>
                <li><strong>Status:</strong> {status}</li>
                <li><strong>Due Date:</strong> {due_date}</li>
                <li><strong>Assigned by:</strong> {previous_owner_name}</li>
                <li><strong>Your Role:</strong> Owner</li>
            </ul>
            <p style="color: #6b7280; font-size: 14px;">As the new owner, you are responsible for managing this task and can edit its details.</p>
            """
            
            # Plain text content for in-app notification - using the same format as task update notifications
            plain_text = f"""**Task Assignment Summary**
You have been assigned as the new owner of:

Task: {task_name}
Task ID: {task_id}
Description: {description}
Status: {status}
Due Date: {due_date}
Assigned by: {previous_owner_name}
Your Role: Owner

As the new owner, you are responsible for managing this task and can edit its details."""
        else:
            # HTML content for email
            notification_content = f"""
            <h3 style="color: #1f2937; margin-bottom: 16px;"><strong>Task Assignment Summary</strong></h3>
            <p style="color: #374151; margin-bottom: 12px;">You have been assigned as the new owner of task (ID: {task_id}) by {previous_owner_name}.</p>
            <p style="color: #6b7280; font-size: 14px;">As the new owner, you are responsible for managing this task and can edit its details.</p>
            """
            
            # Plain text content for in-app notification
            plain_text = f"""
**Task Assignment Summary**
You have been assigned as the new owner of task (ID: {task_id}) by {previous_owner_name}.

As the new owner, you are responsible for managing this task and can edit its details."""
        
        return self.send_notification_based_on_preferences(
            new_owner_id, 
            notification_content, 
            "task_assigned", 
            None,  # Set to None to avoid foreign key constraint
            plain_text
        )
    
    def notify_subtask_assignment(self, subtask_id: int, assigned_user_id: int, parent_task_id: int, assigner_name: str = "System") -> Dict[str, Any]:
        """
        Send notification when a subtask is assigned to a user as a collaborator.
        """
        # Get subtask and parent task details from Supabase
        subtask_details = self._get_task_details_from_supabase(subtask_id)
        parent_task_details = self._get_task_details_from_supabase(parent_task_id)
        
        # Get subtask owner name for "Assigned by" field
        owner_name = assigner_name
        if subtask_details and subtask_details.get("owner_id"):
            owner_details = self.get_user_details(subtask_details.get("owner_id"))
            if owner_details:
                owner_name = owner_details.get("name", assigner_name)
        
        if subtask_details and parent_task_details:
            subtask_name = subtask_details.get("task_name", f"Subtask {subtask_id}")
            parent_task_name = parent_task_details.get("task_name", f"Task {parent_task_id}")
            description = subtask_details.get("description", "No description available")
            due_date = subtask_details.get("due_date", "No due date set")
            status = subtask_details.get("status", "Unknown")
            
            # HTML content for email
            notification_content = f"""
            <p><strong>Subtask Assignment Notification</strong></p>
            <p>You have been assigned as a collaborator to a subtask:</p>
            <ul>
                <li><strong>Subtask:</strong> {subtask_name}</li>
                <li><strong>Subtask ID:</strong> {subtask_id}</li>
                <li><strong>Parent Task:</strong> {parent_task_name}</li>
                <li><strong>Parent Task ID:</strong> {parent_task_id}</li>
                <li><strong>Description:</strong> {description}</li>
                <li><strong>Status:</strong> {status}</li>
                <li><strong>Due Date:</strong> {due_date}</li>
                <li><strong>Assigned by:</strong> {owner_name}</li>
                <li><strong>Role:</strong> Collaborator</li>
            </ul>
            <p>You can now view and collaborate on this subtask in your SPM dashboard.</p>
            """
            
            # Plain text content for in-app notification
            plain_text = f"You have been assigned a new subtask '{subtask_name}' under task '{parent_task_name}' by {owner_name}"
        else:
            # HTML content for email
            notification_content = f"""
            <p><strong>Subtask Assignment Notification</strong></p>
            <p>You have been assigned to subtask (ID: {subtask_id}) under task {parent_task_id} as a collaborator by {owner_name}.</p>
            <p>You can now view and collaborate on this subtask in your SPM dashboard.</p>
            """
            
            # Plain text content for in-app notification
            plain_text = f"You have been assigned to subtask (ID: {subtask_id}) under task {parent_task_id} by {owner_name}"
        
        return self.send_notification_based_on_preferences(
            assigned_user_id, 
            notification_content, 
            "task_assigned", 
            None,  # Set to None to avoid foreign key constraint
            plain_text
        )
    
    
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
    
    def notify_project_collaborator_addition(self, project_id: int, collaborator_ids: List[int], project_name: str, adder_name: str = "System") -> List[Dict[str, Any]]:
        """
        Send notifications when collaborators are added to a project.
        """
        results = []
        
        # Get project details to get all collaborators
        try:
            response = requests.get(f"http://127.0.0.1:5001/projects/{project_id}")
            if response.status_code == 200:
                project_data = response.json().get("data", {})
                all_collaborators = project_data.get("collaborators", [])
                
                # Get collaborator names
                collaborators_info = []
                if all_collaborators:
                    for collab_id in all_collaborators:
                        collab_details = self.get_user_details(collab_id)
                        if collab_details:
                            collaborators_info.append(collab_details.get("name", f"User {collab_id}"))
                
                collaborators_text = ", ".join(collaborators_info) if collaborators_info else "None"
            else:
                collaborators_text = "Unable to fetch"
        except:
            collaborators_text = "Unable to fetch"
        
        for collaborator_id in collaborator_ids:
            # HTML content for email - following the new format
            notification_content = f"""
            <h3 style="color: #1f2937; margin-bottom: 16px;"><strong>Project Assignment Summary</strong></h3>
            <p style="color: #374151; margin-bottom: 12px;">You have been added as a collaborator to:</p>
            <ul style="color: #374151; margin-bottom: 16px;">
                <li><strong>Project:</strong> {project_name}</li>
                <li><strong>Project ID:</strong> {project_id}</li>
                <li><strong>Added by:</strong> {adder_name}</li>
                <li><strong>Your Role:</strong> Collaborator</li>
                <li><strong>All Collaborators:</strong> {collaborators_text}</li>
            </ul>
            <p style="color: #6b7280; font-size: 14px;">You can now view and contribute to this project.</p>
            """
            
            # Plain text content for in-app notification - following the new format
            plain_text = f"""**Project Assignment Summary**
You have been added as a collaborator to:

Project: {project_name}
Project ID: {project_id}
Added by: {adder_name}
Your Role: Collaborator
All Collaborators: {collaborators_text}

You can now view and contribute to this project."""
            
            result = self.send_notification_based_on_preferences(
                collaborator_id,
                notification_content,
                "project_collaborator_added",
                None,
                plain_text
            )
            results.append({"user_id": collaborator_id, "result": result})
        
        return results
    
    def notify_task_consolidated_update(self, task_id: int, user_ids: List[int], changes: List[Dict[str, Any]], updater_name: str = "System") -> List[Dict[str, Any]]:
        """
        Send consolidated notification when multiple task fields are updated.
        This creates one notification per user that includes all changes.
        """
        # Get task details from Supabase for better notification content
        task_details = self._get_task_details_from_supabase(task_id)
        task_name = task_details.get("task_name", f"Task {task_id}") if task_details else f"Task {task_id}"
        
        # Build change summary for email and in-app
        changes_html = ""
        changes_text = []
        
        for change in changes:
            field_name = change.get("field_name", change.get("field", "Unknown"))
            old_value = change.get("old_value", "Not set")
            new_value = change.get("new_value", "Not set")
            
            # Format values for display
            if field_name == "Due Date" and old_value != "Not set":
                try:
                    from datetime import datetime
                    old_date = datetime.fromisoformat(old_value.replace('Z', '+00:00')).strftime('%Y-%m-%d')
                    new_date = datetime.fromisoformat(new_value.replace('Z', '+00:00')).strftime('%Y-%m-%d')
                    old_value = old_date
                    new_value = new_date
                except:
                    pass
            
            changes_html += f"""
            <li><strong>{field_name}:</strong> {old_value} → {new_value}</li>
            """
            changes_text.append(f"{field_name}: {old_value} → {new_value}")
        
        # HTML content for email - using your specified format with bold heading
        notification_content = f"""
        <h3 style="color: #1f2937; margin-bottom: 16px;"><strong>Task Update Summary</strong></h3>
        <p style="color: #374151; margin-bottom: 12px;">Changes made to your task {task_id}:</p>
        <ul style="color: #374151; margin-bottom: 16px;">
            {changes_html}
        </ul>
        <p style="color: #6b7280; font-size: 14px;">Please review the updated task details and take any necessary actions.</p>
        """
        
        # Plain text content for in-app notification - using your specified format with bold heading
        changes_summary = "\n".join(changes_text)
        plain_text = f"""**Task Update Summary**
Changes made to your task {task_id}:
{changes_summary}

Please review the updated task details and take any necessary actions."""
        
        results = []
        for user_id in user_ids:
            result = self.send_notification_based_on_preferences(
                user_id,
                notification_content,
                "task_updated",
                None,  # Set to None to avoid foreign key constraint issues
                plain_text
            )
            results.append({"user_id": user_id, "result": result})
        
        return results

