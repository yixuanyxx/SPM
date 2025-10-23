from flask import Blueprint, request, jsonify
from services.user_service import UserService

user_bp = Blueprint("users", __name__)
service = UserService()

@user_bp.route("/users", methods=["POST"])
def create_user():
    """
    Create a new user.
    
    Required fields in JSON body:
    - id: Supabase Auth user ID (UUID)
    - userid: Unique integer user ID
    - role: User role
    - name: User name
    - email: User email
    
    Optional fields:
    - team_id: Team ID
    - dept_id: Department ID
    
    Returns:
    {
        "message": "User {userid} created successfully",
        "data": { ... created user data ... },
        "status": 201
    }
    
    Responses:
        201: User successfully created
        400: Missing required fields or invalid data
        500: Internal Server Error
    """
    try:
        # Get JSON data from request
        data = request.get_json(silent=True) or {}
        
        # Call service to create user
        result = service.create_user(data)
        status_code = result.pop("status", 201)
        
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500

@user_bp.route("/users/<int:userid>", methods=["GET"])
def get_user_by_userid(userid: int):
    """
    Get user details by userid.
    
    Parameters:
    - userid: The userid (integer) of the user to retrieve
    
    Returns:
    {
        "data": { ... user data ... },
        "status": 200
    }
    
    Responses:
        200: User found and returned
        404: User not found
        500: Internal Server Error
    """
    try:
        result = service.get_user_by_userid(userid)
        status_code = result.get("status", 200)
        
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500


@user_bp.route("/users/<int:userid>", methods=["PUT", "PATCH"])
def update_user_by_userid(userid: int):
    """
    Update user details by userid.
    
    Required fields:
    - userid: The userid (integer) of the user to update
    
    Optional fields in JSON body:
    - role: User role
    - name: User name
    - email: User email
    - team_id: Team ID
    - dept_id: Department ID
    
    Returns:
    {
        "message": "User {userid} updated successfully",
        "data": { ... updated user data ... },
        "status": 200
    }
    
    Responses:
        200: User successfully updated
        400: No valid fields to update provided
        404: User not found
        500: Internal Server Error
    """
    try:
        # Get JSON data from request
        data = request.get_json(silent=True) or {}
        
        # Call service to update user
        result = service.update_user_by_userid(userid, data)
        status_code = result.get("status", 200)
        
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500


@user_bp.route("/users/department/<int:dept_id>", methods=["GET"])
def get_users_by_dept_id(dept_id: int):
    """
    Get all users by department ID.
    
    Parameters:
    - dept_id: The department ID (integer) to get users for
    
    Returns:
    {
        "message": "Retrieved {count} user(s) for department ID {dept_id}",
        "data": [ ... list of users ... ],
        "status": 200
    }
    
    Responses:
        200: Users found and returned (or empty list if no users)
        500: Internal Server Error
    """
    try:
        result = service.get_users_by_dept_id(dept_id)
        status_code = result.pop("status", 200)
        
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500


@user_bp.route("/users/team/<int:team_id>", methods=["GET"])
def get_users_by_team_id(team_id: int):
    """
    Get all users by team ID.
    
    Parameters:
    - team_id: The team ID (integer) to get users for
    
    Returns:
    {
        "message": "Retrieved {count} user(s) for team ID {team_id}",
        "data": [ ... list of users ... ],
        "status": 200
    }
    
    Responses:
        200: Users found and returned (or empty list if no users)
        500: Internal Server Error
    """
    try:
        result = service.get_users_by_team_id(team_id)
        status_code = result.pop("status", 200)
        
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500

@user_bp.route("/users/search", methods=["GET"])
def search_users_by_email():
    """
    Search users by email substring.

    Query Parameters:
        email (str): substring to search for

    Returns:
        {
            "message": "Found X users",
            "data": [ ... list of matching users ... ],
            "status": 200
        }
    """
    try:
        email_query = request.args.get("email", "").strip()
        if not email_query:
            return jsonify({"message": "No search query provided", "data": [], "status": 400}), 400

        result = service.search_users_by_email(email_query)
        status_code = result.get("status", 200)
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500

@user_bp.route("/users/<int:userid>/notification-preferences", methods=["PUT", "PATCH"])
def update_notification_preferences(userid: int):
    """
    Update user notification preferences.
    
    Parameters:
    - userid: The user ID (integer) to update preferences for
    
    Required fields in JSON body:
    - in_app: Boolean for in-app notifications
    - email: Boolean for email notifications
    
    Returns:
    {
        "message": "User {userid} updated successfully",
        "data": { ... updated user data ... },
        "status": 200
    }
    
    Responses:
        200: Preferences successfully updated
        400: Invalid preference data
        404: User not found
        500: Internal Server Error
    """
    try:
        # Get JSON data from request
        data = request.get_json(silent=True) or {}
        
        # Call service to update notification preferences
        result = service.update_notification_preferences(userid, data)
        status_code = result.get("status", 200)
        
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500
    
@user_bp.route("/health")
def health_check():
    return jsonify({"status": "ok"}), 200
