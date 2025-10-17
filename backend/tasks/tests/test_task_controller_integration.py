import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import sys
import os
from io import BytesIO

# Add parent directory to path to find modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.task_service import TaskService
from models.task import Task

# Import the controller and service
from controllers.task_controller import task_bp, service


class TestTaskControllerIntegration(unittest.TestCase):
    """Integration tests for task controller endpoints."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a mock repository
        self.mock_repo = Mock()
        
        # Replace the service's repository with our mock
        service.repo = self.mock_repo

        # Create a test Flask app
        from flask import Flask
        self.app = Flask(__name__)
        self.app.register_blueprint(task_bp)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    # ==================== manager_create_task Tests ====================
    
    def test_manager_create_task_success(self):
        """Test successful task creation with all required fields."""
        # Mock the repository methods
        self.mock_repo.find_by_owner_and_name.return_value = None  # No duplicate
        self.mock_repo.insert_task.return_value = {
            "id": 1,
            "task_name": "Test Task",
            "description": "Test Description",
            "owner_id": 100,
            "status": None,
            "type": "parent",
            "collaborators": None,
            "project_id": None,
            "parent_task": None,
            "subtasks": None,
            "priority": None,
            "due_date": None,
            "attachments": None
        }
        
        # Make request with required fields
        response = self.client.post('/tasks/manager-task/create', json={
            "owner_id": 100,
            "task_name": "Test Task",
            "description": "Test Description"
        })
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 201)
        self.assertIn("Task created! Task ID: 1", data["Message"])
        self.assertIn("data", data)
        self.assertEqual(data["data"]["task_name"], "Test Task")
        
        # Verify repository calls
        self.mock_repo.find_by_owner_and_name.assert_called_once_with(100, "Test Task")
        self.mock_repo.insert_task.assert_called_once()

    def test_manager_create_task_with_all_fields(self):
        """Test task creation with all optional fields."""
        # Mock the repository methods
        self.mock_repo.find_by_owner_and_name.return_value = None
        self.mock_repo.insert_task.return_value = {
            "id": 2,
            "task_name": "Complete Task",
            "description": "Full task description",
            "owner_id": 100,
            "status": "Unassigned",
            "type": "parent",
            "collaborators": [101, 102],
            "project_id": 10,
            "parent_task": None,
            "subtasks": [],
            "priority": 3,
            "due_date": "2025-12-31T00:00:00",
            "attachments": None
        }
        
        # Make request with all fields
        response = self.client.post('/tasks/manager-task/create', json={
            "owner_id": 100,
            "task_name": "Complete Task",
            "description": "Full task description",
            "status": "Unassigned",
            "type": "parent",
            "collaborators": [101, 102],
            "project_id": 10,
            "priority": 3,
            "due_date": "2025-12-31"
        })
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 201)
        self.assertEqual(data["data"]["priority"], 3)
        self.assertEqual(data["data"]["collaborators"], [101, 102])

    def test_manager_create_task_duplicate_name(self):
        """Test task creation when task name already exists for owner."""
        # Mock repository to return existing task
        existing_task = {
            "id": 1,
            "task_name": "Existing Task",
            "description": "Already exists",
            "owner_id": 100
        }
        self.mock_repo.find_by_owner_and_name.return_value = existing_task
        
        # Make request
        response = self.client.post('/tasks/manager-task/create', json={
            "owner_id": 100,
            "task_name": "Existing Task",
            "description": "Test Description"
        })
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertIn("already exists", data["Message"])
        self.assertEqual(data["data"], existing_task)
        
        # Verify insert was not called
        self.mock_repo.insert_task.assert_not_called()

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
            "owner_id": 100,
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
            "owner_id": 100,
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
            "owner_id": 100,
            "task_name": "Test Task",
            "description": "Test Description",
            "type": "invalid_type"  # Invalid type
        })
        
        # Assertions
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 400)
        self.assertIn("Invalid task type", data["Message"])

    def test_manager_create_task_with_attachment(self):
        """Test task creation with file attachment."""
        # Mock the repository methods
        self.mock_repo.find_by_owner_and_name.return_value = None
        self.mock_repo.upload_attachment.return_value = ["https://example.com/file.pdf"]
        self.mock_repo.insert_task.return_value = {
            "id": 5,
            "task_name": "Task with File",
            "description": "Task with attachment",
            "owner_id": 100,
            "attachments": ["https://example.com/file.pdf"],
            "type": "parent"
        }
        
        # Create mock file
        mock_file = (BytesIO(b"PDF content"), "test.pdf")
        
        # Make request with file
        response = self.client.post('/tasks/manager-task/create', 
            data={
                "owner_id": "100",
                "task_name": "Task with File",
                "description": "Task with attachment",
                "attachment": mock_file
            },
            content_type='multipart/form-data'
        )
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 201)
        self.mock_repo.upload_attachment.assert_called_once()

    def test_manager_create_task_attachment_upload_failure(self):
        """Test task creation when attachment upload fails."""
        # Mock upload to raise exception
        self.mock_repo.upload_attachment.side_effect = Exception("S3 upload failed")
        
        # Create mock file
        mock_file = (BytesIO(b"PDF content"), "test.pdf")
        
        # Make request with file
        response = self.client.post('/tasks/manager-task/create',
            data={
                "owner_id": "100",
                "task_name": "Task with File",
                "description": "Task with attachment",
                "attachment": mock_file
            },
            content_type='multipart/form-data'
        )
        
        # Assertions
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 500)
        self.assertIn("Upload failed", data["Message"])

    def test_manager_create_task_repository_error(self):
        """Test task creation when repository raises an exception."""
        # Mock repository to raise exception
        self.mock_repo.find_by_owner_and_name.return_value = None
        self.mock_repo.insert_task.side_effect = Exception("Database error")
        
        # Make request
        response = self.client.post('/tasks/manager-task/create', json={
            "owner_id": 100,
            "task_name": "Test Task",
            "description": "Test Description"
        })
        
        # Assertions
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 500)
        self.assertIn("Database error", data["Message"])

    # ==================== staff_create_task Tests ====================
    
    def test_staff_create_task_success(self):
        """Test staff creates task - owner_id automatically added to collaborators."""
        # Mock the repository methods
        self.mock_repo.find_by_owner_and_name.return_value = None
        self.mock_repo.insert_task.return_value = {
            "id": 10,
            "task_name": "Staff Task",
            "description": "Task by staff",
            "owner_id": 100,
            "collaborators": [100],  # Owner automatically added
            "type": "parent"
        }
        
        # Make request without collaborators
        response = self.client.post('/tasks/staff-task/create', json={
            "owner_id": 100,
            "task_name": "Staff Task",
            "description": "Task by staff"
        })
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 201)
        self.assertIn("Task created! Task ID: 10", data["Message"])
        self.assertEqual(data["data"]["collaborators"], [100])

    def test_staff_create_task_owner_added_to_collaborators(self):
        """Test staff task creation adds owner to existing collaborators."""
        # Mock the repository methods
        self.mock_repo.find_by_owner_and_name.return_value = None
        self.mock_repo.insert_task.return_value = {
            "id": 11,
            "task_name": "Staff Team Task",
            "description": "Task with team",
            "owner_id": 100,
            "collaborators": [100, 101, 102],  # Owner added to existing list
            "type": "parent"
        }
        
        # Make request with collaborators (owner not included)
        response = self.client.post('/tasks/staff-task/create', json={
            "owner_id": 100,
            "task_name": "Staff Team Task",
            "description": "Task with team",
            "collaborators": [101, 102]
        })
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 201)
        # Verify owner was added to collaborators
        self.assertIn(100, data["data"]["collaborators"])

    def test_staff_create_task_owner_already_in_collaborators(self):
        """Test staff task creation when owner already in collaborators list."""
        # Mock the repository methods
        self.mock_repo.find_by_owner_and_name.return_value = None
        self.mock_repo.insert_task.return_value = {
            "id": 12,
            "task_name": "Staff Self Task",
            "description": "Owner already in list",
            "owner_id": 100,
            "collaborators": [100, 101],
            "type": "parent"
        }
        
        # Make request with owner already in collaborators
        response = self.client.post('/tasks/staff-task/create', json={
            "owner_id": 100,
            "task_name": "Staff Self Task",
            "description": "Owner already in list",
            "collaborators": [100, 101]
        })
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 201)
        # Verify owner appears only once
        self.assertEqual(data["data"]["collaborators"].count(100), 1)

    def test_staff_create_task_duplicate_name(self):
        """Test staff task creation with duplicate name."""
        # Mock repository to return existing task
        existing_task = {
            "id": 13,
            "task_name": "Existing Staff Task",
            "description": "Already exists",
            "owner_id": 100
        }
        self.mock_repo.find_by_owner_and_name.return_value = existing_task
        
        # Make request
        response = self.client.post('/tasks/staff-task/create', json={
            "owner_id": 100,
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

    def test_staff_create_task_with_attachment(self):
        """Test staff task creation with file attachment."""
        # Mock the repository methods
        self.mock_repo.find_by_owner_and_name.return_value = None
        self.mock_repo.upload_attachment.return_value = ["https://example.com/staff-file.pdf"]
        self.mock_repo.insert_task.return_value = {
            "id": 14,
            "task_name": "Staff Task with File",
            "description": "Task with attachment",
            "owner_id": 100,
            "collaborators": [100],
            "attachments": ["https://example.com/staff-file.pdf"],
            "type": "parent"
        }
        
        # Create mock file
        mock_file = (BytesIO(b"PDF content"), "staff-doc.pdf")
        
        # Make request with file
        response = self.client.post('/tasks/staff-task/create',
            data={
                "owner_id": "100",
                "task_name": "Staff Task with File",
                "description": "Task with attachment",
                "attachment": mock_file
            },
            content_type='multipart/form-data'
        )
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 201)
        self.mock_repo.upload_attachment.assert_called_once()

    # ==================== manager_create_subtask Tests ====================
    
    def test_manager_create_subtask_success(self):
        """Test successful subtask creation by manager."""
        # Mock the repository methods
        self.mock_repo.get_task.return_value = {"id": 1, "task_name": "Parent Task"}  # Parent exists
        self.mock_repo.find_by_owner_and_name.return_value = None
        self.mock_repo.insert_task.return_value = {
            "id": 20,
            "task_name": "Subtask 1",
            "description": "A subtask",
            "owner_id": 100,
            "parent_task": 1,
            "type": "subtask"
        }
        self.mock_repo.add_subtask_to_parent.return_value = None  # Success
        
        # Make request
        response = self.client.post('/tasks/manager-subtask/create', json={
            "owner_id": 100,
            "task_name": "Subtask 1",
            "description": "A subtask",
            "parent_task": 1
        })
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 201)
        self.assertIn("Subtask created! Task ID: 20", data["Message"])
        self.assertEqual(data["data"]["type"], "subtask")
        self.assertEqual(data["data"]["parent_task"], 1)
        
        # Verify parent was updated
        self.mock_repo.add_subtask_to_parent.assert_called_once_with(1, 20)

    def test_manager_create_subtask_missing_parent_task(self):
        """Test subtask creation fails when parent_task is missing."""
        response = self.client.post('/tasks/manager-subtask/create', json={
            "owner_id": 100,
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
        # Mock parent task not found
        self.mock_repo.get_task.return_value = None
        
        # Make request
        response = self.client.post('/tasks/manager-subtask/create', json={
            "owner_id": 100,
            "task_name": "Subtask",
            "description": "Parent doesn't exist",
            "parent_task": 999
        })
        
        # Assertions
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 400)
        self.assertIn("Parent task with ID 999 not found", data["Message"])

    def test_manager_create_subtask_duplicate_name(self):
        """Test subtask creation with duplicate name."""
        # Mock parent exists
        self.mock_repo.get_task.return_value = {"id": 1, "task_name": "Parent Task"}
        # Mock duplicate subtask name
        existing_subtask = {
            "id": 21,
            "task_name": "Existing Subtask",
            "description": "Already exists",
            "owner_id": 100,
            "parent_task": 1,
            "type": "subtask"
        }
        self.mock_repo.find_by_owner_and_name.return_value = existing_subtask
        
        # Make request
        response = self.client.post('/tasks/manager-subtask/create', json={
            "owner_id": 100,
            "task_name": "Existing Subtask",
            "description": "Test",
            "parent_task": 1
        })
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertIn("already exists", data["Message"])

    def test_manager_create_subtask_with_collaborators(self):
        """Test subtask creation with collaborators."""
        # Mock the repository methods
        self.mock_repo.get_task.return_value = {"id": 1, "task_name": "Parent Task"}
        self.mock_repo.find_by_owner_and_name.return_value = None
        self.mock_repo.insert_task.return_value = {
            "id": 22,
            "task_name": "Team Subtask",
            "description": "Subtask with team",
            "owner_id": 100,
            "parent_task": 1,
            "collaborators": [101, 102],
            "type": "subtask"
        }
        self.mock_repo.add_subtask_to_parent.return_value = None
        
        # Make request with collaborators
        response = self.client.post('/tasks/manager-subtask/create', json={
            "owner_id": 100,
            "task_name": "Team Subtask",
            "description": "Subtask with team",
            "parent_task": 1,
            "collaborators": [101, 102]
        })
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 201)
        self.assertEqual(data["data"]["collaborators"], [101, 102])

    def test_manager_create_subtask_parent_update_fails(self):
        """Test subtask created even if parent update fails (warning logged)."""
        # Mock the repository methods
        self.mock_repo.get_task.return_value = {"id": 1, "task_name": "Parent Task"}
        self.mock_repo.find_by_owner_and_name.return_value = None
        self.mock_repo.insert_task.return_value = {
            "id": 23,
            "task_name": "Subtask",
            "description": "Parent update fails",
            "owner_id": 100,
            "parent_task": 1,
            "type": "subtask"
        }
        # Mock parent update failure
        self.mock_repo.add_subtask_to_parent.side_effect = Exception("Parent update failed")
        
        # Make request
        response = self.client.post('/tasks/manager-subtask/create', json={
            "owner_id": 100,
            "task_name": "Subtask",
            "description": "Parent update fails",
            "parent_task": 1
        })
        
        # Assertions - subtask still created successfully
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 201)
        self.assertIn("Subtask created!", data["Message"])

    # ==================== staff_create_subtask Tests ====================
    
    def test_staff_create_subtask_success(self):
        """Test staff creates subtask - owner automatically added to collaborators."""
        # Mock the repository methods
        self.mock_repo.get_task.return_value = {"id": 1, "task_name": "Parent Task"}
        self.mock_repo.find_by_owner_and_name.return_value = None
        self.mock_repo.insert_task.return_value = {
            "id": 30,
            "task_name": "Staff Subtask",
            "description": "Subtask by staff",
            "owner_id": 100,
            "parent_task": 1,
            "collaborators": [100],  # Owner automatically added
            "type": "subtask"
        }
        self.mock_repo.add_subtask_to_parent.return_value = None
        
        # Make request without collaborators
        response = self.client.post('/tasks/staff-subtask/create', json={
            "owner_id": 100,
            "task_name": "Staff Subtask",
            "description": "Subtask by staff",
            "parent_task": 1
        })
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 201)
        self.assertIn("Subtask created! Task ID: 30", data["Message"])
        self.assertEqual(data["data"]["collaborators"], [100])
        self.assertEqual(data["data"]["type"], "subtask")

    def test_staff_create_subtask_owner_added_to_collaborators(self):
        """Test staff subtask adds owner to existing collaborators."""
        # Mock the repository methods
        self.mock_repo.get_task.return_value = {"id": 1, "task_name": "Parent Task"}
        self.mock_repo.find_by_owner_and_name.return_value = None
        self.mock_repo.insert_task.return_value = {
            "id": 31,
            "task_name": "Staff Team Subtask",
            "description": "Subtask with team",
            "owner_id": 100,
            "parent_task": 1,
            "collaborators": [100, 101, 102],
            "type": "subtask"
        }
        self.mock_repo.add_subtask_to_parent.return_value = None
        
        # Make request with collaborators (owner not included)
        response = self.client.post('/tasks/staff-subtask/create', json={
            "owner_id": 100,
            "task_name": "Staff Team Subtask",
            "description": "Subtask with team",
            "parent_task": 1,
            "collaborators": [101, 102]
        })
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 201)
        self.assertIn(100, data["data"]["collaborators"])
        self.assertIn(101, data["data"]["collaborators"])
        self.assertIn(102, data["data"]["collaborators"])

    def test_staff_create_subtask_missing_parent_task(self):
        """Test staff subtask creation fails when parent_task is missing."""
        response = self.client.post('/tasks/staff-subtask/create', json={
            "owner_id": 100,
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
        # Mock parent task not found
        self.mock_repo.get_task.return_value = None
        
        # Make request
        response = self.client.post('/tasks/staff-subtask/create', json={
            "owner_id": 100,
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
        # Mock parent exists
        self.mock_repo.get_task.return_value = {"id": 1, "task_name": "Parent Task"}
        # Mock duplicate
        existing_subtask = {
            "id": 32,
            "task_name": "Existing Staff Subtask",
            "description": "Already exists",
            "owner_id": 100,
            "parent_task": 1,
            "type": "subtask"
        }
        self.mock_repo.find_by_owner_and_name.return_value = existing_subtask
        
        # Make request
        response = self.client.post('/tasks/staff-subtask/create', json={
            "owner_id": 100,
            "task_name": "Existing Staff Subtask",
            "description": "Test",
            "parent_task": 1
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
        # Mock existing task
        self.mock_repo.get_task.return_value = {
            "id": 1,
            "task_name": "Old Name",
            "description": "Old description",
            "owner_id": 100,
            "status": "Unassigned",
            "type": "parent"
        }
        # Mock updated task
        self.mock_repo.update_task.return_value = {
            "id": 1,
            "task_name": "Updated Name",
            "description": "Updated description",
            "owner_id": 100,
            "status": "Ongoing",
            "type": "parent"
        }
        
        # Make update request
        response = self.client.put('/tasks/update', json={
            "task_id": 1,
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
        # Mock existing task
        self.mock_repo.get_task.return_value = {
            "id": 1,
            "task_name": "Task Name",
            "description": "Description",
            "owner_id": 100,
            "status": "Unassigned",
            "type": "parent"
        }
        # Mock updated task
        self.mock_repo.update_task.return_value = {
            "id": 1,
            "task_name": "Task Name",
            "description": "Description",
            "owner_id": 100,
            "status": "Ongoing",
            "type": "parent"
        }
        
        # Update only status
        response = self.client.patch('/tasks/update', json={
            "task_id": 1,
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
        # Mock task not found
        self.mock_repo.get_task.return_value = None
        
        # Make request
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
        # Mock existing task
        self.mock_repo.get_task.return_value = {
            "id": 1,
            "task_name": "Task Name",
            "description": "Description",
            "owner_id": 100
        }
        
        # Make request with only task_id
        response = self.client.put('/tasks/update', json={
            "task_id": 1
        })
        
        # Assertions
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 400)
        self.assertIn("No fields to update", data["Message"])

    def test_update_task_with_collaborators(self):
        """Test updating collaborators list."""
        # Mock existing task
        self.mock_repo.get_task.return_value = {
            "id": 1,
            "task_name": "Task",
            "description": "Desc",
            "owner_id": 100,
            "collaborators": [100]
        }
        # Mock updated task
        self.mock_repo.update_task.return_value = {
            "id": 1,
            "task_name": "Task",
            "description": "Desc",
            "owner_id": 100,
            "collaborators": [100, 101, 102]
        }
        
        # Update collaborators
        response = self.client.put('/tasks/update', json={
            "task_id": 1,
            "collaborators": [100, 101, 102]
        })
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertEqual(data["data"]["collaborators"], [100, 101, 102])

    def test_update_task_invalid_type(self):
        """Test update fails with invalid task type."""
        # Mock existing task
        self.mock_repo.get_task.return_value = {
            "id": 1,
            "task_name": "Task",
            "description": "Desc",
            "owner_id": 100
        }
        
        # Update with invalid type
        response = self.client.put('/tasks/update', json={
            "task_id": 1,
            "type": "invalid_type"
        })
        
        # Assertions
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 400)
        self.assertIn("Invalid task type", data["Message"])

    def test_update_task_repository_error(self):
        """Test update fails on repository error."""
        # Mock existing task
        self.mock_repo.get_task.return_value = {
            "id": 1,
            "task_name": "Task",
            "description": "Desc",
            "owner_id": 100
        }
        # Mock update error
        self.mock_repo.update_task.side_effect = Exception("Database error")
        
        # Make request
        response = self.client.put('/tasks/update', json={
            "task_id": 1,
            "task_name": "New Name"
        })
        
        # Assertions
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 500)

    # ==================== get_task_by_id Tests ====================
    
    def test_get_task_by_id_success(self):
        """Test successfully retrieving a task by ID."""
        # Mock task data
        self.mock_repo.get_task.return_value = {
            "id": 1,
            "task_name": "Test Task",
            "description": "Test Description",
            "owner_id": 100,
            "status": "Ongoing",
            "type": "parent"
        }
        
        # Make request
        response = self.client.get('/tasks/1')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertIn("task", data)
        self.assertEqual(data["task"]["id"], 1)
        self.assertEqual(data["task"]["task_name"], "Test Task")

    def test_get_task_by_id_not_found(self):
        """Test get task by ID when task doesn't exist."""
        # Mock task not found
        self.mock_repo.get_task.return_value = None
        
        # Make request
        response = self.client.get('/tasks/999')
        
        # Assertions
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 500)


    def test_get_task_by_id_repository_error(self):
        """Test get task by ID with repository error."""
        # Mock repository error
        self.mock_repo.get_task.side_effect = Exception("Database connection failed")
        
        # Make request
        response = self.client.get('/tasks/1')
        
        # Assertions
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 500)
        self.assertIn("Database connection failed", data["Message"])

    # ==================== get_tasks_by_user Tests ====================
    
    def test_get_tasks_by_user_success(self):
        """Test successfully retrieving tasks for a user."""
        # Mock tasks with nested subtasks
        self.mock_repo.find_parent_tasks_by_user.return_value = [
            {
                "id": 1,
                "task_name": "Parent Task 1",
                "description": "Description 1",
                "owner_id": 100
            },
            {
                "id": 2,
                "task_name": "Parent Task 2",
                "description": "Description 2",
                "owner_id": 100
            }
        ]
        self.mock_repo.find_subtasks_by_parent.return_value = []
        
        # Make request
        response = self.client.get('/tasks/user-task/100')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertEqual(data["status"], "success")
        self.assertIn("data", data)

    def test_get_tasks_by_user_with_subtasks(self):
        """Test retrieving tasks with nested subtasks."""
        # Mock parent tasks
        self.mock_repo.find_parent_tasks_by_user.return_value = [
            {
                "id": 1,
                "task_name": "Parent Task",
                "description": "Description",
                "owner_id": 100
            }
        ]
        # Mock subtasks
        self.mock_repo.find_subtasks_by_parent.return_value = [
            {
                "id": 10,
                "task_name": "Subtask 1",
                "description": "Sub desc",
                "owner_id": 100,
                "parent_task": 1,
                "type": "subtask",
                "status": "Ongoing",
                "due_date": None,
                "collaborators": [100],
                "project_id": None,
                "created_at": "2025-01-01"
            }
        ]
        
        # Make request
        response = self.client.get('/tasks/user-task/100')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertEqual(data["status"], "success")
        self.assertIn("data", data)

    def test_get_tasks_by_user_not_found(self):
        """Test get tasks by user when no tasks found."""
        # Mock no tasks
        self.mock_repo.find_parent_tasks_by_user.return_value = []
        
        # Make request
        response = self.client.get('/tasks/user-task/999')
        
        # Assertions
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 404)
        self.assertIn("No tasks found", data["Message"])
        self.assertIn("999", data["Message"])

    def test_get_tasks_by_user_repository_error(self):
        """Test get tasks by user with repository error."""
        # Mock repository error
        self.mock_repo.find_parent_tasks_by_user.side_effect = Exception("Database error")
        
        # Make request
        response = self.client.get('/tasks/user-task/100')
        
        # Assertions
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 500)

    # ==================== get_tasks_by_project Tests ====================
    
    def test_get_tasks_by_project_success(self):
        """Test successfully retrieving tasks for a project."""
        # Mock tasks for project
        self.mock_repo.find_by_project.return_value = [
            {
                "id": 1,
                "task_name": "Project Task 1",
                "description": "Task for project",
                "owner_id": 100,
                "project_id": 10
            },
            {
                "id": 2,
                "task_name": "Project Task 2",
                "description": "Another task",
                "owner_id": 101,
                "project_id": 10
            }
        ]
        
        # Make request
        response = self.client.get('/tasks/project/10')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertIn("data", data)
        self.assertEqual(len(data["data"]), 2)

    def test_get_tasks_by_project_not_found(self):
        """Test get tasks by project when no tasks found."""
        # Mock no tasks
        self.mock_repo.find_by_project.return_value = []
        
        # Make request
        response = self.client.get('/tasks/project/999')
        
        # Assertions
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 404)
        self.assertIn("No tasks found", data["Message"])

    def test_get_tasks_by_project_repository_error(self):
        """Test get tasks by project with repository error."""
        # Mock repository error
        self.mock_repo.find_by_project.side_effect = Exception("Database error")
        
        # Make request
        response = self.client.get('/tasks/project/10')
        
        # Assertions
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 500)

    # ==================== get_tasks_by_owner Tests ====================
    
    def test_get_tasks_by_owner_success(self):
        """Test successfully retrieving tasks by owner."""
        # Mock tasks owned by user
        self.mock_repo.find_by_owner.return_value = [
            {
                "id": 1,
                "task_name": "My Task 1",
                "description": "Owned task",
                "owner_id": 100
            },
            {
                "id": 2,
                "task_name": "My Task 2",
                "description": "Another owned task",
                "owner_id": 100
            }
        ]
        
        # Make request
        response = self.client.get('/tasks/owner/100')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertIn("data", data)
        self.assertEqual(len(data["data"]), 2)
        self.assertEqual(data["data"][0]["owner_id"], 100)

    def test_get_tasks_by_owner_not_found(self):
        """Test get tasks by owner when no tasks found."""
        # Mock no tasks
        self.mock_repo.find_by_owner.return_value = []
        
        # Make request
        response = self.client.get('/tasks/owner/999')
        
        # Assertions
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 404)
        self.assertIn("No tasks found", data["Message"])

    def test_get_tasks_by_owner_repository_error(self):
        """Test get tasks by owner with repository error."""
        # Mock repository error
        self.mock_repo.find_by_owner.side_effect = Exception("Database error")
        
        # Make request
        response = self.client.get('/tasks/owner/100')
        
        # Assertions
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 500)

    # ==================== get_subtasks_by_parent Tests ====================
    
    def test_get_subtasks_by_parent_success(self):
        """Test successfully retrieving subtasks for a parent task."""
        # Mock parent task exists
        self.mock_repo.get_task.return_value = {
            "id": 1,
            "task_name": "Parent Task",
            "subtasks": [10, 11]
        }
        # Mock subtask details
        def get_task_side_effect(task_id):
            if task_id == 1:
                return {"id": 1, "task_name": "Parent Task", "subtasks": [10, 11]}
            elif task_id == 10:
                return {"id": 10, "task_name": "Subtask 1", "parent_task": 1}
            elif task_id == 11:
                return {"id": 11, "task_name": "Subtask 2", "parent_task": 1}
        
        self.mock_repo.get_task.side_effect = get_task_side_effect
        
        # Make request
        response = self.client.get('/tasks/1/subtasks')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertIn("Successfully retrieved", data["Message"])
        self.assertEqual(data["data"]["parent_task_id"], 1)
        self.assertEqual(data["data"]["subtask_count"], 2)

    def test_get_subtasks_by_parent_no_subtasks(self):
        """Test retrieving subtasks when parent has no subtasks."""
        # Mock parent task with empty subtasks
        self.mock_repo.get_task.return_value = {
            "id": 1,
            "task_name": "Parent Task",
            "subtasks": []
        }
        
        # Make request
        response = self.client.get('/tasks/1/subtasks')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertIn("No subtasks found", data["Message"])
        self.assertEqual(data["data"]["subtask_count"], 0)

    def test_get_subtasks_by_parent_not_found(self):
        """Test retrieving subtasks when parent task doesn't exist."""
        # Mock parent task not found
        self.mock_repo.get_task.return_value = None
        
        # Make request
        response = self.client.get('/tasks/999/subtasks')
        
        # Assertions
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 404)
        self.assertIn("Parent task with ID 999 not found", data["Message"])

    def test_get_subtasks_by_parent_partial_success(self):
        """Test retrieving subtasks with some failures."""
        # Mock parent task with subtasks
        self.mock_repo.get_task.return_value = {
            "id": 1,
            "task_name": "Parent Task",
            "subtasks": [10, 11, 12]
        }
        
        # Mock some subtasks not found
        def get_task_side_effect(task_id):
            if task_id == 1:
                return {"id": 1, "task_name": "Parent Task", "subtasks": [10, 11, 12]}
            elif task_id == 10:
                return {"id": 10, "task_name": "Subtask 1", "parent_task": 1}
            elif task_id == 11:
                return None  # Not found
            elif task_id == 12:
                return {"id": 12, "task_name": "Subtask 3", "parent_task": 1}
        
        self.mock_repo.get_task.side_effect = get_task_side_effect
        
        # Make request
        response = self.client.get('/tasks/1/subtasks')
        
        # Assertions
        self.assertEqual(response.status_code, 207)  # Multi-status
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 207)
        self.assertIn("failed", data["Message"])
        self.assertEqual(data["data"]["subtask_count"], 2)
        self.assertIn("failed_subtasks", data["data"])

    # ==================== get_tasks_by_team Tests ====================
    
    def test_get_tasks_by_team_success(self):
        """Test successfully retrieving tasks for a team."""
        # Mock tasks for team
        self.mock_repo.find_parent_tasks_by_team.return_value = [
            {
                "id": 1,
                "task_name": "Team Task 1",
                "description": "Task for team",
                "owner_id": 100
            }
        ]
        self.mock_repo.find_subtasks_by_parent.return_value = []
        
        # Make request
        response = self.client.get('/tasks/team/5')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertIn("Successfully retrieved", data["Message"])
        self.assertIn("team 5", data["Message"])
        self.assertEqual(len(data["data"]), 1)

    def test_get_tasks_by_team_not_found(self):
        """Test get tasks by team when no tasks found."""
        # Mock no tasks
        self.mock_repo.find_parent_tasks_by_team.return_value = []
        
        # Make request
        response = self.client.get('/tasks/team/999')
        
        # Assertions
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 404)
        self.assertIn("No tasks found for team 999", data["Message"])

    def test_get_tasks_by_team_repository_error(self):
        """Test get tasks by team with repository error."""
        # Mock repository error
        self.mock_repo.find_parent_tasks_by_team.side_effect = Exception("Database error")
        
        # Make request
        response = self.client.get('/tasks/team/5')
        
        # Assertions
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 500)
        self.assertIn("Error retrieving team tasks", data["Message"])

    # ==================== get_tasks_by_department Tests ====================
    
    def test_get_tasks_by_department_success(self):
        """Test successfully retrieving tasks for a department."""
        # Mock tasks for department
        self.mock_repo.find_parent_tasks_by_department.return_value = [
            {
                "id": 1,
                "task_name": "Dept Task 1",
                "description": "Task for department",
                "owner_id": 100
            },
            {
                "id": 2,
                "task_name": "Dept Task 2",
                "description": "Another dept task",
                "owner_id": 101
            }
        ]
        self.mock_repo.find_subtasks_by_parent.return_value = []
        
        # Make request
        response = self.client.get('/tasks/department/3')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertIn("Successfully retrieved", data["Message"])
        self.assertIn("department 3", data["Message"])
        self.assertEqual(len(data["data"]), 2)

    def test_get_tasks_by_department_not_found(self):
        """Test get tasks by department when no tasks found."""
        # Mock no tasks
        self.mock_repo.find_parent_tasks_by_department.return_value = []
        
        # Make request
        response = self.client.get('/tasks/department/999')
        
        # Assertions
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 404)
        self.assertIn("No tasks found for department 999", data["Message"])

    def test_get_tasks_by_department_repository_error(self):
        """Test get tasks by department with repository error."""
        # Mock repository error
        self.mock_repo.find_parent_tasks_by_department.side_effect = Exception("Database error")
        
        # Make request
        response = self.client.get('/tasks/department/3')
        
        # Assertions
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 500)
        self.assertIn("Error retrieving department tasks", data["Message"])


if __name__ == "__main__":
    unittest.main()