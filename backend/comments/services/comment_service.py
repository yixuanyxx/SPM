from typing import Dict, Any, Optional, List
from datetime import datetime, UTC
from models.comment import Comment
from repo.comment_repo import CommentRepo

class CommentService:
    def __init__(self, repo: Optional[CommentRepo] = None):
        self.repo = repo or CommentRepo()

    def _extract_username_from_email(self, email: str) -> str:
        """Extract username from email (part before @)"""
        if not email:
            return "Unknown"
        
        at_index = email.find('@')
        if at_index > 0:
            return email[:at_index]
        return email

    def _get_user_data(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch user data from the user table.
        Returns email and role for the user.
        """
        try:
            user = self.repo.client.table("user").select("email, role").eq("userid", user_id).single().execute()
            return user.data if user.data else None
        except Exception as e:
            print(f"Error fetching user data for user_id {user_id}: {e}")
            return None

    def create_comment(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new comment.
        Required fields: task_id, user_id, content
        Optional fields: user_name (will be extracted from email if not provided), user_role
        """
        # Validate required fields
        required_fields = ['task_id', 'user_id', 'content']
        missing_fields = [field for field in required_fields if not payload.get(field)]
        
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        # If user_name is not provided, fetch from user table
        if not payload.get('user_name'):
            user_data = self._get_user_data(payload['user_id'])
            if user_data and user_data.get('email'):
                payload['user_name'] = self._extract_username_from_email(user_data['email'])
            else:
                payload['user_name'] = "Unknown"
        
        # If user_role is not provided, fetch from user table
        if not payload.get('user_role'):
            user_data = self._get_user_data(payload['user_id'])
            payload['user_role'] = user_data.get('role', 'user').lower() if user_data else 'user'

        # Create comment from payload
        comment = Comment.from_dict(payload)
        
        # Convert to dictionary for database insertion
        data = comment.to_dict()
        data.pop("id", None)

        # Insert into database
        created = self.repo.insert_comment(data)
        return {
            "Code": 201,
            "Message": f"Comment created! Comment ID: {created.get('id')}",
            "data": created
        }

    def get_comments_by_task(self, task_id: int) -> Dict[str, Any]:
        """Get all comments for a specific task."""
        comments = self.repo.find_by_task(task_id)
        if not comments:
            return {
                "Code": 404,
                "Message": f"No comments found for task ID {task_id}",
                "data": []
            }
        return {
            "Code": 200,
            "Message": "Success",
            "data": comments
        }

    def get_comment_by_id(self, comment_id: int) -> Dict[str, Any]:
        """Get a single comment by its ID."""
        comment = self.repo.get_comment(comment_id)
        if not comment:
            return {
                "Code": 404,
                "Message": f"Comment with ID {comment_id} not found"
            }
        return {
            "Code": 200,
            "Message": "Success",
            "data": comment
        }

    def update_comment(self, comment_id: int, content: str) -> Dict[str, Any]:
        """Update a comment's content."""
        # Update the comment
        updated_data = {
            "content": content,
            "updated_at": datetime.now(UTC).isoformat()
        }
        updated_comment = self.repo.update_comment(comment_id, updated_data)
        
        if not updated_comment:
            return {
                "Code": 404,
                "Message": f"Comment with ID {comment_id} not found"
            }
        
        return {
            "Code": 200,
            "Message": f"Comment {comment_id} updated successfully",
            "data": updated_comment
        }

    def delete_comment(self, comment_id: int) -> Dict[str, Any]:
        """Delete a comment by its ID."""
        # Delete the comment
        success = self.repo.delete_comment(comment_id)
        if success:
            return {
                "Code": 200,
                "Message": f"Comment {comment_id} deleted successfully"
            }
        else:
            return {
                "Code": 404,
                "Message": f"Comment with ID {comment_id} not found"
            }