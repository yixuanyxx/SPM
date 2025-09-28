from flask import Blueprint, request, jsonify
from services.user_service import UserService

user_bp = Blueprint("users", __name__)
service = UserService()

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
        status_code = result.pop("status", 200)
        
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
        status_code = result.pop("status", 200)
        
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
