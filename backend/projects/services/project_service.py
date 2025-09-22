from typing import Dict, Any, Optional
from models.project import Project
from repo.supa_project_repo import SupabaseProjectRepo

class ProjectService:
    def __init__(self, repo: Optional[SupabaseProjectRepo] = None):
        self.repo = repo or SupabaseProjectRepo()

    def create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new project.
        Required fields: owner_id, proj_name
        Optional fields: collaborators, tasks
        """
        # Validate required fields
        if not payload.get("owner_id"):
            raise ValueError("owner_id is required")
        if not payload.get("proj_name"):
            raise ValueError("proj_name is required")

        # Create project instance
        project = Project(
            owner_id=payload["owner_id"],
            proj_name=payload["proj_name"],
            collaborators=payload.get("collaborators"),
            tasks=payload.get("tasks"),
        )

        # Convert to dict and remove None id for database insertion
        data = project.__dict__.copy()
        data.pop("id", None)

        # Insert into database
        created = self.repo.insert_project(data)
        return {"status": 201, "message": f"Project created! Project ID: {created.get('id')}", "data": created}

    def get_projects_by_user(self, user_id: int) -> Dict[str, Any]:
        """
        Get all projects where user is either owner or collaborator.
        """
        projects = self.repo.find_by_user(user_id)
        if not projects:
            return {"status": 404, "message": f"No projects found for user ID {user_id}"}
        return {"status": 200, "data": projects}

    def get_project_by_id(self, project_id: int) -> Dict[str, Any]:
        """
        Get a single project by its ID.
        """
        project = self.repo.get_project(project_id)
        if not project:
            return {"status": 404, "message": f"Project with ID {project_id} not found"}
        return {"status": 200, "data": project}

    def update_project_by_id(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a project with the provided fields. Only project_id is required.
        """
        project_id = payload.get("project_id")
        if not project_id:
            raise ValueError("project_id is required for updates")
        
        # Check if project exists
        existing_project = self.repo.get_project(project_id)
        if not existing_project:
            return {"status": 404, "message": f"Project with ID {project_id} not found"}
        
        # Extract update fields (exclude project_id from the update data)
        update_fields = {k: v for k, v in payload.items() if k != "project_id"}
        
        if not update_fields:
            return {"status": 400, "message": "No fields to update provided", "data": existing_project}
        
        # Perform the update
        try:
            updated_project = self.repo.update_project(project_id, update_fields)
            return {"status": 200, "message": f"Project {project_id} updated successfully", "data": updated_project}
        except Exception as e:
            raise RuntimeError(f"Failed to update project {project_id}: {str(e)}")
