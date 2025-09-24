from typing import Dict, Any, Optional
from models.user import User
from repo.supa_user_repo import SupabaseUserRepo

class UserService:
    def __init__(self, repo: Optional[SupabaseUserRepo] = None):
        self.repo = repo or SupabaseUserRepo()

    def get_user_by_userid(self, userid: int) -> Dict[str, Any]:
        """
        Get user details by userid.
        """
        user = self.repo.get_user_by_userid(userid)
        if not user:
            return {"status": 404, "message": f"User with userid {userid} not found"}
        return {"status": 200, "data": user}


    def update_user_by_userid(self, userid: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user details by userid.
        """
        # Check if user exists
        existing_user = self.repo.get_user_by_userid(userid)
        if not existing_user:
            return {"status": 404, "message": f"User with userid {userid} not found"}
        
        # Validate update data
        allowed_fields = {"role", "name", "email", "team_id", "dept_id"}
        filtered_data = {k: v for k, v in update_data.items() if k in allowed_fields}
        
        if not filtered_data:
            return {"status": 400, "message": "No valid fields to update provided"}
        
        try:
            updated_user = self.repo.update_user_by_userid(userid, filtered_data)
            return {"status": 200, "message": f"User {userid} updated successfully", "data": updated_user}
        except Exception as e:
            return {"status": 500, "message": f"Failed to update user: {str(e)}"}
