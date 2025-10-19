from flask import Blueprint, request, jsonify
from services.dept_service import DeptService
from utils.parsing import parse_dept_payload, parse_dept_update_payload

dept_bp = Blueprint("departments", __name__)
service = DeptService()

@dept_bp.route("/departments", methods=["POST"])
def create_department():
    """
    Endpoint to create a new department.

    Required fields:
    - name: Department name (string)

    RETURNS:
    {
        "Message": "Department created! Department ID: <int>",
        "data": { ... department data ... },
        "Code": 201
    }

    RESPONSES:
        200: Department name already exists
        201: Department successfully created
        400: Missing required fields or validation error
        500: Internal Server Error
    """
    try:
        data = request.form if request.form else (request.get_json(silent=True) or {})
        payload = parse_dept_payload(data)
        result = service.create_dept(payload)
        status = result.pop("__status", 201)
        result["Code"] = status
        return jsonify(result), status
    except ValueError as ve:
        return jsonify({"Message": str(ve), "Code": 400}), 400
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500

@dept_bp.route("/departments", methods=["GET"])
def get_all_departments():
    """
    Endpoint to get all departments.

    RETURNS:
    {
        "Message": "Retrieved <count> department(s)",
        "data": [ ... list of departments ... ],
        "Code": 200
    }

    RESPONSES:
        200: Departments retrieved successfully
        500: Internal Server Error
    """
    try:
        result = service.get_all_depts()
        status = result.pop("__status", 200)
        result["Code"] = status
        return jsonify(result), status
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500

@dept_bp.route("/departments/<int:dept_id>", methods=["GET"])
def get_department_by_id(dept_id: int):
    """
    Endpoint to get a department by its ID.

    Parameters:
    - dept_id: Department ID (integer)

    RETURNS:
    {
        "Message": "Department retrieved successfully",
        "data": { ... department data ... },
        "Code": 200
    }

    RESPONSES:
        200: Department found and returned
        404: Department not found
        500: Internal Server Error
    """
    try:
        result = service.get_dept_by_id(dept_id)
        status = result.pop("__status", 200)
        result["Code"] = status
        return jsonify(result), status
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500

@dept_bp.route("/departments/<int:dept_id>", methods=["PUT", "PATCH"])
def update_department(dept_id: int):
    """
    Endpoint to update a department.

    Parameters:
    - dept_id: Department ID (integer)

    Optional fields:
    - name: Department name (string)

    RETURNS:
    {
        "Message": "Department <dept_id> updated successfully",
        "data": { ... updated department data ... },
        "Code": 200
    }

    RESPONSES:
        200: Department successfully updated
        400: Validation error or duplicate name
        404: Department not found
        500: Internal Server Error
    """
    try:
        data = request.form if request.form else (request.get_json(silent=True) or {})
        payload = parse_dept_update_payload(data)
        
        if not payload:
            return jsonify({"Message": "No fields to update provided", "Code": 400}), 400
        
        result = service.update_dept(dept_id, payload)
        status = result.pop("__status", 200)
        result["Code"] = status
        return jsonify(result), status
    except ValueError as ve:
        return jsonify({"Message": str(ve), "Code": 400}), 400
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500

@dept_bp.route("/departments/<int:dept_id>", methods=["DELETE"])
def delete_department(dept_id: int):
    """
    Endpoint to delete a department.

    Parameters:
    - dept_id: Department ID (integer)

    RETURNS:
    {
        "Message": "Department <dept_id> deleted successfully",
        "Code": 200
    }

    RESPONSES:
        200: Department successfully deleted
        404: Department not found
        500: Internal Server Error
    """
    try:
        result = service.delete_dept(dept_id)
        status = result.pop("__status", 200)
        result["Code"] = status
        return jsonify(result), status
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500

@dept_bp.route("/departments/<int:dept_id>/teams", methods=["GET"])
def get_department_with_teams(dept_id: int):
    """
    Endpoint to get department details along with its teams.
    Note: This endpoint requires integration with the team service.
    Currently returns department info only.

    Parameters:
    - dept_id: Department ID (integer)

    RETURNS:
    {
        "Message": "Department with teams retrieved successfully",
        "data": { ... department data with teams ... },
        "Code": 200
    }

    RESPONSES:
        200: Department found and returned
        404: Department not found
        500: Internal Server Error
    """
    try:
        result = service.get_dept_with_teams(dept_id)
        status = result.pop("__status", 200)
        result["Code"] = status
        return jsonify(result), status
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500
    
@dept_bp.route('/health')
def health_check():
    return jsonify({"status": "ok"}), 200

