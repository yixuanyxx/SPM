from flask import Blueprint, request, jsonify
from services.comment_service import CommentService

comment_bp = Blueprint("comments", __name__, url_prefix="/comments")
service = CommentService()

@comment_bp.route("/create", methods=["POST"])
def create_comment():
    """
    Create a new comment.
    
    Required fields in JSON body:
    - task_id: ID of the task
    - user_id: ID of the user posting comment
    - user_name: Name of the user
    - user_role: Role of the user
    - content: Comment content
    
    Returns:
    {
        "Code": 201,
        "Message": "Comment created! Comment ID: <id>",
        "data": { ... comment data ... }
    }
    """
    try:
        data = request.get_json(silent=True) or {}
        result = service.create_comment(data)
        status_code = result.pop("Code", 201)
        return jsonify(result), status_code
        
    except ValueError as ve:
        return jsonify({"Code": 400, "Message": str(ve)}), 400
    except Exception as e:
        return jsonify({"Code": 500, "Message": str(e)}), 500

@comment_bp.route("/task/<int:task_id>", methods=["GET"])
def get_task_comments(task_id: int):
    """
    Get all comments for a specific task.
    
    Parameters:
    - task_id: ID of the task
    
    Returns:
    {
        "Code": 200,
        "Message": "Success",
        "data": [ ... list of comments ... ]
    }
    """
    try:
        result = service.get_comments_by_task(task_id)
        status_code = result.pop("Code", 200)
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({"Code": 500, "Message": str(e)}), 500

@comment_bp.route("/<int:comment_id>", methods=["GET"])
def get_comment(comment_id: int):
    """
    Get a single comment by its ID.
    
    Parameters:
    - comment_id: ID of the comment to retrieve
    
    Returns:
    {
        "Code": 200,
        "Message": "Success",
        "data": { ... comment data ... }
    }
    """
    try:
        result = service.get_comment_by_id(comment_id)
        status_code = result.pop("Code", 200)
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({"Code": 500, "Message": str(e)}), 500

@comment_bp.route("/<int:comment_id>", methods=["PUT"])
def update_comment(comment_id: int):
    """
    Update a comment's content.
    
    Parameters:
    - comment_id: ID of the comment to update
    
    Required fields in JSON body:
    - content: New comment content
    
    Returns:
    {
        "Code": 200,
        "Message": "Comment <comment_id> updated successfully",
        "data": { ... updated comment data ... }
    }
    """
    try:
        data = request.get_json(silent=True) or {}
        content = data.get("content")
        
        if not content:
            return jsonify({"Code": 400, "Message": "Content is required"}), 400
        
        result = service.update_comment(comment_id, content)
        status_code = result.pop("Code", 200)
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({"Code": 500, "Message": str(e)}), 500

@comment_bp.route("/<int:comment_id>", methods=["DELETE"])
def delete_comment(comment_id: int):
    """
    Delete a comment by its ID.
    
    Parameters:
    - comment_id: ID of the comment to delete
    
    Returns:
    {
        "Code": 200,
        "Message": "Comment <comment_id> deleted successfully"
    }
    """
    try:
        result = service.delete_comment(comment_id)
        status_code = result.pop("Code", 200)
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({"Code": 500, "Message": str(e)}), 500

@comment_bp.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "Comments service is running"}), 200