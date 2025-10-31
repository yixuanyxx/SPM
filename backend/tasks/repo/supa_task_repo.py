import os
import uuid
from typing import Optional, Dict, Any, List
from supabase import create_client, Client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_KEY"]

# Table name kept as 'task' to match your existing schema.
TABLE = "task"

class SupabaseTaskRepo:
    def __init__(self):
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    def find_by_owner_and_name(self, owner_id: int, task_name: str) -> List[Dict[str, Any]]:
        return self.client.table(TABLE).select("*").eq("owner_id", owner_id).eq("task_name", task_name).execute().data

    def insert_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = self.client.table(TABLE).insert(data).execute()
        if not res.data:
            raise RuntimeError("Insert failed — no data returned")
        return res.data[0]

    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        try:
            res = self.client.table(TABLE).select("*").eq("id", task_id).single().execute()
            return res.data
        except Exception:
            # Task not found or other error
            return None

    def find_by_user(self, user_id: int) -> list:
        """
        Find all tasks (parent and subtask) where user is owner or collaborator.
        This includes both parent tasks and subtasks that the user has access to.
        """
        client = getattr(self, "client", None) or getattr(self, "supabase", None)
        if client is None:
            raise RuntimeError("Supabase client not configured on SupabaseTaskRepo")

        # Get tasks where user is owner
        owner_res = client.table(TABLE).select("*").eq("owner_id", user_id).execute()
        owner_tasks = owner_res.data or []

        # Get tasks where user is collaborator
        collab_res = client.table(TABLE).select("*").filter("collaborators", "cs", [user_id]).execute()
        collab_tasks = collab_res.data or []

        # Combine and deduplicate by ID
        combined = {t["id"]: t for t in (owner_tasks + collab_tasks)}
        return list(combined.values())

    def find_subtasks_by_parent(self, parent_task_id: int) -> List[Dict[str, Any]]:
        """
        Find all subtasks for a given parent task.
        """
        res = self.client.table(TABLE).select("*").eq("parent_task", parent_task_id).eq("type", "subtask").execute()
        return res.data or []

    def find_parent_tasks_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Find only parent tasks (type='parent' or null) where user is owner or collaborator.
        """
        # Get parent tasks where user is owner
        owner_res = self.client.table(TABLE).select("*").eq("owner_id", user_id).in_("type", ["parent", None]).execute()
        owner_tasks = owner_res.data or []

        # Get parent tasks where user is collaborator  
        collab_res = self.client.table(TABLE).select("*").filter("collaborators", "cs", [user_id]).in_("type", ["parent", None]).execute()
        collab_tasks = collab_res.data or []

        # Combine and deduplicate
        combined = {t["id"]: t for t in (owner_tasks + collab_tasks)}
        return list(combined.values())

    def update_task(self, task_id: int, patch: Dict[str, Any]) -> Dict[str, Any]:
        res = self.client.table(TABLE).update(patch).eq("id", task_id).execute()
        if not res.data:
            raise RuntimeError("Update failed — no data returned")
        return res.data[0]

    def add_subtask_to_parent(self, parent_task_id: int, subtask_id: int) -> Dict[str, Any]:
        """
        Add a subtask ID to the parent task's subtasks list.
        """
        # First get the current parent task
        parent_task = self.get_task(parent_task_id)
        if not parent_task:
            raise RuntimeError(f"Parent task with ID {parent_task_id} not found")
        
        # Get current subtasks list or initialize empty list
        current_subtasks = parent_task.get("subtasks") or []
        
        # Add the new subtask ID if not already present
        if subtask_id not in current_subtasks:
            current_subtasks.append(subtask_id)
        
        # Update the parent task with the new subtasks list
        return self.update_task(parent_task_id, {"subtasks": current_subtasks})

    def find_by_project(self, project_id: int) -> list:
        """
        Find all tasks that belong to a specific project.
        """
        res = self.client.table(TABLE).select("*").eq("project_id", project_id).execute()
        return res.data or []

    def find_by_owner(self, owner_id: int) -> list:
        """
        Find all tasks that are owned by a specific user (by owner_id only).
        """
        res = self.client.table(TABLE).select("*").eq("owner_id", owner_id).execute()
        return res.data or []
    
    def upload_attachment(self, file) -> list[dict]:
        """
        Upload a file to Supabase storage and return attachment info.

        Returns:
            [{"url": <public_url>, "name": <filename>}]
        """
        file_name = f"attachments/{uuid.uuid4()}_{file.filename}"
        storage = self.client.storage.from_("task-files")

        try:
            storage.upload(file_name, file.read(), file_options={"content-type": "application/pdf"})
        
            public_url_response = storage.get_public_url(file_name)
            if isinstance(public_url_response, dict):
                public_url = public_url_response.get("data", {}).get("publicUrl")
                if not public_url:
                    raise RuntimeError("Failed to retrieve public URL from Supabase response")
            elif isinstance(public_url_response, str):
                public_url = public_url_response
            else:
                raise RuntimeError(f"Unexpected type for public URL response: {type(public_url_response)}")

            return [{"url": public_url, "name": file.filename}]
    
        except Exception as e:
            raise RuntimeError(f"Upload failed: {str(e)}")
    
    def update_attachments(self, task_id: int, attachments: List[Dict[str, str]]) -> Dict[str, Any]:
        return self.update_task(task_id, {"attachments": attachments})

    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by its ID.
        
        Returns:
            bool: True if task was deleted, False if task not found
        """
        try:
            res = self.client.table(TABLE).delete().eq("id", task_id).execute()
            # Check if any rows were affected
            return res.data is not None and len(res.data) > 0
        except Exception as e:
            print(f"Delete error for task {task_id}: {e}")
            return False

    def find_parent_tasks_by_team(self, team_id: int) -> List[Dict[str, Any]]:
        """
        Find all parent tasks for users in a specific team.
        """
        # Get all users in the team first
        user_res = self.client.table("user").select("userid").eq("team_id", team_id).execute()
        user_ids = [user["userid"] for user in (user_res.data or [])]
        
        if not user_ids:
            return []
        
        # Get parent tasks where any team member is owner or collaborator
        all_tasks = []
        
        for user_id in user_ids:
            # Get parent tasks where user is owner
            owner_res = self.client.table(TABLE).select("*").eq("owner_id", user_id).in_("type", ["parent", None]).execute()
            owner_tasks = owner_res.data or []
            
            # Get parent tasks where user is collaborator  
            collab_res = self.client.table(TABLE).select("*").filter("collaborators", "cs", [user_id]).in_("type", ["parent", None]).execute()
            collab_tasks = collab_res.data or []
            
            all_tasks.extend(owner_tasks + collab_tasks)
        
        # Deduplicate by task ID
        combined = {t["id"]: t for t in all_tasks}
        return list(combined.values())

    def find_parent_tasks_by_department(self, dept_id: int) -> List[Dict[str, Any]]:
        """
        Find all parent tasks for users in a specific department.
        """
        # Get all users in the department first
        user_res = self.client.table("user").select("userid").eq("dept_id", dept_id).execute()
        user_ids = [user["userid"] for user in (user_res.data or [])]
        
        if not user_ids:
            return []
        
        # Get parent tasks where any department member is owner or collaborator
        all_tasks = []
        
        for user_id in user_ids:
            # Get parent tasks where user is owner
            owner_res = self.client.table(TABLE).select("*").eq("owner_id", user_id).in_("type", ["parent", None]).execute()
            owner_tasks = owner_res.data or []
            
            # Get parent tasks where user is collaborator  
            collab_res = self.client.table(TABLE).select("*").filter("collaborators", "cs", [user_id]).in_("type", ["parent", None]).execute()
            collab_tasks = collab_res.data or []
            
            all_tasks.extend(owner_tasks + collab_tasks)
        
        # Deduplicate by task ID
        combined = {t["id"]: t for t in all_tasks}
        return list(combined.values())

    def find_tasks_with_upcoming_deadlines(self, max_days_ahead: int = 7) -> List[Dict[str, Any]]:
        """
        Find tasks with upcoming deadlines within the specified number of days.
        
        Args:
            max_days_ahead: Maximum number of days to look ahead for deadlines
            
        Returns:
            List of tasks with due dates in the next max_days_ahead days
        """
        from datetime import datetime, timedelta
        
        # Calculate date range
        today = datetime.now().date()
        end_date = today + timedelta(days=max_days_ahead)
        
        # Query tasks with due dates in the next max_days_ahead days
        # Exclude completed tasks
        res = self.client.table(TABLE).select("*").gte(
            "due_date", today.isoformat()
        ).lte(
            "due_date", end_date.isoformat()
        ).neq(
            "status", "Completed"
        ).execute()
        
        return res.data or []
    
    def find_all_parent_tasks(self) -> list:
        """
        Find all tasks (parent and subtasks) in the system.
        """
        res = self.client.table(TABLE).select("*").is_("parent_task", None).execute()
        return res.data or []
