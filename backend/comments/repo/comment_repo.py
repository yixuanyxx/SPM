import os
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_KEY"]

TABLE = "comment"

class CommentRepo:
    def __init__(self):
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    def insert_comment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a new comment into the database."""
        res = self.client.table(TABLE).insert(data).execute()
        if not res.data:
            raise RuntimeError("Insert failed – no data returned")
        return res.data[0]

    def find_by_task(self, task_id: int) -> List[Dict[str, Any]]:
        """Find all comments for a specific task, ordered by created_at descending."""
        res = self.client.table(TABLE).select("*").eq("task_id", task_id).order("created_at", desc=True).execute()
        return res.data or []

    def get_comment(self, comment_id: int) -> Optional[Dict[str, Any]]:
        """Get a single comment by its ID."""
        res = self.client.table(TABLE).select("*").eq("id", comment_id).single().execute()
        return res.data

    def update_comment(self, comment_id: int, patch: Dict[str, Any]) -> Dict[str, Any]:
        """Update a comment with the provided fields."""
        res = self.client.table(TABLE).update(patch).eq("id", comment_id).execute()
        if not res.data:
            raise RuntimeError("Update failed – no data returned")
        return res.data[0]

    def delete_comment(self, comment_id: int) -> bool:
        """Delete a comment by its ID."""
        res = self.client.table(TABLE).delete().eq("id", comment_id).execute()
        return len(res.data) > 0
