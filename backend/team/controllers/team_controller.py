from flask import Blueprint, request, jsonify
from services.team_service import TeamService
from utils.parsing import parse_team_payload, parse_team_update_payload

team_bp = Blueprint("teams", __name__)
service = TeamService()

@team_bp.route("/teams", methods=["POST"])
def create_team():
    """
    Endpoint to create a new team.

    Required fields:
    - name: Team name (string)
    - dept_id: Department ID (integer)

    RETURNS:
    {
        "Message": "Team created! Team ID: <int>",
        "data": { ... team data ... },
        "Code": 201
    }

    RESPONSES:
        200: Team name already exists in this department
        201: Team successfully created
        400: Missing required fields or validation error
        500: Internal Server Error
    """
    try:
        data = request.form if request.form else (request.get_json(silent=True) or {})
        payload = parse_team_payload(data)
        result = service.create_team(payload)
        status = result.pop("__status", 201)
        result["Code"] = status
        return jsonify(result), status
    except ValueError as ve:
        return jsonify({"Message": str(ve), "Code": 400}), 400
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500

@team_bp.route("/teams", methods=["GET"])
def get_all_teams():
    """
    Endpoint to get all teams.

    Optional query parameters:
    - include_dept_info: Include department information (true/false)

    RETURNS:
    {
        "Message": "Retrieved <count> team(s)",
        "data": [ ... list of teams ... ],
        "Code": 200
    }

    RESPONSES:
        200: Teams retrieved successfully
        500: Internal Server Error
    """
    try:
        include_dept_info = request.args.get("include_dept_info", "false").lower() == "true"
        result = service.get_all_teams(include_dept_info=include_dept_info)
        status = result.pop("__status", 200)
        result["Code"] = status
        return jsonify(result), status
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500

@team_bp.route("/teams/<int:team_id>", methods=["GET"])
def get_team_by_id(team_id: int):
    """
    Endpoint to get a team by its ID.

    Parameters:
    - team_id: Team ID (integer)

    Optional query parameters:
    - include_dept_info: Include department information (true/false)

    RETURNS:
    {
        "Message": "Team retrieved successfully",
        "data": { ... team data ... },
        "Code": 200
    }

    RESPONSES:
        200: Team found and returned
        404: Team not found
        500: Internal Server Error
    """
    try:
        include_dept_info = request.args.get("include_dept_info", "false").lower() == "true"
        result = service.get_team_by_id(team_id, include_dept_info=include_dept_info)
        status = result.pop("__status", 200)
        result["Code"] = status
        return jsonify(result), status
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500

@team_bp.route("/teams/department/<int:dept_id>", methods=["GET"])
def get_teams_by_dept_id(dept_id: int):
    """
    Endpoint to get all teams by department ID.

    Parameters:
    - dept_id: Department ID (integer)

    Optional query parameters:
    - include_dept_info: Include department information (true/false)

    RETURNS:
    {
        "Message": "Retrieved <count> team(s) for department <dept_id>",
        "data": [ ... list of teams ... ],
        "Code": 200
    }

    RESPONSES:
        200: Teams retrieved successfully
        500: Internal Server Error
    """
    try:
        include_dept_info = request.args.get("include_dept_info", "false").lower() == "true"
        result = service.get_teams_by_dept_id(dept_id, include_dept_info=include_dept_info)
        status = result.pop("__status", 200)
        result["Code"] = status
        return jsonify(result), status
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500

@team_bp.route("/teams/<int:team_id>", methods=["PUT", "PATCH"])
def update_team(team_id: int):
    """
    Endpoint to update a team.

    Parameters:
    - team_id: Team ID (integer)

    Optional fields:
    - name: Team name (string)
    - dept_id: Department ID (integer)

    RETURNS:
    {
        "Message": "Team <team_id> updated successfully",
        "data": { ... updated team data ... },
        "Code": 200
    }

    RESPONSES:
        200: Team successfully updated
        400: Validation error or duplicate name in department
        404: Team not found
        500: Internal Server Error
    """
    try:
        data = request.form if request.form else (request.get_json(silent=True) or {})
        payload = parse_team_update_payload(data)
        
        if not payload:
            return jsonify({"Message": "No fields to update provided", "Code": 400}), 400
        
        result = service.update_team(team_id, payload)
        status = result.pop("__status", 200)
        result["Code"] = status
        return jsonify(result), status
    except ValueError as ve:
        return jsonify({"Message": str(ve), "Code": 400}), 400
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500

@team_bp.route("/teams/<int:team_id>", methods=["DELETE"])
def delete_team(team_id: int):
    """
    Endpoint to delete a team.

    Parameters:
    - team_id: Team ID (integer)

    RETURNS:
    {
        "Message": "Team <team_id> deleted successfully",
        "Code": 200
    }

    RESPONSES:
        200: Team successfully deleted
        404: Team not found
        500: Internal Server Error
    """
    try:
        result = service.delete_team(team_id)
        status = result.pop("__status", 200)
        result["Code"] = status
        return jsonify(result), status
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500
    
@team_bp.route("/health")
def health_check():
    return jsonify({"status": "ok"}), 200