import os
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
        res = self.client.table(TABLE).select("*").eq("id", task_id).single().execute()
        return res.data

    def find_by_user(self, user_id: int) -> list:
        client = getattr(self, "client", None) or getattr(self, "supabase", None)
        if client is None:
            raise RuntimeError("Supabase client not configured on SupabaseTaskRepo")

        # owner
        owner_res = client.table("task").select("*").eq("owner_id", user_id).execute()
        owner_tasks = owner_res.data or []

        # collaborator
        collab_res = client.table("task").select("*").filter("collaborators", "cs", [user_id]).execute()
        collab_tasks = collab_res.data or []

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