import os
from typing import Optional, Dict, Any, List
from supabase import create_client, Client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_KEY"]

TABLE = "team"

class SupabaseTeamRepo:
    def __init__(self):
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    def insert_team(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a new team"""
        res = self.client.table(TABLE).insert(data).execute()
        if not res.data:
            raise RuntimeError("Insert failed — no data returned")
        return res.data[0]

    def get_team(self, team_id: int) -> Optional[Dict[str, Any]]:
        """Get team by ID"""
        res = self.client.table(TABLE).select("*").eq("id", team_id).single().execute()
        return res.data

    def get_all_teams(self) -> List[Dict[str, Any]]:
        """Get all teams"""
        res = self.client.table(TABLE).select("*").execute()
        return res.data or []

    def find_by_dept_id(self, dept_id: int) -> List[Dict[str, Any]]:
        """Find teams by department ID"""
        res = self.client.table(TABLE).select("*").eq("dept_id", dept_id).execute()
        return res.data or []

    def find_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Find teams by name"""
        res = self.client.table(TABLE).select("*").eq("name", name).execute()
        return res.data or []

    def find_by_name_and_dept(self, name: str, dept_id: int) -> List[Dict[str, Any]]:
        """Find teams by name within a specific department"""
        res = self.client.table(TABLE).select("*").eq("name", name).eq("dept_id", dept_id).execute()
        return res.data or []

    def update_team(self, team_id: int, patch: Dict[str, Any]) -> Dict[str, Any]:
        """Update team by ID"""
        res = self.client.table(TABLE).update(patch).eq("id", team_id).execute()
        if not res.data:
            raise RuntimeError("Update failed — no data returned")
        return res.data[0]

    def delete_team(self, team_id: int) -> bool:
        """Delete team by ID"""
        res = self.client.table(TABLE).delete().eq("id", team_id).execute()
        return len(res.data) > 0

    def get_teams_with_dept_info(self) -> List[Dict[str, Any]]:
        """Get all teams with department information joined"""
        res = self.client.table(TABLE).select("*, dept:dept_id(id, name)").execute()
        return res.data or []

    def get_team_with_dept_info(self, team_id: int) -> Optional[Dict[str, Any]]:
        """Get team by ID with department information joined"""
        res = self.client.table(TABLE).select("*, dept:dept_id(id, name)").eq("id", team_id).single().execute()
        return res.data

    def get_teams_by_dept_with_info(self, dept_id: int) -> List[Dict[str, Any]]:
        """Get teams by department ID with department information joined"""
        res = self.client.table(TABLE).select("*, dept:dept_id(id, name)").eq("dept_id", dept_id).execute()
        return res.data or []