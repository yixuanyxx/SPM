from flask import Blueprint, request, jsonify
from services.project_service import ProjectService
from utils.parsing import parse_project_update_payload

project_bp = Blueprint("projects", __name__)
service = ProjectService()

@project_bp.route("/projects/create", methods=["POST"])
def create_project():
    """
    Create a new project.
    
    Required fields:
    - owner_id: ID of the user creating the project
    - proj_name: Name of the project
    
    Optional fields:
    - collaborators: List of user IDs
    - tasks: List of task IDs
    
    Returns:
    {
        "message": "Project created! Project ID: <id>",
        "data": { ... project data ... },
        "status": 201
    }
    """
    try:
        # Get JSON data from request
        data = request.get_json(silent=True) or {}
        
        # Call service to create project
        result = service.create(data)
        status_code = result.pop("status", 201)
        
        return jsonify(result), status_code
        
    except ValueError as ve:
        return jsonify({"error": str(ve), "status": 400}), 400
    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500

@project_bp.route("/projects/user/<int:user_id>", methods=["GET"])
def get_projects_by_user(user_id: int):
    """
    Get all projects where user is either owner or collaborator.
    
    Parameters:
    - user_id: ID of the user (owner_id OR in collaborators list)
    
    Returns:
    {
        "data": [ ... list of projects ... ],
        "status": 200
    }
    
    Responses:
        200: Projects found and returned
        404: No projects found for this user
        500: Internal Server Error
    """
    try:
        result = service.get_projects_by_user(user_id)
        status_code = result.pop("status", 200)
        
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500

@project_bp.route("/projects/<int:project_id>", methods=["GET"])
def get_project_by_id(project_id: int):
    """
    Get a single project by its ID.
    
    Parameters:
    - project_id: ID of the project to retrieve
    
    Returns:
    {
        "data": { ... project data ... },
        "status": 200
    }
    
    Responses:
        200: Project found and returned
        404: Project not found
        500: Internal Server Error
    """
    try:
        result = service.get_project_by_id(project_id)
        status_code = result.pop("status", 200)
        
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500

@project_bp.route("/projects/update", methods=["PUT", "PATCH"])
def update_project():
    """
    Update an existing project.
    
    Required fields:
    - project_id: ID of the project to update
    
    Optional fields:
    - owner_id: ID of the project owner
    - proj_name: Name of the project
    - collaborators: List of user IDs
    - tasks: List of task IDs
    
    Returns:
    {
        "message": "Project <project_id> updated successfully",
        "data": { ... updated project data ... },
        "status": 200
    }
    
    Responses:
        200: Project successfully updated
        400: Missing project_id, no fields to update, or validation error
        404: Project not found
        500: Internal Server Error
    """
    try:
        # Get JSON data from request
        data = request.get_json(silent=True) or {}
        
        # Parse the update payload
        payload = parse_project_update_payload(data)
        
        # Call service to update project
        result = service.update_project_by_id(payload)
        status_code = result.pop("status", 200)
        
        return jsonify(result), status_code
        
    except ValueError as ve:
        return jsonify({"error": str(ve), "status": 400}), 400
    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500
