import unittest
import json
import sys
import os
from io import BytesIO

# Add parent directory to path to find modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.task_service import TaskService
from models.task import Task
from repo.supa_task_repo import SupabaseTaskRepo

# Import the controller and service
from controllers.task_controller import task_bp, service


class TestTaskControllerIntegration(unittest.TestCase):
    """Integration tests for task controller endpoints."""

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
            self.repo = SupabaseTaskRepo()
            print(f"[SUCCESS] Supabase connection successful")
        except Exception as e:
            print(f"[ERROR] Supabase connection failed: {e}")
            raise
        
        # Replace the service's repository with our real repository
        service.repo = self.repo

        # Create a test Flask app
        from flask import Flask
        self.app = Flask(__name__)
        self.app.register_blueprint(task_bp)
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
            # Delete test tasks for common test owner IDs
            test_owners = [297, 102, 103, 999]  # Common test owner IDs
            deleted_count = 0
            
            for owner_id in test_owners:
                # Get tasks for this owner
                tasks = self.repo.find_by_owner(owner_id)
                print(f"Found {len(tasks)} tasks for owner {owner_id}")
                
                # Delete subtasks first, then parent tasks
                subtasks = [task for task in tasks if task.get('type') == 'subtask']
                parent_tasks = [task for task in tasks if task.get('type') != 'subtask']
                
                # Delete subtasks first
                for task in subtasks:
                    task_id = task['id']
                    if self.repo.delete_task(task_id):
                        deleted_count += 1
                        print(f"[SUCCESS] Deleted subtask {task_id} for owner {owner_id}")
                    else:
                        print(f"[ERROR] Failed to delete subtask {task_id} for owner {owner_id}")
                
                # Then delete parent tasks
                for task in parent_tasks:
                    task_id = task['id']
                    if self.repo.delete_task(task_id):
                        deleted_count += 1
                        print(f"[SUCCESS] Deleted parent task {task_id} for owner {owner_id}")
                    else:
                        print(f"[ERROR] Failed to delete parent task {task_id} for owner {owner_id}")
            
            if deleted_count > 0:
                print(f"Cleanup completed: {deleted_count} tasks deleted")
            else:
                print("No tasks found to clean up")
                
        except Exception as e:
            print(f"Warning: Could not clean up test data: {e}")
            import traceback
            traceback.print_exc()

    # ==================== manager_create_task Tests ====================
    
    def test_manager_create_task_success(self):
        """Test successful task creation with all required fields."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Make request with required fields
        response = self.client.post('/tasks/manager-task/create', json={
            "owner_id": 297,
            "task_name": "Test Task",
            "description": "Test Description"
        })
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 201)
        # self.assertIn("Task created! Task ID:", data["Message"])
        self.assertIn("data", data)
        self.assertEqual(data["data"]["task_name"], "Test Task")
        self.assertEqual(data["data"]["owner_id"], 297)
        self.assertEqual(data["data"]["description"], "Test Description")

    def test_manager_create_task_with_all_fields(self):
        """Test task creation with all optional fields."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Make request with all fields
        response = self.client.post('/tasks/manager-task/create', json={
            "owner_id": 297,
            "task_name": "Complete Task",
            "description": "Full task description",
            "status": "Unassigned",
            "type": "parent",
            "collaborators": [102, 103],
            "project_id": 10,
            "priority": 3,
            "due_date": "2025-12-31"
        })
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 201)
        self.assertEqual(data["data"]["priority"], 3)
        self.assertEqual(data["data"]["collaborators"], [102, 103])
        self.assertEqual(data["data"]["status"], "Unassigned")
        self.assertEqual(data["data"]["project_id"], 10)

    def test_manager_create_task_duplicate_name(self):
        """Test task creation when task name already exists for owner."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create a task
        first_response = self.client.post('/tasks/manager-task/create', json={
            "owner_id": 297,
            "task_name": "Existing Task",
            "description": "First task"
        })
        self.assertEqual(first_response.status_code, 201)
        
        # Try to create another task with the same name for the same owner
        response = self.client.post('/tasks/manager-task/create', json={
            "owner_id": 297,
            "task_name": "Existing Task",
            "description": "Test Description"
        })
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertIn("already exists", data["Message"])

    def test_manager_create_task_missing_owner_id(self):
        """Test task creation fails when owner_id is missing."""
        response = self.client.post('/tasks/manager-task/create', json={
            "task_name": "Test Task",
            "description": "Test Description"
            # owner_id is missing
        })
        
        # Assertions
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 400)
        self.assertIn("Missing required fields", data["Message"])

    def test_manager_create_task_missing_task_name(self):
        """Test task creation fails when task_name is missing."""
        response = self.client.post('/tasks/manager-task/create', json={
            "owner_id": 297,
            "description": "Test Description"
            # task_name is missing
        })
        
        # Assertions
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 400)
        self.assertIn("Missing required fields", data["Message"])

    def test_manager_create_task_missing_description(self):
        """Test task creation fails when description is missing."""
        response = self.client.post('/tasks/manager-task/create', json={
            "owner_id": 297,
            "task_name": "Test Task"
            # description is missing
        })
        
        # Assertions
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 400)
        self.assertIn("Missing required fields", data["Message"])

    def test_manager_create_task_invalid_task_type(self):
        """Test task creation fails with invalid task type."""
        response = self.client.post('/tasks/manager-task/create', json={
            "owner_id": 297,
            "task_name": "Test Task",
            "description": "Test Description",
            "type": "invalid_type"  # Invalid type
        })
        
        # Assertions
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 400)
        self.assertIn("Invalid task type", data["Message"])



    # ==================== staff_create_task Tests ====================
    
    def test_staff_create_task_success(self):
        """Test staff creates task - owner_id automatically added to collaborators."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Make request without collaborators
        response = self.client.post('/tasks/staff-task/create', json={
            "owner_id": 297,
            "task_name": "Staff Task",
            "description": "Task by staff"
        })
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 201)
        self.assertEqual(data["data"]["collaborators"], [297])
        self.assertEqual(data["data"]["owner_id"], 297)

    def test_staff_create_task_owner_added_to_collaborators(self):
        """Test staff task creation adds owner to existing collaborators."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Make request with collaborators (owner not included)
        response = self.client.post('/tasks/staff-task/create', json={
            "owner_id": 297,
            "task_name": "Staff Team Task",
            "description": "Task with team",
            "collaborators": [102, 103]
        })
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 201)
        # Verify owner was added to collaborators
        self.assertIn(297, data["data"]["collaborators"])
        self.assertIn(297, data["data"]["collaborators"])
        self.assertIn(103, data["data"]["collaborators"])

    def test_staff_create_task_owner_already_in_collaborators(self):
        """Test staff task creation when owner already in collaborators list."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Make request with owner already in collaborators
        response = self.client.post('/tasks/staff-task/create', json={
            "owner_id": 297,
            "task_name": "Staff Self Task",
            "description": "Owner already in list",
            "collaborators": [102, 103]
        })
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 201)
        # Verify owner appears only once
        self.assertEqual(data["data"]["collaborators"].count(297), 1)
        self.assertIn(297, data["data"]["collaborators"])

    def test_staff_create_task_duplicate_name(self):
        """Test staff task creation with duplicate name."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create a task
        first_response = self.client.post('/tasks/staff-task/create', json={
            "owner_id": 297,
            "task_name": "Existing Staff Task",
            "description": "First task"
        })
        self.assertEqual(first_response.status_code, 201)
        
        # Try to create another task with the same name for the same owner
        response = self.client.post('/tasks/staff-task/create', json={
            "owner_id": 297,
            "task_name": "Existing Staff Task",
            "description": "Test Description"
        })
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertIn("already exists", data["Message"])

    def test_staff_create_task_missing_fields(self):
        """Test staff task creation with missing required fields."""
        response = self.client.post('/tasks/staff-task/create', json={
            "task_name": "Test Task"
            # owner_id and description missing
        })
        
        # Assertions
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 400)
        self.assertIn("Missing required fields", data["Message"])

    # def test_staff_create_task_with_attachment(self):
    #     """Test staff task creation with file attachment."""
    #     # Clean up any existing test data first
    #     self.cleanup_test_data()
        
    #     # Create mock file
    #     mock_file = (BytesIO(b"PDF content"), "staff-doc.pdf")
        
    #     # Make request with file
    #     response = self.client.post('/tasks/staff-task/create',
    #         data={
    #             "owner_id": "297",
    #             "task_name": "Staff Task with File",
    #             "description": "Task with attachment",
    #             "attachment": mock_file
    #         },
    #         content_type='multipart/form-data'
    #     )
        
    #     # Assertions
    #     self.assertEqual(response.status_code, 201)
    #     data = json.loads(response.data)
    #     self.assertEqual(data["Code"], 201)
    #     self.assertIn("data", data)
    #     self.assertEqual(data["data"]["task_name"], "Staff Task with File")
    #     # Check that attachment was uploaded (URL should be present)
    #     self.assertIsNotNone(data["data"].get("attachments"))

    # ==================== manager_create_subtask Tests ====================
    
    def test_manager_create_subtask_success(self):
        """Test successful subtask creation by manager."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create a parent task
        parent_response = self.client.post('/tasks/manager-task/create', json={
            "owner_id": 297,
            "task_name": "Parent Task",
            "description": "Parent task for subtask"
        })
        self.assertEqual(parent_response.status_code, 201)
        parent_data = json.loads(parent_response.data)
        parent_task_id = parent_data["data"]["id"]
        
        # Now create a subtask
        response = self.client.post('/tasks/manager-subtask/create', json={
            "owner_id": 297,
            "task_name": "Subtask 1",
            "description": "A subtask",
            "parent_task": parent_task_id
        })
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 201)
        self.assertEqual(data["data"]["type"], "subtask")
        self.assertEqual(data["data"]["parent_task"], parent_task_id)

    def test_manager_create_subtask_missing_parent_task(self):
        """Test subtask creation fails when parent_task is missing."""
        response = self.client.post('/tasks/manager-subtask/create', json={
            "owner_id": 297,
            "task_name": "Subtask",
            "description": "Missing parent"
            # parent_task is missing
        })
        
        # Assertions
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 400)
        self.assertIn("Missing required fields", data["Message"])

    def test_manager_create_subtask_parent_not_found(self):
        """Test subtask creation fails when parent task doesn't exist."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Make request with non-existent parent task
        response = self.client.post('/tasks/manager-subtask/create', json={
            "owner_id": 297,
            "task_name": "Subtask",
            "description": "Parent doesn't exist",
            "parent_task": 999
        })
        
        # Assertions
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("Parent task with ID 999 not found", data["Message"])

    def test_manager_create_subtask_duplicate_name(self):
        """Test subtask creation with duplicate name."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create a parent task
        parent_response = self.client.post('/tasks/manager-task/create', json={
            "owner_id": 297,
            "task_name": "Parent Task",
            "description": "Parent task for subtask"
        })
        self.assertEqual(parent_response.status_code, 201)
        parent_data = json.loads(parent_response.data)
        parent_task_id = parent_data["data"]["id"]
        
        # Create first subtask
        first_response = self.client.post('/tasks/manager-subtask/create', json={
            "owner_id": 297,
            "task_name": "Existing Subtask",
            "description": "First subtask",
            "parent_task": parent_task_id
        })
        self.assertEqual(first_response.status_code, 201)
        
        # Try to create another subtask with the same name for the same owner
        response = self.client.post('/tasks/manager-subtask/create', json={
            "owner_id": 297,
            "task_name": "Existing Subtask",
            "description": "Test",
            "parent_task": parent_task_id
        })
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertIn("already exists", data["Message"])

    def test_manager_create_subtask_with_collaborators(self):
        """Test subtask creation with collaborators."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create a parent task
        parent_response = self.client.post('/tasks/manager-task/create', json={
            "owner_id": 297,
            "task_name": "Parent Task",
            "description": "Parent task for subtask"
        })
        self.assertEqual(parent_response.status_code, 201)
        parent_data = json.loads(parent_response.data)
        parent_task_id = parent_data["data"]["id"]
        
        # Make request with collaborators
        response = self.client.post('/tasks/manager-subtask/create', json={
            "owner_id": 297,
            "task_name": "Team Subtask",
            "description": "Subtask with team",
            "parent_task": parent_task_id,
            "collaborators": [102, 103]
        })
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 201)
        self.assertEqual(data["data"]["collaborators"], [102, 103])
        self.assertEqual(data["data"]["type"], "subtask")
        self.assertEqual(data["data"]["parent_task"], parent_task_id)


    # ==================== staff_create_subtask Tests ====================
    
    def test_staff_create_subtask_success(self):
        """Test staff creates subtask - owner automatically added to collaborators."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create a parent task
        parent_response = self.client.post('/tasks/manager-task/create', json={
            "owner_id": 297,
            "task_name": "Parent Task",
            "description": "Parent task for subtask"
        })
        self.assertEqual(parent_response.status_code, 201)
        parent_data = json.loads(parent_response.data)
        parent_task_id = parent_data["data"]["id"]
        
        # Make request without collaborators
        response = self.client.post('/tasks/staff-subtask/create', json={
            "owner_id": 297,
            "task_name": "Staff Subtask",
            "description": "Subtask by staff",
            "parent_task": parent_task_id
        })
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 201)

        self.assertEqual(data["data"]["collaborators"], [297])
        self.assertEqual(data["data"]["type"], "subtask")
        self.assertEqual(data["data"]["parent_task"], parent_task_id)

    def test_staff_create_subtask_owner_added_to_collaborators(self):
        """Test staff subtask adds owner to existing collaborators."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create a parent task
        parent_response = self.client.post('/tasks/manager-task/create', json={
            "owner_id": 297,
            "task_name": "Parent Task",
            "description": "Parent task for subtask"
        })
        self.assertEqual(parent_response.status_code, 201)
        parent_data = json.loads(parent_response.data)
        parent_task_id = parent_data["data"]["id"]
        
        # Make request with collaborators (owner not included)
        response = self.client.post('/tasks/staff-subtask/create', json={
            "owner_id": 297,
            "task_name": "Staff Team Subtask",
            "description": "Subtask with team",
            "parent_task": parent_task_id,
            "collaborators": [102, 103]
        })
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 201)
        self.assertIn(297, data["data"]["collaborators"])
        self.assertIn(297, data["data"]["collaborators"])
        self.assertIn(103, data["data"]["collaborators"])
        self.assertEqual(data["data"]["type"], "subtask")

    def test_staff_create_subtask_missing_parent_task(self):
        """Test staff subtask creation fails when parent_task is missing."""
        response = self.client.post('/tasks/staff-subtask/create', json={
            "owner_id": 297,
            "task_name": "Subtask",
            "description": "Missing parent"
            # parent_task is missing
        })
        
        # Assertions
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 400)
        self.assertIn("Missing required fields", data["Message"])

    def test_staff_create_subtask_parent_not_found(self):
        """Test staff subtask creation fails when parent doesn't exist."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Make request with non-existent parent task
        response = self.client.post('/tasks/staff-subtask/create', json={
            "owner_id": 297,
            "task_name": "Subtask",
            "description": "Parent doesn't exist",
            "parent_task": 999
        })
        
        # Assertions
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 400)
        self.assertIn("Parent task with ID 999 not found", data["Message"])

    def test_staff_create_subtask_duplicate_name(self):
        """Test staff subtask creation with duplicate name."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create a parent task
        parent_response = self.client.post('/tasks/manager-task/create', json={
            "owner_id": 297,
            "task_name": "Parent Task",
            "description": "Parent task for subtask"
        })
        self.assertEqual(parent_response.status_code, 201)
        parent_data = json.loads(parent_response.data)
        parent_task_id = parent_data["data"]["id"]
        
        # Create first subtask
        first_response = self.client.post('/tasks/staff-subtask/create', json={
            "owner_id": 297,
            "task_name": "Existing Staff Subtask",
            "description": "First subtask",
            "parent_task": parent_task_id
        })
        self.assertEqual(first_response.status_code, 201)
        
        # Try to create another subtask with the same name for the same owner
        response = self.client.post('/tasks/staff-subtask/create', json={
            "owner_id": 297,
            "task_name": "Existing Staff Subtask",
            "description": "Test",
            "parent_task": parent_task_id
        })
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertIn("already exists", data["Message"])

    def test_staff_create_subtask_missing_required_fields(self):
        """Test staff subtask creation with missing owner_id."""
        response = self.client.post('/tasks/staff-subtask/create', json={
            "task_name": "Subtask",
            "description": "Missing owner",
            "parent_task": 1
            # owner_id is missing
        })
        
        # Assertions
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 400)
        self.assertIn("Missing required fields", data["Message"])

    # ==================== update_task Tests ====================
    
    def test_update_task_success(self):
        """Test successful task update with multiple fields."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create a task
        create_response = self.client.post('/tasks/manager-task/create', json={
            "owner_id": 297,
            "task_name": "Old Name",
            "description": "Old description"
        })
        self.assertEqual(create_response.status_code, 201)
        create_data = json.loads(create_response.data)
        task_id = create_data["data"]["id"]
        
        # Make update request
        response = self.client.put('/tasks/update', json={
            "task_id": task_id,
            "task_name": "Updated Name",
            "description": "Updated description",
            "status": "Ongoing"
        })
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertIn("updated successfully", data["Message"])
        self.assertEqual(data["data"]["task_name"], "Updated Name")
        self.assertEqual(data["data"]["status"], "Ongoing")

    def test_update_task_single_field(self):
        """Test updating a single field."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create a task
        create_response = self.client.post('/tasks/manager-task/create', json={
            "owner_id": 297,
            "task_name": "Task Name",
            "description": "Description"
        })
        self.assertEqual(create_response.status_code, 201)
        create_data = json.loads(create_response.data)
        task_id = create_data["data"]["id"]
        
        # Update only status
        response = self.client.patch('/tasks/update', json={
            "task_id": task_id,
            "status": "Ongoing"
        })
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertEqual(data["data"]["status"], "Ongoing")

    def test_update_task_missing_task_id(self):
        """Test update fails when task_id is missing."""
        response = self.client.put('/tasks/update', json={
            "task_name": "New Name"
            # task_id is missing
        })
        
        # Assertions
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 400)
        self.assertIn("task_id", data["Message"].lower())

    def test_update_task_not_found(self):
        """Test update fails when task doesn't exist."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Make request with non-existent task
        response = self.client.put('/tasks/update', json={
            "task_id": 999,
            "task_name": "New Name"
        })
        
        # Assertions
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 404)
        self.assertIn("not found", data["Message"])

    def test_update_task_no_fields_to_update(self):
        """Test update with only task_id (no fields to update)."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create a task
        create_response = self.client.post('/tasks/manager-task/create', json={
            "owner_id": 297,
            "task_name": "Task Name",
            "description": "Description"
        })
        
        # Debug: Print response details if creation fails
        if create_response.status_code != 201:
            print(f"[ERROR] Task creation failed with status {create_response.status_code}")
            print(f"Response data: {create_response.data}")
            try:
                error_data = json.loads(create_response.data)
                print(f"Error message: {error_data.get('Message', 'No message')}")
            except:
                print(f"Raw response: {create_response.data}")
        
        self.assertEqual(create_response.status_code, 201)
        create_data = json.loads(create_response.data)
        task_id = create_data["data"]["id"]
        
        # Make request with only task_id
        response = self.client.put('/tasks/update', json={
            "task_id": task_id
        })
        
        # Assertions
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 400)
        self.assertIn("No fields to update", data["Message"])

    def test_update_task_with_collaborators(self):
        """Test updating collaborators list."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create a task
        create_response = self.client.post('/tasks/manager-task/create', json={
            "owner_id": 297,
            "task_name": "Task",
            "description": "Desc"
        })
        self.assertEqual(create_response.status_code, 201)
        create_data = json.loads(create_response.data)
        task_id = create_data["data"]["id"]
        
        # Update collaborators
        response = self.client.put('/tasks/update', json={
            "task_id": task_id,
            "collaborators": [297, 102, 103]
        })
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertEqual(data["data"]["collaborators"], [297, 102, 103])

    def test_update_task_invalid_type(self):
        """Test update fails with invalid task type."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create a task
        create_response = self.client.post('/tasks/manager-task/create', json={
            "owner_id": 297,
            "task_name": "Task",
            "description": "Desc"
        })
        self.assertEqual(create_response.status_code, 201)
        create_data = json.loads(create_response.data)
        task_id = create_data["data"]["id"]
        
        # Update with invalid type
        response = self.client.put('/tasks/update', json={
            "task_id": task_id,
            "type": "invalid_type"
        })
        
        # Assertions
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 400)
        self.assertIn("Invalid task type", data["Message"])


    # ==================== get_task_by_id Tests ====================
    
    def test_get_task_by_id_success(self):
        """Test successfully retrieving a task by ID."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create a task
        create_response = self.client.post('/tasks/manager-task/create', json={
            "owner_id": 297,
            "task_name": "Test Task",
            "description": "Test Description"
        })
        self.assertEqual(create_response.status_code, 201)
        create_data = json.loads(create_response.data)
        task_id = create_data["data"]["id"]
        
        # Make request
        response = self.client.get(f'/tasks/{task_id}')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertIn("task", data)
        self.assertEqual(data["task"]["id"], task_id)
        self.assertEqual(data["task"]["task_name"], "Test Task")

    def test_get_task_by_id_not_found(self):
        """Test get task by ID when task doesn't exist."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Make request with non-existent task
        response = self.client.get('/tasks/999')
        
        # Assertions
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 404)


    # ==================== get_tasks_by_user Tests ====================
    
    def test_get_tasks_by_user_success(self):
        """Test successfully retrieving tasks for a user."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create some tasks for the user
        create_response1 = self.client.post('/tasks/manager-task/create', json={
            "owner_id": 297,
            "task_name": "Parent Task 1",
            "description": "Description 1"
        })
        self.assertEqual(create_response1.status_code, 201)
        
        create_response2 = self.client.post('/tasks/manager-task/create', json={
            "owner_id": 297,
            "task_name": "Parent Task 2",
            "description": "Description 2"
        })
        self.assertEqual(create_response2.status_code, 201)
        
        # Make request
        response = self.client.get('/tasks/user-task/297')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertEqual(data["status"], "success")
        self.assertIn("data", data)

    def test_get_tasks_by_user_with_subtasks(self):
        """Test retrieving tasks with nested subtasks."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create a parent task
        parent_response = self.client.post('/tasks/manager-task/create', json={
            "owner_id": 297,
            "task_name": "Parent Task",
            "description": "Description"
        })
        self.assertEqual(parent_response.status_code, 201)
        parent_data = json.loads(parent_response.data)
        parent_task_id = parent_data["data"]["id"]
        
        # Create a subtask
        subtask_response = self.client.post('/tasks/manager-subtask/create', json={
            "owner_id": 297,
            "task_name": "Subtask 1",
            "description": "Sub desc",
            "parent_task": parent_task_id
        })
        self.assertEqual(subtask_response.status_code, 201)
        
        # Make request
        response = self.client.get('/tasks/user-task/297')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertEqual(data["status"], "success")
        self.assertIn("data", data)
        # Check that parent task has subtasks
        parent_task = data["data"][0]
        self.assertIn("subtasks", parent_task)
        self.assertEqual(len(parent_task["subtasks"]), 1)

    def test_get_tasks_by_user_not_found(self):
        """Test get tasks by user when no tasks found."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Make request for user with no tasks
        response = self.client.get('/tasks/user-task/999')
        
        # Assertions
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 404)
        self.assertIn("No tasks found", data["Message"])
        self.assertIn("999", data["Message"])

    # ==================== get_tasks_by_project Tests ====================
    
    def test_get_tasks_by_project_success(self):
        """Test successfully retrieving tasks for a project."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create some tasks for the project
        create_response1 = self.client.post('/tasks/manager-task/create', json={
            "owner_id": 297,
            "task_name": "Project Task 1",
            "description": "Task for project",
            "project_id": 10
        })
        self.assertEqual(create_response1.status_code, 201)
        
        create_response2 = self.client.post('/tasks/manager-task/create', json={
            "owner_id": 297,
            "task_name": "Project Task 2",
            "description": "Another task",
            "project_id": 10
        })
        self.assertEqual(create_response2.status_code, 201)
        
        # Make request
        response = self.client.get('/tasks/project/10')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertIn("data", data)

    def test_get_tasks_by_project_not_found(self):
        """Test get tasks by project when no tasks found."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Make request for project with no tasks
        response = self.client.get('/tasks/project/999')
        
        # Assertions
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 404)
        self.assertIn("No tasks found", data["Message"])


    # ==================== get_tasks_by_owner Tests ====================
    
    def test_get_tasks_by_owner_success(self):
        """Test successfully retrieving tasks by owner."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create some tasks for the owner
        create_response1 = self.client.post('/tasks/manager-task/create', json={
            "owner_id": 297,
            "task_name": "My Task 1",
            "description": "Owned task"
        })
        self.assertEqual(create_response1.status_code, 201)
        
        create_response2 = self.client.post('/tasks/manager-task/create', json={
            "owner_id": 297,
            "task_name": "My Task 2",
            "description": "Another owned task"
        })
        self.assertEqual(create_response2.status_code, 201)
        
        # Make request
        response = self.client.get('/tasks/owner/297')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertIn("data", data)
        self.assertEqual(data["data"][0]["owner_id"], 297)

    def test_get_tasks_by_owner_not_found(self):
        """Test get tasks by owner when no tasks found."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Make request for owner with no tasks
        response = self.client.get('/tasks/owner/999')
        
        # Assertions
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 404)
        self.assertIn("No tasks found", data["Message"])


    # ==================== get_subtasks_by_parent Tests ====================
    
    def test_get_subtasks_by_parent_success(self):
        """Test successfully retrieving subtasks for a parent task."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create a parent task
        parent_response = self.client.post('/tasks/manager-task/create', json={
            "owner_id": 297,
            "task_name": "Parent Task",
            "description": "Parent task for subtasks"
        })
        self.assertEqual(parent_response.status_code, 201)
        parent_data = json.loads(parent_response.data)
        parent_task_id = parent_data["data"]["id"]
        
        # Create subtasks
        subtask_response1 = self.client.post('/tasks/manager-subtask/create', json={
            "owner_id": 297,
            "task_name": "Subtask 1",
            "description": "First subtask",
            "parent_task": parent_task_id
        })
        self.assertEqual(subtask_response1.status_code, 201)
        
        subtask_response2 = self.client.post('/tasks/manager-subtask/create', json={
            "owner_id": 297,
            "task_name": "Subtask 2",
            "description": "Second subtask",
            "parent_task": parent_task_id
        })
        self.assertEqual(subtask_response2.status_code, 201)
        
        # Make request
        response = self.client.get(f'/tasks/{parent_task_id}/subtasks')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertIn("Successfully retrieved 2 subtasks for parent task", data["Message"])
        self.assertEqual(data["data"]["parent_task_id"], parent_task_id)
        self.assertEqual(data["data"]["subtask_count"], 2)

    def test_get_subtasks_by_parent_no_subtasks(self):
        """Test retrieving subtasks when parent has no subtasks."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create a parent task
        parent_response = self.client.post('/tasks/manager-task/create', json={
            "owner_id": 297,
            "task_name": "Parent Task",
            "description": "Parent task with no subtasks"
        })
        self.assertEqual(parent_response.status_code, 201)
        parent_data = json.loads(parent_response.data)
        parent_task_id = parent_data["data"]["id"]
        
        # Make request
        response = self.client.get(f'/tasks/{parent_task_id}/subtasks')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertIn("No subtasks found for parent task", data["Message"])
        self.assertEqual(data["data"]["subtask_count"], 0)

    def test_get_subtasks_by_parent_not_found(self):
        """Test retrieving subtasks when parent task doesn't exist."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Make request with non-existent parent task
        response = self.client.get('/tasks/999/subtasks')
        
        # Assertions
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 404)
        self.assertIn("Parent task with ID 999 not found", data["Message"])


    # ==================== get_tasks_by_team Tests ====================
    
    def test_get_tasks_by_team_success(self):
        """Test successfully retrieving tasks for a team."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create some tasks for the team
        create_response = self.client.post('/tasks/manager-task/create', json={
            "owner_id": 297,
            "task_name": "Team Task 1",
            "description": "Task for team"
        })
        self.assertEqual(create_response.status_code, 201)
        
        # Make request
        response = self.client.get('/tasks/team/5')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertIn("Successfully retrieved", data["Message"])
        self.assertIn("team 5", data["Message"])
        self.assertIn("data", data)

    def test_get_tasks_by_team_not_found(self):
        """Test get tasks by team when no tasks found."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Make request for team with no tasks
        response = self.client.get('/tasks/team/999')
        
        # Assertions
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 404)
        self.assertIn("No tasks found for team 999", data["Message"])



if __name__ == "__main__":
    unittest.main()