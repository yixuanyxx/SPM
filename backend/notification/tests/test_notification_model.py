import unittest
from datetime import datetime, UTC
from unittest.mock import patch
import sys
import os

# Add the parent directory to the path to import the model
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.notification import Notification


class TestNotificationModel(unittest.TestCase):
    """Test cases for the Notification model"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.sample_data = {
            'id': 1,
            'userid': 123,
            'notification': 'Test notification message',
            'created_at': '2024-01-15T10:30:00.000Z',
            'is_read': False,
            'notification_type': 'task_assigned',
            'related_task_id': 456
        }
    
    def test_notification_creation_with_defaults(self):
        """Test creating a notification with default values"""
        notification = Notification()
        
        self.assertIsNone(notification.id)
        self.assertEqual(notification.userid, 0)
        self.assertEqual(notification.notification, "")
        self.assertIsInstance(notification.created_at, str)
        self.assertFalse(notification.is_read)
        self.assertEqual(notification.notification_type, "general")
        self.assertIsNone(notification.related_task_id)
    
    def test_notification_creation_with_custom_values(self):
        """Test creating a notification with custom values"""
        notification = Notification(
            userid=123,
            notification="Custom notification",
            is_read=True,
            notification_type="task_updated",
            related_task_id=789
        )
        
        self.assertEqual(notification.userid, 123)
        self.assertEqual(notification.notification, "Custom notification")
        self.assertTrue(notification.is_read)
        self.assertEqual(notification.notification_type, "task_updated")
        self.assertEqual(notification.related_task_id, 789)
        self.assertIsInstance(notification.created_at, str)
    
    # def test_notification_creation_with_id_set_after(self):
    #     """Test setting ID after creation"""
    #     notification = Notification(userid=123, notification="Test")
    #     notification.id = 999
        
    #     self.assertEqual(notification.id, 999)
    
    def test_to_dict_without_id(self):
        """Test converting notification to dictionary without ID"""
        notification = Notification(
            userid=123,
            notification="Test notification",
            is_read=True,
            notification_type="task_assigned",
            related_task_id=456
        )
        
        result = notification.to_dict()
        
        expected = {
            'userid': 123,
            'notification': 'Test notification',
            'is_read': True,
            'notification_type': 'task_assigned',
            'related_task_id': 456
        }
        
        # Check that all expected keys are present
        for key in expected:
            self.assertEqual(result[key], expected[key])
        
        # Check that created_at is present and is a string
        self.assertIn('created_at', result)
        self.assertIsInstance(result['created_at'], str)
        
        # ID should not be present since it's None
        self.assertNotIn('id', result)
    
    def test_to_dict_with_id(self):
        """Test converting notification to dictionary with ID"""
        notification = Notification(
            userid=123,
            notification="Test notification"
        )
        notification.id = 999
        
        result = notification.to_dict()
        
        self.assertEqual(result['id'], 999)
        self.assertEqual(result['userid'], 123)
        self.assertEqual(result['notification'], 'Test notification')
    
    def test_from_dict_complete_data(self):
        """Test creating notification from complete dictionary data"""
        data = {
            'id': 1,
            'userid': 123,
            'notification': 'Test notification',
            'created_at': '2024-01-15T10:30:00.000Z',
            'is_read': True,
            'notification_type': 'task_assigned',
            'related_task_id': 456
        }
        
        notification = Notification.from_dict(data)
        
        self.assertEqual(notification.id, 1)
        self.assertEqual(notification.userid, 123)
        self.assertEqual(notification.notification, 'Test notification')
        self.assertEqual(notification.created_at, '2024-01-15T10:30:00.000Z')
        self.assertTrue(notification.is_read)
        self.assertEqual(notification.notification_type, 'task_assigned')
        self.assertEqual(notification.related_task_id, 456)
    
    def test_from_dict_minimal_data(self):
        """Test creating notification from minimal dictionary data"""
        data = {
            'userid': 123,
            'notification': 'Test notification'
        }
        
        notification = Notification.from_dict(data)
        
        self.assertIsNone(notification.id)
        self.assertEqual(notification.userid, 123)
        self.assertEqual(notification.notification, 'Test notification')
        self.assertIsInstance(notification.created_at, str)
        self.assertFalse(notification.is_read)
        self.assertEqual(notification.notification_type, 'general')
        self.assertIsNone(notification.related_task_id)
    
    def test_from_dict_with_none_values(self):
        """Test creating notification with None values"""
        data = {
            'userid': 123,
            'notification': 'Test notification',
            'related_task_id': None
        }
        
        notification = Notification.from_dict(data)
        
        self.assertEqual(notification.userid, 123)
        self.assertEqual(notification.notification, 'Test notification')
        self.assertIsNone(notification.related_task_id)
    
    def test_from_dict_type_conversion(self):
        """Test type conversion in from_dict method"""
        data = {
            'userid': '123',  # String that should be converted to int
            'notification': 12345,  # Number that should be converted to string
            'is_read': 1,  # Number that should be converted to bool
            'notification_type': 999,  # Number that should be converted to string
            'related_task_id': '456'  # String that should be converted to int
        }
        
        notification = Notification.from_dict(data)
        
        self.assertEqual(notification.userid, 123)
        self.assertEqual(notification.notification, '12345')
        self.assertTrue(notification.is_read)
        self.assertEqual(notification.notification_type, '999')
        self.assertEqual(notification.related_task_id, 456)
    
    def test_from_dict_missing_keys(self):
        """Test from_dict with missing keys uses defaults"""
        data = {}
        
        notification = Notification.from_dict(data)
        
        self.assertEqual(notification.userid, 0)
        self.assertEqual(notification.notification, '')
        self.assertFalse(notification.is_read)
        self.assertEqual(notification.notification_type, 'general')
        self.assertIsNone(notification.related_task_id)
        self.assertIsInstance(notification.created_at, str)
    
    def test_round_trip_conversion(self):
        """Test that to_dict and from_dict are inverse operations"""
        original = Notification(
            userid=123,
            notification="Test notification",
            is_read=True,
            notification_type="task_updated",
            related_task_id=789
        )
        original.id = 999
        
        # Convert to dict and back
        data = original.to_dict()
        restored = Notification.from_dict(data)
        
        self.assertEqual(restored.id, original.id)
        self.assertEqual(restored.userid, original.userid)
        self.assertEqual(restored.notification, original.notification)
        self.assertEqual(restored.created_at, original.created_at)
        self.assertEqual(restored.is_read, original.is_read)
        self.assertEqual(restored.notification_type, original.notification_type)
        self.assertEqual(restored.related_task_id, original.related_task_id)
    
    def test_created_at_auto_generation(self):
        """Test that created_at is automatically generated"""
        with patch('models.notification.datetime') as mock_datetime:
            mock_now = datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC)
            mock_datetime.now.return_value = mock_now
            mock_datetime.now.UTC = UTC
            
            notification = Notification()
            
            self.assertEqual(notification.created_at, mock_now.isoformat())
    
    def test_created_at_auto_generation_in_from_dict(self):
        """Test that created_at is auto-generated when missing in from_dict"""
        with patch('models.notification.datetime') as mock_datetime:
            mock_now = datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC)
            mock_datetime.now.return_value = mock_now
            mock_datetime.now.UTC = UTC
            
            data = {'userid': 123}
            notification = Notification.from_dict(data)
            
            self.assertEqual(notification.created_at, mock_now.isoformat())
    
    def test_edge_case_empty_strings(self):
        """Test handling of empty strings"""
        notification = Notification(
            userid=0,
            notification="",
            notification_type=""
        )
        
        self.assertEqual(notification.userid, 0)
        self.assertEqual(notification.notification, "")
        self.assertEqual(notification.notification_type, "")
    
    def test_edge_case_zero_values(self):
        """Test handling of zero values"""
        notification = Notification(
            userid=0,
            related_task_id=0
        )
        
        self.assertEqual(notification.userid, 0)
        self.assertEqual(notification.related_task_id, 0)
    
    def test_boolean_edge_cases(self):
        """Test boolean conversion edge cases"""
        # Test various truthy/falsy values
        test_cases = [
            (True, True),
            (False, False),
            (1, True),
            (0, False),
            ("true", True),
            ("false", True),  # Non-empty string is truthy
            ("", False),
            (None, False)
        ]
        
        for input_val, expected in test_cases:
            with self.subTest(input_val=input_val):
                data = {'is_read': input_val}
                notification = Notification.from_dict(data)
                self.assertEqual(notification.is_read, expected)
    
    def test_string_conversion_edge_cases(self):
        """Test string conversion for various input types"""
        test_cases = [
            (123, "123"),
            ("hello", "hello"),
            (None, ""),
            (True, "True"),
            (False, "False")
        ]
        
        for input_val, expected in test_cases:
            with self.subTest(input_val=input_val):
                data = {'notification': input_val}
                notification = Notification.from_dict(data)
                self.assertEqual(notification.notification, expected)
    
    def test_integer_conversion_edge_cases(self):
        """Test integer conversion for various input types"""
        test_cases = [
            ("123", 123),
            (123, 123),
            (123.45, 123),
            (None, 0),
            ('', 0)
        ]
        
        for input_val, expected in test_cases:
            with self.subTest(input_val=input_val):
                data = {'userid': input_val}
                notification = Notification.from_dict(data)
                self.assertEqual(notification.userid, expected)


if __name__ == '__main__':
    unittest.main()
