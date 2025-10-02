from typing import Dict, Any, Optional
from models.task import Task
from repo.supa_task_repo import SupabaseTaskRepo

class TaskService:
    def __init__(self, repo: Optional[SupabaseTaskRepo] = None):
        self.repo = repo or SupabaseTaskRepo()

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
        return {"__status": 201, "Message": f"Task created! Task ID: {created.get('id')}", "data": created}

    # get tasks by user_id (in owner_id or collaborators) with nested subtasks
    def get_by_user(self, user_id: int) -> Dict[str, Any]:

        # Get only parent tasks for the user
        parent_tasks = self.repo.find_parent_tasks_by_user(user_id)
        
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
        payload["type"] = "subtask"
        
        # Create the subtask using the regular create method
        result = self.manager_create(payload)
        
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
            return {"__status": 200, "Message": f"Task {task_id} updated successfully", "data": updated_task_data}
        except Exception as e:
            return {"__status": 500, "Message": f"Failed to update task {task_id}: {str(e)}"}

    def get_task(self, task_id: int) -> Dict[str, Any]:
        task = self.repo.get_task(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
        return task

    def staff_create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a task for staff and automatically add owner_id to collaborators list.
        """
        # Get the owner_id
        owner_id = payload.get("owner_id")
        if not owner_id:
            raise ValueError("owner_id is required")
        
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
        
        # Update payload with modified collaborators and ensure type is subtask
        payload["collaborators"] = collaborators
        payload["type"] = "subtask"
        
        # Create the subtask using the regular manager_create method
        result = self.manager_create(payload)
        
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