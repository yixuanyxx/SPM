import os
from flask import Flask, jsonify, request
from datetime import datetime
from dateutil import parser # pip install python-dateutil
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app, origins=os.getenv("CORS_ORIGINS", "*").split(","), supports_credentials=True)

# Supabase client (server-side)
from supabase import create_client, Client
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

error_list = [400, 404, 500]

@app.route("/create_task", methods=['POST'])
def create_task(): 
    """
    Endpoint to create a task.

    FORM DATA:
    owner_id: ID of the user creating the task
    task_name: Name of the task
    due_date: Due date as 'Wed Sep 16 2025'
    description: Task description
    collaborators: Comma-separated user_ids (optional)
    status: Unassigned, Ongoing, Under Review, Completed
    project_id: project ID (optional)
    assigned_by : user_id of manager (optional)

    RETURNS:
    {
        "Message": "Task created! Task ID: <int8>",
        "Code": 201
    }

    RESPONSES:
        200: Task name already exists
        201: Task successfully created
        400: Missing required fields
        500: Internal Server Error
    """
    required_fields = {'task_name', 'due_date', 'description', 'status', 'owner_id'}
    if not request.form or not all(field in request.form for field in required_fields):
        return jsonify({
            "error": f"Missing required fields. Required fields: {required_fields}",
            "Code": 400
        }), 400
    
    try:
        # -----------------------
        # Parse form data
        # -----------------------
        task_name = request.form["task_name"]
        due_date_str = request.form["due_date"]
        due_date = parser.parse(due_date_str)
        description = request.form["description"]
        status = request.form["status"]
        project_id = request.form.get("project_id", None)
        owner_id = request.form["owner_id"]

        # -----------------------
        # Parse collaborators as user IDs (comma-separated)
        # -----------------------
        collaborators_raw = request.form.get("collaborators", "")
        collaborators = [int(c.strip()) for c in collaborators_raw.split(",") if c.strip()]

        existing_task = supabase.table("task")\
            .select("*")\
            .eq("owner_id", owner_id)\
            .eq("task_name", task_name)\
            .execute()
        
        if existing_task.data:
            return jsonify({
                "Message": f"Task with name '{task_name}' already exists for this user.",
                "Code": 200
            }), 200
        
        task_data = {
            "owner_id": int(owner_id),
            "task_name": task_name,
            "due_date": due_date.isoformat(),
            "description": description,
            "collaborators": collaborators,
            "status": status,
            "project_id": int(project_id) if project_id else None,
            "created_at": datetime.utcnow().isoformat() 
        }

        insert_result = supabase.table("task").insert(task_data).execute()
        if insert_result.error:
            return jsonify({"Message": str(insert_result.error), "Code": 500}), 500
        task_id = insert_result.data[0]["id"]

        return jsonify({
            "Message": f"Task created! Task ID: {task_id}",
            "Code": 201
        }), 201

    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500
    
if __name__ == "__main__":
    app.run(debug=True)
        