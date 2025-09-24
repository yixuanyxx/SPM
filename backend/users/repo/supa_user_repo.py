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