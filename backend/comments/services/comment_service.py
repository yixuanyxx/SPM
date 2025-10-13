from typing import Dict, Any, Optional, List
from datetime import datetime, UTC
from models.comment import Comment
from repo.comment_repo import CommentRepo

class CommentService:
    def __init__(self, repo: Optional[CommentRepo] = None):
        self.repo = repo or CommentRepo()

    def create_comment(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new comment.
        Required fields: task_id, user_id, user_name, user_role, content
        """
        # Validate required fields
        required_fields = ['task_id', 'user_id', 'user_name', 'user_role', 'content']
        missing_fields = [field for field in required_fields if not payload.get(field)]
        
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

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
        # Check if comment exists
        existing_comment = self.repo.get_comment(comment_id)
        if not existing_comment:
            return {
                "Code": 404,
                "Message": f"Comment with ID {comment_id} not found"
            }

        # Update the comment
        updated_data = {
            "content": content,
            "updated_at": datetime.now(UTC).isoformat()
        }
        updated_comment = self.repo.update_comment(comment_id, updated_data)
        
        return {
            "Code": 200,
            "Message": f"Comment {comment_id} updated successfully",
            "data": updated_comment
        }

    def delete_comment(self, comment_id: int) -> Dict[str, Any]:
        """Delete a comment by its ID."""
        # Check if comment exists
        existing_comment = self.repo.get_comment(comment_id)
        if not existing_comment:
            return {
                "Code": 404,
                "Message": f"Comment with ID {comment_id} not found"
            }

        # Delete the comment
        success = self.repo.delete_comment(comment_id)
        if success:
            return {
                "Code": 200,
                "Message": f"Comment {comment_id} deleted successfully"
            }
        else:
            return {
                "Code": 500,
                "Message": f"Failed to delete comment {comment_id}"
            }

