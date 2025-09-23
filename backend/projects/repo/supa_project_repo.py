import os
from typing import Optional, Dict, Any, List
from supabase import create_client, Client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_KEY"]

# Table name for projects
TABLE = "project"

class SupabaseProjectRepo:
    def __init__(self):
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    def insert_project(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = self.client.table(TABLE).insert(data).execute()
        if not res.data:
            raise RuntimeError("Insert failed — no data returned")
        return res.data[0]

    def find_by_user(self, user_id: int) -> list:
        """
        Find all projects where user is either owner or collaborator.
        """
        # Get projects where user is the owner
        owner_res = self.client.table(TABLE).select("*").eq("owner_id", user_id).execute()
        owner_projects = owner_res.data or []

        # Get projects where user is in collaborators list
        collab_res = self.client.table(TABLE).select("*").filter("collaborators", "cs", [user_id]).execute()
        collab_projects = collab_res.data or []

        # Combine results and remove duplicates using project ID as key
        combined = {p["id"]: p for p in (owner_projects + collab_projects)}
        return list(combined.values())

    def get_project(self, project_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a single project by its ID.
        """
        res = self.client.table(TABLE).select("*").eq("id", project_id).single().execute()
        return res.data

    def update_project(self, project_id: int, patch: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a project with the provided fields.
        """
        res = self.client.table(TABLE).update(patch).eq("id", project_id).execute()
        if not res.data:
            raise RuntimeError("Update failed — no data returned")
        return res.data[0]

    def find_by_owner(self, owner_id: int) -> list:
        """
        Find all projects that are owned by a specific user (by owner_id only).
        """
        res = self.client.table(TABLE).select("*").eq("owner_id", owner_id).execute()
        return res.data or []