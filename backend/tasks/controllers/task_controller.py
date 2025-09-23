from flask import Blueprint, request, jsonify
from services.task_service import TaskService
from utils.parsing import parse_task_payload, parse_subtask_payload, parse_task_update_payload

task_bp = Blueprint("tasks", __name__)
service = TaskService()

@task_bp.route("/tasks/manager-task/create", methods=["POST"])
def manager_create_task():
    """
    Endpoint to create a task.

    Required fields:
    - owner_id: ID of the user creating the task
    - task_name: Name of the task  
    - description: Task description
    - type: Task type ("parent" or "subtask") - defaults to "parent"

    Optional fields:
    - due_date: Due date (various formats accepted)
    - status: Task status (Unassigned|Ongoing|Under Review|Completed)
    - project_id: Project ID
    - collaborators: List of user IDs or comma-separated string
    - parent_task: Parent task ID (for subtasks)
    - subtasks: List of subtask IDs

    RETURNS:
    {
        "Message": "Task created! Task ID: <int>",
        "data": { ... task data ... },
        "Code": 201
    }

    RESPONSES:
        200: Task name already exists for this user
        201: Task successfully created
        400: Missing required fields or validation error
        500: Internal Server Error
    """
    try:
        data = request.form if request.form else (request.get_json(silent=True) or {})
        payload = parse_task_payload(data)
        result = service.manager_create(payload)
        status = result.pop("__status", 201)
        result["Code"] = status
        return jsonify(result), status
    except ValueError as ve:
        return jsonify({"Message": str(ve), "Code": 400}), 400
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500

@task_bp.route("/tasks/staff-task/create", methods=["POST"])
def staff_create_task():
    """
    Endpoint to create a task for staff (automatically adds owner as collaborator).

    Required fields:
    - owner_id: ID of the user creating the task
    - task_name: Name of the task  
    - description: Task description

    Optional fields:
    - due_date: Due date (various formats accepted)
    - status: Task status (Unassigned|Ongoing|Under Review|Completed)
    - project_id: Project ID
    - collaborators: List of user IDs or comma-separated string
    - parent_task: Parent task ID (for subtasks)
    - subtasks: List of subtask IDs
    - type: Task type ("parent" or "subtask") - defaults to "parent"

    Note: owner_id is automatically added to the collaborators list

    RETURNS:
    {
        "Message": "Task created! Task ID: <int>",
        "data": { ... task data ... },
        "Code": 201
    }

    RESPONSES:
        200: Task name already exists for this user
        201: Task successfully created
        400: Missing required fields or validation error
        500: Internal Server Error
    """
    try:
        data = request.form if request.form else (request.get_json(silent=True) or {})
        payload = parse_task_payload(data)
        result = service.staff_create(payload)
        status = result.pop("__status", 201)
        result["Code"] = status
        return jsonify(result), status
    except ValueError as ve:
        return jsonify({"Message": str(ve), "Code": 400}), 400
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500

@task_bp.route("/tasks/manager-subtask/create", methods=["POST"])
def manager_create_subtask():
    """
    Endpoint to create a subtask.

    Required fields:
    - owner_id: ID of the user creating the subtask
    - task_name: Name of the subtask
    - description: Subtask description
    - parent_task: Parent task ID (REQUIRED for subtasks)

    Optional fields:
    - due_date: Due date (various formats accepted)
    - status: Task status (Unassigned|Ongoing|Under Review|Completed)
    - project_id: Project ID
    - collaborators: List of user IDs or comma-separated string

    Note: type is automatically set to "subtask"
    Note: The parent task's subtasks list will be automatically updated

    RETURNS:
    {
        "Message": "Subtask created! Task ID: <int>",
        "data": { ... task data ... },
        "Code": 201
    }

    RESPONSES:
        200: Subtask name already exists for this user
        201: Subtask successfully created
        400: Missing required fields or validation error
        500: Internal Server Error
    """
    try:
        data = request.form if request.form else (request.get_json(silent=True) or {})
        
        # Parse using the specialized subtask parser that requires parent_task
        payload = parse_subtask_payload(data)
        
        # Use the specialized subtask creation service
        result = service.manager_create_subtask(payload)
        status = result.pop("__status", 201)
        result["Code"] = status
        
        # Update message to indicate subtask
        if "Message" in result and "Task created!" in result["Message"]:
            result["Message"] = result["Message"].replace("Task created!", "Subtask created!")
        
        return jsonify(result), status
    except ValueError as ve:
        return jsonify({"Message": str(ve), "Code": 400}), 400
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500

@task_bp.route("/tasks/staff-subtask/create", methods=["POST"])
def staff_create_subtask():
    """
    Endpoint to create a subtask for staff (automatically adds owner as collaborator).

    Required fields:
    - owner_id: ID of the user creating the subtask
    - task_name: Name of the subtask
    - description: Subtask description
    - parent_task: Parent task ID (REQUIRED for subtasks)

    Optional fields:
    - due_date: Due date (various formats accepted)
    - status: Task status (Unassigned|Ongoing|Under Review|Completed)
    - project_id: Project ID
    - collaborators: List of user IDs or comma-separated string

    Note: type is automatically set to "subtask"
    Note: owner_id is automatically added to the collaborators list
    Note: The parent task's subtasks list will be automatically updated

    RETURNS:
    {
        "Message": "Subtask created! Task ID: <int>",
        "data": { ... task data ... },
        "Code": 201
    }

    RESPONSES:
        200: Subtask name already exists for this user
        201: Subtask successfully created
        400: Missing required fields or validation error
        500: Internal Server Error
    """
    try:
        data = request.form if request.form else (request.get_json(silent=True) or {})
        
        # Parse using the specialized subtask parser that requires parent_task
        payload = parse_subtask_payload(data)
        
        # Use the specialized staff subtask creation service
        result = service.staff_create_subtask(payload)
        status = result.pop("__status", 201)
        result["Code"] = status
        
        # Update message to indicate subtask
        if "Message" in result and "Task created!" in result["Message"]:
            result["Message"] = result["Message"].replace("Task created!", "Subtask created!")
        
        return jsonify(result), status
    except ValueError as ve:
        return jsonify({"Message": str(ve), "Code": 400}), 400
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500

@task_bp.route("/tasks/update", methods=["PUT", "PATCH"])
def update_task():
    """
    Endpoint to update an existing task.

    Required fields:
    - task_id: ID of the task to update

    Optional fields (any combination):
    - owner_id: ID of the task owner
    - task_name: Name of the task
    - description: Task description
    - due_date: Due date (various formats accepted)
    - status: Task status (Unassigned|Ongoing|Under Review|Completed)
    - project_id: Project ID
    - collaborators: List of user IDs or comma-separated string
    - parent_task: Parent task ID
    - subtasks: List of subtask IDs
    - type: Task type ("parent" or "subtask")

    RETURNS:
    {
        "Message": "Task <task_id> updated successfully",
        "data": { ... updated task data ... },
        "Code": 200
    }

    RESPONSES:
        200: Task successfully updated
        400: Missing task_id, no fields to update, or validation error
        404: Task not found
        500: Internal Server Error
    """
    try:
        data = request.form if request.form else (request.get_json(silent=True) or {})
        payload = parse_task_update_payload(data)
        result = service.update_task_by_id(payload)
        status = result.pop("__status", 200)
        result["Code"] = status
        return jsonify(result), status
    except ValueError as ve:
        return jsonify({"Message": str(ve), "Code": 400}), 400
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500

# get task by task_id
@task_bp.route("/tasks/<int:task_id>", methods=["GET"])
def get_task_by_id(task_id: int):
    try:
        task = service.get_task(task_id)
        if not task:
            return jsonify({"Message": f"Task ID {task_id} not found", "Code": 404}), 404
        return jsonify({"task": task, "Code": 200}), 200
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500
    

# get tasks by user_id (in owner_id or collaborators) with nested subtasks
@task_bp.route("/tasks/user-task/<int:user_id>", methods=["GET"])
def get_tasks_by_user(user_id: int):
    try:
        tasks = service.get_by_user(user_id)
        if not tasks:
            return jsonify({"Message": f"No tasks found for user ID {user_id}", "Code": 404}), 404
        return jsonify({"tasks": tasks, "Code": 200}), 200
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500

@task_bp.route("/tasks/<int:task_id>", methods=["GET"])
def get_task_by_id(task_id: int):
    """
    Get a single task by its ID.
    
    Parameters:
    - task_id: ID of the task to retrieve
    
    RETURNS:
    {
        "data": { ... task data ... },
        "Code": 200
    }
    
    RESPONSES:
        200: Task found and returned
        404: Task not found
        500: Internal Server Error
    """
    try:
        task = service.get_task(task_id)
        if not task:
            return jsonify({"Message": f"Task ID {task_id} not found", "Code": 404}), 404
        return jsonify({"task": task, "Code": 200}), 200
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500

@task_bp.route("/tasks/project/<int:project_id>", methods=["GET"])
def get_tasks_by_project(project_id: int):
    """
    Get all tasks that belong to a specific project.
    
    Parameters:
    - project_id: ID of the project
    
    RETURNS:
    {
        "data": [ ... list of tasks ... ],
        "Code": 200
    }
    
    RESPONSES:
        200: Tasks found and returned
        404: No tasks found for this project
        500: Internal Server Error
    """
    try:
        result = service.get_tasks_by_project(project_id)
        status = result.pop("__status", 200)
        result["Code"] = status
        return jsonify(result), status
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500

@task_bp.route("/tasks/owner/<int:owner_id>", methods=["GET"])
def get_tasks_by_owner(owner_id: int):
    """
    Get all tasks that are owned by a specific user (by owner_id only).
    
    Parameters:
    - owner_id: ID of the user who owns the tasks
    
    RETURNS:
    {
        "data": [ ... list of tasks ... ],
        "Code": 200
    }
    
    RESPONSES:
        200: Tasks found and returned
        404: No tasks found for this owner
        500: Internal Server Error
    """
    try:
        result = service.get_tasks_by_owner(owner_id)
        status = result.pop("__status", 200)
        result["Code"] = status
        return jsonify(result), status
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500


# helper function to be used in assign task to project inside project microservice
@task_bp.route("/tasks/update-project/bulk", methods=["POST"])
def bulk_update_project_id():
    """
    Bulk update the project_id for multiple tasks.
    
    Required fields in JSON body:
    - task_ids: List of task IDs (integers) to update
    - project_id: The project ID (integer) to set for all tasks
    
    RETURNS:
    {
        "Message": "Successfully updated project_id to {project_id} for {count} tasks",
        "data": {
            "total_tasks": int,
            "successful_updates": int,
            "failed_updates": int,
            "updated_tasks": [ ... list of updated task objects ... ],
            "failed_details": [ ... list of failed updates with error details ... ] (only if failures)
        },
        "Code": 200
    }
    
    RESPONSES:
        200: All tasks successfully updated
        207: Partially successful (some tasks updated, some failed)
        400: Invalid input or all tasks failed to update
        500: Internal Server Error
    """
    try:
        data = request.get_json(silent=True) or {}
        
        # Validate required fields
        if "task_ids" not in data:
            return jsonify({"Message": "task_ids is required", "Code": 400}), 400
        
        if "project_id" not in data:
            return jsonify({"Message": "project_id is required", "Code": 400}), 400
        
        task_ids = data["task_ids"]
        project_id = data["project_id"]
        
        # Call service to perform bulk update
        result = service.bulk_update_project_id(task_ids, project_id)
        status = result.pop("__status", 200)
        result["Code"] = status
        
        return jsonify(result), status
        
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500

@task_bp.route("/tasks/<int:parent_task_id>/subtasks", methods=["GET"])
def get_subtasks_by_parent(parent_task_id: int):
    """
    Get all subtask details for a given parent task ID.
    
    Parameters:
    - parent_task_id: ID of the parent task
    
    RETURNS:
    {
        "Message": "Successfully retrieved {count} subtasks for parent task {parent_task_id}",
        "data": {
            "parent_task_id": int,
            "subtasks": [ ... list of subtask objects with full details ... ],
            "subtask_count": int,
            "failed_subtasks": [ ... list of failed subtasks with error details ... ] (only if failures)
        },
        "Code": 200
    }
    
    RESPONSES:
        200: All subtasks successfully retrieved
        207: Partially successful (some subtasks retrieved, some failed)
        404: Parent task not found or no valid subtasks found
        500: Internal Server Error
    """
    try:
        result = service.get_subtasks_by_parent(parent_task_id)
        status = result.pop("__status", 200)
        result["Code"] = status
        
        return jsonify(result), status
        
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500






# get all tasks, or filter by owner_id and/or project_id 
# eg: http://127.0.0.1:5002/tasks?owner_id=101
# eg: http://127.0.0.1:5002/tasks?owner_id=101&project_id=10

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

# get tasks by user_id (in owner_id or collaborators)
