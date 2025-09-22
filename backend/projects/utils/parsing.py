from typing import Dict, Any, List
from dateutil import parser as dateparser

def parse_project_payload(form_or_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Accepts either request.form (ImmutableMultiDict) or request.json (dict)
    and normalizes to a dict for Project creation/update.
    """
    # allow .get for both types
    g = form_or_json.get

    proj_name = g("proj_name")
    owner_id = g("owner_id")
    collaborators_raw = g("collaborators", "")
    tasks_raw = g("tasks", "")

    if not all([proj_name, owner_id]):
        missing = [k for k in ["proj_name", "owner_id"] if not g(k)]
        raise ValueError(f"Missing required fields: {missing}")

    # parse collaborators (comma-separated ints) - optional
    collaborators: List[int] = []
    if isinstance(collaborators_raw, str) and collaborators_raw.strip():
        collaborators = [int(c.strip()) for c in collaborators_raw.split(",") if c.strip()]
    elif isinstance(collaborators_raw, list):
        collaborators = [int(x) for x in collaborators_raw]

    # parse tasks (comma-separated ints or list) - optional
    tasks: List[int] = []
    if isinstance(tasks_raw, str) and tasks_raw.strip():
        tasks = [int(t.strip()) for t in tasks_raw.split(",") if t.strip()]
    elif isinstance(tasks_raw, list):
        tasks = [int(x) for x in tasks_raw]

    return {
        "proj_name": proj_name,
        "owner_id": int(owner_id),
        "collaborators": collaborators if collaborators else None,
        "tasks": tasks if tasks else None,
    }

def parse_project_update_payload(form_or_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse payload for project updates. Only project_id is required, everything else is optional.
    """
    # allow .get for both types
    g = form_or_json.get

    project_id = g("project_id")
    
    # Only project_id is required for updates
    if not project_id:
        raise ValueError("Missing required field: project_id")

    # Parse all optional fields
    update_data = {"project_id": int(project_id)}
    
    # Optional string fields
    proj_name = g("proj_name")
    if proj_name is not None and proj_name != "":
        update_data["proj_name"] = proj_name
    
    # Optional integer fields
    for field in ["owner_id"]:
        value = g(field)
        if value is not None and value != "":
            update_data[field] = int(value)
    
    # Optional list fields (collaborators, tasks)
    for field_name, raw_field in [("collaborators", "collaborators"), ("tasks", "tasks")]:
        raw_value = g(raw_field, "")
        if raw_value:
            parsed_list = []
            if isinstance(raw_value, str) and raw_value.strip():
                parsed_list = [int(x.strip()) for x in raw_value.split(",") if x.strip()]
            elif isinstance(raw_value, list):
                parsed_list = [int(x) for x in raw_value]
            
            if parsed_list:
                update_data[field_name] = parsed_list
    
    return update_data
