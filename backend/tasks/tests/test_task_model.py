import unittest
import sys
import os
from datetime import datetime, UTC

# Add parent directory to path to find modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.task import Task


class TestTaskModel(unittest.TestCase):
    """Unit tests for the Task model class."""

    def test_task_creation_with_defaults(self):
        """Test creating a task with default values."""
        task = Task()
        
        assert task.id is None
        assert task.owner_id == 0
        assert task.task_name == ""
        assert task.due_date is None
        assert task.description == ""
        assert task.collaborators is None
        assert task.status is None
        assert task.project_id is None
        assert task.parent_task is None
        assert task.type == "parent"
        assert task.subtasks is None
        assert task.completed_at is None
        assert task.attachments is None
        assert task.priority is None
        assert isinstance(task.created_at, str)

    def test_task_creation_with_values(self):
        """Test creating a task with specific values."""
        due_date = datetime(2024, 12, 31, 23, 59, 59, tzinfo=UTC)
        task = Task(
            owner_id=123,
            task_name="Test Task",
            due_date=due_date,
            description="Test Description",
            collaborators=[1, 2, 3],
            status="Ongoing",
            project_id=456,
            parent_task=789,
            type="subtask",
            subtasks=[10, 11, 12],
            attachments=[{"url": "http://example.com/file.pdf", "name": "file.pdf"}],
            priority=5
        )
        
        assert task.owner_id == 123
        assert task.task_name == "Test Task"
        assert task.due_date == due_date
        assert task.description == "Test Description"
        assert task.collaborators == [1, 2, 3]
        assert task.status == "Ongoing"
        assert task.project_id == 456
        assert task.parent_task == 789
        assert task.type == "subtask"
        assert task.subtasks == [10, 11, 12]
        assert task.attachments == [{"url": "http://example.com/file.pdf", "name": "file.pdf"}]
        assert task.priority == 5

    def test_to_dict_without_id(self):
        """Test converting task to dictionary without ID."""
        task = Task(
            owner_id=123,
            task_name="Test Task",
            description="Test Description",
            status="Ongoing",
            project_id=456,
            priority=3
        )
        
        result = task.to_dict()
        
        expected = {
            'owner_id': 123,
            'task_name': 'Test Task',
            'description': 'Test Description',
            'status': 'Ongoing',
            'project_id': 456,
            'parent_task': None,
            'type': 'parent',
            'collaborators': None,
            'subtasks': None,
            'created_at': task.created_at,
            'completed_at': None,
            'attachments': None,
            'priority': 3,
            'due_date': None
        }
        
        assert result == expected
        assert 'id' not in result

    def test_to_dict_with_id(self):
        """Test converting task to dictionary with ID."""
        task = Task(owner_id=123, task_name="Test Task", description="Test Description")
        task.id = 999
        
        result = task.to_dict()
        
        assert result['id'] == 999
        assert result['owner_id'] == 123
        assert result['task_name'] == "Test Task"

    def test_to_dict_with_datetime_due_date(self):
        """Test converting task to dictionary with datetime due_date."""
        due_date = datetime(2024, 12, 31, 23, 59, 59, tzinfo=UTC)
        task = Task(owner_id=123, task_name="Test Task", due_date=due_date)
        
        result = task.to_dict()
        
        assert result['due_date'] == due_date.isoformat()

    def test_to_dict_with_string_due_date(self):
        """Test converting task to dictionary with string due_date."""
        due_date_str = "2024-12-31T23:59:59+00:00"
        task = Task(owner_id=123, task_name="Test Task", due_date=due_date_str)
        
        result = task.to_dict()
        
        assert result['due_date'] == due_date_str

    def test_from_dict_basic(self):
        """Test creating task from dictionary with basic fields."""
        data = {
            'id': 123,
            'owner_id': 456,
            'task_name': 'Test Task',
            'description': 'Test Description',
            'status': 'Ongoing',
            'project_id': 789,
            'type': 'parent',
            'priority': 3
        }
        
        task = Task.from_dict(data)
        
        assert task.id == 123
        assert task.owner_id == 456
        assert task.task_name == 'Test Task'
        assert task.description == 'Test Description'
        assert task.status == 'Ongoing'
        assert task.project_id == 789
        assert task.type == 'parent'
        assert task.priority == 3

    def test_from_dict_with_due_date_string(self):
        """Test creating task from dictionary with string due_date."""
        data = {
            'owner_id': 123,
            'task_name': 'Test Task',
            'description': 'Test Description',
            'due_date': '2024-12-31T23:59:59+00:00'
        }
        
        task = Task.from_dict(data)
        
        assert isinstance(task.due_date, datetime)
        assert task.due_date.year == 2024
        assert task.due_date.month == 12
        assert task.due_date.day == 31

    def test_from_dict_with_invalid_due_date(self):
        """Test creating task from dictionary with invalid due_date."""
        data = {
            'owner_id': 123,
            'task_name': 'Test Task',
            'description': 'Test Description',
            'due_date': 'invalid-date'
        }
        
        task = Task.from_dict(data)
        
        assert task.due_date is None

    def test_from_dict_with_collaborators_string(self):
        """Test creating task from dictionary with comma-separated collaborators string."""
        data = {
            'owner_id': 123,
            'task_name': 'Test Task',
            'description': 'Test Description',
            'collaborators': '1, 2, 3'
        }
        
        task = Task.from_dict(data)
        
        assert task.collaborators == [1, 2, 3]

    def test_from_dict_with_collaborators_list(self):
        """Test creating task from dictionary with collaborators list."""
        data = {
            'owner_id': 123,
            'task_name': 'Test Task',
            'description': 'Test Description',
            'collaborators': [1, 2, 3]
        }
        
        task = Task.from_dict(data)
        
        assert task.collaborators == [1, 2, 3]

    def test_from_dict_with_empty_collaborators_string(self):
        """Test creating task from dictionary with empty collaborators string."""
        data = {
            'owner_id': 123,
            'task_name': 'Test Task',
            'description': 'Test Description',
            'collaborators': ''
        }
        
        task = Task.from_dict(data)
        
        assert task.collaborators is None

    def test_from_dict_with_subtasks_string(self):
        """Test creating task from dictionary with comma-separated subtasks string."""
        data = {
            'owner_id': 123,
            'task_name': 'Test Task',
            'description': 'Test Description',
            'subtasks': '10, 11, 12'
        }
        
        task = Task.from_dict(data)
        
        assert task.subtasks == [10, 11, 12]

    def test_from_dict_with_subtasks_list(self):
        """Test creating task from dictionary with subtasks list."""
        data = {
            'owner_id': 123,
            'task_name': 'Test Task',
            'description': 'Test Description',
            'subtasks': [10, 11, 12]
        }
        
        task = Task.from_dict(data)
        
        assert task.subtasks == [10, 11, 12]

    def test_from_dict_with_attachments(self):
        """Test creating task from dictionary with attachments."""
        data = {
            'owner_id': 123,
            'task_name': 'Test Task',
            'description': 'Test Description',
            'attachments': [{"url": "http://example.com/file.pdf", "name": "file.pdf"}]
        }
        
        task = Task.from_dict(data)
        
        assert task.attachments == [{"url": "http://example.com/file.pdf", "name": "file.pdf"}]

    def test_from_dict_with_invalid_attachments(self):
        """Test creating task from dictionary with invalid attachments."""
        data = {
            'owner_id': 123,
            'task_name': 'Test Task',
            'description': 'Test Description',
            'attachments': "invalid"
        }
        
        task = Task.from_dict(data)
        
        assert task.attachments is None

    def test_from_dict_with_priority_string(self):
        """Test creating task from dictionary with string priority."""
        data = {
            'owner_id': 123,
            'task_name': 'Test Task',
            'description': 'Test Description',
            'priority': '5'
        }
        
        task = Task.from_dict(data)
        
        assert task.priority == 5

    def test_from_dict_with_invalid_priority(self):
        """Test creating task from dictionary with invalid priority."""
        data = {
            'owner_id': 123,
            'task_name': 'Test Task',
            'description': 'Test Description',
            'priority': 'invalid'
        }
        
        task = Task.from_dict(data)
        
        assert task.priority is None

    def test_from_dict_with_none_priority(self):
        """Test creating task from dictionary with None priority."""
        data = {
            'owner_id': 123,
            'task_name': 'Test Task',
            'description': 'Test Description',
            'priority': None
        }
        
        task = Task.from_dict(data)
        
        assert task.priority is None

    def test_from_dict_with_empty_strings(self):
        """Test creating task from dictionary with empty string values."""
        data = {
            'owner_id': 123,
            'task_name': 'Test Task',
            'description': 'Test Description',
            'project_id': '',
            'parent_task': '',
            'priority': ''
        }
        
        task = Task.from_dict(data)
        
        assert task.project_id is None
        assert task.parent_task is None
        assert task.priority is None

    def test_from_dict_with_created_at(self):
        """Test creating task from dictionary with custom created_at."""
        custom_created_at = "2024-01-01T00:00:00+00:00"
        data = {
            'owner_id': 123,
            'task_name': 'Test Task',
            'description': 'Test Description',
            'created_at': custom_created_at
        }
        
        task = Task.from_dict(data)
        
        assert task.created_at == custom_created_at

    def test_from_dict_without_created_at(self):
        """Test creating task from dictionary without created_at (should use default)."""
        data = {
            'owner_id': 123,
            'task_name': 'Test Task',
            'description': 'Test Description'
        }
        
        task = Task.from_dict(data)
        
        assert isinstance(task.created_at, str)
        assert len(task.created_at) > 0

    def test_roundtrip_conversion(self):
        """Test converting task to dict and back to task."""
        original_task = Task(
            owner_id=123,
            task_name="Test Task",
            description="Test Description",
            status="Ongoing",
            project_id=456,
            parent_task=789,
            type="subtask",
            collaborators=[1, 2, 3],
            subtasks=[10, 11, 12],
            priority=5,
            attachments=[{"url": "http://example.com/file.pdf", "name": "file.pdf"}]
        )
        original_task.id = 999
        
        # Convert to dict and back
        task_dict = original_task.to_dict()
        reconstructed_task = Task.from_dict(task_dict)
        
        # Check that all fields match
        assert reconstructed_task.id == original_task.id
        assert reconstructed_task.owner_id == original_task.owner_id
        assert reconstructed_task.task_name == original_task.task_name
        assert reconstructed_task.description == original_task.description
        assert reconstructed_task.status == original_task.status
        assert reconstructed_task.project_id == original_task.project_id
        assert reconstructed_task.parent_task == original_task.parent_task
        assert reconstructed_task.type == original_task.type
        assert reconstructed_task.collaborators == original_task.collaborators
        assert reconstructed_task.subtasks == original_task.subtasks
        assert reconstructed_task.priority == original_task.priority
        assert reconstructed_task.attachments == original_task.attachments
        assert reconstructed_task.created_at == original_task.created_at
        assert reconstructed_task.completed_at == original_task.completed_at

    def test_completed_at_field(self):
        """Test completed_at field handling."""
        # Test with None completed_at
        task = Task(task_name="Test Task")
        assert task.completed_at is None
        
        # Test with specific completed_at timestamp
        completed_timestamp = "2024-12-31T23:59:59+00:00"
        task_with_completed = Task(
            task_name="Completed Task",
            completed_at=completed_timestamp
        )
        assert task_with_completed.completed_at == completed_timestamp
        
        # Test to_dict includes completed_at
        task_dict = task_with_completed.to_dict()
        assert 'completed_at' in task_dict
        assert task_dict['completed_at'] == completed_timestamp
        
        # Test from_dict with completed_at
        data = {
            'task_name': 'Test Task',
            'completed_at': completed_timestamp
        }
        reconstructed_task = Task.from_dict(data)
        assert reconstructed_task.completed_at == completed_timestamp
