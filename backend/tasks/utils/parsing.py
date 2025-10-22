from typing import Dict, Any, List
from dateutil import parser as dateparser

def parse_task_payload(form_or_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Accepts either request.form (ImmutableMultiDict) or request.json (dict)
    and normalizes to a dict for Task creation/update.
    """
    # allow .get for both types
    g = form_or_json.get

    task_name = g("task_name")
    due_date_raw = g("due_date")
    description = g("description")
    status = g("status")
    owner_id = g("owner_id")
    project_id = g("project_id")
    collaborators_raw = g("collaborators", "")
    parent_task = g("parent_task")
    task_type = g("type","parent")  # Default to "parent" if not specified
    subtasks_raw = g("subtasks", "")
    priority = g("priority")
    attachments_raw = g("attachments")
    reminder_intervals_raw = g("reminder_intervals", "")


    if not all([task_name, description, owner_id]):
        missing = [k for k in ["task_name","description","owner_id"] if not g(k)]
        raise ValueError(f"Missing required fields: {missing}")

    # Validate task type
    if task_type not in ["parent", "subtask"]:
        raise ValueError(f"Invalid task type: {task_type}. Must be 'parent' or 'subtask'.")

    # parse date (accepts formats like 'Wed Sep 16 2025') - optional
    due_date = dateparser.parse(due_date_raw).isoformat() if due_date_raw else None

    # parse collaborators (comma-separated ints) - optional
    collaborators: List[int] = []
    if isinstance(collaborators_raw, str) and collaborators_raw.strip():
        collaborators = [int(c.strip()) for c in collaborators_raw.split(",") if c.strip()]
    elif isinstance(collaborators_raw, list):
        collaborators = [int(x) for x in collaborators_raw]

    # parse subtasks (comma-separated ints or list)
    subtasks: List[int] = []
    if isinstance(subtasks_raw, str) and subtasks_raw.strip():
        subtasks = [int(s.strip()) for s in subtasks_raw.split(",") if s.strip()]
    elif isinstance(subtasks_raw, list):
        subtasks = [int(x) for x in subtasks_raw]

    attachments = None
    if attachments_raw:
        if isinstance(attachments_raw, str):
        # could be JSON stringified
            import json
            try:
                attachments = json.loads(attachments_raw)
            except Exception:
                raise ValueError("attachments must be valid JSON if provided as string")
        elif isinstance(attachments_raw, list):
            attachments = attachments_raw

    recurrence_fields = parse_recurrence_fields(form_or_json)
    
    # Parse reminder_intervals (comma-separated ints or list) - optional
    reminder_intervals: List[int] = [7, 3, 1]  # Default
    if reminder_intervals_raw:
        if isinstance(reminder_intervals_raw, str) and reminder_intervals_raw.strip():
            try:
                reminder_intervals = [int(x.strip()) for x in reminder_intervals_raw.split(",") if x.strip()]
            except ValueError:
                reminder_intervals = [7, 3, 1]  # Default fallback
        elif isinstance(reminder_intervals_raw, list):
            try:
                reminder_intervals = [int(x) for x in reminder_intervals_raw]
            except (ValueError, TypeError):
                reminder_intervals = [7, 3, 1]  # Default fallback

    return {
        "task_name": task_name,
        "due_date": due_date,
        "description": description,
        "status": status if status not in (None, "",) else None,
        "owner_id": int(owner_id),
        "project_id": int(project_id) if project_id not in (None, "",) else None,
        "collaborators": collaborators if collaborators else None,
        "parent_task": int(parent_task) if parent_task not in (None, "",) else None,
        "type": task_type,
        "subtasks": subtasks if subtasks else None,
        "priority": int(priority) if priority not in (None, "",) else None,
        "attachments": attachments,
        "recurrence_type": recurrence_fields["recurrence_type"],
        "recurrence_end_date": recurrence_fields["recurrence_end_date"],
        "recurrence_interval_days": recurrence_fields["recurrence_interval_days"],
        "reminder_intervals": reminder_intervals      
    }

def parse_subtask_payload(form_or_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Specialized parsing for subtasks that requires parent_task as a mandatory field.
    """
    # allow .get for both types
    g = form_or_json.get

    task_name = g("task_name")
    description = g("description")
    owner_id = g("owner_id")
    parent_task = g("parent_task")
    
    # For subtasks, parent_task is required
    if not all([task_name, description, owner_id, parent_task]):
        missing = [k for k in ["task_name","description","owner_id","parent_task"] if not g(k)]
        raise ValueError(f"Missing required fields for subtask: {missing}")

    # Use the regular parsing for the rest but ensure type is "subtask"
    regular_payload = parse_task_payload(form_or_json)
    regular_payload["type"] = "subtask"
    
    return regular_payload

def parse_task_update_payload(form_or_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse payload for task updates. Only task_id is required, everything else is optional.
    """
    # allow .get for both types
    g = form_or_json.get

    task_id = g("task_id")
    
    # Only task_id is required for updates
    if not task_id:
        raise ValueError("Missing required field: task_id")

    # Parse all optional fields
    update_data = {"task_id": int(task_id)}
    
    # Optional string fields
    for field in ["task_name", "description", "status", "type"]:
        value = g(field)
        if value is not None and value != "":
            if field == "type" and value not in ["parent", "subtask"]:
                raise ValueError(f"Invalid task type: {value}. Must be 'parent' or 'subtask'.")
            update_data[field] = value
    
    # Optional integer fields
    for field in ["owner_id", "project_id", "parent_task", "priority"]:
        value = g(field)
        if value is not None and value != "":
            update_data[field] = int(value)
    
    # Optional date field
    due_date_raw = g("due_date")
    if due_date_raw:
        update_data["due_date"] = dateparser.parse(due_date_raw).isoformat()
    
    # Optional list fields (collaborators, subtasks, reminder_intervals)
    for field_name, raw_field in [("collaborators", "collaborators"), ("subtasks", "subtasks"), ("reminder_intervals", "reminder_intervals")]:
        raw_value = g(raw_field, "")
        if raw_value:
            parsed_list = []
            if isinstance(raw_value, str) and raw_value.strip():
                parsed_list = [int(x.strip()) for x in raw_value.split(",") if x.strip()]
            elif isinstance(raw_value, list):
                parsed_list = [int(x) for x in raw_value]
            
            if parsed_list:
                update_data[field_name] = parsed_list

    attachments_raw = g("attachments")
    if attachments_raw:
        if isinstance(attachments_raw, str):
            import json
            attachments = json.loads(attachments_raw)
            update_data["attachments"] = attachments
        elif isinstance(attachments_raw, list):
            update_data["attachments"] = attachments_raw

    # Optional recurrence fields
    recurrence_type = g("recurrence_type")
    recurrence_end_raw = g("recurrence_end_date")

    if recurrence_type:
        valid_types = [None, "daily", "weekly", "bi-weekly", "monthly", "yearly","custom"]
        if recurrence_type.lower() not in valid_types:
            raise ValueError(f"Invalid recurrence_type: {recurrence_type}. Must be one of {valid_types}.")
        update_data["recurrence_type"] = recurrence_type.lower()

    if recurrence_end_raw:
        try:
            update_data["recurrence_end_date"] = dateparser.parse(recurrence_end_raw).isoformat()
        except Exception:
            raise ValueError(f"Invalid recurrence_end_date: '{recurrence_end_raw}'")
    
    return update_data

# ---- Recurrence Parsing ----
def parse_recurrence_fields(form_or_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parses recurrence fields from form or JSON input.
    Accepts recurrence_type (daily, weekly, bi-weekly, monthly, yearly, none)
    and recurrence_end_date (any parsable date format).
    """
    g = form_or_json.get

    recurrence_type_raw = g("recurrence_type")
    if recurrence_type_raw is not None:
        recurrence_type_raw = str(recurrence_type_raw).lower().strip()

    valid_types = ["daily", "weekly", "bi-weekly", "monthly", "yearly","custom"]
    if recurrence_type_raw not in valid_types:
        recurrence_type_raw = None
    
    recurrence_end_raw = g("recurrence_end_date")
    recurrence_end_date = None
    if recurrence_end_raw:
        try:
            recurrence_end_date = dateparser.parse(recurrence_end_raw).isoformat()
        except Exception:
            raise ValueError(f"Invalid recurrence_end_date: '{recurrence_end_raw}'")
        
    recurrence_interval_days = None
    if recurrence_type_raw == "custom":
        interval_raw = g("recurrence_interval_days")
        if interval_raw not in (None, ""):
            try:
                recurrence_interval_days = int(interval_raw)
                if recurrence_interval_days <= 0:
                    raise ValueError
            except Exception:
                raise ValueError("recurrence_interval_days must be a positive integer for custom recurrence")
    
    return {
        "recurrence_type": recurrence_type_raw,
        "recurrence_end_date": recurrence_end_date,
        "recurrence_interval_days": recurrence_interval_days
    }

