import unittest
import sys
import os
from datetime import datetime, UTC

# Add parent directory to path to find modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.comment import Comment


class TestCommentModel(unittest.TestCase):
    """Unit tests for the Comment model class."""

    def test_comment_creation_with_defaults(self):
        """Test creating a comment with default values."""
        comment = Comment()
        
        assert comment.id is None
        assert comment.task_id == 0
        assert comment.user_id == 0
        assert comment.user_name == ""
        assert comment.user_role == ""
        assert comment.content == ""
        assert isinstance(comment.created_at, str)
        assert isinstance(comment.updated_at, str)

    def test_comment_creation_with_values(self):
        """Test creating a comment with specific values."""
        comment = Comment(
            task_id=123,
            user_id=456,
            user_name="John Doe",
            user_role="manager",
            content="This is a test comment"
        )
        
        assert comment.task_id == 123
        assert comment.user_id == 456
        assert comment.user_name == "John Doe"
        assert comment.user_role == "manager"
        assert comment.content == "This is a test comment"
        assert isinstance(comment.created_at, str)
        assert isinstance(comment.updated_at, str)

    def test_to_dict_without_id(self):
        """Test converting comment to dictionary without ID."""
        comment = Comment(
            task_id=123,
            user_id=456,
            user_name="John Doe",
            user_role="manager",
            content="This is a test comment"
        )
        
        result = comment.to_dict()
        
        expected = {
            'task_id': 123,
            'user_id': 456,
            'user_name': 'John Doe',
            'user_role': 'manager',
            'content': 'This is a test comment',
            'created_at': comment.created_at,
            'updated_at': comment.updated_at
        }
        
        assert result == expected
        assert 'id' not in result

    def test_to_dict_with_id(self):
        """Test converting comment to dictionary with ID."""
        comment = Comment(
            task_id=123,
            user_id=456,
            user_name="John Doe",
            content="This is a test comment"
        )
        comment.id = 999
        
        result = comment.to_dict()
        
        assert result['id'] == 999
        assert result['task_id'] == 123
        assert result['user_id'] == 456
        assert result['user_name'] == "John Doe"
        assert result['content'] == "This is a test comment"

    def test_from_dict_basic(self):
        """Test creating comment from dictionary with basic fields."""
        data = {
            'id': 123,
            'task_id': 456,
            'user_id': 789,
            'user_name': 'Jane Smith',
            'user_role': 'staff',
            'content': 'Test comment content',
            'created_at': '2024-01-01T00:00:00+00:00',
            'updated_at': '2024-01-01T00:00:00+00:00'
        }
        
        comment = Comment.from_dict(data)
        
        assert comment.id == 123
        assert comment.task_id == 456
        assert comment.user_id == 789
        assert comment.user_name == 'Jane Smith'
        assert comment.user_role == 'staff'
        assert comment.content == 'Test comment content'
        assert comment.created_at == '2024-01-01T00:00:00+00:00'
        assert comment.updated_at == '2024-01-01T00:00:00+00:00'

    def test_from_dict_with_missing_fields(self):
        """Test creating comment from dictionary with missing fields."""
        data = {
            'task_id': 123,
            'user_id': 456,
            'content': 'Test comment'
        }
        
        comment = Comment.from_dict(data)
        
        assert comment.task_id == 123
        assert comment.user_id == 456
        assert comment.content == 'Test comment'
        assert comment.user_name == ''  # Default value
        assert comment.user_role == ''  # Default value
        assert isinstance(comment.created_at, str)  # Generated timestamp
        assert isinstance(comment.updated_at, str)  # Generated timestamp

    def test_from_dict_with_none_id(self):
        """Test creating comment from dictionary with None ID."""
        data = {
            'id': None,
            'task_id': 123,
            'user_id': 456,
            'content': 'Test comment'
        }
        
        comment = Comment.from_dict(data)
        
        assert comment.id is None
        assert comment.task_id == 123
        assert comment.user_id == 456
        assert comment.content == 'Test comment'

    def test_from_dict_with_string_values(self):
        """Test creating comment from dictionary with string values that need conversion."""
        data = {
            'id': '123',
            'task_id': '456',
            'user_id': '789',
            'user_name': 'Test User',
            'user_role': 'manager',
            'content': 'Test content'
        }
        
        comment = Comment.from_dict(data)
        
        assert comment.id == 123
        assert comment.task_id == 456
        assert comment.user_id == 789
        assert comment.user_name == 'Test User'
        assert comment.user_role == 'manager'
        assert comment.content == 'Test content'

    def test_roundtrip_conversion(self):
        """Test converting comment to dict and back to comment."""
        original_comment = Comment(
            task_id=123,
            user_id=456,
            user_name="John Doe",
            user_role="manager",
            content="This is a test comment"
        )
        original_comment.id = 999
        
        # Convert to dict and back
        comment_dict = original_comment.to_dict()
        reconstructed_comment = Comment.from_dict(comment_dict)
        
        # Check that all fields match
        assert reconstructed_comment.id == original_comment.id
        assert reconstructed_comment.task_id == original_comment.task_id
        assert reconstructed_comment.user_id == original_comment.user_id
        assert reconstructed_comment.user_name == original_comment.user_name
        assert reconstructed_comment.user_role == original_comment.user_role
        assert reconstructed_comment.content == original_comment.content
        assert reconstructed_comment.created_at == original_comment.created_at
        assert reconstructed_comment.updated_at == original_comment.updated_at

    def test_created_at_timestamp_generation(self):
        """Test that created_at timestamp is generated when not provided."""
        comment = Comment(task_id=123, user_id=456, content="Test")
        
        # Should be a valid ISO format timestamp
        assert isinstance(comment.created_at, str)
        assert len(comment.created_at) > 0
        
        # Should be able to parse as datetime
        try:
            datetime.fromisoformat(comment.created_at.replace('Z', '+00:00'))
        except ValueError:
            self.fail("created_at is not a valid ISO format timestamp")

    def test_updated_at_timestamp_generation(self):
        """Test that updated_at timestamp is generated when not provided."""
        comment = Comment(task_id=123, user_id=456, content="Test")
        
        # Should be a valid ISO format timestamp
        assert isinstance(comment.updated_at, str)
        assert len(comment.updated_at) > 0
        
        # Should be able to parse as datetime
        try:
            datetime.fromisoformat(comment.updated_at.replace('Z', '+00:00'))
        except ValueError:
            self.fail("updated_at is not a valid ISO format timestamp")

    # def test_empty_string_handling(self):
    #     """Test handling of empty string values."""
    #     data = {
    #         'task_id': '',
    #         'user_id': '',
    #         'user_name': '',
    #         'user_role': '',
    #         'content': ''
    #     }
        
    #     comment = Comment.from_dict(data)
        
    #     # Empty strings should be converted to appropriate defaults
    #     assert comment.task_id == 0  # Empty string converted to 0
    #     assert comment.user_id == 0  # Empty string converted to 0
    #     assert comment.user_name == ''  # Empty string remains empty
    #     assert comment.user_role == ''  # Empty string remains empty
    #     assert comment.content == ''  # Empty string remains empty

    def test_comment_with_special_characters(self):
        """Test comment with special characters in content."""
        special_content = "This is a comment with special chars: @#$%^&*()_+-=[]{}|;':\",./<>?"
        comment = Comment(
            task_id=123,
            user_id=456,
            content=special_content
        )
        
        result = comment.to_dict()
        assert result['content'] == special_content
        
        # Test roundtrip
        reconstructed = Comment.from_dict(result)
        assert reconstructed.content == special_content

    def test_comment_with_unicode_content(self):
        """Test comment with unicode characters."""
        unicode_content = "This is a comment with unicode: 你好世界 🌍 émojis"
        comment = Comment(
            task_id=123,
            user_id=456,
            content=unicode_content
        )
        
        result = comment.to_dict()
        assert result['content'] == unicode_content
        
        # Test roundtrip
        reconstructed = Comment.from_dict(result)
        assert reconstructed.content == unicode_content

    def test_comment_with_long_content(self):
        """Test comment with very long content."""
        long_content = "This is a very long comment. " * 100  # 2000+ characters
        comment = Comment(
            task_id=123,
            user_id=456,
            content=long_content
        )
        
        result = comment.to_dict()
        assert result['content'] == long_content
        assert len(result['content']) > 2000
        
        # Test roundtrip
        reconstructed = Comment.from_dict(result)
        assert reconstructed.content == long_content
