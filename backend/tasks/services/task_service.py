from typing import Dict, Any, Optional
from datetime import datetime, UTC, timedelta,timezone
from dateutil import parser as dateparser
from dateutil.relativedelta import relativedelta
from models.task import Task
from repo.supa_task_repo import SupabaseTaskRepo
import requests
import time
import copy
import calendar

class TaskService:
    def __init__(self, repo: Optional[SupabaseTaskRepo] = None):
        self.repo = repo or SupabaseTaskRepo()
        self._notification_cache = {}  # Cache to prevent duplicate notifications

    def manager_create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # uniqueness per owner: task_name
        existing = self.repo.find_by_owner_and_name(payload["owner_id"], payload["task_name"])
        if existing:
            # convention: 200 with message (kept from your original)
            return {"__status": 200, "Message": f"Task '{payload['task_name']}' already exists for this user.", "data": existing}


        # Use the new Task.from_dict constructor for proper type handling
        task = Task.from_dict(payload)

        # Convert to dictionary for database insertion (excludes id=None)
        data = task.to_dict()
        data.pop("id", None)

        created = self.repo.insert_task(data)
        
        # Trigger collaborator notifications after successful task creation
        self._trigger_collaborator_notifications(created.get('id'), payload)
        
        return {"__status": 201, "Message": f"Task created! Task ID: {created.get('id')}", "data": created}

    # get tasks by user_id (in owner_id or collaborators) with nested subtasks
    def get_by_user(self, user_id: int) -> Dict[str, Any]:

        # Get only parent tasks for the user
        parent_tasks = self.repo.find_parent_tasks_by_user(user_id)
        
        # Check if no tasks found
        if not parent_tasks:
            return {"__status": 404, "Message": f"No tasks found for user ID {user_id}"}
        
        # For each parent task, get its subtasks
        for parent_task in parent_tasks:
            parent_task_id = parent_task["id"]
            subtasks = self.repo.find_subtasks_by_parent(parent_task_id)
            
            # Format subtasks for frontend
            formatted_subtasks = []
            for subtask in subtasks:
                formatted_subtask = {
                    "id": subtask["id"],
                    "task_name": subtask["task_name"], 
                    "description": subtask["description"],
                    "due_date": subtask["due_date"],  
                    "status": subtask["status"],
                    "owner_id": subtask["owner_id"],
                    "collaborators": subtask["collaborators"] or [],
                    "project_id": subtask["project_id"],
                    "created_at": subtask["created_at"],
                    "parent_task": subtask["parent_task"],
                    "type": subtask["type"]
                }
                formatted_subtasks.append(formatted_subtask)
            
            # Format parent task for frontend
            parent_task["subtasks"] = formatted_subtasks
        
        return {
            "__status": 200,
            "status": "success",
            "data": parent_tasks
        }

    def update_status(self, task_id: int, new_status: str):
        updated = self.repo.update_task(task_id, {"status": new_status})
        return updated

    def manager_create_subtask(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a subtask and automatically update the parent task's subtasks list.
        """
        # Check that parent task exists
        parent_task_id = payload.get("parent_task")
        if not parent_task_id:
            raise ValueError("parent_task is required for subtasks")
        
        parent_task = self.repo.get_task(parent_task_id)
        if not parent_task:
            raise ValueError(f"Parent task with ID {parent_task_id} not found")
        
        # Ensure type is set to subtask
        subtask_payload = self._prepare_subtask_payload(payload)
        
        # Create the subtask using the regular create method
        result = self.manager_create(subtask_payload)
        
        # If subtask was successfully created, update the parent
        if result.get("__status") == 201 and result.get("data", {}).get("id"):
            subtask_id = result["data"]["id"]
            try:
                # Add this subtask to the parent's subtasks list
                self.repo.add_subtask_to_parent(parent_task_id, subtask_id)
            except Exception as e:
                # Log the error but don't fail the subtask creation
                print(f"Warning: Failed to update parent task {parent_task_id} with subtask {subtask_id}: {e}")
        
        return result

    def update_task_by_id(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a task with the provided fields. Only task_id is required.
        """
        task_id = payload.get("task_id")
        if not task_id:
            return {"__status": 400, "Message": "task_id is required for updates"}
        
        # Check if task exists
        existing_task_data = self.repo.get_task(task_id)
        if not existing_task_data:
            return {"__status": 404, "Message": f"Task with ID {task_id} not found"}
        
        # Extract update fields (exclude task_id from the update data)
        update_fields = {k: v for k, v in payload.items() if k != "task_id"}
        
        if not update_fields:
            return {"__status": 400, "Message": "No fields to update provided", "data": existing_task_data}
        
        # Handle status change logic - auto-set completed_at timestamp
        if 'status' in update_fields:
            new_status = update_fields['status']
            old_status = existing_task_data.get('status')
            
            # If status is changing TO "Completed", set completed_at timestamp
            if new_status == 'Completed' and old_status != 'Completed':
                update_fields['completed_at'] = datetime.now(UTC).isoformat()
                try:
                    self._generate_next_occurrence(existing_task_data)
                except Exception as e:
                    print(f"⚠️ Failed to generate recurring task for {task_id}: {e}")
            
            # If status is changing FROM "Completed" to something else, clear completed_at
            elif old_status == 'Completed' and new_status != 'Completed':
                update_fields['completed_at'] = None
        
        # Create Task object from existing data for proper type handling
        existing_task = Task.from_dict(existing_task_data)
        
        # Merge update fields with existing data
        merged_data = existing_task.to_dict()
        merged_data.update(update_fields)
        
        # Create updated task object to ensure proper type conversion
        updated_task_obj = Task.from_dict(merged_data)
        
        # Convert back to dict for database update
        update_data = updated_task_obj.to_dict()
        
        # Perform the update
        try:
            updated_task_data = self.repo.update_task(task_id, update_data)
            
            # Check for collaborator additions and trigger notifications
            self._trigger_collaborator_addition_notifications(existing_task_data, update_fields, task_id)
            
            # Notifications are now handled by the frontend to prevent duplicates
            # self._trigger_update_notifications(existing_task_data, update_fields, task_id)
            
            return {"__status": 200, "Message": f"Task {task_id} updated successfully", "data": updated_task_data}
        except Exception as e:
            return {"__status": 500, "Message": f"Failed to update task {task_id}: {str(e)}"}

    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        task = self.repo.get_task(task_id)
        return task

    def _trigger_update_notifications(self, existing_task_data: Dict[str, Any], update_fields: Dict[str, Any], task_id: int):
        """
        Trigger consolidated notifications when specific task fields are updated.
        """
        try:
            print(f"DEBUG: Triggering consolidated notifications for task {task_id} with fields: {list(update_fields.keys())}")
            
            # Create a cache key for this update to prevent duplicates
            cache_key = f"{task_id}_{hash(str(sorted(update_fields.items())))}"
            
            # Check if we've already sent notifications for this exact update
            if cache_key in self._notification_cache:
                print(f"DEBUG: Notifications already sent for this update, skipping duplicate")
                return
            
            # Get collaborators to notify
            collaborators = existing_task_data.get("collaborators", [])
            if not collaborators:
                print(f"DEBUG: No collaborators found for task {task_id}")
                return  # No collaborators to notify
            
            print(f"DEBUG: Notifying collaborators: {collaborators}")
            
            # Get updater name (not used in notifications anymore)
            updater_name = "System"
            
            # Collect all changes for consolidated notification
            changes = []
            
            # Check for status changes
            if "status" in update_fields:
                old_status = existing_task_data.get("status", "Unknown")
                new_status = update_fields["status"]
                if old_status != new_status:
                    changes.append({
                        "field": "status",
                        "old_value": old_status,
                        "new_value": new_status,
                        "field_name": "Status"
                    })
            
            # Check for due date changes
            if "due_date" in update_fields:
                old_due_date = existing_task_data.get("due_date", "No due date set")
                new_due_date = update_fields["due_date"]
                if old_due_date != new_due_date:
                    changes.append({
                        "field": "due_date",
                        "old_value": old_due_date,
                        "new_value": new_due_date,
                        "field_name": "Due Date"
                    })
            
            # Check for description changes
            if "description" in update_fields:
                old_description = existing_task_data.get("description", "")
                new_description = update_fields["description"]
                if old_description != new_description:
                    changes.append({
                        "field": "description",
                        "old_value": old_description,
                        "new_value": new_description,
                        "field_name": "Description"
                    })
            
            # Check for task name/title changes
            if "task_name" in update_fields:
                old_task_name = existing_task_data.get("task_name", "")
                new_task_name = update_fields["task_name"]
                if old_task_name != new_task_name:
                    changes.append({
                        "field": "task_name",
                        "old_value": old_task_name,
                        "new_value": new_task_name,
                        "field_name": "Task Title"
                    })
            
            # Check for priority changes
            if "priority" in update_fields:
                old_priority = existing_task_data.get("priority", "Not set")
                new_priority = update_fields["priority"]
                if old_priority != new_priority:
                    changes.append({
                        "field": "priority",
                        "old_value": old_priority,
                        "new_value": new_priority,
                        "field_name": "Priority"
                    })
            
            # Check for ownership changes (this is handled separately as it's a different type of notification)
            if "owner_id" in update_fields:
                old_owner_id = existing_task_data.get("owner_id")
                new_owner_id = update_fields["owner_id"]
                if old_owner_id != new_owner_id and new_owner_id:
                    self._send_task_ownership_transfer_notification(task_id, new_owner_id, old_owner_id, updater_name)
            
            # Send consolidated notification if there are changes
            if changes:
                self._send_consolidated_task_update_notification(task_id, collaborators, changes, updater_name)
                
                # Cache this update to prevent duplicates (expire after 5 minutes)
                self._notification_cache[cache_key] = {
                    'timestamp': time.time(),
                    'changes': [change['field'] for change in changes]
                }
                print(f"DEBUG: Cached consolidated notification for {cache_key}, changes: {[change['field'] for change in changes]}")
                
                # Clean up old cache entries (older than 5 minutes)
                current_time = time.time()
                self._notification_cache = {
                    k: v for k, v in self._notification_cache.items() 
                    if current_time - v['timestamp'] < 300
                }
                    
        except Exception as e:
            print(f"Warning: Failed to trigger update notifications for task {task_id}: {e}")
    
    # Individual notification methods removed - now using consolidated notifications only
    
    def _send_consolidated_task_update_notification(self, task_id: int, collaborators: list, changes: list, updater_name: str):
        """Send consolidated notification for multiple task changes."""
        try:
            response = requests.post("http://127.0.0.1:5006/notifications/triggers/task-consolidated-update",
                                   json={
                                       "task_id": task_id,
                                       "user_ids": collaborators,
                                       "changes": changes,
                                       "updater_name": updater_name
                                   })
            if response.status_code not in [200, 201]:
                print(f"Warning: Failed to send consolidated update notification: {response.status_code}")
        except Exception as e:
            print(f"Warning: Failed to send consolidated update notification: {e}")
    
    def _send_task_ownership_transfer_notification(self, task_id: int, new_owner_id: int, old_owner_id: int, updater_name: str):
        """Send notification for task ownership transfer."""
        try:
            # Get old owner name for the notification
            old_owner_name = "Previous Owner"
            if old_owner_id:
                try:
                    response = requests.get(f"http://127.0.0.1:5003/users/{old_owner_id}")
                    if response.status_code == 200:
                        user_data = response.json()
                        old_owner_name = user_data.get("data", {}).get("name", "Previous Owner")
                except Exception:
                    pass  # Use default name if we can't fetch it
            
            response = requests.post("http://127.0.0.1:5006/notifications/triggers/task-ownership-transfer", 
                                   json={
                                       "task_id": task_id,
                                       "new_owner_id": new_owner_id,
                                       "previous_owner_name": old_owner_name
                                   })
            if response.status_code not in [200, 201]:
                print(f"Warning: Failed to send ownership transfer notification: {response.status_code}")
        except Exception as e:
            print(f"Warning: Failed to send ownership transfer notification: {e}")

    def _trigger_collaborator_notifications(self, task_id: int, payload: Dict[str, Any]):
        """
        Trigger notifications for collaborators when a new task is created.
        """
        try:
            # Get collaborators from payload
            collaborators = payload.get("collaborators", [])
            owner_id = payload.get("owner_id")
            
            # Get creator name
            creator_name = "System"
            if owner_id:
                try:
                    response = requests.get(f"http://127.0.0.1:5003/users/{owner_id}")
                    if response.status_code == 200:
                        user_data = response.json()
                        creator_name = user_data.get("data", {}).get("name", "System")
                except Exception:
                    pass  # Use default name if we can't fetch it
            
            # Send notifications to all collaborators except the owner
            collaborator_ids = [collab_id for collab_id in collaborators if collab_id != owner_id]
            
            if collaborator_ids:
                response = requests.post("http://127.0.0.1:5006/notifications/triggers/task-collaborator-addition", 
                                       json={
                                           "task_id": task_id,
                                           "collaborator_ids": collaborator_ids,
                                           "creator_name": creator_name
                                       })
                if response.status_code not in [200, 201]:
                    print(f"Warning: Failed to send collaborator notifications: {response.status_code}")
        except Exception as e:
            print(f"Warning: Failed to send collaborator notifications: {e}")

    def _trigger_collaborator_addition_notifications(self, existing_task_data: Dict[str, Any], update_fields: Dict[str, Any], task_id: int):
        """
        Trigger notifications for newly added collaborators when updating an existing task.
        """
        try:
            # Check if collaborators field was updated
            if 'collaborators' not in update_fields:
                return
            
            # Get existing and new collaborators
            existing_collaborators = set(existing_task_data.get("collaborators", []) or [])
            new_collaborators = set(update_fields.get("collaborators", []) or [])
            
            # Find newly added collaborators (excluding the owner)
            owner_id = existing_task_data.get("owner_id")
            newly_added_collaborators = new_collaborators - existing_collaborators
            
            # Remove owner from newly added collaborators (they shouldn't get notifications)
            if owner_id:
                newly_added_collaborators.discard(owner_id)
            
            if not newly_added_collaborators:
                return
            
            # Get updater name
            updater_name = "System"
            # Try to get updater from request context or use owner as fallback
            if owner_id:
                try:
                    response = requests.get(f"http://127.0.0.1:5003/users/{owner_id}")
                    if response.status_code == 200:
                        user_data = response.json()
                        updater_name = user_data.get("data", {}).get("name", "System")
                except Exception:
                    pass  # Use default name if we can't fetch it
            
            # Send notifications to newly added collaborators
            collaborator_ids = list(newly_added_collaborators)
            if collaborator_ids:
                response = requests.post("http://127.0.0.1:5006/notifications/triggers/task-collaborator-addition", 
                                       json={
                                           "task_id": task_id,
                                           "collaborator_ids": collaborator_ids,
                                           "creator_name": updater_name
                                       })
                if response.status_code not in [200, 201]:
                    print(f"Warning: Failed to send collaborator addition notifications: {response.status_code}")
        except Exception as e:
            print(f"Warning: Failed to send collaborator addition notifications: {e}")

    def staff_create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a task for staff and automatically add owner_id to collaborators list.
        """
        # Get the owner_id
        owner_id = payload.get("owner_id")
        if not owner_id:
            raise ValueError("owner_id is required")
        
        # Check for existing task with same name for this owner
        existing = self.repo.find_by_owner_and_name(payload["owner_id"], payload["task_name"])
        if existing:
            # Return 200 with existing task data (same as manager_create)
            return {"__status": 200, "Message": f"Task '{payload['task_name']}' already exists for this user.", "data": existing}
        
        # Get existing collaborators or initialize empty list
        collaborators = payload.get("collaborators") or []
        
        # Add owner_id to collaborators if not already present
        if owner_id not in collaborators:
            collaborators.append(owner_id)
        
        # Update payload with modified collaborators
        payload["collaborators"] = collaborators
        
        # Use the regular manager_create method
        return self.manager_create(payload)

    def staff_create_subtask(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a subtask for staff and automatically add owner_id to collaborators list.
        Also updates the parent task's subtasks list.
        """
        # Check that parent task exists
        parent_task_id = payload.get("parent_task")
        if not parent_task_id:
            raise ValueError("parent_task is required for subtasks")
        
        parent_task = self.repo.get_task(parent_task_id)
        if not parent_task:
            raise ValueError(f"Parent task with ID {parent_task_id} not found")
        
        # Get the owner_id
        owner_id = payload.get("owner_id")
        if not owner_id:
            raise ValueError("owner_id is required")
        
        # Get existing collaborators or initialize empty list
        collaborators = payload.get("collaborators") or []
        
        # Add owner_id to collaborators if not already present
        if owner_id not in collaborators:
            collaborators.append(owner_id)
        
        subtask_payload = self._prepare_subtask_payload(payload)
        result = self.manager_create(subtask_payload)
        
        # If subtask was successfully created, update the parent
        if result.get("__status") == 201 and result.get("data", {}).get("id"):
            subtask_id = result["data"]["id"]
            try:
                # Add this subtask to the parent's subtasks list
                self.repo.add_subtask_to_parent(parent_task_id, subtask_id)
            except Exception as e:
                # Log the error but don't fail the subtask creation
                print(f"Warning: Failed to update parent task {parent_task_id} with subtask {subtask_id}: {e}")
        
        return result

    # def get_task_by_id(self, task_id: int) -> Dict[str, Any]:
    #     """
    #     Get a single task by its ID.
    #     """
    #     task = self.repo.get_task(task_id)
    #     if not task:
    #         return {"__status": 404, "Message": f"Task with ID {task_id} not found"}
    #     return {"__status": 200, "data": task}

    def get_tasks_by_project(self, project_id: int) -> Dict[str, Any]:
        """
        Get all tasks that belong to a specific project.
        """
        tasks = self.repo.find_by_project(project_id)
        if not tasks:
            return {"__status": 404, "Message": f"No tasks found for project ID {project_id}"}
        return {"__status": 200, "data": tasks}

    def get_tasks_by_owner(self, owner_id: int) -> Dict[str, Any]:
        """
        Get all tasks that are owned by a specific user (by owner_id only).
        """
        tasks = self.repo.find_by_owner(owner_id)
        if not tasks:
            return {"__status": 404, "Message": f"No tasks found for owner ID {owner_id}"}
        return {"__status": 200, "data": tasks}

    def bulk_update_project_id(self, task_ids: list, project_id: int) -> Dict[str, Any]:
        """
        Bulk update the project_id for multiple tasks.
        
        Args:
            task_ids: List of task IDs to update
            project_id: The project ID to set for all tasks
            
        Returns:
            Dict with status, message, and results
        """
        if not task_ids:
            return {"__status": 400, "Message": "task_ids list cannot be empty"}
        
        if not isinstance(task_ids, list):
            return {"__status": 400, "Message": "task_ids must be a list"}
        
        if not all(isinstance(task_id, int) for task_id in task_ids):
            return {"__status": 400, "Message": "All task_ids must be integers"}
        
        if not isinstance(project_id, int):
            return {"__status": 400, "Message": "project_id must be an integer"}
        
        updated_tasks = []
        failed_updates = []
        
        for task_id in task_ids:
            try:
                # Check if task exists
                existing_task = self.repo.get_task(task_id)
                if not existing_task:
                    failed_updates.append({"task_id": task_id, "error": "Task not found"})
                    continue
                
                # Update the task's project_id
                updated_task = self.repo.update_task(task_id, {"project_id": project_id})
                updated_tasks.append(updated_task)
                
            except Exception as e:
                failed_updates.append({"task_id": task_id, "error": str(e)})
        
        # Prepare response
        total_tasks = len(task_ids)
        successful_updates = len(updated_tasks)
        failed_count = len(failed_updates)
        
        if successful_updates == 0:
            return {
                "__status": 400,
                "Message": f"Failed to update any tasks. {failed_count} tasks failed to update.",
                "data": {
                    "total_tasks": total_tasks,
                    "successful_updates": successful_updates,
                    "failed_updates": failed_count,
                    "failed_details": failed_updates
                }
            }
        elif failed_count > 0:
            return {
                "__status": 207,  # Multi-status
                "Message": f"Partially successful: {successful_updates} tasks updated, {failed_count} failed",
                "data": {
                    "total_tasks": total_tasks,
                    "successful_updates": successful_updates,
                    "failed_updates": failed_count,
                    "updated_tasks": updated_tasks,
                    "failed_details": failed_updates
                }
            }
        else:
            return {
                "__status": 200,
                "Message": f"Successfully updated project_id to {project_id} for {successful_updates} tasks",
                "data": {
                    "total_tasks": total_tasks,
                    "successful_updates": successful_updates,
                    "failed_updates": failed_count,
                    "updated_tasks": updated_tasks
                }
            }

    def get_subtasks_by_parent(self, parent_task_id: int) -> Dict[str, Any]:
        """
        Get all subtask details for a given parent task ID.
        
        Args:
            parent_task_id: ID of the parent task
            
        Returns:
            Dict with status, message, and subtask details
        """
        # First, get the parent task to verify it exists and get its subtasks list
        parent_task = self.repo.get_task(parent_task_id)
        if not parent_task:
            return {"__status": 404, "Message": f"Parent task with ID {parent_task_id} not found"}
        
        # Get the subtasks list from the parent task
        subtask_ids = parent_task.get("subtasks") or []
        
        if not subtask_ids:
            return {
                "__status": 200,
                "Message": f"No subtasks found for parent task {parent_task_id}",
                "data": {
                    "parent_task_id": parent_task_id,
                    "subtasks": [],
                    "subtask_count": 0
                }
            }
        
        # Get details for each subtask
        subtask_details = []
        failed_subtasks = []
        
        for subtask_id in subtask_ids:
            try:
                subtask = self.repo.get_task(subtask_id)
                if subtask:
                    subtask_details.append(subtask)
                else:
                    failed_subtasks.append({"subtask_id": subtask_id, "error": "Subtask not found"})
            except Exception as e:
                failed_subtasks.append({"subtask_id": subtask_id, "error": str(e)})
        
        # Prepare response
        if not subtask_details:
            return {
                "__status": 404,
                "Message": f"No valid subtasks found for parent task {parent_task_id}",
                "data": {
                    "parent_task_id": parent_task_id,
                    "subtasks": [],
                    "subtask_count": 0,
                    "failed_subtasks": failed_subtasks
                }
            }
        
        response_data = {
            "parent_task_id": parent_task_id,
            "subtasks": subtask_details,
            "subtask_count": len(subtask_details)
        }
        
        if failed_subtasks:
            response_data["failed_subtasks"] = failed_subtasks
            return {
                "__status": 207,  # Multi-status for partial success
                "Message": f"Retrieved {len(subtask_details)} subtasks for parent task {parent_task_id}, {len(failed_subtasks)} failed",
                "data": response_data
            }
        else:
            return {
                "__status": 200,
                "Message": f"Successfully retrieved {len(subtask_details)} subtasks for parent task {parent_task_id}",
                "data": response_data
            }

    def get_tasks_by_team(self, team_id: int) -> Dict[str, Any]:
        """
        Get all tasks for users in a specific team.
        """
        try:
            # Get all parent tasks for team members
            parent_tasks = self.repo.find_parent_tasks_by_team(team_id)
            
            # For each parent task, get its subtasks
            for parent_task in parent_tasks:
                parent_task_id = parent_task["id"]
                subtasks = self.repo.find_subtasks_by_parent(parent_task_id)
                
                # Format subtasks for frontend
                formatted_subtasks = []
                for subtask in subtasks:
                    formatted_subtask = {
                        "id": subtask["id"],
                        "task_name": subtask["task_name"], 
                        "description": subtask["description"],
                        "due_date": subtask["due_date"],  
                        "status": subtask["status"],
                        "owner_id": subtask["owner_id"],
                        "collaborators": subtask["collaborators"] or [],
                        "project_id": subtask["project_id"],
                        "created_at": subtask["created_at"],
                        "parent_task": subtask["parent_task"],
                        "type": "subtask",
                        "priority": subtask["priority"],
                        "attachments": subtask["attachments"] or []
                    }
                    formatted_subtasks.append(formatted_subtask)
                
                # Add subtasks to parent task
                parent_task["subtasks"] = formatted_subtasks
            
            if not parent_tasks:
                return {
                    "__status": 404,
                    "Message": f"No tasks found for team {team_id}",
                    "data": []
                }
            
            return {
                "__status": 200,
                "Message": f"Successfully retrieved {len(parent_tasks)} tasks for team {team_id}",
                "data": parent_tasks
            }
        except Exception as e:
            return {
                "__status": 500,
                "Message": f"Error retrieving team tasks: {str(e)}",
                "data": []
            }

    def get_tasks_by_department(self, dept_id: int) -> Dict[str, Any]:
        """
        Get all tasks for users in a specific department.
        """
        try:
            # Get all parent tasks for department members
            parent_tasks = self.repo.find_parent_tasks_by_department(dept_id)
            
            # For each parent task, get its subtasks
            for parent_task in parent_tasks:
                parent_task_id = parent_task["id"]
                subtasks = self.repo.find_subtasks_by_parent(parent_task_id)
                
                # Format subtasks for frontend
                formatted_subtasks = []
                for subtask in subtasks:
                    formatted_subtask = {
                        "id": subtask["id"],
                        "task_name": subtask["task_name"], 
                        "description": subtask["description"],
                        "due_date": subtask["due_date"],  
                        "status": subtask["status"],
                        "owner_id": subtask["owner_id"],
                        "collaborators": subtask["collaborators"] or [],
                        "project_id": subtask["project_id"],
                        "created_at": subtask["created_at"],
                        "parent_task": subtask["parent_task"],
                        "type": "subtask",
                        "priority": subtask["priority"],
                        "attachments": subtask["attachments"] or []
                    }
                    formatted_subtasks.append(formatted_subtask)
                
                # Add subtasks to parent task
                parent_task["subtasks"] = formatted_subtasks
            
            if not parent_tasks:
                return {
                    "__status": 404,
                    "Message": f"No tasks found for department {dept_id}",
                    "data": []
                }
            
            return {
                "__status": 200,
                "Message": f"Successfully retrieved {len(parent_tasks)} tasks for department {dept_id}",
                "data": parent_tasks
            }
        except Exception as e:
            return {
                "__status": 500,
                "Message": f"Error retrieving department tasks: {str(e)}",
                "data": []
            }

    def get_tasks_with_upcoming_deadlines(self, max_days_ahead: int = 7) -> Dict[str, Any]:
        """
        Get tasks with upcoming deadlines within the specified number of days.
        
        Args:
            max_days_ahead: Maximum number of days to look ahead for deadlines
            
        Returns:
            Dict with status, message, and task data
        """
        try:
            tasks = self.repo.find_tasks_with_upcoming_deadlines(max_days_ahead)
            
            if not tasks:
                return {
                    "__status": 404,
                    "Message": f"No tasks with upcoming deadlines found in the next {max_days_ahead} days",
                    "data": []
                }
            
            return {
                "__status": 200,
                "Message": f"Successfully retrieved {len(tasks)} tasks with upcoming deadlines",
                "data": tasks
            }
        except Exception as e:
            return {
                "__status": 500,
                "Message": f"Error retrieving tasks with upcoming deadlines: {str(e)}",
                "data": []
            }
        
    def _generate_next_occurrence(self, completed_task: dict):
        """
        Automatically generate the next task occurrence based on recurrence frequency.
        Keeps timezone-awareness intact and ensures next due date > completed_at.
        """
        print(f"⚙️ Generating next occurrence for task {completed_task.get('id')} "
            f"with recurrence_type={completed_task.get('recurrence_type')}")

        recurrence_type = completed_task.get("recurrence_type")
        recurrence_end_date = completed_task.get("recurrence_end_date")
        recurrence_interval_days = completed_task.get("recurrence_interval_days")

        if not recurrence_type or recurrence_type.lower() == "none":
            return  # No recurrence

        due_date_str = completed_task.get("due_date")
        completed_at_str = completed_task.get("completed_at")

        # --- Parse dates safely ---
        try:
            due_date = dateparser.parse(due_date_str)
            if due_date and due_date.tzinfo is None:
                due_date = due_date.replace(tzinfo=timezone.utc)
        except Exception:
            print(f"⚠️ Could not parse due date for task {completed_task.get('id')}")
            return

        try:
            completed_at = dateparser.parse(completed_at_str) if completed_at_str else datetime.now(timezone.utc)
            if completed_at and completed_at.tzinfo is None:
                completed_at = completed_at.replace(tzinfo=timezone.utc)
        except Exception:
            completed_at = datetime.now(timezone.utc)

        # --- Use timezone-aware now() as fallback ---
        now_aware = datetime.now(timezone.utc)

        # --- Determine base date ---
        base_date = max(due_date, completed_at)
        base_date = base_date.replace(
            hour=due_date.hour,
            minute=due_date.minute,
            second=due_date.second,
            microsecond=due_date.microsecond
        )

        # --- Calculate next due date ---
        next_due_date = None
        rec_type = recurrence_type.lower()

        if rec_type == "daily":
            next_due_date = base_date + timedelta(days=1)

        elif rec_type == "weekly":
            next_due_date = due_date
            while next_due_date <= completed_at:
                next_due_date += timedelta(weeks=1)

        elif rec_type == "bi-weekly":
            next_due_date = due_date
            while next_due_date <= completed_at:
                next_due_date += timedelta(weeks=2)

        elif rec_type == "monthly":
            original_day = due_date.day
            next_due_date = due_date
            while next_due_date <= completed_at:
                month = next_due_date.month + 1
                year = next_due_date.year + (month - 1) // 12
                month = (month - 1) % 12 + 1
                last_day = calendar.monthrange(year, month)[1]
                day = min(original_day, last_day)
                next_due_date = next_due_date.replace(year=year, month=month, day=day)

        elif rec_type == "yearly":
            next_due_date = due_date
            while next_due_date <= completed_at:
                next_due_date = next_due_date.replace(year=next_due_date.year + 1)

        elif rec_type == "custom":
            interval = completed_task.get("recurrence_interval_days")
            try:
                interval = int(interval)
            except (TypeError, ValueError):
                interval = None

            if interval and interval > 0:
                next_due_date = base_date + timedelta(days=interval)
            else:
                print(f"⚠️ Invalid custom recurrence interval for task {completed_task.get('id')} (interval={interval})")
                return

        else:
            print(f"⚠️ Unsupported recurrence type '{recurrence_type}'")
            return

        # --- Handle recurrence end date ---
        if recurrence_end_date:
            try:
                recurrence_end = dateparser.parse(recurrence_end_date)
                if recurrence_end and recurrence_end.tzinfo is None:
                    recurrence_end = recurrence_end.replace(tzinfo=timezone.utc)
                if next_due_date > recurrence_end:
                    print(f"ℹ️ Recurrence ended for task {completed_task.get('id')} (end date reached)")
                    return None
            except Exception:
                print(f"⚠️ Could not parse recurrence_end_date '{recurrence_end_date}'")

        # --- Prepare new task payload ---
        task_payload = copy.deepcopy(completed_task)
        task_payload.pop("id", None)
        task_payload["status"] = "Ongoing"
        task_payload["completed_at"] = None
        task_payload["created_at"] = now_aware.isoformat()
        task_payload["due_date"] = next_due_date.isoformat()
        task_payload["type"] = completed_task.get("type", "parent")
        task_payload["recurrence_type"] = recurrence_type
        task_payload["recurrence_end_date"] = recurrence_end_date
        task_payload["recurrence_interval_days"] = recurrence_interval_days

        if completed_task.get("type") == "subtask":
            task_payload["parent_task"] = completed_task.get("parent_task")

        # --- Insert new recurring task ---
        try:
            created = self.repo.insert_task(task_payload)
            print(f"✅ Created recurring task {created.get('id')} for recurrence '{recurrence_type}'")
            if task_payload.get("type") == "subtask" and task_payload.get("parent_task"):
                self.repo.add_subtask_to_parent(task_payload["parent_task"], created["id"])
            return created
        except Exception as e:
            print(f"❌ Failed to create recurring task: {e}")
            return None
        
    def _prepare_subtask_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensures subtask payload has type, owner in collaborators, and recurrence fields.
        """
        owner_id = payload.get("owner_id")
        if not owner_id:
            raise ValueError("owner_id is required")

        collaborators = set(payload.get("collaborators") or [])
        collaborators.add(owner_id)

        subtask_payload = copy.deepcopy(payload)
        subtask_payload["type"] = "subtask"
        subtask_payload["collaborators"] = list(collaborators)
        
        # Include recurrence fields explicitly
        subtask_payload["recurrence_type"] = payload.get("recurrence_type")
        subtask_payload["recurrence_end_date"] = payload.get("recurrence_end_date")
        subtask_payload["recurrence_interval_days"] = payload.get("recurrence_interval_days")
        
        return subtask_payload