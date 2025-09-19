from typing import Dict, Any, Optional
from models.task import Task
from repo.supa_task_repo import SupabaseTaskRepo

class TaskService:
    def __init__(self, repo: Optional[SupabaseTaskRepo] = None):
        self.repo = repo or SupabaseTaskRepo()

    def create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # uniqueness per owner: task_name
        existing = self.repo.find_by_owner_and_name(payload["owner_id"], payload["task_name"])
        if existing:
            # convention: 200 with message (kept from your original)
            return {"__status": 200, "Message": f"Task '{payload['task_name']}' already exists for this user.", "data": existing}

        task = Task(
            owner_id=payload["owner_id"],
            task_name=payload["task_name"],
            due_date=payload["due_date"],
            description=payload["description"],
            collaborators=payload.get("collaborators", []),
            status=payload["status"],
            project_id=payload.get("project_id"),
        )

        # ⬇️ Do NOT send id=None
        data = task.__dict__.copy()
        data.pop("id", None)

        created = self.repo.insert_task(data)
        return {"__status": 201, "Message": f"Task created! Task ID: {created.get('id')}", "data": created}

    # get tasks by user_id (in owner_id or collaborators)
    def get_by_user(self, user_id: int) -> Optional[list]:
        tasks = self.repo.find_by_user(user_id)
        return tasks

    def update_status(self, task_id: int, new_status: str):
        updated = self.repo.update_task(task_id, {"status": new_status})
        return updated
