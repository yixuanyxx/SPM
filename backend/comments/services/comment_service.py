from typing import Dict, Any, Optional, List
from datetime import datetime, UTC
import re
import requests
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
        Returns email, role, and name for the user.
        """
        try:
            user = self.repo.client.table("user").select("email, role, name").eq("userid", user_id).single().execute()
            return user.data if user.data else None
        except Exception as e:
            print(f"Error fetching user data for user_id {user_id}: {e}")
            return None

    def _extract_mentions(self, content: str) -> List[str]:
        """
        Extract @username mentions from comment content.
        Returns a list of usernames (without @ symbol).
        """
        # Pattern to match @username mentions
        mention_pattern = r'@(\w+)'
        mentions = re.findall(mention_pattern, content)
        return list(set(mentions))  # Remove duplicates

    def _get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user by username (extracted from email).
        """
        try:
            # Search for user by email pattern (username@domain)
            users = self.repo.client.table("user").select("userid, email, name, role").execute()
            for user in users.data:
                if user.get('email'):
                    email_username = self._extract_username_from_email(user['email'])
                    if email_username.lower() == username.lower():
                        return user
            return None
        except Exception as e:
            print(f"Error fetching user by username {username}: {e}")
            return None

    def _get_task_collaborators(self, task_id: int) -> List[int]:
        """
        Get all collaborators for a task (owner + collaborators list).
        """
        try:
            # Get task details from tasks service
            response = requests.get(f"http://127.0.0.1:5002/tasks/{task_id}")
            if response.status_code == 200:
                task_data = response.json()
                collaborators = []
                
                # Add owner
                if task_data.get('task', {}).get('owner_id'):
                    collaborators.append(task_data['task']['owner_id'])
                
                # Add collaborators
                task_collaborators = task_data.get('task', {}).get('collaborators', [])
                if task_collaborators:
                    collaborators.extend(task_collaborators)
                
                return list(set(collaborators))  # Remove duplicates
            return []
        except Exception as e:
            print(f"Error fetching task collaborators for task {task_id}: {e}")
            return []

    def _send_mention_notifications(self, mentions: List[str], commenter_name: str, task_id: int, task_title: str, comment_content: str, commenter_id: int):
        """
        Send notifications to mentioned users using structured format.
        """
        # Fetch the commenter's actual name from the database
        commenter_user_data = self._get_user_data(commenter_id)
        actual_commenter_name = commenter_name
        if commenter_user_data and commenter_user_data.get('name'):
            actual_commenter_name = commenter_user_data['name']
        
        for username in mentions:
            user = self._get_user_by_username(username)
            if user:
                try:
                    response = requests.post("http://127.0.0.1:5006/notifications/triggers/comment-mention-structured", 
                                           json={
                                               "task_id": task_id,
                                               "mentioned_user_id": user['userid'],
                                               "commenter_name": actual_commenter_name,
                                               "comment_content": comment_content,
                                               "task_name": task_title
                                           })
                    if response.status_code not in [200, 201]:
                        print(f"Warning: Failed to send mention notification to user {user['userid']}: {response.status_code}")
                except Exception as e:
                    print(f"Error sending mention notification: {e}")

    def _send_collaborator_notifications(self, collaborator_ids: List[int], commenter_name: str, task_id: int, task_title: str, comment_content: str, commenter_id: int):
        """
        Send notifications to task collaborators (excluding the commenter) using structured format.
        """
        # Fetch the commenter's actual name from the database
        commenter_user_data = self._get_user_data(commenter_id)
        actual_commenter_name = commenter_name
        if commenter_user_data and commenter_user_data.get('name'):
            actual_commenter_name = commenter_user_data['name']
        
        # Exclude the commenter from notifications
        collaborators_to_notify = [cid for cid in collaborator_ids if cid != commenter_id]
        
        for user_id in collaborators_to_notify:
            try:
                response = requests.post("http://127.0.0.1:5006/notifications/triggers/comment-collaborator-structured", 
                                       json={
                                           "task_id": task_id,
                                           "collaborator_user_id": user_id,
                                           "commenter_name": actual_commenter_name,
                                           "comment_content": comment_content,
                                           "task_name": task_title
                                       })
                if response.status_code not in [200, 201]:
                    print(f"Warning: Failed to send collaborator notification to user {user_id}: {response.status_code}")
            except Exception as e:
                print(f"Error sending collaborator notification: {e}")

    def _trigger_comment_notifications(self, task_id: int, commenter_id: int, commenter_name: str, comment_content: str):
        """
        Main method to trigger all comment notifications based on the user story requirements.
        """
        try:
            # Get task title
            task_title = "Unknown Task"
            try:
                response = requests.get(f"http://127.0.0.1:5002/tasks/{task_id}")
                if response.status_code == 200:
                    task_data = response.json()
                    task_title = task_data.get('task', {}).get('task_name', 'Unknown Task')
            except Exception as e:
                print(f"Warning: Could not fetch task title: {e}")

            # Extract mentions from comment content
            mentions = self._extract_mentions(comment_content)
            
            # Get task collaborators
            collaborators = self._get_task_collaborators(task_id)
            
            # If there are mentions, send mention notifications only
            if mentions:
                self._send_mention_notifications(mentions, commenter_name, task_id, task_title, comment_content, commenter_id)
            else:
                # No mentions, send collaborator notifications to all collaborators
                self._send_collaborator_notifications(collaborators, commenter_name, task_id, task_title, comment_content, commenter_id)
                
        except Exception as e:
            print(f"Error in _trigger_comment_notifications: {e}")

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
            if user_data and user_data.get('name'):
                payload['user_name'] = user_data['name']
            elif user_data and user_data.get('email'):
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
        
        # Trigger notifications after successful comment creation
        try:
            self._trigger_comment_notifications(
                task_id=payload['task_id'],
                commenter_id=payload['user_id'],
                commenter_name=payload['user_name'],
                comment_content=payload['content']
            )
        except Exception as e:
            print(f"Warning: Failed to trigger comment notifications: {e}")
        
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