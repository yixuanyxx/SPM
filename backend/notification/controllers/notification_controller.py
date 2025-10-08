from flask import Blueprint, request, jsonify
from services.notification_service import NotificationService
from services.notification_trigger_service import NotificationTriggerService

notification_bp = Blueprint("notifications", __name__)
service = NotificationService()
trigger_service = NotificationTriggerService()

@notification_bp.route("/notifications/create", methods=["POST"])
def create_notification():
    """
    Create a new notification.
    
    Required fields:
    - userid: ID of the user receiving the notification
    - notification: Notification message content
    
    Optional fields:
    - notification_type: Type of notification (default: "general")
    - related_task_id: ID of related task if applicable
    
    Returns:
    {
        "message": "Notification created! Notification ID: <id>",
        "data": { ... notification data ... },
        "status": 201
    }
    """
    try:
        # Get JSON data from request
        data = request.get_json(silent=True) or {}
        
        # Call service to create notification
        result = service.create_notification(data)
        status_code = result.pop("status", 201)
        
        return jsonify(result), status_code
        
    except ValueError as ve:
        return jsonify({"error": str(ve), "status": 400}), 400
    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500

@notification_bp.route("/notifications/user/<int:user_id>", methods=["GET"])
def get_notifications_by_user(user_id: int):
    """
    Get all notifications for a specific user.
    
    Parameters:
    - user_id: ID of the user
    
    Returns:
    {
        "data": [ ... list of notifications ... ],
        "status": 200
    }
    
    Responses:
        200: Notifications found and returned
        404: No notifications found for this user
        500: Internal Server Error
    """
    try:
        result = service.get_notifications_by_user(user_id)
        status_code = result.pop("status", 200)
        
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500

@notification_bp.route("/notifications/<int:notification_id>", methods=["GET"])
def get_notification_by_id(notification_id: int):
    """
    Get a single notification by its ID.
    
    Parameters:
    - notification_id: ID of the notification to retrieve
    
    Returns:
    {
        "data": { ... notification data ... },
        "status": 200
    }
    
    Responses:
        200: Notification found and returned
        404: Notification not found
        500: Internal Server Error
    """
    try:
        result = service.get_notification_by_id(notification_id)
        status_code = result.pop("status", 200)
        
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500

@notification_bp.route("/notifications/<int:notification_id>/read", methods=["PUT", "PATCH"])
def mark_notification_as_read(notification_id: int):
    """
    Mark a notification as read.
    
    Parameters:
    - notification_id: ID of the notification to mark as read
    
    Returns:
    {
        "message": "Notification <notification_id> marked as read",
        "data": { ... updated notification data ... },
        "status": 200
    }
    
    Responses:
        200: Notification successfully marked as read
        404: Notification not found
        500: Internal Server Error
    """
    try:
        result = service.mark_notification_as_read(notification_id)
        status_code = result.pop("status", 200)
        
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500

@notification_bp.route("/notifications/<int:notification_id>/unread", methods=["PUT", "PATCH"])
def mark_notification_as_unread(notification_id: int):
    """
    Mark a notification as unread.
    
    Parameters:
    - notification_id: ID of the notification to mark as unread
    
    Returns:
    {
        "message": "Notification <notification_id> marked as unread",
        "data": { ... updated notification data ... },
        "status": 200
    }
    
    Responses:
        200: Notification successfully marked as unread
        404: Notification not found
        500: Internal Server Error
    """
    try:
        result = service.mark_notification_as_unread(notification_id)
        status_code = result.pop("status", 200)
        
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500

@notification_bp.route("/notifications/user/<int:user_id>/unread-count", methods=["GET"])
def get_unread_count(user_id: int):
    """
    Get the count of unread notifications for a user.
    
    Parameters:
    - user_id: ID of the user
    
    Returns:
    {
        "data": { "unread_count": <count> },
        "status": 200
    }
    
    Responses:
        200: Unread count returned
        500: Internal Server Error
    """
    try:
        result = service.get_unread_count(user_id)
        status_code = result.pop("status", 200)
        
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500

@notification_bp.route("/notifications/user/<int:user_id>/unread", methods=["GET"])
def get_unread_notifications(user_id: int):
    """
    Get all unread notifications for a user.
    
    Parameters:
    - user_id: ID of the user
    
    Returns:
    {
        "data": [ ... list of unread notifications ... ],
        "status": 200
    }
    
    Responses:
        200: Unread notifications found and returned
        404: No unread notifications found for this user
        500: Internal Server Error
    """
    try:
        result = service.get_unread_notifications(user_id)
        status_code = result.pop("status", 200)
        
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500

@notification_bp.route("/notifications/<int:notification_id>", methods=["DELETE"])
def delete_notification(notification_id: int):
    """
    Delete a notification by its ID.
    
    Parameters:
    - notification_id: ID of the notification to delete
    
    Returns:
    {
        "message": "Notification <notification_id> deleted successfully",
        "status": 200
    }
    
    Responses:
        200: Notification successfully deleted
        404: Notification not found
        500: Internal Server Error
    """
    try:
        result = service.delete_notification(notification_id)
        status_code = result.pop("status", 200)
        
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500

# Notification trigger endpoints
@notification_bp.route("/notifications/triggers/task-assignment", methods=["POST"])
def trigger_task_assignment_notification():
    """
    Trigger notification for task assignment.
    
    Required fields in JSON body:
    - task_id: ID of the assigned task
    - assigned_user_id: ID of the user assigned to the task
    - assigner_name: Name of the person who assigned the task (optional, defaults to "System")
    
    Returns:
    {
        "message": "Notifications sent based on user preferences",
        "results": [ ... notification results ... ],
        "status": 200
    }
    """
    try:
        data = request.get_json(silent=True) or {}
        
        task_id = data.get("task_id")
        assigned_user_id = data.get("assigned_user_id")
        assigner_name = data.get("assigner_name", "System")
        
        if not task_id or not assigned_user_id:
            return jsonify({"error": "task_id and assigned_user_id are required", "status": 400}), 400
        
        result = trigger_service.notify_task_assignment(task_id, assigned_user_id, assigner_name)
        status_code = result.pop("status", 200)
        
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500

@notification_bp.route("/notifications/triggers/task-ownership-transfer", methods=["POST"])
def trigger_task_ownership_transfer_notification():
    """
    Trigger notification for task ownership transfer.
    
    Required fields in JSON body:
    - task_id: ID of the task
    - new_owner_id: ID of the new owner
    - previous_owner_name: Name of the previous owner (optional, defaults to "System")
    
    Returns:
    {
        "message": "Notifications sent based on user preferences",
        "results": [ ... notification results ... ],
        "status": 200
    }
    """
    try:
        data = request.get_json(silent=True) or {}
        
        task_id = data.get("task_id")
        new_owner_id = data.get("new_owner_id")
        previous_owner_name = data.get("previous_owner_name", "System")
        
        if not task_id or not new_owner_id:
            return jsonify({"error": "task_id and new_owner_id are required", "status": 400}), 400
        
        result = trigger_service.notify_task_ownership_transfer(task_id, new_owner_id, previous_owner_name)
        status_code = result.pop("status", 200)
        
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500

@notification_bp.route("/notifications/triggers/task-status-change", methods=["POST"])
def trigger_task_status_change_notification():
    """
    Trigger notification for task status change.
    
    Required fields in JSON body:
    - task_id: ID of the task
    - user_ids: List of user IDs to notify (collaborators)
    - old_status: Previous status
    - new_status: New status
    - updater_name: Name of the person who updated the task (optional, defaults to "System")
    
    Returns:
    {
        "message": "Notifications sent to all collaborators",
        "results": [ ... notification results for each user ... ],
        "status": 200
    }
    """
    try:
        data = request.get_json(silent=True) or {}
        
        task_id = data.get("task_id")
        user_ids = data.get("user_ids", [])
        old_status = data.get("old_status")
        new_status = data.get("new_status")
        updater_name = data.get("updater_name", "System")
        
        if not task_id or not user_ids or not old_status or not new_status:
            return jsonify({"error": "task_id, user_ids, old_status, and new_status are required", "status": 400}), 400
        
        results = trigger_service.notify_task_status_change(task_id, user_ids, old_status, new_status, updater_name)
        
        return jsonify({"message": "Notifications sent to all collaborators", "results": results, "status": 200}), 200
        
    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500

@notification_bp.route("/notifications/triggers/task-due-date-change", methods=["POST"])
def trigger_task_due_date_change_notification():
    """
    Trigger notification for task due date change.
    
    Required fields in JSON body:
    - task_id: ID of the task
    - user_ids: List of user IDs to notify (collaborators)
    - old_due_date: Previous due date
    - new_due_date: New due date
    - updater_name: Name of the person who updated the task (optional, defaults to "System")
    
    Returns:
    {
        "message": "Notifications sent to all collaborators",
        "results": [ ... notification results for each user ... ],
        "status": 200
    }
    """
    try:
        data = request.get_json(silent=True) or {}
        
        task_id = data.get("task_id")
        user_ids = data.get("user_ids", [])
        old_due_date = data.get("old_due_date")
        new_due_date = data.get("new_due_date")
        updater_name = data.get("updater_name", "System")
        
        if not task_id or not user_ids or not old_due_date or not new_due_date:
            return jsonify({"error": "task_id, user_ids, old_due_date, and new_due_date are required", "status": 400}), 400
        
        results = trigger_service.notify_task_due_date_change(task_id, user_ids, old_due_date, new_due_date, updater_name)
        
        return jsonify({"message": "Notifications sent to all collaborators", "results": results, "status": 200}), 200
        
    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500

@notification_bp.route("/notifications/triggers/task-description-change", methods=["POST"])
def trigger_task_description_change_notification():
    """
    Trigger notification for task description change.
    
    Required fields in JSON body:
    - task_id: ID of the task
    - user_ids: List of user IDs to notify (collaborators)
    - updater_name: Name of the person who updated the task (optional, defaults to "System")
    
    Returns:
    {
        "message": "Notifications sent to all collaborators",
        "results": [ ... notification results for each user ... ],
        "status": 200
    }
    """
    try:
        data = request.get_json(silent=True) or {}
        
        task_id = data.get("task_id")
        user_ids = data.get("user_ids", [])
        updater_name = data.get("updater_name", "System")
        
        if not task_id or not user_ids:
            return jsonify({"error": "task_id and user_ids are required", "status": 400}), 400
        
        results = trigger_service.notify_task_description_change(task_id, user_ids, updater_name)
        
        return jsonify({"message": "Notifications sent to all collaborators", "results": results, "status": 200}), 200
        
    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500