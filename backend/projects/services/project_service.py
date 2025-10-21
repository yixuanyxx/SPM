from typing import Dict, Any, Optional
import requests
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

        # Use the new Project.from_dict constructor for proper type handling
        project = Project.from_dict(payload)

        # Convert to dictionary for database insertion (excludes id=None)
        data = project.to_dict()
        data.pop("id", None)

        # Insert into database
        created = self.repo.insert_project(data)
        
        # Trigger collaborator notifications after successful project creation
        self._trigger_collaborator_notifications(created.get('id'), payload)
        
        return {"status": 201, "message": f"Project created! Project ID: {created.get('id')}", "data": created}

    def _trigger_collaborator_notifications(self, project_id: int, payload: Dict[str, Any]):
        """
        Trigger notifications for collaborators when a new project is created.
        """
        try:
            # Get collaborators from payload
            collaborators = payload.get("collaborators", [])
            owner_id = payload.get("owner_id")
            project_name = payload.get("proj_name", f"Project {project_id}")
            
            # Get creator name
            creator_name = "System"
            if owner_id:
                try:
                    response = requests.get(f"http://127.0.0.1:5003/users/{owner_id}")
                    if response.status_code == 200:
                        user_data = response.json()
                        creator_name = user_data.get("data", {}).get("name", "System")
                except Exception:
                    pass  # Use default name if we can't fetch it
            
            # Send notifications to all collaborators except the owner
            collaborator_ids = [collab_id for collab_id in collaborators if collab_id != owner_id]
            
            if collaborator_ids:
                response = requests.post("http://127.0.0.1:5006/notifications/triggers/project-collaborator-addition", 
                                       json={
                                           "project_id": project_id,
                                           "collaborator_ids": collaborator_ids,
                                           "project_name": project_name,
                                           "creator_name": creator_name
                                       })
                if response.status_code not in [200, 201]:
                    print(f"Warning: Failed to send project collaborator notifications: {response.status_code}")
        except Exception as e:
            print(f"Warning: Failed to send project collaborator notifications: {e}")

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
            return {"status": 400, "message": "project_id is required for updates"}
        
        # Check if project exists
        existing_project_data = self.repo.get_project(project_id)
        if not existing_project_data:
            return {"status": 404, "message": f"Project with ID {project_id} not found"}
        
        # Extract update fields (exclude project_id from the update data)
        update_fields = {k: v for k, v in payload.items() if k != "project_id"}
        
        if not update_fields:
            return {"status": 400, "message": "No fields to update provided", "data": existing_project_data}
        
        # Create Project object from existing data for proper type handling
        existing_project = Project.from_dict(existing_project_data)
        
        # Merge update fields with existing data
        merged_data = existing_project.to_dict()
        merged_data.update(update_fields)
        
        # Create updated project object to ensure proper type conversion
        updated_project_obj = Project.from_dict(merged_data)
        
        # Convert back to dict for database update
        update_data = updated_project_obj.to_dict()
        
        # Perform the update
        try:
            updated_project_data = self.repo.update_project(project_id, update_data)
            
            # Check for collaborator additions and trigger notifications
            self._trigger_collaborator_addition_notifications(existing_project_data, update_fields, project_id)
            
            return {"status": 200, "message": f"Project {project_id} updated successfully", "data": updated_project_data}
        except RuntimeError as e:
            if "not found" in str(e).lower():
                return {"status": 404, "message": f"Project with ID {project_id} not found"}
            else:
                return {"status": 500, "message": f"Failed to update project {project_id}: {str(e)}"}
        except Exception as e:
            return {"status": 500, "message": f"Failed to update project {project_id}: {str(e)}"}

    def _trigger_collaborator_addition_notifications(self, existing_project_data: Dict[str, Any], update_fields: Dict[str, Any], project_id: int):
        """
        Trigger notifications for newly added collaborators when updating an existing project.
        """
        try:
            # Check if collaborators field was updated
            if 'collaborators' not in update_fields:
                return
            
            # Get existing and new collaborators
            existing_collaborators = set(existing_project_data.get("collaborators", []) or [])
            new_collaborators = set(update_fields.get("collaborators", []) or [])
            
            # Find newly added collaborators (excluding the owner)
            owner_id = existing_project_data.get("owner_id")
            newly_added_collaborators = new_collaborators - existing_collaborators
            
            # Remove owner from newly added collaborators (they shouldn't get notifications)
            if owner_id:
                newly_added_collaborators.discard(owner_id)
            
            if not newly_added_collaborators:
                return
            
            # Get project name and updater name
            project_name = existing_project_data.get("proj_name", f"Project {project_id}")
            updater_name = "System"
            # Try to get updater from request context or use owner as fallback
            if owner_id:
                try:
                    response = requests.get(f"http://127.0.0.1:5003/users/{owner_id}")
                    if response.status_code == 200:
                        user_data = response.json()
                        updater_name = user_data.get("data", {}).get("name", "System")
                except Exception:
                    pass  # Use default name if we can't fetch it
            
            # Send notifications to newly added collaborators
            collaborator_ids = list(newly_added_collaborators)
            if collaborator_ids:
                response = requests.post("http://127.0.0.1:5006/notifications/triggers/project-collaborator-addition", 
                                       json={
                                           "project_id": project_id,
                                           "collaborator_ids": collaborator_ids,
                                           "project_name": project_name,
                                           "creator_name": updater_name
                                       })
                if response.status_code not in [200, 201]:
                    print(f"Warning: Failed to send project collaborator addition notifications: {response.status_code}")
        except Exception as e:
            print(f"Warning: Failed to send project collaborator addition notifications: {e}")

    def get_projects_by_owner(self, owner_id: int) -> Dict[str, Any]:
        """
        Get all projects that are owned by a specific user (by owner_id only).
        """
        projects = self.repo.find_by_owner(owner_id)
        if not projects:
            return {"status": 404, "message": f"No projects found for owner ID {owner_id}"}
        return {"status": 200, "data": projects}

    def add_task_to_project(self, project_id: int, task_id: int) -> Dict[str, Any]:
        """
        Add a task and its subtasks to a project by:
        1. Getting task details from task microservice
        2. Adding task_id and all subtask_ids to project's tasks list
        3. Adding new task collaborators to project's collaborators list
        4. Using bulk update to set project_id for task and all subtasks
        """
        # Check if project exists
        project = self.repo.get_project(project_id)
        if not project:
            return {"status": 404, "message": f"Project with ID {project_id} not found"}

        # Get task details from task microservice
        try:
            task_response = requests.get(f"http://127.0.0.1:5002/tasks/{task_id}")
            if task_response.status_code != 200:
                return {"status": 404, "message": f"Task with ID {task_id} not found in task microservice"}
            
            task_data = task_response.json()
            task = task_data.get("task", {})
            
            if not task:
                return {"status": 404, "message": f"Task with ID {task_id} not found"}
                
        except requests.RequestException as e:
            return {"status": 500, "message": f"Failed to communicate with task microservice: {str(e)}"}

        # Get current project data
        current_tasks = project.get("tasks") or []
        current_collaborators = project.get("collaborators") or []
        
        # Get task and subtask IDs
        task_collaborators = task.get("collaborators") or []
        subtasks = task.get("subtasks") or []
        
        # Create list of all task IDs (main task + subtasks)
        all_task_ids = [task_id] + subtasks
        
        # Check if any of these tasks are already in the project -lowkey dont need
        existing_tasks = [tid for tid in all_task_ids if tid in current_tasks]
        if existing_tasks:
            return {"status": 400, "message": f"Tasks {existing_tasks} are already in project {project_id}"}

        # Add all task IDs to project's tasks list
        updated_tasks = current_tasks + all_task_ids

        # Add new task collaborators to project collaborators
        updated_collaborators = current_collaborators.copy()
        added_collaborators = []
        
        for collaborator_id in task_collaborators:
            if collaborator_id not in updated_collaborators:
                updated_collaborators.append(collaborator_id)
                added_collaborators.append(collaborator_id)

        # Update project in database
        try:
            updated_project = self.repo.update_project(project_id, {
                "tasks": updated_tasks,
                "collaborators": updated_collaborators
            })
        except Exception as e:
            return {"status": 500, "message": f"Failed to update project: {str(e)}"}

        # Use bulk update to set project_id for task and all subtasks
        try:
            bulk_update_response = requests.post("http://127.0.0.1:5002/tasks/update-project/bulk", 
                json={
                    "task_ids": all_task_ids,
                    "project_id": project_id
                })
            
            if bulk_update_response.status_code not in [200, 207]:
                # Log warning but don't fail the operation
                print(f"Warning: Failed to bulk update tasks {all_task_ids} project_id: {bulk_update_response.text}")
            else:
                bulk_result = bulk_update_response.json()
                print(f"Bulk update result: {bulk_result.get('Message', 'No message')}")
                
        except requests.RequestException as e:
            # Log warning but don't fail the operation
            print(f"Warning: Failed to communicate with task microservice for bulk update: {str(e)}")

        return {
            "status": 200, 
            "message": f"Task {task_id} and {len(subtasks)} subtasks successfully added to project {project_id}",
            "data": {
                "project": updated_project,
                "main_task_id": task_id,
                "subtask_ids": subtasks,
                "all_task_ids": all_task_ids,
                "added_collaborators": added_collaborators
            }
        }