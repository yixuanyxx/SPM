import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from services.project_service import ProjectService
from models.project import Project

# Import the controller and service
from controllers.project_controller import project_bp, service


class TestProjectControllerIntegration(unittest.TestCase):
    """Integration tests for project controller endpoints."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a mock repository
        self.mock_repo = Mock()
        
        # Replace the service's repository with our mock
        service.repo = self.mock_repo

        # Create a test Flask app
        from flask import Flask
        self.app = Flask(__name__)
        self.app.register_blueprint(project_bp)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    # ==================== create_project Tests ====================
    
    def test_create_project_success(self):
        """Test successful project creation with all required fields."""
        # Mock the repository method
        self.mock_repo.insert_project.return_value = {
            "id": 1,
            "owner_id": 100,
            "proj_name": "Test Project",
            "collaborators": None,
            "tasks": None,
            "created_at": "2025-01-01T00:00:00+00:00"
        }
        
        # Make request with required fields
        response = self.client.post('/projects/create', json={
            "owner_id": 100,
            "proj_name": "Test Project"
        })
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 201)
        self.assertIn("Project created! Project ID: 1", data["message"])
        self.assertIn("data", data)
        self.assertEqual(data["data"]["proj_name"], "Test Project")
        self.assertEqual(data["data"]["owner_id"], 100)
        
        # Verify repository call
        self.mock_repo.insert_project.assert_called_once()

    def test_create_project_with_all_fields(self):
        """Test project creation with all optional fields."""
        # Mock the repository method
        self.mock_repo.insert_project.return_value = {
            "id": 2,
            "owner_id": 100,
            "proj_name": "Complete Project",
            "collaborators": [101, 102, 103],
            "tasks": [10, 11, 12],
            "created_at": "2025-01-01T00:00:00+00:00"
        }
        
        # Make request with all fields
        response = self.client.post('/projects/create', json={
            "owner_id": 100,
            "proj_name": "Complete Project",
            "collaborators": [101, 102, 103],
            "tasks": [10, 11, 12]
        })
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 201)
        self.assertEqual(data["data"]["collaborators"], [101, 102, 103])
        self.assertEqual(data["data"]["tasks"], [10, 11, 12])

    def test_create_project_missing_owner_id(self):
        """Test project creation fails when owner_id is missing."""
        response = self.client.post('/projects/create', json={
            "proj_name": "Test Project"
            # owner_id is missing
        })
        
        # Assertions
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 400)
        self.assertIn("error", data)

    def test_create_project_missing_proj_name(self):
        """Test project creation fails when proj_name is missing."""
        response = self.client.post('/projects/create', json={
            "owner_id": 100
            # proj_name is missing
        })
        
        # Assertions
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 400)
        self.assertIn("error", data)

    def test_create_project_empty_json(self):
        """Test project creation with empty JSON payload."""
        response = self.client.post('/projects/create', json={})
        
        # Assertions
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 400)

    def test_create_project_repository_error(self):
        """Test project creation when repository raises an exception."""
        # Mock repository to raise exception
        self.mock_repo.insert_project.side_effect = Exception("Database error")
        
        # Make request
        response = self.client.post('/projects/create', json={
            "owner_id": 100,
            "proj_name": "Test Project"
        })
        
        # Assertions
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 500)
        self.assertIn("Database error", data["error"])

    def test_create_project_with_empty_collaborators(self):
        """Test project creation with empty collaborators list."""
        # Mock the repository method
        self.mock_repo.insert_project.return_value = {
            "id": 3,
            "owner_id": 100,
            "proj_name": "Project No Collabs",
            "collaborators": [],
            "tasks": None,
            "created_at": "2025-01-01T00:00:00+00:00"
        }
        
        # Make request
        response = self.client.post('/projects/create', json={
            "owner_id": 100,
            "proj_name": "Project No Collabs",
            "collaborators": []
        })
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 201)

    # ==================== get_projects_by_user Tests ====================
    
    def test_get_projects_by_user_success(self):
        """Test successfully retrieving projects for a user."""
        # Mock projects where user is owner or collaborator
        self.mock_repo.find_by_user.return_value = [
            {
                "id": 1,
                "owner_id": 100,
                "proj_name": "Project 1",
                "collaborators": [100, 101],
                "tasks": [10, 11],
                "created_at": "2025-01-01T00:00:00+00:00"
            },
            {
                "id": 2,
                "owner_id": 200,
                "proj_name": "Project 2",
                "collaborators": [100, 102],
                "tasks": None,
                "created_at": "2025-01-02T00:00:00+00:00"
            }
        ]
        
        # Make request
        response = self.client.get('/projects/user/100')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 200)
        self.assertIn("data", data)
        self.assertEqual(len(data["data"]), 2)
        
        # Verify repository call
        self.mock_repo.find_by_user.assert_called_once_with(100)

    def test_get_projects_by_user_single_project(self):
        """Test retrieving a single project for a user."""
        # Mock single project
        self.mock_repo.find_by_user.return_value = [
            {
                "id": 1,
                "owner_id": 100,
                "proj_name": "Solo Project",
                "collaborators": None,
                "tasks": None,
                "created_at": "2025-01-01T00:00:00+00:00"
            }
        ]
        
        # Make request
        response = self.client.get('/projects/user/100')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 200)
        self.assertEqual(len(data["data"]), 1)
        self.assertEqual(data["data"][0]["proj_name"], "Solo Project")

    def test_get_projects_by_user_not_found(self):
        """Test get projects by user when no projects found."""
        # Mock no projects
        self.mock_repo.find_by_user.return_value = []
        
        # Make request
        response = self.client.get('/projects/user/999')
        
        # Assertions
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 404)
        self.assertIn("No projects found", data["message"])

    def test_get_projects_by_user_repository_error(self):
        """Test get projects by user with repository error."""
        # Mock repository error
        self.mock_repo.find_by_user.side_effect = Exception("Database connection failed")
        
        # Make request
        response = self.client.get('/projects/user/100')
        
        # Assertions
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 500)
        self.assertIn("Database connection failed", data["error"])

    # ==================== get_project_by_id Tests ====================
    
    def test_get_project_by_id_success(self):
        """Test successfully retrieving a project by ID."""
        # Mock project data
        self.mock_repo.get_project.return_value = {
            "id": 1,
            "owner_id": 100,
            "proj_name": "Test Project",
            "collaborators": [100, 101, 102],
            "tasks": [10, 11],
            "created_at": "2025-01-01T00:00:00+00:00"
        }
        
        # Make request
        response = self.client.get('/projects/1')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 200)
        self.assertIn("data", data)
        self.assertEqual(data["data"]["id"], 1)
        self.assertEqual(data["data"]["proj_name"], "Test Project")
        
        # Verify repository call
        self.mock_repo.get_project.assert_called_once_with(1)

    def test_get_project_by_id_not_found(self):
        """Test get project by ID when project doesn't exist."""
        # Mock project not found
        self.mock_repo.get_project.return_value = None
        
        # Make request
        response = self.client.get('/projects/999')
        
        # Assertions
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 404)
        self.assertIn("not found", data["message"])

    def test_get_project_by_id_repository_error(self):
        """Test get project by ID with repository error."""
        # Mock repository error
        self.mock_repo.get_project.side_effect = Exception("Database query failed")
        
        # Make request
        response = self.client.get('/projects/1')
        
        # Assertions
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 500)
        self.assertIn("Database query failed", data["error"])

    def test_get_project_by_id_with_minimal_data(self):
        """Test retrieving project with minimal data (no collaborators/tasks)."""
        # Mock project with minimal data
        self.mock_repo.get_project.return_value = {
            "id": 5,
            "owner_id": 100,
            "proj_name": "Minimal Project",
            "collaborators": None,
            "tasks": None,
            "created_at": "2025-01-01T00:00:00+00:00"
        }
        
        # Make request
        response = self.client.get('/projects/5')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 200)
        self.assertIsNone(data["data"]["collaborators"])
        self.assertIsNone(data["data"]["tasks"])

#     # ==================== update_project Tests ====================
    
    def test_update_project_success(self):
        """Test successful project update with multiple fields."""
        # Mock existing project
        self.mock_repo.get_project.return_value = {
            "id": 1,
            "owner_id": 100,
            "proj_name": "Old Name",
            "collaborators": [100],
            "tasks": [10],
            "created_at": "2025-01-01T00:00:00+00:00"
        }
        # Mock the repository update method
        self.mock_repo.update_project.return_value = {
            "id": 1,
            "owner_id": 100,
            "proj_name": "Updated Project Name",
            "collaborators": [100, 101, 102],
            "tasks": [10, 11, 12],
            "created_at": "2025-01-01T00:00:00+00:00"
        }
        
        # Make update request
        response = self.client.put('/projects/update', json={
            "project_id": 1,
            "proj_name": "Updated Project Name",
            "collaborators": [100, 101, 102],
            "tasks": [10, 11, 12]
        })
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 200)
        self.assertIn("updated successfully", data["message"])
        self.assertEqual(data["data"]["proj_name"], "Updated Project Name")
        self.assertEqual(data["data"]["collaborators"], [100, 101, 102])

    def test_update_project_single_field(self):
        """Test updating a single field."""
        # Mock existing project
        self.mock_repo.get_project.return_value = {
            "id": 1,
            "owner_id": 100,
            "proj_name": "Old Name",
            "collaborators": [100],
            "tasks": None,
            "created_at": "2025-01-01T00:00:00+00:00"
        }
        # Mock the repository method
        self.mock_repo.update_project.return_value = {
            "id": 1,
            "owner_id": 100,
            "proj_name": "New Name Only",
            "collaborators": [100],
            "tasks": None,
            "created_at": "2025-01-01T00:00:00+00:00"
        }
        
        # Update only proj_name
        response = self.client.patch('/projects/update', json={
            "project_id": 1,
            "proj_name": "New Name Only"
        })
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 200)
        self.assertEqual(data["data"]["proj_name"], "New Name Only")

    def test_update_project_missing_project_id(self):
        """Test update fails when project_id is missing."""
        response = self.client.put('/projects/update', json={
            "proj_name": "New Name"
            # project_id is missing
        })
        
        # Assertions
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 400)
        self.assertIn("Missing required field", data["error"])

    def test_update_project_not_found(self):
        """Test update fails when project doesn't exist."""
        # Mock project not found
        self.mock_repo.get_project.return_value = None
        
        # Make request
        response = self.client.put('/projects/update', json={
            "project_id": 999,
            "proj_name": "New Name"
        })
        
        # Assertions
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 404)
        self.assertIn("not found", data["message"])

    def test_update_project_no_fields_to_update(self):
        """Test update with only project_id (no fields to update)."""
        # Mock existing project
        self.mock_repo.get_project.return_value = {
            "id": 1,
            "owner_id": 100,
            "proj_name": "Project",
            "collaborators": None,
            "tasks": None,
            "created_at": "2025-01-01T00:00:00+00:00"
        }
        
        response = self.client.put('/projects/update', json={
            "project_id": 1
        })
        
        # Assertions
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 400)
        self.assertIn("No fields to update", data["message"])

    def test_update_project_with_collaborators(self):
        """Test updating collaborators list."""
        # Mock existing project
        self.mock_repo.get_project.return_value = {
            "id": 1,
            "owner_id": 100,
            "proj_name": "Project",
            "collaborators": [100],
            "tasks": None,
            "created_at": "2025-01-01T00:00:00+00:00"
        }
        # Mock the repository method
        self.mock_repo.update_project.return_value = {
            "id": 1,
            "owner_id": 100,
            "proj_name": "Project",
            "collaborators": [100, 101, 102, 103],
            "tasks": None,
            "created_at": "2025-01-01T00:00:00+00:00"
        }
        
        # Update collaborators
        response = self.client.put('/projects/update', json={
            "project_id": 1,
            "collaborators": [100, 101, 102, 103]
        })
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 200)
        self.assertEqual(data["data"]["collaborators"], [100, 101, 102, 103])

    def test_update_project_with_tasks(self):
        """Test updating tasks list."""
        # Mock existing project
        self.mock_repo.get_project.return_value = {
            "id": 1,
            "owner_id": 100,
            "proj_name": "Project",
            "collaborators": None,
            "tasks": [10],
            "created_at": "2025-01-01T00:00:00+00:00"
        }
        # Mock the repository method
        self.mock_repo.update_project.return_value = {
            "id": 1,
            "owner_id": 100,
            "proj_name": "Project",
            "collaborators": None,
            "tasks": [10, 11, 12, 13, 14],
            "created_at": "2025-01-01T00:00:00+00:00"
        }
        
        # Update tasks
        response = self.client.patch('/projects/update', json={
            "project_id": 1,
            "tasks": [10, 11, 12, 13, 14]
        })
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 200)
        self.assertEqual(data["data"]["tasks"], [10, 11, 12, 13, 14])

    def test_update_project_repository_error(self):
        """Test update fails on repository error."""
        # Mock existing project
        self.mock_repo.get_project.return_value = {
            "id": 1,
            "owner_id": 100,
            "proj_name": "Project",
            "collaborators": None,
            "tasks": None,
            "created_at": "2025-01-01T00:00:00+00:00"
        }
        # Mock update error
        self.mock_repo.update_project.side_effect = Exception("Database update failed")
        
        # Make request
        response = self.client.put('/projects/update', json={
            "project_id": 1,
            "proj_name": "New Name"
        })
        
        # Assertions
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 500)
        self.assertIn("Failed to update project", data["message"])

    def test_update_project_change_owner(self):
        """Test updating project owner."""
        # Mock existing project
        self.mock_repo.get_project.return_value = {
            "id": 1,
            "owner_id": 100,
            "proj_name": "Project",
            "collaborators": [100],
            "tasks": None,
            "created_at": "2025-01-01T00:00:00+00:00"
        }
        # Mock the repository method
        self.mock_repo.update_project.return_value = {
            "id": 1,
            "owner_id": 200,  # Changed owner
            "proj_name": "Project",
            "collaborators": [100, 200],
            "tasks": None,
            "created_at": "2025-01-01T00:00:00+00:00"
        }
        
        # Update owner_id
        response = self.client.put('/projects/update', json={
            "project_id": 1,
            "owner_id": 200
        })
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 200)
        self.assertEqual(data["data"]["owner_id"], 200)

#     # ==================== get_projects_by_owner Tests ====================
    
    def test_get_projects_by_owner_success(self):
        """Test successfully retrieving projects by owner."""
        # Mock projects owned by user
        self.mock_repo.find_by_owner.return_value = [
            {
                "id": 1,
                "owner_id": 100,
                "proj_name": "My Project 1",
                "collaborators": [100, 101],
                "tasks": [10],
                "created_at": "2025-01-01T00:00:00+00:00"
            },
            {
                "id": 2,
                "owner_id": 100,
                "proj_name": "My Project 2",
                "collaborators": None,
                "tasks": None,
                "created_at": "2025-01-02T00:00:00+00:00"
            }
        ]
        
        # Make request
        response = self.client.get('/projects/owner/100')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 200)
        self.assertIn("data", data)
        self.assertEqual(len(data["data"]), 2)
        self.assertEqual(data["data"][0]["owner_id"], 100)
        self.assertEqual(data["data"][1]["owner_id"], 100)
        
        # Verify repository call
        self.mock_repo.find_by_owner.assert_called_once_with(100)

    def test_get_projects_by_owner_single_project(self):
        """Test retrieving single project by owner."""
        # Mock single project
        self.mock_repo.find_by_owner.return_value = [
            {
                "id": 5,
                "owner_id": 100,
                "proj_name": "Single Owner Project",
                "collaborators": None,
                "tasks": None,
                "created_at": "2025-01-01T00:00:00+00:00"
            }
        ]
        
        # Make request
        response = self.client.get('/projects/owner/100')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 200)
        self.assertEqual(len(data["data"]), 1)
        self.assertEqual(data["data"][0]["proj_name"], "Single Owner Project")

    def test_get_projects_by_owner_not_found(self):
        """Test get projects by owner when no projects found."""
        # Mock no projects
        self.mock_repo.find_by_owner.return_value = []
        
        # Make request
        response = self.client.get('/projects/owner/999')
        
        # Assertions
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 404)
        self.assertIn("No projects found", data["message"])

    def test_get_projects_by_owner_repository_error(self):
        """Test get projects by owner with repository error."""
        # Mock repository error
        self.mock_repo.find_by_owner.side_effect = Exception("Database error")
        
        # Make request
        response = self.client.get('/projects/owner/100')
        
        # Assertions
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 500)
        self.assertIn("Database error", data["error"])

#     # ==================== add_task_to_project Tests ====================
    
    def test_add_task_to_project_success(self):
        """Test successfully adding a task to a project."""
        # Mock the service method
        with patch.object(service, 'add_task_to_project') as mock_add_task:
            mock_add_task.return_value = {
                "message": "Task 10 and 2 subtasks successfully added to project 1",
                "data": {
                    "project": {
                        "id": 1,
                        "owner_id": 100,
                        "proj_name": "Project",
                        "collaborators": [100, 101],
                        "tasks": [10, 11, 12],
                        "created_at": "2025-01-01T00:00:00+00:00"
                    },
                    "main_task_id": 10,
                    "subtask_ids": [11, 12],
                    "all_task_ids": [10, 11, 12],
                    "added_collaborators": [101]
                },
                "status": 200
            }
            
            # Make request
            response = self.client.post('/projects/1/task/10')
            
            # Assertions
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data["status"], 200)
            self.assertIn("successfully added", data["message"])
            self.assertEqual(data["data"]["main_task_id"], 10)
            self.assertEqual(data["data"]["subtask_ids"], [11, 12])
            
            # Verify service call
            mock_add_task.assert_called_once_with(1, 10)

    def test_add_task_to_project_no_subtasks(self):
        """Test adding a task without subtasks to a project."""
        # Mock the service method
        with patch.object(service, 'add_task_to_project') as mock_add_task:
            mock_add_task.return_value = {
                "message": "Task 10 and 0 subtasks successfully added to project 1",
                "data": {
                    "project": {
                        "id": 1,
                        "owner_id": 100,
                        "proj_name": "Project",
                        "collaborators": [100],
                        "tasks": [10],
                        "created_at": "2025-01-01T00:00:00+00:00"
                    },
                    "main_task_id": 10,
                    "subtask_ids": [],
                    "all_task_ids": [10],
                    "added_collaborators": []
                },
                "status": 200
            }
            
            # Make request
            response = self.client.post('/projects/1/task/10')
            
            # Assertions
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data["status"], 200)
            self.assertEqual(len(data["data"]["subtask_ids"]), 0)

    def test_add_task_to_project_task_already_exists(self):
        """Test adding a task that already exists in the project."""
        # Mock the service method to return error
        with patch.object(service, 'add_task_to_project') as mock_add_task:
            mock_add_task.return_value = {
                "message": "Tasks [10] are already in project 1",
                "status": 400
            }
            
            # Make request
            response = self.client.post('/projects/1/task/10')
            
            # Assertions
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertEqual(data["status"], 400)

    def test_add_task_to_project_project_not_found(self):
        """Test adding a task when project doesn't exist."""
        # Mock the service method to return error
        with patch.object(service, 'add_task_to_project') as mock_add_task:
            mock_add_task.return_value = {
                "message": "Project with ID 999 not found",
                "status": 404
            }
            
            # Make request
            response = self.client.post('/projects/999/task/10')
            
            # Assertions
            self.assertEqual(response.status_code, 404)
            data = json.loads(response.data)
            self.assertEqual(data["status"], 404)

    def test_add_task_to_project_task_not_found(self):
        """Test adding a task that doesn't exist."""
        # Mock the service method to return error
        with patch.object(service, 'add_task_to_project') as mock_add_task:
            mock_add_task.return_value = {
                "message": "Task with ID 999 not found",
                "status": 404
            }
            
            # Make request
            response = self.client.post('/projects/1/task/999')
            
            # Assertions
            self.assertEqual(response.status_code, 404)
            data = json.loads(response.data)
            self.assertEqual(data["status"], 404)

    def test_add_task_to_project_service_error(self):
        """Test add task to project with service error."""
        # Mock the service method to raise exception
        with patch.object(service, 'add_task_to_project') as mock_add_task:
            mock_add_task.side_effect = Exception("Service error occurred")
            
            # Make request
            response = self.client.post('/projects/1/task/10')
            
            # Assertions
            self.assertEqual(response.status_code, 500)
            data = json.loads(response.data)
            self.assertEqual(data["status"], 500)
            self.assertIn("Service error occurred", data["error"])

    def test_add_task_to_project_with_multiple_subtasks(self):
        """Test adding a task with multiple subtasks to a project."""
        # Mock the service method
        with patch.object(service, 'add_task_to_project') as mock_add_task:
            mock_add_task.return_value = {
                "message": "Task 10 and 5 subtasks successfully added to project 1",
                "data": {
                    "project": {
                        "id": 1,
                        "owner_id": 100,
                        "proj_name": "Project",
                        "collaborators": [100, 101, 102, 103],
                        "tasks": [10, 11, 12, 13, 14, 15],
                        "created_at": "2025-01-01T00:00:00+00:00"
                    },
                    "main_task_id": 10,
                    "subtask_ids": [11, 12, 13, 14, 15],
                    "all_task_ids": [10, 11, 12, 13, 14, 15],
                    "added_collaborators": [101, 102, 103]
                },
                "status": 200
            }
            
            # Make request
            response = self.client.post('/projects/1/task/10')
            
            # Assertions
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data["status"], 200)
            self.assertEqual(len(data["data"]["subtask_ids"]), 5)
            self.assertEqual(len(data["data"]["all_task_ids"]), 6)
            self.assertEqual(len(data["data"]["added_collaborators"]), 3)


if __name__ == "__main__":
    unittest.main()
