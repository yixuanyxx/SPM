import unittest
import json
import sys
import os

# Add parent directory to path to find modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.project_service import ProjectService
from models.project import Project
from repo.supa_project_repo import SupabaseProjectRepo

# Import the controller and service
from controllers.project_controller import project_bp, service


class TestProjectControllerIntegration(unittest.TestCase):
    """Integration tests for project controller endpoints."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Set up environment variables for Supabase connection
        # You'll need to set these in your environment or .env file
        if not os.getenv("SUPABASE_URL"):
            os.environ["SUPABASE_URL"] = "your_supabase_url_here"
        if not os.getenv("SUPABASE_SERVICE_KEY"):
            os.environ["SUPABASE_SERVICE_KEY"] = "your_supabase_service_key_here"
        
        # Test Supabase connection
        try:
            self.repo = SupabaseProjectRepo()
            print(f"[SUCCESS] Supabase connection successful")
        except Exception as e:
            print(f"[ERROR] Supabase connection failed: {e}")
            raise
        
        # Replace the service's repository with our real repository
        service.repo = self.repo

        # Create a test Flask app
        from flask import Flask
        self.app = Flask(__name__)
        self.app.register_blueprint(project_bp)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Clean up any existing test data
        self.cleanup_test_data()

    def tearDown(self):
        """Clean up after each test method."""
        self.cleanup_test_data()

    def cleanup_test_data(self):
        """Clean up test data from the database."""
        try:
            # Delete test projects for common test owner IDs
            test_owners = [297]  # Common test owner IDs (removed duplicate)
            deleted_count = 0
            deleted_project_ids = set()  # Track deleted projects to avoid duplicates
            
            for owner_id in test_owners:
                # Get projects for this owner
                projects = self.repo.find_by_owner(owner_id)
                print(f"Found {len(projects)} projects for owner {owner_id}")
                
                # Delete projects
                for project in projects:
                    project_id = project['id']
                    if project_id in deleted_project_ids:
                        continue  # Skip if already deleted
                    
                    try:
                        # Delete the project (this will cascade delete related data)
                        result = self.repo.client.table("project").delete().eq("id", project_id).execute()
                        if result.data:
                            deleted_count += 1
                            deleted_project_ids.add(project_id)
                            print(f"SUCCESS: Deleted project {project_id} for owner {owner_id}")
                        else:
                            print(f"FAILED: Failed to delete project {project_id} for owner {owner_id}")
                    except Exception as e:
                        print(f"ERROR: Error deleting project {project_id}: {e}")
            
            # Also clean up any projects that might have been created with other owner IDs
            # by looking for projects with test names
            test_project_names = [
                "Test Project", "Complete Project", "Project No Collabs", "Project 1", "Project 2",
                "Solo Project", "Minimal Project", "Old Name", "Updated Project Name", "New Name Only",
                "Project", "My Project 1", "My Project 2", "Single Owner Project"
            ]
            
            for project_name in test_project_names:
                try:
                    # Find projects with test names
                    result = self.repo.client.table("project").select("id").ilike("proj_name", f"%{project_name}%").execute()
                    if result.data:
                        for project in result.data:
                            project_id = project['id']
                            if project_id in deleted_project_ids:
                                continue
                            
                            try:
                                delete_result = self.repo.client.table("project").delete().eq("id", project_id).execute()
                                if delete_result.data:
                                    deleted_count += 1
                                    deleted_project_ids.add(project_id)
                                    print(f"SUCCESS: Deleted test project {project_id} with name containing '{project_name}'")
                            except Exception as e:
                                print(f"ERROR: Error deleting test project {project_id}: {e}")
                except Exception as e:
                    print(f"Warning: Could not search for test projects with name '{project_name}': {e}")
            
            if deleted_count > 0:
                print(f"Cleanup completed: {deleted_count} projects deleted")
            else:
                print("No projects found to clean up")
                
        except Exception as e:
            print(f"Warning: Could not clean up test data: {e}")
            import traceback
            traceback.print_exc()

    def cleanup_specific_project(self, project_id: int):
        """Clean up a specific project by ID."""
        try:
            result = self.repo.client.table("project").delete().eq("id", project_id).execute()
            if result.data:
                print(f"SUCCESS: Deleted specific project {project_id}")
                return True
            else:
                print(f"FAILED: Could not delete specific project {project_id}")
                return False
        except Exception as e:
            print(f"ERROR: Error deleting specific project {project_id}: {e}")
            return False

    def cleanup_projects_by_owner(self, owner_id: int):
        """Clean up all projects for a specific owner."""
        try:
            projects = self.repo.find_by_owner(owner_id)
            deleted_count = 0
            
            for project in projects:
                project_id = project['id']
                if self.cleanup_specific_project(project_id):
                    deleted_count += 1
            
            print(f"Cleaned up {deleted_count} projects for owner {owner_id}")
            return deleted_count
        except Exception as e:
            print(f"ERROR: Error cleaning up projects for owner {owner_id}: {e}")
            return 0

    # ==================== create_project Tests ====================
    
    def test_create_project_success(self):
        """Test successful project creation with all required fields."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Make request with required fields
        response = self.client.post('/projects/create', json={
            "owner_id": 297,
            "proj_name": "Test Project"
        })
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 201)
        self.assertIn("Project created! Project ID:", data["message"])
        self.assertIn("data", data)
        self.assertEqual(data["data"]["proj_name"], "Test Project")
        self.assertEqual(data["data"]["owner_id"], 297)
        
        # Clean up the created project
        project_id = data["data"]["id"]
        self.cleanup_specific_project(project_id)

    def test_create_project_with_all_fields(self):
        """Test project creation with all optional fields."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Make request with all fields
        response = self.client.post('/projects/create', json={
            "owner_id": 297,
            "proj_name": "Complete Project",
            "collaborators": [297, 102, 103],
            "tasks": [10, 11, 12]
        })
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 201)
        self.assertEqual(data["data"]["collaborators"], [297, 102, 103])
        self.assertEqual(data["data"]["tasks"], [10, 11, 12])
        
        # Clean up the created project
        project_id = data["data"]["id"]
        self.cleanup_specific_project(project_id)

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
            "owner_id": 297
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

    def test_create_project_with_empty_collaborators(self):
        """Test project creation with empty collaborators list."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Make request
        response = self.client.post('/projects/create', json={
            "owner_id": 297,
            "proj_name": "Project No Collabs",
            "collaborators": []
        })
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 201)
        
        # Clean up the created project
        project_id = data["data"]["id"]
        self.cleanup_specific_project(project_id)

    # ==================== get_projects_by_user Tests ====================
    
    def test_get_projects_by_user_success(self):
        """Test successfully retrieving projects for a user."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create some projects for the user
        create_response1 = self.client.post('/projects/create', json={
            "owner_id": 297,
            "proj_name": "Project 1",
            "collaborators": [297],
            "tasks": [10, 11]
        })
        self.assertEqual(create_response1.status_code, 201)
        project1_id = json.loads(create_response1.data)["data"]["id"]
        
        create_response2 = self.client.post('/projects/create', json={
            "owner_id": 538,
            "proj_name": "Project 2",
            "collaborators": [297, 102]
        })
        self.assertEqual(create_response2.status_code, 201)
        project2_id = json.loads(create_response2.data)["data"]["id"]
        
        # Make request
        response = self.client.get('/projects/user/297')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 200)
        self.assertIn("data", data)
        self.assertGreaterEqual(len(data["data"]), 2)
        
        # Clean up the created projects
        self.cleanup_specific_project(project1_id)
        self.cleanup_specific_project(project2_id)

    def test_get_projects_by_user_not_found(self):
        """Test get projects by user when no projects found."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Make request for user with no projects
        response = self.client.get('/projects/user/999')
        
        # Assertions
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 404)
        self.assertIn("No projects found", data["message"])

    # ==================== get_project_by_id Tests ====================
    
    def test_get_project_by_id_success(self):
        """Test successfully retrieving a project by ID."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create a project
        create_response = self.client.post('/projects/create', json={
            "owner_id": 297,
            "proj_name": "Test Project",
            "collaborators": [297, 297, 102],
            "tasks": [10, 11]
        })
        self.assertEqual(create_response.status_code, 201)
        create_data = json.loads(create_response.data)
        project_id = create_data["data"]["id"]
        
        # Make request
        response = self.client.get(f'/projects/{project_id}')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 200)
        self.assertIn("data", data)
        self.assertEqual(data["data"]["id"], project_id)
        self.assertEqual(data["data"]["proj_name"], "Test Project")
        
        # Clean up the created project
        self.cleanup_specific_project(project_id)

    def test_get_project_by_id_not_found(self):
        """Test get project by ID when project doesn't exist."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Make request for non-existent project
        response = self.client.get('/projects/999')
        
        # Assertions
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 404)
        self.assertIn("not found", data["message"])

    def test_get_project_by_id_with_minimal_data(self):
        """Test retrieving project with minimal data (no collaborators/tasks)."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create a project with minimal data
        create_response = self.client.post('/projects/create', json={
            "owner_id": 297,
            "proj_name": "Minimal Project"
        })
        self.assertEqual(create_response.status_code, 201)
        create_data = json.loads(create_response.data)
        project_id = create_data["data"]["id"]
        
        # Make request
        response = self.client.get(f'/projects/{project_id}')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 200)
        self.assertIsNone(data["data"]["collaborators"])
        self.assertIsNone(data["data"]["tasks"])
        
        # Clean up the created project
        self.cleanup_specific_project(project_id)

#     # ==================== update_project Tests ====================
    
    def test_update_project_success(self):
        """Test successful project update with multiple fields."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create a project
        create_response = self.client.post('/projects/create', json={
            "owner_id": 297,
            "proj_name": "Old Name",
            "collaborators": [297],
            "tasks": [10]
        })
        self.assertEqual(create_response.status_code, 201)
        create_data = json.loads(create_response.data)
        project_id = create_data["data"]["id"]
        
        # Make update request
        response = self.client.put('/projects/update', json={
            "project_id": project_id,
            "proj_name": "Updated Project Name",
            "collaborators": [297, 297, 102],
            "tasks": [10, 11, 12]
        })
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 200)
        self.assertIn("updated successfully", data["message"])
        self.assertEqual(data["data"]["proj_name"], "Updated Project Name")
        self.assertEqual(data["data"]["collaborators"], [297, 297, 102])

    def test_update_project_single_field(self):
        """Test updating a single field."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create a project
        create_response = self.client.post('/projects/create', json={
            "owner_id": 297,
            "proj_name": "Old Name",
            "collaborators": [297]
        })
        self.assertEqual(create_response.status_code, 201)
        create_data = json.loads(create_response.data)
        project_id = create_data["data"]["id"]
        
        # Update only proj_name
        response = self.client.patch('/projects/update', json={
            "project_id": project_id,
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
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Make request for non-existent project
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
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create a project
        create_response = self.client.post('/projects/create', json={
            "owner_id": 297,
            "proj_name": "Project"
        })
        self.assertEqual(create_response.status_code, 201)
        create_data = json.loads(create_response.data)
        project_id = create_data["data"]["id"]
        
        response = self.client.put('/projects/update', json={
            "project_id": project_id
        })
        
        # Assertions
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 400)
        self.assertIn("No fields to update", data["message"])

    def test_update_project_with_collaborators(self):
        """Test updating collaborators list."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create a project
        create_response = self.client.post('/projects/create', json={
            "owner_id": 297,
            "proj_name": "Project",
            "collaborators": [297]
        })
        self.assertEqual(create_response.status_code, 201)
        create_data = json.loads(create_response.data)
        project_id = create_data["data"]["id"]
        
        # Update collaborators
        response = self.client.put('/projects/update', json={
            "project_id": project_id,
            "collaborators": [297, 297, 102, 103]
        })
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 200)
        self.assertEqual(data["data"]["collaborators"], [297, 297, 102, 103])

    def test_update_project_with_tasks(self):
        """Test updating tasks list."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create a project
        create_response = self.client.post('/projects/create', json={
            "owner_id": 297,
            "proj_name": "Project",
            "tasks": [10]
        })
        self.assertEqual(create_response.status_code, 201)
        create_data = json.loads(create_response.data)
        project_id = create_data["data"]["id"]
        
        # Update tasks
        response = self.client.patch('/projects/update', json={
            "project_id": project_id,
            "tasks": [10, 11, 12, 13, 14]
        })
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 200)
        self.assertEqual(data["data"]["tasks"], [10, 11, 12, 13, 14])

    def test_update_project_change_owner(self):
        """Test updating project owner."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create a project
        create_response = self.client.post('/projects/create', json={
            "owner_id": 297,
            "proj_name": "Project",
            "collaborators": [297]
        })
        self.assertEqual(create_response.status_code, 201)
        create_data = json.loads(create_response.data)
        project_id = create_data["data"]["id"]
        
        # Update owner_id
        response = self.client.put('/projects/update', json={
            "project_id": project_id,
            "owner_id": 538
        })
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 200)
        self.assertEqual(data["data"]["owner_id"], 538)

#     # ==================== get_projects_by_owner Tests ====================
    
    def test_get_projects_by_owner_success(self):
        """Test successfully retrieving projects by owner."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create some projects for the owner
        create_response1 = self.client.post('/projects/create', json={
            "owner_id": 297,
            "proj_name": "My Project 1",
            "collaborators": [297],
            "tasks": [10]
        })
        self.assertEqual(create_response1.status_code, 201)
        
        create_response2 = self.client.post('/projects/create', json={
            "owner_id": 297,
            "proj_name": "My Project 2"
        })
        self.assertEqual(create_response2.status_code, 201)
        
        # Make request
        response = self.client.get('/projects/owner/297')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 200)
        self.assertIn("data", data)
        self.assertEqual(len(data["data"]), 2)
        self.assertEqual(data["data"][0]["owner_id"], 297)
        self.assertEqual(data["data"][1]["owner_id"], 297)

    def test_get_projects_by_owner_single_project(self):
        """Test retrieving single project by owner."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create a project for the owner
        create_response = self.client.post('/projects/create', json={
            "owner_id": 297,
            "proj_name": "Single Owner Project"
        })
        self.assertEqual(create_response.status_code, 201)
        
        # Make request
        response = self.client.get('/projects/owner/297')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 200)
        self.assertEqual(len(data["data"]), 1)
        self.assertEqual(data["data"][0]["proj_name"], "Single Owner Project")

    def test_get_projects_by_owner_not_found(self):
        """Test get projects by owner when no projects found."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Make request for owner with no projects
        response = self.client.get('/projects/owner/999')
        
        # Assertions
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 404)
        self.assertIn("No projects found", data["message"])

#     # ==================== add_task_to_project Tests ====================
    
    # def test_add_task_to_project_success(self):
    #     """Test successfully adding a task to a project."""
    #     # Clean up any existing test data first
    #     self.cleanup_test_data()
        
    #     # First, create a project
    #     create_response = self.client.post('/projects/create', json={
    #         "owner_id": 297,
    #         "proj_name": "Test Project"
    #     })
    #     self.assertEqual(create_response.status_code, 201)
    #     create_data = json.loads(create_response.data)
    #     project_id = create_data["data"]["id"]
        
    #     # Note: This test requires the task microservice to be running
    #     # and a task with ID 10 to exist in the task database
    #     # For now, we'll skip this test as it requires external dependencies
    #     self.skipTest("Requires task microservice and existing task data")

    # def test_add_task_to_project_no_subtasks(self):
    #     """Test adding a task without subtasks to a project."""
    #     # Clean up any existing test data first
    #     self.cleanup_test_data()
        
    #     # First, create a project
    #     create_response = self.client.post('/projects/create', json={
    #         "owner_id": 297,
    #         "proj_name": "Test Project"
    #     })
    #     self.assertEqual(create_response.status_code, 201)
    #     create_data = json.loads(create_response.data)
    #     project_id = create_data["data"]["id"]
        
    #     # Note: This test requires the task microservice to be running
    #     # and a task with ID 10 to exist in the task database
    #     # For now, we'll skip this test as it requires external dependencies
    #     self.skipTest("Requires task microservice and existing task data")

    # def test_add_task_to_project_task_already_exists(self):
    #     """Test adding a task that already exists in the project."""
    #     # Clean up any existing test data first
    #     self.cleanup_test_data()
        
    #     # First, create a project
    #     create_response = self.client.post('/projects/create', json={
    #         "owner_id": 297,
    #         "proj_name": "Test Project"
    #     })
    #     self.assertEqual(create_response.status_code, 201)
    #     create_data = json.loads(create_response.data)
    #     project_id = create_data["data"]["id"]
        
    #     # Note: This test requires the task microservice to be running
    #     # and a task with ID 10 to exist in the task database
    #     # For now, we'll skip this test as it requires external dependencies
    #     self.skipTest("Requires task microservice and existing task data")

    # def test_add_task_to_project_project_not_found(self):
    #     """Test adding a task when project doesn't exist."""
    #     # Clean up any existing test data first
    #     self.cleanup_test_data()
        
    #     # Make request for non-existent project
    #     response = self.client.post('/projects/999/task/10')
        
    #     # Assertions
    #     self.assertEqual(response.status_code, 404)
    #     data = json.loads(response.data)
    #     self.assertEqual(data["status"], 404)

    # def test_add_task_to_project_task_not_found(self):
    #     """Test adding a task that doesn't exist."""
    #     # Clean up any existing test data first
    #     self.cleanup_test_data()
        
    #     # First, create a project
    #     create_response = self.client.post('/projects/create', json={
    #         "owner_id": 297,
    #         "proj_name": "Test Project"
    #     })
    #     self.assertEqual(create_response.status_code, 201)
    #     create_data = json.loads(create_response.data)
    #     project_id = create_data["data"]["id"]
        
    #     # Make request for non-existent task
    #     response = self.client.post(f'/projects/{project_id}/task/999')
        
    #     # Assertions
    #     self.assertEqual(response.status_code, 404)
    #     data = json.loads(response.data)
    #     self.assertEqual(data["status"], 404)

    # def test_add_task_to_project_service_error(self):
    #     """Test add task to project with service error."""
    #     # This test is not applicable with real database connection
    #     # as we can't easily simulate service errors in integration tests
    #     # Skip this test or modify to test actual error scenarios
    #     self.skipTest("Service error testing not applicable with real database")

    # def test_add_task_to_project_with_multiple_subtasks(self):
    #     """Test adding a task with multiple subtasks to a project."""
    #     # Clean up any existing test data first
    #     self.cleanup_test_data()
        
    #     # First, create a project
    #     create_response = self.client.post('/projects/create', json={
    #         "owner_id": 297,
    #         "proj_name": "Test Project"
    #     })
    #     self.assertEqual(create_response.status_code, 201)
    #     create_data = json.loads(create_response.data)
    #     project_id = create_data["data"]["id"]
        
    #     # Note: This test requires the task microservice to be running
    #     # and a task with ID 10 to exist in the task database
    #     # For now, we'll skip this test as it requires external dependencies
    #     self.skipTest("Requires task microservice and existing task data")


if __name__ == "__main__":
    unittest.main()
