import os
from typing import Optional, Dict, Any
from supabase import create_client, Client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_KEY"]

TABLE = "user"

class SupabaseUserRepo:
    def __init__(self):
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    def get_user_by_userid(self, userid: int) -> Optional[Dict[str, Any]]:
        """
        Get user details by userid.
        """
        res = self.client.table(TABLE).select("*").eq("userid", userid).single().execute()
        return res.data

    def update_user_by_userid(self, userid: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user details by userid.
        """
        res = self.client.table(TABLE).update(update_data).eq("userid", userid).execute()
        if not res.data:
            raise RuntimeError("Update failed — no data returned")
        return res.data[0]

    def get_users_by_dept_id(self, dept_id: int) -> list:
        """
        Get all users by department ID.
        """
        res = self.client.table(TABLE).select("*").eq("dept_id", dept_id).execute()
        return res.data or []

    def get_users_by_team_id(self, team_id: int) -> list:
        """
        Get all users by team ID.
        """
        res = self.client.table(TABLE).select("*").eq("team_id", team_id).execute()
        return res.data or []

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user record.
        """
        res = self.client.table(TABLE).insert(user_data).execute()
        if not res.data:
            raise RuntimeError("Insert failed — no data returned")
        return res.data[0]
    
    def search_users_by_email(self, email_substring: str) -> list:
        """
        Search for users whose email contains the substring (case-insensitive).
        """
        res = (
            self.client
            .table("user")
            .select("*")
            .ilike("email", f"%{email_substring}%")
            .execute()
        )
        return res.data or []