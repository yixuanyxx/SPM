from flask import Blueprint, request, jsonify
from services.task_service import TaskService
from utils.parsing import parse_task_payload

task_bp = Blueprint("tasks", __name__)
service = TaskService()

@task_bp.route("/tasks/create", methods=["POST"])
def create_task():
    """
    Endpoint to create a task.

    FORM DATA:
    {
        "task_name": "Prepare Sprint Report",
        "due_date": "2025-09-25T17:00:00Z", (ISO8601 format but in string)
        "description": "Compile sprint metrics and retrospective notes",
        "status": "Unassigned",
        "owner_id": 101,
        "project_id": 10, (optional)
        "collaborators": [102, 103, 104] (optional)
    }

    RETURNS:
    {
        "Message": "Task created! Task ID: <int8>",
        "data": {
        "assigned_by": null,
        "collaborators": [
            102,
            103,
            104
        ],
        "created_at": "2025-09-18T15:48:32.245055+00:00",
        "description": "Compile sprint metrics and retrospective notes",
        "due_date": "2025-09-25T17:00:00+00:00",
        "id": 5,
        "owner_id": 101,
        "project_id": null,
        "status": "Unassigned",
        "sub_task": null,
        "task_name": "Prepare Sprint Report"
        }
    }

    RESPONSES:
        200: Task name already exists
        201: Task successfully created
        400: Missing required fields
        500: Internal Server Error
    """
    try:
        data = request.form if request.form else (request.get_json(silent=True) or {})
        payload = parse_task_payload(data)
        result = service.create(payload)
        status = result.pop("__status", 201)
        result["Code"] = status
        return jsonify(result), status
    except ValueError as ve:
        return jsonify({"Message": str(ve), "Code": 400}), 400
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500

# get all tasks, or filter by owner_id and/or project_id 
# eg: http://127.0.0.1:5002/tasks?owner_id=101
# eg: http://127.0.0.1:5002/tasks?owner_id=101&project_id=10
@task_bp.route("/tasks", methods=["GET"])
def list_tasks():
    owner_id = request.args.get("owner_id", type=int)
    project_id = request.args.get("project_id", type=int)
    try:
        rows = service.list(owner_id=owner_id, project_id=project_id)
        return jsonify({
            "Message": "Tasks retrieved successfully",
            "Code": 200,
            "data": rows
        }), 200
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500

# @task_bp.route("/tasks/<int:task_id>/status", methods=["PUT"])
# def set_status(task_id: int):
#     """
#     JSON body: { "status": "Ongoing" | "Under Review" | "Completed" | "Unassigned" }
#     """
#     try:
#         body = request.get_json(force=True)
#         new_status = body.get("status")
#         if not new_status:
#             return jsonify({"Message": "status is required", "Code": 400}), 400
#         updated = service.update_status(task_id, new_status)
#         return jsonify(updated), 200
#     except Exception as e:
#         return jsonify({"Message": str(e), "Code": 500}), 500
