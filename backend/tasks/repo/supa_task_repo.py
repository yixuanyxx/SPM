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

    def list_tasks(self, owner_id: Optional[int] = None, project_id: Optional[int] = None) -> List[Dict[str, Any]]:
        q = self.client.table(TABLE).select("*")
        if owner_id is not None:
            q = q.eq("owner_id", owner_id)
        if project_id is not None:
            q = q.eq("project_id", project_id)
        return q.order("created_at", desc=True).execute().data

    def update_task(self, task_id: int, patch: Dict[str, Any]) -> Dict[str, Any]:
        res = self.client.table(TABLE).update(patch).eq("id", task_id).execute()
        if not res.data:
            raise RuntimeError("Update failed — no data returned")
        return res.data[0]
