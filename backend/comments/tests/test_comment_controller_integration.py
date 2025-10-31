import unittest
import json
import sys
import os
from io import BytesIO

# Add parent directory to path to find modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.comment_service import CommentService
from models.comment import Comment
from repo.comment_repo import CommentRepo

# Import the controller and service
from controllers.comment_controller import comment_bp, service


class TestCommentControllerIntegration(unittest.TestCase):
    """Integration tests for comment controller endpoints."""

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
            self.repo = CommentRepo()
            print(f"[SUCCESS] Supabase connection successful")
        except Exception as e:
            print(f"[ERROR] Supabase connection failed: {e}")
            raise
        
        # Replace the service's repository with our real repository
        service.repo = self.repo

        # Create a test Flask app
        from flask import Flask
        self.app = Flask(__name__)
        self.app.register_blueprint(comment_bp)
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
            # Delete test comments for common test task IDs
            test_task_ids = [284, 285, 999]  # Common test task IDs
            deleted_count = 0
            
            for task_id in test_task_ids:
                # Get comments for this task
                comments = self.repo.find_by_task(task_id)
                print(f"Found {len(comments)} comments for task {task_id}")
                
                # Delete comments
                for comment in comments:
                    comment_id = comment['id']
                    if self.repo.delete_comment(comment_id):
                        deleted_count += 1
                        print(f"Deleted comment {comment_id} for task {task_id}")
                    else:
                        print(f"Failed to delete comment {comment_id} for task {task_id}")
            
            if deleted_count > 0:
                print(f"Cleanup completed: {deleted_count} comments deleted")
            else:
                print("No comments found to clean up")
                
        except Exception as e:
            print(f"Warning: Could not clean up test data: {e}")
            import traceback
            traceback.print_exc()

    # ==================== create_comment Tests ====================
    
    def test_create_comment_success(self):
        """Test successful comment creation with all required fields."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Make request with required fields
        response = self.client.post('/comments/create', json={
            "task_id": 284,
            "user_id": 297,
            "user_name": "Test User",
            "user_role": "manager",
            "content": "This is a test comment"
        })
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 201)
        self.assertIn("Comment created! Comment ID:", data["Message"])
        self.assertIn("data", data)
        self.assertEqual(data["data"]["task_id"], 284)
        self.assertEqual(data["data"]["user_id"], 297)
        self.assertEqual(data["data"]["content"], "This is a test comment")

    def test_create_comment_with_minimal_fields(self):
        """Test comment creation with only required fields."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Make request with only required fields
        response = self.client.post('/comments/create', json={
            "task_id": 284,
            "user_id": 297,
            "content": "Minimal comment"
        })
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 201)
        self.assertEqual(data["data"]["task_id"], 284)
        self.assertEqual(data["data"]["user_id"], 297)
        self.assertEqual(data["data"]["content"], "Minimal comment")

    def test_create_comment_missing_task_id(self):
        """Test comment creation fails when task_id is missing."""
        response = self.client.post('/comments/create', json={
            "user_id": 297,
            "content": "Test comment"
            # task_id is missing
        })
        
        # Assertions
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 400)
        self.assertIn("Missing required fields", data["Message"])

    def test_create_comment_missing_user_id(self):
        """Test comment creation fails when user_id is missing."""
        response = self.client.post('/comments/create', json={
            "task_id": 284,
            "content": "Test comment"
            # user_id is missing
        })
        
        # Assertions
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 400)
        self.assertIn("Missing required fields", data["Message"])

    def test_create_comment_missing_content(self):
        """Test comment creation fails when content is missing."""
        response = self.client.post('/comments/create', json={
            "task_id": 284,
            "user_id": 297
            # content is missing
        })
        
        # Assertions
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 400)
        self.assertIn("Missing required fields", data["Message"])


    def test_create_comment_with_unicode_content(self):
        """Test comment creation with unicode characters."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        unicode_content = "Comment with unicode: 你好世界 🌍 émojis"
        response = self.client.post('/comments/create', json={
            "task_id": 284,
            "user_id": 297,
            "content": unicode_content
        })
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 201)
        self.assertEqual(data["data"]["content"], unicode_content)

    # ==================== get_task_comments Tests ====================
    
    def test_get_task_comments_success(self):
        """Test successfully retrieving comments for a task."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create some comments for the task
        comment1_response = self.client.post('/comments/create', json={
            "task_id": 284,
            "user_id": 297,
            "content": "First comment"
        })
        self.assertEqual(comment1_response.status_code, 201)
        
        comment2_response = self.client.post('/comments/create', json={
            "task_id": 284,
            "user_id": 297,
            "content": "Second comment"
        })
        self.assertEqual(comment2_response.status_code, 201)
        
        # Make request
        response = self.client.get('/comments/task/284')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertEqual(data["Message"], "Success")
        self.assertIn("data", data)
        self.assertEqual(len(data["data"]), 2)

    def test_get_task_comments_not_found(self):
        """Test get task comments when no comments found."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Make request for task with no comments
        response = self.client.get('/comments/task/999')
        
        # Assertions
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 404)
        self.assertIn("No comments found for task ID 999", data["Message"])

    # ==================== get_comment Tests ====================
    
    def test_get_comment_success(self):
        """Test successfully retrieving a single comment."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create a comment
        create_response = self.client.post('/comments/create', json={
            "task_id": 284,
            "user_id": 297,
            "user_name": "Test User",
            "content": "Test comment"
        })
        self.assertEqual(create_response.status_code, 201)
        create_data = json.loads(create_response.data)
        comment_id = create_data["data"]["id"]
        
        # Make request
        response = self.client.get(f'/comments/{comment_id}')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertEqual(data["Message"], "Success")
        self.assertIn("data", data)
        self.assertEqual(data["data"]["id"], comment_id)
        self.assertEqual(data["data"]["content"], "Test comment")

    def test_get_comment_not_found(self):
        """Test get comment when comment doesn't exist."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Make request with non-existent comment
        response = self.client.get('/comments/999')
        
        # Assertions
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 404)
        self.assertIn("Comment with ID 999 not found", data["Message"])

    def test_get_comment_invalid_id(self):
        """Test get comment with invalid ID format."""
        # Make request with invalid ID
        response = self.client.get('/comments/invalid')
        
        # Assertions - should return 404 due to Flask routing
        self.assertEqual(response.status_code, 404)

    def test_get_comment_with_all_fields(self):
        """Test retrieving a comment with all fields populated."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create a comment with all fields
        create_response = self.client.post('/comments/create', json={
            "task_id": 284,
            "user_id": 297,
            "user_name": "Test User",
            "user_role": "manager",
            "content": "Complete test comment with all fields"
        })
        self.assertEqual(create_response.status_code, 201)
        create_data = json.loads(create_response.data)
        comment_id = create_data["data"]["id"]
        
        # Make request
        response = self.client.get(f'/comments/{comment_id}')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertEqual(data["Message"], "Success")
        self.assertIn("data", data)
        
        # Verify all fields are present
        comment_data = data["data"]
        self.assertEqual(comment_data["id"], comment_id)
        self.assertEqual(comment_data["task_id"], 284)
        self.assertEqual(comment_data["user_id"], 297)
        self.assertEqual(comment_data["user_name"], "Test User")
        self.assertEqual(comment_data["user_role"], "manager")
        self.assertEqual(comment_data["content"], "Complete test comment with all fields")
        self.assertIn("created_at", comment_data)

    def test_get_comment_with_unicode_content(self):
        """Test retrieving a comment with unicode content."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        unicode_content = "Test comment with unicode: 测试 🚀 émojis"
        
        # First, create a comment with unicode content
        create_response = self.client.post('/comments/create', json={
            "task_id": 284,
            "user_id": 297,
            "user_name": "Unicode User",
            "content": unicode_content
        })
        self.assertEqual(create_response.status_code, 201)
        create_data = json.loads(create_response.data)
        comment_id = create_data["data"]["id"]
        
        # Make request
        response = self.client.get(f'/comments/{comment_id}')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertEqual(data["data"]["content"], unicode_content)

    def test_get_comment_with_long_content(self):
        """Test retrieving a comment with very long content."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        long_content = "A" * 1000  # 1000 character content
        
        # First, create a comment with long content
        create_response = self.client.post('/comments/create', json={
            "task_id": 284,
            "user_id": 297,
            "user_name": "Long Content User",
            "content": long_content
        })
        self.assertEqual(create_response.status_code, 201)
        create_data = json.loads(create_response.data)
        comment_id = create_data["data"]["id"]
        
        # Make request
        response = self.client.get(f'/comments/{comment_id}')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertEqual(data["data"]["content"], long_content)
        self.assertEqual(len(data["data"]["content"]), 1000)

    def test_get_comment_with_special_characters(self):
        """Test retrieving a comment with special characters."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        special_content = "Comment with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?`~"
        
        # First, create a comment with special characters
        create_response = self.client.post('/comments/create', json={
            "task_id": 284,
            "user_id": 297,
            "user_name": "Special User",
            "content": special_content
        })
        self.assertEqual(create_response.status_code, 201)
        create_data = json.loads(create_response.data)
        comment_id = create_data["data"]["id"]
        
        # Make request
        response = self.client.get(f'/comments/{comment_id}')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertEqual(data["data"]["content"], special_content)

    def test_get_comment_negative_id(self):
        """Test get comment with negative ID."""
        # Make request with negative ID
        response = self.client.get('/comments/-1')
        
        # Assertions - should return 404 due to Flask routing
        self.assertEqual(response.status_code, 404)

    def test_get_comment_zero_id(self):
        """Test get comment with zero ID."""
        # Make request with zero ID
        response = self.client.get('/comments/0')
        
        # Assertions - should return 404 (assuming no comment with ID 0)
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 404)
        self.assertIn("Comment with ID 0 not found", data["Message"])

    def test_get_comment_very_large_id(self):
        """Test get comment with very large ID that doesn't exist."""
        # Make request with very large ID
        response = self.client.get('/comments/999999')
        
        # Assertions - should return 404, not 500
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 404)
        self.assertIn("Comment with ID 999999 not found", data["Message"])

    # ==================== update_comment Tests ====================
    
    def test_update_comment_success(self):
        """Test successful comment update."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create a comment
        create_response = self.client.post('/comments/create', json={
            "task_id": 284,
            "user_id": 297,
            "content": "Original content"
        })
        self.assertEqual(create_response.status_code, 201)
        create_data = json.loads(create_response.data)
        comment_id = create_data["data"]["id"]
        
        # Update the comment
        response = self.client.put(f'/comments/{comment_id}', json={
            "content": "Updated content"
        })
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertIn("updated successfully", data["Message"])
        self.assertEqual(data["data"]["content"], "Updated content")

    def test_update_comment_missing_content(self):
        """Test update comment fails when content is missing."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create a comment
        create_response = self.client.post('/comments/create', json={
            "task_id": 284,
            "user_id": 297,
            "content": "Original content"
        })
        self.assertEqual(create_response.status_code, 201)
        create_data = json.loads(create_response.data)
        comment_id = create_data["data"]["id"]
        
        # Try to update without content
        response = self.client.put(f'/comments/{comment_id}', json={})
        
        # Assertions
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 400)
        self.assertIn("Content is required", data["Message"])

    def test_update_comment_not_found(self):
        """Test update comment fails when comment doesn't exist."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Make request with non-existent comment
        response = self.client.put('/comments/999', json={
            "content": "Updated content"
        })
        
        # Assertions
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 404)
        self.assertIn("Comment with ID 999 not found", data["Message"])

    # ==================== delete_comment Tests ====================
    
    def test_delete_comment_success(self):
        """Test successful comment deletion."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # First, create a comment
        create_response = self.client.post('/comments/create', json={
            "task_id": 284,
            "user_id": 297,
            "content": "Comment to delete"
        })
        self.assertEqual(create_response.status_code, 201)
        create_data = json.loads(create_response.data)
        comment_id = create_data["data"]["id"]
        
        # Delete the comment
        response = self.client.delete(f'/comments/{comment_id}')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertIn("deleted successfully", data["Message"])
        
        # Verify comment is actually deleted
        get_response = self.client.get(f'/comments/{comment_id}')
        self.assertEqual(get_response.status_code, 404)

    def test_delete_comment_not_found(self):
        """Test delete comment fails when comment doesn't exist."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Make request with non-existent comment
        response = self.client.delete('/comments/999')
        
        # Assertions
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 404)
        self.assertIn("Comment with ID 999 not found", data["Message"])

    def test_delete_comment_very_large_id(self):
        """Test delete comment with very large ID that doesn't exist."""
        # Make request with very large ID
        response = self.client.delete('/comments/999999')
        
        # Assertions - should return 404, not 500
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 404)
        self.assertIn("Comment with ID 999999 not found", data["Message"])

    def test_update_comment_very_large_id(self):
        """Test update comment with very large ID that doesn't exist."""
        # Make request with very large ID
        response = self.client.put('/comments/999999', json={
            "content": "Updated content"
        })
        
        # Assertions - should return 404, not 500
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 404)
        self.assertIn("Comment with ID 999999 not found", data["Message"])

    # ==================== health Tests ====================
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get('/comments/health')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "Comments service is running")

    # ==================== Multiple Comments Tests ====================
    
    def test_multiple_comments_same_task(self):
        """Test creating and retrieving multiple comments for the same task."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Create multiple comments for the same task
        comments_data = [
            {"user_id": 297, "user_name": "User 1", "content": "First comment"},
            {"user_id": 297, "user_name": "User 2", "content": "Second comment"},
            {"user_id": 297, "user_name": "User 3", "content": "Third comment"}
        ]
        
        created_comment_ids = []
        for comment_data in comments_data:
            response = self.client.post('/comments/create', json={
                "task_id": 284,
                **comment_data
            })
            self.assertEqual(response.status_code, 201)
            data = json.loads(response.data)
            created_comment_ids.append(data["data"]["id"])
        
        # Retrieve all comments for the task
        response = self.client.get('/comments/task/284')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertEqual(len(data["data"]), 3)
        
        # Verify all comments are present
        retrieved_ids = [comment["id"] for comment in data["data"]]
        for comment_id in created_comment_ids:
            self.assertIn(comment_id, retrieved_ids)

    def test_comments_different_tasks(self):
        """Test comments for different tasks are isolated."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Create comments for different tasks
        self.client.post('/comments/create', json={
            "task_id": 284,
            "user_id": 297,
            "content": "Comment for task 284"
        })
        
        self.client.post('/comments/create', json={
            "task_id": 285,
            "user_id": 297,
            "content": "Comment for task 285"
        })
        
        # Get comments for task 1
        response1 = self.client.get('/comments/task/284')
        self.assertEqual(response1.status_code, 200)
        data1 = json.loads(response1.data)
        self.assertEqual(len(data1["data"]), 1)
        self.assertEqual(data1["data"][0]["content"], "Comment for task 284")
        
        # Get comments for task 2
        response2 = self.client.get('/comments/task/285')
        self.assertEqual(response2.status_code, 200)
        data2 = json.loads(response2.data)
        self.assertEqual(len(data2["data"]), 1)
        self.assertEqual(data2["data"][0]["content"], "Comment for task 285")


if __name__ == "__main__":
    unittest.main()
