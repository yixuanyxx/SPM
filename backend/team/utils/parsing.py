from typing import Dict, Any

def parse_team_payload(form_or_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse team creation payload.
    Accepts either request.form (ImmutableMultiDict) or request.json (dict)
    and normalizes to a dict for Team creation.
    """
    # allow .get for both types
    g = form_or_json.get

    name = g("name")
    dept_id = g("dept_id")

    if not all([name, dept_id]):
        missing = [k for k in ["name", "dept_id"] if not g(k)]
        raise ValueError(f"Missing required fields: {missing}")

    # Validate name is not empty after stripping whitespace
    if not name.strip():
        raise ValueError("Team name cannot be empty")

    try:
        dept_id_int = int(dept_id)
    except (ValueError, TypeError):
        raise ValueError("dept_id must be a valid integer")

    return {
        "name": name.strip(),
        "dept_id": dept_id_int
    }

def parse_team_update_payload(form_or_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse team update payload.
    All fields are optional for updates.
    """
    # allow .get for both types
    g = form_or_json.get

    update_data = {}

    # Optional name field
    name = g("name")
    if name is not None and name != "":
        if not name.strip():
            raise ValueError("Team name cannot be empty")
        update_data["name"] = name.strip()

    # Optional dept_id field
    dept_id = g("dept_id")
    if dept_id is not None and dept_id != "":
        try:
            update_data["dept_id"] = int(dept_id)
        except (ValueError, TypeError):
            raise ValueError("dept_id must be a valid integer")

    return update_data