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
        user_data = self.repo.get_user_by_userid(userid)
        if not user_data:
            return {"status": 404, "message": f"User with userid {userid} not found"}
        
        # Convert dict to User object for validation
        try:
            user = User(**user_data)
            return {"status": 200, "data": user.__dict__}
        except Exception as e:
            return {"status": 500, "message": f"Failed to parse user data: {str(e)}"}

    def update_user_by_userid(self, userid: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user details by userid.
        """
        # Check if user exists
        existing_user_data = self.repo.get_user_by_userid(userid)
        if not existing_user_data:
            return {"status": 404, "message": f"User with userid {userid} not found"}
        
        # Validate update data
        allowed_fields = {"role", "name", "email", "team_id", "dept_id", "notification_preferences"}
        filtered_data = {k: v for k, v in update_data.items() if k in allowed_fields}
        
        if not filtered_data:
            return {"status": 400, "message": "No valid fields to update provided"}
        
        try:
            # Create User object from existing data
            existing_user = User(**existing_user_data)
            
            # Update the User object with new data
            for field, value in filtered_data.items():
                if hasattr(existing_user, field):
                    setattr(existing_user, field, value)
            
            # Update in repository
            updated_user_data = self.repo.update_user_by_userid(userid, filtered_data)
            
            # Return updated User object
            updated_user = User(**updated_user_data)
            return {"status": 200, "message": f"User {userid} updated successfully", "data": updated_user.__dict__}
        except Exception as e:
            return {"status": 500, "message": f"Failed to update user: {str(e)}"}

    def get_users_by_dept_id(self, dept_id: int) -> Dict[str, Any]:
        """
        Get all users by department ID.
        """
        try:
            users_data = self.repo.get_users_by_dept_id(dept_id)
            
            if not users_data:
                return {
                    "status": 200, 
                    "message": f"No users found for department ID {dept_id}",
                    "data": []
                }
            
            # Convert each user dict to User object for validation
            users = []
            for user_data in users_data:
                try:
                    user = User(**user_data)
                    users.append(user.__dict__)
                except Exception as e:
                    # Log the error but continue with other users
                    print(f"Warning: Failed to parse user data: {str(e)}")
                    continue
            
            return {
                "status": 200, 
                "message": f"Retrieved {len(users)} user(s) for department ID {dept_id}",
                "data": users
            }
            
        except Exception as e:
            return {"status": 500, "message": f"Failed to get users by department: {str(e)}"}

    def get_users_by_team_id(self, team_id: int) -> Dict[str, Any]:
        """
        Get all users by team ID.
        """
        try:
            users_data = self.repo.get_users_by_team_id(team_id)
            
            if not users_data:
                return {
                    "status": 200, 
                    "message": f"No users found for team ID {team_id}",
                    "data": []
                }
            
            # Convert each user dict to User object for validation
            users = []
            for user_data in users_data:
                try:
                    user = User(**user_data)
                    users.append(user.__dict__)
                except Exception as e:
                    # Log the error but continue with other users
                    print(f"Warning: Failed to parse user data: {str(e)}")
                    continue
            
            return {
                "status": 200, 
                "message": f"Retrieved {len(users)} user(s) for team ID {team_id}",
                "data": users
            }
            
        except Exception as e:
            return {"status": 500, "message": f"Failed to get users by team: {str(e)}"}

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user.
        """
        # Validate required fields
        required_fields = {"id", "userid", "role", "name", "email"}
        missing_fields = required_fields - set(user_data.keys())
        if missing_fields:
            return {"status": 400, "message": f"Missing required fields: {missing_fields}"}
        
        # Validate allowed fields
        allowed_fields = {"id", "userid", "role", "name", "email", "team_id", "dept_id", "notification_preferences"}
        filtered_data = {k: v for k, v in user_data.items() if k in allowed_fields}
        
        try:
            # Create User object for validation
            user = User(**filtered_data)
            
            # Create in repository
            created_user_data = self.repo.create_user(filtered_data)
            
            # Return created User object
            created_user = User(**created_user_data)
            return {"status": 201, "message": f"User {created_user.userid} created successfully", "data": created_user.__dict__}
        except Exception as e:
            return {"status": 500, "message": f"Failed to create user: {str(e)}"}
        
    def search_users_by_email(self, email_substring: str) -> Dict[str, Any]:
        """
        Search users whose email contains the given substring.
        """
        try:
            users_data = self.repo.search_users_by_email(email_substring)
            if not users_data:
                return {"status": 200, "message": "No users found", "data": []}

            # Convert each to User object
            users = []
            for user_data in users_data:
                try:
                    user = User(**user_data)
                    users.append(user.__dict__)
                except Exception as e:
                    print(f"Warning: Failed to parse user data: {str(e)}")
                    continue

            return {
                "status": 200,
                "message": f"Found {len(users)} user(s)",
                "data": users
            }
        except Exception as e:
            return {"status": 500, "message": f"Failed to search users: {str(e)}"}

    def update_notification_preferences(self, userid: int, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user notification preferences.
        """
        # Validate preferences structure
        valid_keys = {"in_app", "email"}
        if not all(key in valid_keys for key in preferences.keys()):
            return {"status": 400, "message": f"Invalid preference keys. Valid keys are: {valid_keys}"}
        
        # Ensure boolean values
        for key, value in preferences.items():
            if not isinstance(value, bool):
                return {"status": 400, "message": f"Preference '{key}' must be a boolean value"}
        
        # Update using the existing update method
        return self.update_user_by_userid(userid, {"notification_preferences": preferences})

    def search_users(self, search_query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search users for mention suggestions.
        Searches by username (extracted from email) and email.
        """
        try:
            # Search users by email substring
            users_data = self.repo.search_users_by_email(search_query)
            
            # Filter and limit results
            filtered_users = []
            for user_data in users_data:
                if len(filtered_users) >= limit:
                    break
                    
                # Extract username from email for additional matching
                email = user_data.get('email', '')
                if email:
                    username = email.split('@')[0] if '@' in email else email
                    
                    # Check if search query matches username or email
                    if (search_query.lower() in email.lower() or 
                        search_query.lower() in username.lower()):
                        
                        # Convert to User object for validation
                        try:
                            user = User(**user_data)
                            # Add username field for frontend convenience
                            user_dict = user.__dict__
                            user_dict['username'] = username
                            filtered_users.append(user_dict)
                        except Exception as e:
                            print(f"Warning: Failed to parse user data: {str(e)}")
                            continue

            return {
                "status": 200,
                "message": f"Found {len(filtered_users)} user(s) matching '{search_query}'",
                "data": filtered_users
            }
            
        except Exception as e:
            return {"status": 500, "message": f"Failed to search users: {str(e)}"}

