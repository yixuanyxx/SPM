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

    if not all([task_name, due_date_raw, description, status, owner_id]):
        missing = [k for k in ["task_name","due_date","description","status","owner_id"] if not g(k)]
        raise ValueError(f"Missing required fields: {missing}")

    # parse date (accepts formats like 'Wed Sep 16 2025')
    due_date = dateparser.parse(due_date_raw).isoformat()

    # parse collaborators (comma-separated ints)
    collaborators: List[int] = []
    if isinstance(collaborators_raw, str):
        collaborators = [int(c.strip()) for c in collaborators_raw.split(",") if c.strip()]
    elif isinstance(collaborators_raw, list):
        collaborators = [int(x) for x in collaborators_raw]

    return {
        "task_name": task_name,
        "due_date": due_date,
        "description": description,
        "status": status,
        "owner_id": int(owner_id),
        "project_id": int(project_id) if project_id not in (None, "",) else None,
        "collaborators": collaborators,
    }
