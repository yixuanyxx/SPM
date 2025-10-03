import os
from typing import Optional, Dict, Any, List
from supabase import create_client, Client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_KEY"]

# Table name for notifications
TABLE = "notification"

class SupabaseNotificationRepo:
    def __init__(self):
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    def insert_notification(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a new notification into the database."""
        res = self.client.table(TABLE).insert(data).execute()
        if not res.data:
            raise RuntimeError("Insert failed — no data returned")
        return res.data[0]

    def find_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Find all notifications for a specific user, ordered by created_at descending.
        """
        res = self.client.table(TABLE).select("*").eq("userid", user_id).order("created_at", desc=True).execute()
        return res.data or []

    def get_notification(self, notification_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a single notification by its ID.
        """
        res = self.client.table(TABLE).select("*").eq("id", notification_id).single().execute()
        return res.data

    def update_notification(self, notification_id: int, patch: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a notification with the provided fields.
        """
        res = self.client.table(TABLE).update(patch).eq("id", notification_id).execute()
        if not res.data:
            raise RuntimeError("Update failed — no data returned")
        return res.data[0]

    def mark_as_read(self, notification_id: int) -> Dict[str, Any]:
        """
        Mark a notification as read.
        """
        return self.update_notification(notification_id, {"is_read": True})

    def mark_as_unread(self, notification_id: int) -> Dict[str, Any]:
        """
        Mark a notification as unread.
        """
        return self.update_notification(notification_id, {"is_read": False})

    def get_unread_count(self, user_id: int) -> int:
        """
        Get the count of unread notifications for a user.
        """
        res = self.client.table(TABLE).select("id", count="exact").eq("userid", user_id).eq("is_read", False).execute()
        return res.count or 0

    def find_unread_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Find all unread notifications for a specific user, ordered by created_at descending.
        """
        res = self.client.table(TABLE).select("*").eq("userid", user_id).eq("is_read", False).order("created_at", desc=True).execute()
        return res.data or []

    def delete_notification(self, notification_id: int) -> bool:
        """
        Delete a notification by its ID.
        """
        res = self.client.table(TABLE).delete().eq("id", notification_id).execute()
        return len(res.data) > 0