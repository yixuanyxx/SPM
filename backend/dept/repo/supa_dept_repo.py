import os
from typing import Optional, Dict, Any, List
from supabase import create_client, Client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_KEY"]

TABLE = "dept"

class SupabaseDeptRepo:
    def __init__(self):
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    def insert_dept(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a new department"""
        res = self.client.table(TABLE).insert(data).execute()
        if not res.data:
            raise RuntimeError("Insert failed — no data returned")
        return res.data[0]

    def get_dept(self, dept_id: int) -> Optional[Dict[str, Any]]:
        """Get department by ID"""
        res = self.client.table(TABLE).select("*").eq("id", dept_id).single().execute()
        return res.data

    def get_all_depts(self) -> List[Dict[str, Any]]:
        """Get all departments"""
        res = self.client.table(TABLE).select("*").execute()
        return res.data or []

    def find_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Find departments by name"""
        res = self.client.table(TABLE).select("*").eq("name", name).execute()
        return res.data or []

    def update_dept(self, dept_id: int, patch: Dict[str, Any]) -> Dict[str, Any]:
        """Update department by ID"""
        res = self.client.table(TABLE).update(patch).eq("id", dept_id).execute()
        if not res.data:
            raise RuntimeError("Update failed — no data returned")
        return res.data[0]

    def delete_dept(self, dept_id: int) -> bool:
        """Delete department by ID"""
        res = self.client.table(TABLE).delete().eq("id", dept_id).execute()
        return len(res.data) > 0