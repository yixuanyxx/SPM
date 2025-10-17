import unittest
import sys
import os
from datetime import datetime, UTC

# Add parent directory to path to find modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.project import Project


class TestProjectModel(unittest.TestCase):
    """Unit tests for the Project model class."""

    def test_project_creation_with_defaults(self):
        """Test creating a project with default values."""
        project = Project()
        
        assert project.id is None
        assert project.owner_id == 0
        assert project.proj_name == ""
        assert project.collaborators is None
        assert project.tasks is None
        assert isinstance(project.created_at, str)

    def test_project_creation_with_values(self):
        """Test creating a project with specific values."""
        project = Project(
            owner_id=123,
            proj_name="Test Project",
            collaborators=[1, 2, 3],
            tasks=[10, 11, 12]
        )
        
        assert project.owner_id == 123
        assert project.proj_name == "Test Project"
        assert project.collaborators == [1, 2, 3]
        assert project.tasks == [10, 11, 12]

    def test_to_dict_without_id(self):
        """Test converting project to dictionary without ID."""
        project = Project(
            owner_id=123,
            proj_name="Test Project",
            collaborators=[1, 2, 3],
            tasks=[10, 11]
        )
        
        result = project.to_dict()
        
        expected = {
            'owner_id': 123,
            'proj_name': 'Test Project',
            'collaborators': [1, 2, 3],
            'tasks': [10, 11],
            'created_at': project.created_at
        }
        
        assert result == expected
        assert 'id' not in result

    def test_to_dict_with_id(self):
        """Test converting project to dictionary with ID."""
        project = Project(owner_id=123, proj_name="Test Project")
        project.id = 999
        
        result = project.to_dict()
        
        assert result['id'] == 999
        assert result['owner_id'] == 123
        assert result['proj_name'] == "Test Project"

    def test_to_dict_with_none_values(self):
        """Test converting project to dictionary with None values."""
        project = Project(owner_id=123, proj_name="Test Project")
        
        result = project.to_dict()
        
        assert result['collaborators'] is None
        assert result['tasks'] is None

    def test_from_dict_basic(self):
        """Test creating project from dictionary with basic fields."""
        data = {
            'id': 123,
            'owner_id': 456,
            'proj_name': 'Test Project',
            'collaborators': [1, 2, 3],
            'tasks': [10, 11, 12]
        }
        
        project = Project.from_dict(data)
        
        assert project.id == 123
        assert project.owner_id == 456
        assert project.proj_name == 'Test Project'
        assert project.collaborators == [1, 2, 3]
        assert project.tasks == [10, 11, 12]

    def test_from_dict_with_collaborators_string(self):
        """Test creating project from dictionary with comma-separated collaborators string."""
        data = {
            'owner_id': 123,
            'proj_name': 'Test Project',
            'collaborators': '1, 2, 3'
        }
        
        project = Project.from_dict(data)
        
        assert project.collaborators == [1, 2, 3]

    def test_from_dict_with_collaborators_list(self):
        """Test creating project from dictionary with collaborators list."""
        data = {
            'owner_id': 123,
            'proj_name': 'Test Project',
            'collaborators': [1, 2, 3]
        }
        
        project = Project.from_dict(data)
        
        assert project.collaborators == [1, 2, 3]

    def test_from_dict_with_empty_collaborators_string(self):
        """Test creating project from dictionary with empty collaborators string."""
        data = {
            'owner_id': 123,
            'proj_name': 'Test Project',
            'collaborators': ''
        }
        
        project = Project.from_dict(data)
        
        assert project.collaborators is None

    def test_from_dict_with_tasks_string(self):
        """Test creating project from dictionary with comma-separated tasks string."""
        data = {
            'owner_id': 123,
            'proj_name': 'Test Project',
            'tasks': '10, 11, 12'
        }
        
        project = Project.from_dict(data)
        
        assert project.tasks == [10, 11, 12]

    def test_from_dict_with_tasks_list(self):
        """Test creating project from dictionary with tasks list."""
        data = {
            'owner_id': 123,
            'proj_name': 'Test Project',
            'tasks': [10, 11, 12]
        }
        
        project = Project.from_dict(data)
        
        assert project.tasks == [10, 11, 12]

    def test_from_dict_with_empty_tasks_string(self):
        """Test creating project from dictionary with empty tasks string."""
        data = {
            'owner_id': 123,
            'proj_name': 'Test Project',
            'tasks': ''
        }
        
        project = Project.from_dict(data)
        
        assert project.tasks is None

    def test_from_dict_with_none_collaborators(self):
        """Test creating project from dictionary with None collaborators."""
        data = {
            'owner_id': 123,
            'proj_name': 'Test Project',
            'collaborators': None
        }
        
        project = Project.from_dict(data)
        
        assert project.collaborators is None

    def test_from_dict_with_none_tasks(self):
        """Test creating project from dictionary with None tasks."""
        data = {
            'owner_id': 123,
            'proj_name': 'Test Project',
            'tasks': None
        }
        
        project = Project.from_dict(data)
        
        assert project.tasks is None

    def test_from_dict_with_created_at(self):
        """Test creating project from dictionary with custom created_at."""
        custom_created_at = "2024-01-01T00:00:00+00:00"
        data = {
            'owner_id': 123,
            'proj_name': 'Test Project',
            'created_at': custom_created_at
        }
        
        project = Project.from_dict(data)
        
        assert project.created_at == custom_created_at

    def test_from_dict_without_created_at(self):
        """Test creating project from dictionary without created_at (should use default)."""
        data = {
            'owner_id': 123,
            'proj_name': 'Test Project'
        }
        
        project = Project.from_dict(data)
        
        assert isinstance(project.created_at, str)
        assert len(project.created_at) > 0

    def test_from_dict_with_string_owner_id(self):
        """Test creating project from dictionary with string owner_id."""
        data = {
            'owner_id': '123',
            'proj_name': 'Test Project'
        }
        
        project = Project.from_dict(data)
        
        assert project.owner_id == 123

    def test_from_dict_with_empty_proj_name(self):
        """Test creating project from dictionary with empty proj_name."""
        data = {
            'owner_id': 123,
            'proj_name': ''
        }
        
        project = Project.from_dict(data)
        
        assert project.proj_name == ''

    def test_from_dict_with_mixed_type_collaborators(self):
        """Test creating project from dictionary with mixed type collaborators."""
        data = {
            'owner_id': 123,
            'proj_name': 'Test Project',
            'collaborators': [1, 2, 3]
        }
        
        project = Project.from_dict(data)
        
        assert project.collaborators == [1, 2, 3]
        assert all(isinstance(c, int) for c in project.collaborators)

    def test_from_dict_with_mixed_type_tasks(self):
        """Test creating project from dictionary with mixed type tasks."""
        data = {
            'owner_id': 123,
            'proj_name': 'Test Project',
            'tasks': [10, 11, 12]
        }
        
        project = Project.from_dict(data)
        
        assert project.tasks == [10, 11, 12]
        assert all(isinstance(t, int) for t in project.tasks)

    def test_roundtrip_conversion(self):
        """Test converting project to dict and back to project."""
        original_project = Project(
            owner_id=123,
            proj_name="Test Project",
            collaborators=[1, 2, 3],
            tasks=[10, 11, 12]
        )
        original_project.id = 999
        
        # Convert to dict and back
        project_dict = original_project.to_dict()
        reconstructed_project = Project.from_dict(project_dict)
        
        # Check that all fields match
        assert reconstructed_project.id == original_project.id
        assert reconstructed_project.owner_id == original_project.owner_id
        assert reconstructed_project.proj_name == original_project.proj_name
        assert reconstructed_project.collaborators == original_project.collaborators
        assert reconstructed_project.tasks == original_project.tasks
        assert reconstructed_project.created_at == original_project.created_at

    def test_roundtrip_conversion_with_none_values(self):
        """Test converting project with None values to dict and back."""
        original_project = Project(
            owner_id=123,
            proj_name="Test Project"
        )
        original_project.id = 999
        
        # Convert to dict and back
        project_dict = original_project.to_dict()
        reconstructed_project = Project.from_dict(project_dict)
        
        # Check that all fields match
        assert reconstructed_project.id == original_project.id
        assert reconstructed_project.owner_id == original_project.owner_id
        assert reconstructed_project.proj_name == original_project.proj_name
        assert reconstructed_project.collaborators is None
        assert reconstructed_project.tasks is None
        assert reconstructed_project.created_at == original_project.created_at

