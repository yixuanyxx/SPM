import unittest
import sys
import os
import uuid
from datetime import datetime, UTC

# Add parent directory to path to find modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.user import User


class TestUserModel(unittest.TestCase):
    """Unit tests for the User model class."""

    def test_user_creation_with_defaults(self):
        """Test creating a user with default values."""
        user_id = uuid.uuid4()
        user = User(id=user_id)
        
        assert user.id == user_id
        assert user.userid == 0
        assert user.role == ""
        assert user.name == ""
        assert user.email == ""
        assert user.team_id is None
        assert user.dept_id is None
        assert user.notification_preferences == {"in_app": True, "email": True}

    def test_user_creation_with_values(self):
        """Test creating a user with specific values."""
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            userid=123,
            role="manager",
            name="John Doe",
            email="john.doe@example.com",
            team_id=1,
            dept_id=2,
            notification_preferences={"in_app": False, "email": True}
        )
        
        assert user.id == user_id
        assert user.userid == 123
        assert user.role == "manager"
        assert user.name == "John Doe"
        assert user.email == "john.doe@example.com"
        assert user.team_id == 1
        assert user.dept_id == 2
        assert user.notification_preferences == {"in_app": False, "email": True}

    def test_to_dict_with_all_fields(self):
        """Test converting user to dictionary with all fields."""
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            userid=123,
            role="staff",
            name="Jane Smith",
            email="jane.smith@example.com",
            team_id=5,
            dept_id=3,
            notification_preferences={"in_app": True, "email": False}
        )
        
        result = user.to_dict()
        
        expected = {
            'id': str(user_id),
            'userid': 123,
            'role': 'staff',
            'name': 'Jane Smith',
            'email': 'jane.smith@example.com',
            'team_id': 5,
            'dept_id': 3,
            'notification_preferences': {"in_app": True, "email": False}
        }
        
        assert result == expected

    def test_to_dict_with_minimal_fields(self):
        """Test converting user to dictionary with minimal fields."""
        user_id = uuid.uuid4()
        user = User(id=user_id)
        
        result = user.to_dict()
        
        assert result['id'] == str(user_id)
        assert result['userid'] == 0
        assert result['role'] == ""
        assert result['name'] == ""
        assert result['email'] == ""
        assert result['team_id'] is None
        assert result['dept_id'] is None
        assert result['notification_preferences'] == {"in_app": True, "email": True}

    def test_from_dict_basic(self):
        """Test creating user from dictionary with basic fields."""
        user_id = uuid.uuid4()
        data = {
            'id': str(user_id),
            'userid': 456,
            'role': 'admin',
            'name': 'Admin User',
            'email': 'admin@example.com',
            'team_id': 10,
            'dept_id': 5,
            'notification_preferences': {"in_app": True, "email": True}
        }
        
        user = User.from_dict(data)
        
        assert user.id == user_id
        assert user.userid == 456
        assert user.role == 'admin'
        assert user.name == 'Admin User'
        assert user.email == 'admin@example.com'
        assert user.team_id == 10
        assert user.dept_id == 5
        assert user.notification_preferences == {"in_app": True, "email": True}

    def test_from_dict_with_missing_fields(self):
        """Test creating user from dictionary with missing fields."""
        user_id = uuid.uuid4()
        data = {
            'id': str(user_id),
            'userid': 789,
            'name': 'Test User'
        }
        
        user = User.from_dict(data)
        
        assert user.id == user_id
        assert user.userid == 789
        assert user.name == 'Test User'
        assert user.role == ''  # Default value
        assert user.email == ''  # Default value
        assert user.team_id is None  # Default value
        assert user.dept_id is None  # Default value
        assert user.notification_preferences == {"in_app": True, "email": True}  # Default value

    def test_from_dict_with_none_values(self):
        """Test creating user from dictionary with None values."""
        user_id = uuid.uuid4()
        data = {
            'id': str(user_id),
            'userid': 123,
            'role': None,
            'name': None,
            'email': None,
            'team_id': None,
            'dept_id': None,
            'notification_preferences': None
        }
        
        user = User.from_dict(data)
        
        assert user.id == user_id
        assert user.userid == 123
        assert user.role == ''  # None converted to empty string
        assert user.name == ''  # None converted to empty string
        assert user.email == ''  # None converted to empty string
        assert user.team_id is None
        assert user.dept_id is None
        assert user.notification_preferences == {"in_app": True, "email": True}  # Default when None


    def test_from_dict_with_json_notification_preferences(self):
        """Test creating user from dictionary with JSON string notification preferences."""
        user_id = uuid.uuid4()
        data = {
            'id': str(user_id),
            'userid': 123,
            'notification_preferences': '{"in_app": false, "email": true}'
        }
        
        user = User.from_dict(data)
        
        assert user.id == user_id
        assert user.userid == 123
        assert user.notification_preferences == {"in_app": False, "email": True}

    def test_from_dict_with_invalid_json_notification_preferences(self):
        """Test creating user from dictionary with invalid JSON notification preferences."""
        user_id = uuid.uuid4()
        data = {
            'id': str(user_id),
            'userid': 123,
            'notification_preferences': 'invalid json'
        }
        
        user = User.from_dict(data)
        
        assert user.id == user_id
        assert user.userid == 123
        assert user.notification_preferences == {"in_app": True, "email": True}  # Default when JSON is invalid

    def test_roundtrip_conversion(self):
        """Test converting user to dict and back to user."""
        user_id = uuid.uuid4()
        original_user = User(
            id=user_id,
            userid=123,
            role="manager",
            name="John Doe",
            email="john.doe@example.com",
            team_id=1,
            dept_id=2,
            notification_preferences={"in_app": False, "email": True}
        )
        
        # Convert to dict and back
        user_dict = original_user.to_dict()
        reconstructed_user = User.from_dict(user_dict)
        
        # Check that all fields match
        assert reconstructed_user.id == original_user.id
        assert reconstructed_user.userid == original_user.userid
        assert reconstructed_user.role == original_user.role
        assert reconstructed_user.name == original_user.name
        assert reconstructed_user.email == original_user.email
        assert reconstructed_user.team_id == original_user.team_id
        assert reconstructed_user.dept_id == original_user.dept_id
        assert reconstructed_user.notification_preferences == original_user.notification_preferences

    # def test_user_with_special_characters(self):
    #     """Test user with special characters in name and email."""
    #     user_id = uuid.uuid4()
    #     special_name = "José María O'Connor-Smith"
    #     special_email = "josé.maría@example.com"
        
    #     user = User(
    #         id=user_id,
    #         userid=123,
    #         name=special_name,
    #         email=special_email
    #     )
        
    #     result = user.to_dict()
    #     assert result['name'] == special_name
    #     assert result['email'] == special_email
        
    #     # Test roundtrip
    #     reconstructed = User.from_dict(result)
    #     assert reconstructed.name == special_name
    #     assert reconstructed.email == special_email

    # def test_user_with_unicode_content(self):
    #     """Test user with unicode characters."""
    #     user_id = uuid.uuid4()
    #     unicode_name = "张三李四"
    #     unicode_email = "张三@example.com"
        
    #     user = User(
    #         id=user_id,
    #         userid=123,
    #         name=unicode_name,
    #         email=unicode_email
    #     )
        
    #     result = user.to_dict()
    #     assert result['name'] == unicode_name
    #     assert result['email'] == unicode_email
        
    #     # Test roundtrip
    #     reconstructed = User.from_dict(result)
    #     assert reconstructed.name == unicode_name
    #     assert reconstructed.email == unicode_email

    def test_user_with_long_content(self):
        """Test user with very long name and email."""
        user_id = uuid.uuid4()
        long_name = "This is a very long name that might cause issues in some systems. " * 10
        long_email = "very.long.email.address.that.might.cause.issues@very.long.domain.name.com"
        
        user = User(
            id=user_id,
            userid=123,
            name=long_name,
            email=long_email
        )
        
        result = user.to_dict()
        assert result['name'] == long_name
        assert result['email'] == long_email
        assert len(result['name']) > 500
        assert len(result['email']) > 50
        
        # Test roundtrip
        reconstructed = User.from_dict(result)
        assert reconstructed.name == long_name
        assert reconstructed.email == long_email


    def test_user_with_zero_values(self):
        """Test user with zero values for numeric fields."""
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            userid=0,
            team_id=0,
            dept_id=0
        )
        
        result = user.to_dict()
        assert result['userid'] == 0
        assert result['team_id'] == 0
        assert result['dept_id'] == 0
        
        # Test roundtrip
        reconstructed = User.from_dict(result)
        assert reconstructed.userid == 0
        assert reconstructed.team_id == 0
        assert reconstructed.dept_id == 0

    def test_user_with_empty_strings(self):
        """Test user with empty string values."""
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            role="",
            name="",
            email=""
        )
        
        result = user.to_dict()
        assert result['role'] == ""
        assert result['name'] == ""
        assert result['email'] == ""
        
        # Test roundtrip
        reconstructed = User.from_dict(result)
        assert reconstructed.role == ""
        assert reconstructed.name == ""
        assert reconstructed.email == ""


if __name__ == '__main__':
    unittest.main()
