from typing import Dict, Any

def parse_dept_payload(form_or_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse department creation payload.
    Accepts either request.form (ImmutableMultiDict) or request.json (dict)
    and normalizes to a dict for Department creation.
    """
    # allow .get for both types
    g = form_or_json.get

    name = g("name")

    if not name:
        raise ValueError("Missing required field: name")

    # Validate name is not empty after stripping whitespace
    if not name.strip():
        raise ValueError("Department name cannot be empty")

    return {
        "name": name.strip()
    }

def parse_dept_update_payload(form_or_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse department update payload.
    All fields are optional for updates.
    """
    # allow .get for both types
    g = form_or_json.get

    update_data = {}

    # Optional name field
    name = g("name")
    if name is not None and name != "":
        if not name.strip():
            raise ValueError("Department name cannot be empty")
        update_data["name"] = name.strip()

    return update_data