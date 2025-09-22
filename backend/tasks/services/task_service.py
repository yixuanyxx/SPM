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

        task = Task(
            owner_id=payload["owner_id"],
            task_name=payload["task_name"],
            due_date=payload["due_date"],
            description=payload["description"],
            collaborators=payload.get("collaborators"),
            status=payload.get("status"),
            project_id=payload.get("project_id"),
            parent_task=payload.get("parent_task"),
            type=payload.get("type", "parent"),
            subtasks=payload.get("subtasks"),
        )

        # ⬇️ Do NOT send id=None
        data = task.__dict__.copy()
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
            raise ValueError("task_id is required for updates")
        
        # Check if task exists
        existing_task = self.repo.get_task(task_id)
        if not existing_task:
            raise ValueError(f"Task with ID {task_id} not found")
        
        # Extract update fields (exclude task_id from the update data)
        update_fields = {k: v for k, v in payload.items() if k != "task_id"}
        
        if not update_fields:
            return {"__status": 400, "Message": "No fields to update provided", "data": existing_task}
        
        # Perform the update
        try:
            updated_task = self.repo.update_task(task_id, update_fields)
            return {"__status": 200, "Message": f"Task {task_id} updated successfully", "data": updated_task}
        except Exception as e:
            raise RuntimeError(f"Failed to update task {task_id}: {str(e)}")

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

    def update_task_by_id(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a task with the provided fields. Only task_id is required.
        """
        task_id = payload.get("task_id")
        if not task_id:
            raise ValueError("task_id is required for updates")
        
        # Check if task exists
        existing_task = self.repo.get_task(task_id)
        if not existing_task:
            raise ValueError(f"Task with ID {task_id} not found")
        
        # Extract update fields (exclude task_id from the update data)
        update_fields = {k: v for k, v in payload.items() if k != "task_id"}
        
        if not update_fields:
            return {"__status": 400, "Message": "No fields to update provided", "data": existing_task}
        
        # Perform the update
        try:
            updated_task = self.repo.update_task(task_id, update_fields)
            return {"__status": 200, "Message": f"Task {task_id} updated successfully", "data": updated_task}
        except Exception as e:
            raise RuntimeError(f"Failed to update task {task_id}: {str(e)}")
    

    def get_tasks_by_project(self, project_id: int) -> Dict[str, Any]:
        """
        Get all tasks that belong to a specific project.
        """
        tasks = self.repo.find_by_project(project_id)
        if not tasks:
            return {"__status": 404, "Message": f"No tasks found for project ID {project_id}"}
        return {"__status": 200, "data": tasks}

