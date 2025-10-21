import unittest
import json
import sys
import os
from io import BytesIO

# Add parent directory to path to find modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.dept_service import DeptService
from models.dept import Department
from repo.supa_dept_repo import SupabaseDeptRepo

# Import the controller and service
from controllers.dept_controller import dept_bp, service


class TestDeptControllerIntegration(unittest.TestCase):
    """Integration tests for department controller endpoints."""

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
            self.repo = SupabaseDeptRepo()
            print(f"[SUCCESS] Supabase connection successful")
        except Exception as e:
            print(f"[ERROR] Supabase connection failed: {e}")
            raise
        
        # Replace the service's repository with our real repository
        service.repo = self.repo

        # Create a test Flask app
        from flask import Flask
        self.app = Flask(__name__)
        self.app.register_blueprint(dept_bp)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # # Clean up any existing test data BEFORE starting the test
        # print(f"\n=== Setting up test: {self._testMethodName} ===")
        # self.cleanup_test_data()
        
        # # Initialize tracking for departments created during this test
        # self.created_department_ids = []

    # def tearDown(self):
    #     """Clean up after each test method."""
    #     print(f"\n=== Cleaning up after test: {self._testMethodName} ===")
        
    #     # First, clean up departments created during this specific test
    #     # self.cleanup_created_departments()
        
    #     # Then do general cleanup
    #     self.cleanup_test_data()
    #     print(f"=== Cleanup completed for: {self._testMethodName} ===\n")
    
    # def cleanup_created_departments(self):
    #     """Clean up departments created during this specific test."""
    #     if hasattr(self, 'created_department_ids') and self.created_department_ids:
    #         print(f"Cleaning up {len(self.created_department_ids)} departments created during this test")
    #         for dept_id in self.created_department_ids:
    #             try:
    #                 if self.repo.delete_dept(dept_id):
    #                     print(f"[SUCCESS] Deleted department {dept_id} created during test")
    #                 else:
    #                     print(f"[FAILED] Failed to delete department {dept_id} created during test")
    #             except Exception as e:
    #                 print(f"[ERROR] Error deleting department {dept_id}: {e}")
    #         self.created_department_ids.clear()
    
    # def track_created_department(self, dept_id):
    #     """Track a department ID for cleanup after the test."""
    #     if hasattr(self, 'created_department_ids'):
    #         self.created_department_ids.append(dept_id)
    #         print(f"Tracking department {dept_id} for cleanup")

    # def cleanup_test_data(self):
    #     """Clean up test data from the database."""
    #     try:
    #         # Delete test departments with common test names
    #         test_names = [
    #             "Test Department",
    #             "Test Dept",
    #             "Integration Test Dept",
    #             "Test Department 1",
    #             "Test Department 2",
    #             "Updated Department",
    #             "Duplicate Test Dept",
    #             "Empty Name Test",
    #             "Staff Department",
    #             "Manager Department",
    #             "Original Department",
    #             "Patched Department",
    #             "Department to Delete",
    #             "Department with Teams",
    #             "Department 1",
    #             "Department 2",
    #             "Trimmed Department",
    #             "Trimmed Updated Department",
    #             "Department to Delete",
    #             "Department with Teams",
    #             "Complete Department",
    #             "Valid Department",
    #             "Invalid Department",
    #             "Same Department",
    #             "Different Department",
    #             "Type Test",
    #             "Timezone Test",
    #             "Test",
    #             "A" * 1000,  # Long name test
    #             "   ",  # Whitespace test
    #             "Trimmed Department",
    #             "Trimmed Updated Department"
    #         ]
            
    #         deleted_count = 0
            
    #         for name in test_names:
    #             # Find departments with this name
    #             depts = self.repo.find_by_name(name)
    #             if len(depts) > 0:
    #                 print(f"Found {len(depts)} departments with name '{name}'")
                
    #             # Delete each department found
    #             for dept in depts:
    #                 dept_id = dept['id']
    #                 if self.repo.delete_dept(dept_id):
    #                     deleted_count += 1
    #                     print(f"[SUCCESS] Deleted department {dept_id} with name '{name}'")
    #                 else:
    #                     print(f"[FAILED] Failed to delete department {dept_id} with name '{name}'")
            
    #         # Also clean up any departments created during tests that might not match our test names
    #         # This is a safety net to ensure we don't leave any test data
    #         try:
    #             all_depts = self.repo.get_all_depts()
    #             test_patterns = [
    #                 "Test", "test", "TEST",
    #                 "Department", "Dept", "dept",
    #                 "Integration", "integration",
    #                 "Updated", "updated",
    #                 "Duplicate", "duplicate",
    #                 "Original", "original",
    #                 "Patched", "patched",
    #                 "Trimmed", "trimmed",
    #                 "Valid", "valid",
    #                 "Invalid", "invalid"
    #             ]
                
    #             for dept in all_depts:
    #                 dept_name = dept.get('name', '')
    #                 should_delete = False
                    
    #                 # Check if department name contains any test patterns
    #                 for pattern in test_patterns:
    #                     if pattern in dept_name:
    #                         should_delete = True
    #                         break
                    
    #                 # Also delete departments with very long names (likely test data)
    #                 if len(dept_name) > 100:
    #                     should_delete = True
                    
    #                 # Also delete departments with only whitespace
    #                 if dept_name.strip() == "":
    #                     should_delete = True
                    
    #                 if should_delete:
    #                     dept_id = dept['id']
    #                     if self.repo.delete_dept(dept_id):
    #                         deleted_count += 1
    #                         print(f"[SUCCESS] Deleted test department {dept_id} with name '{dept_name}'")
    #                     else:
    #                         print(f"[FAILED] Failed to delete test department {dept_id} with name '{dept_name}'")
                            
    #         except Exception as cleanup_error:
    #             print(f"Warning: Error during pattern-based cleanup: {cleanup_error}")
            
    #         if deleted_count > 0:
    #             print(f"Cleanup completed: {deleted_count} departments deleted")
    #         else:
    #             print("No test departments found to clean up")
                
    #     except Exception as e:
    #         print(f"Warning: Could not clean up test data: {e}")
    #         import traceback
    #         traceback.print_exc()

    # # ==================== create_department Tests ====================
    
    # def test_create_department_success(self):
    #     """Test successful department creation with required field."""
    #     # Make request with required field
    #     response = self.client.post('/departments', json={
    #         "name": "Test Department"
    #     })
        
    #     # Assertions
    #     self.assertEqual(response.status_code, 201)
    #     data = json.loads(response.data)
    #     self.assertEqual(data["Code"], 201)
    #     self.assertIn("Department created! Department ID:", data["Message"])
    #     self.assertIn("data", data)
    #     self.assertEqual(data["data"]["name"], "Test Department")
    #     self.assertIn("id", data["data"])
    #     self.assertIn("created_at", data["data"])
        
    #     # Track the created department for cleanup
    #     dept_id = data["data"]["id"]
    #     self.track_created_department(dept_id)

    # def test_create_department_with_form_data(self):
    #     """Test department creation with form data instead of JSON."""
    #     # Make request with form data
    #     response = self.client.post('/departments', data={
    #         "name": "Test Dept"
    #     })
        
    #     # Assertions
    #     self.assertEqual(response.status_code, 201)
    #     data = json.loads(response.data)
    #     self.assertEqual(data["Code"], 201)
    #     self.assertEqual(data["data"]["name"], "Test Dept")
        
    #     # Track the created department for cleanup
    #     dept_id = data["data"]["id"]
    #     self.track_created_department(dept_id)

    # def test_create_department_duplicate_name(self):
    #     """Test department creation when department name already exists."""
    #     # First, create a department
    #     first_response = self.client.post('/departments', json={
    #         "name": "Duplicate Test Dept"
    #     })
    #     self.assertEqual(first_response.status_code, 201)
        
    #     # Track the first department for cleanup
    #     first_data = json.loads(first_response.data)
    #     first_dept_id = first_data["data"]["id"]
    #     self.track_created_department(first_dept_id)
        
    #     # Try to create another department with the same name
    #     response = self.client.post('/departments', json={
    #         "name": "Duplicate Test Dept"
    #     })
        
    #     # Assertions
    #     self.assertEqual(response.status_code, 200)
    #     data = json.loads(response.data)
    #     self.assertEqual(data["Code"], 200)
    #     self.assertIn("already exists", data["Message"])
    #     self.assertIn("Duplicate Test Dept", data["Message"])

    # def test_create_department_missing_name(self):
    #     """Test department creation fails when name is missing."""
    #     response = self.client.post('/departments', json={
    #         # name is missing
    #     })
        
    #     # Assertions
    #     self.assertEqual(response.status_code, 400)
    #     data = json.loads(response.data)
    #     self.assertEqual(data["Code"], 400)
    #     self.assertIn("Missing required field: name", data["Message"])

    # def test_create_department_empty_name(self):
    #     """Test department creation fails when name is empty."""
    #     response = self.client.post('/departments', json={
    #         "name": ""
    #     })
        
    #     # Assertions
    #     self.assertEqual(response.status_code, 400)
    #     data = json.loads(response.data)
    #     self.assertEqual(data["Code"], 400)
    #     self.assertIn("Missing required field", data["Message"])

    # def test_create_department_whitespace_name(self):
    #     """Test department creation fails when name is only whitespace."""
    #     response = self.client.post('/departments', json={
    #         "name": "   "
    #     })
        
    #     # Assertions
    #     self.assertEqual(response.status_code, 400)
    #     data = json.loads(response.data)
    #     self.assertEqual(data["Code"], 400)
    #     self.assertIn("Department name cannot be empty", data["Message"])

    # def test_create_department_name_trimmed(self):
    #     """Test department creation trims whitespace from name."""
    #     # Make request with name that has leading/trailing whitespace
    #     response = self.client.post('/departments', json={
    #         "name": "  Trimmed Department  "
    #     })
        
    #     # Assertions
    #     self.assertEqual(response.status_code, 201)
    #     data = json.loads(response.data)
    #     self.assertEqual(data["Code"], 201)
    #     self.assertEqual(data["data"]["name"], "Trimmed Department")  # Should be trimmed
        
    #     # Track the created department for cleanup
    #     dept_id = data["data"]["id"]
    #     self.track_created_department(dept_id)

    # def test_create_department_invalid_json(self):
    #     """Test department creation with invalid JSON."""
    #     response = self.client.post('/departments', 
    #         data="invalid json",
    #         content_type='application/json'
    #     )
        
    #     # Assertions
    #     self.assertEqual(response.status_code, 400)
    #     data = json.loads(response.data)
    #     self.assertEqual(data["Code"], 400)

    # ==================== get_all_departments Tests ====================
    
    def test_get_all_departments_success(self):
        """Test successfully retrieving all departments."""
        # Clean up any existing test data first
        # self.cleanup_test_data()
        
        # Make request
        response = self.client.get('/departments')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertIn("Retrieved", data["Message"])
        self.assertIn("data", data)
        self.assertIsInstance(data["data"], list)

    # ==================== get_department_by_id Tests ====================
    
    def test_get_department_by_id_success(self):
        """Test successfully retrieving a department by ID."""
        # Clean up any existing test data first
        # self.cleanup_test_data()
        
        dept_id = 1
        
        # Make request
        response = self.client.get(f'/departments/{dept_id}')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertEqual(data["data"]["id"], dept_id)

    def test_get_department_by_id_not_found(self):
        """Test get department by ID when department doesn't exist."""
        # Clean up any existing test data first
        # self.cleanup_test_data()
        
        # Make request with non-existent department
        response = self.client.get('/departments/999')
        
        # Assertions
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 404)
        self.assertIn("Department with ID 999 not found", data["Message"])

    def test_get_department_by_id_invalid_id(self):
        """Test get department by ID with invalid ID format."""
        # Make request with invalid ID
        response = self.client.get('/departments/invalid')
        
        # Assertions - Flask should return 404 for invalid route
        self.assertEqual(response.status_code, 404)

#     # ==================== update_department Tests ====================
    
#     def test_update_department_success(self):
#         """Test successful department update."""
#         # Clean up any existing test data first
#         self.cleanup_test_data()
        
#         # First, create a department
#         create_response = self.client.post('/departments', json={
#             "name": "Original Department"
#         })
#         self.assertEqual(create_response.status_code, 201)
#         create_data = json.loads(create_response.data)
#         dept_id = create_data["data"]["id"]
        
#         # Make update request
#         response = self.client.put(f'/departments/{dept_id}', json={
#             "name": "Updated Department"
#         })
        
#         # Assertions
#         self.assertEqual(response.status_code, 200)
#         data = json.loads(response.data)
#         self.assertEqual(data["Code"], 200)
#         self.assertIn("updated successfully", data["Message"])
#         self.assertEqual(data["data"]["name"], "Updated Department")

#     def test_update_department_patch_method(self):
#         """Test department update using PATCH method."""
#         # Clean up any existing test data first
#         self.cleanup_test_data()
        
#         # First, create a department
#         create_response = self.client.post('/departments', json={
#             "name": "Original Department"
#         })
#         self.assertEqual(create_response.status_code, 201)
#         create_data = json.loads(create_response.data)
#         dept_id = create_data["data"]["id"]
        
#         # Make update request using PATCH
#         response = self.client.patch(f'/departments/{dept_id}', json={
#             "name": "Patched Department"
#         })
        
#         # Assertions
#         self.assertEqual(response.status_code, 200)
#         data = json.loads(response.data)
#         self.assertEqual(data["Code"], 200)
#         self.assertEqual(data["data"]["name"], "Patched Department")

#     def test_update_department_not_found(self):
#         """Test update department when department doesn't exist."""
#         # Clean up any existing test data first
#         self.cleanup_test_data()
        
#         # Make request with non-existent department
#         response = self.client.put('/departments/999', json={
#             "name": "Updated Name"
#         })
        
#         # Assertions
#         self.assertEqual(response.status_code, 404)
#         data = json.loads(response.data)
#         self.assertEqual(data["Code"], 404)
#         self.assertIn("Department with ID 999 not found", data["Message"])

#     def test_update_department_no_fields(self):
#         """Test update department with no fields to update."""
#         # Clean up any existing test data first
#         self.cleanup_test_data()
        
#         # First, create a department
#         create_response = self.client.post('/departments', json={
#             "name": "Test Department"
#         })
#         self.assertEqual(create_response.status_code, 201)
#         create_data = json.loads(create_response.data)
#         dept_id = create_data["data"]["id"]
        
#         # Make request with no fields to update
#         response = self.client.put(f'/departments/{dept_id}', json={})
        
#         # Assertions
#         self.assertEqual(response.status_code, 400)
#         data = json.loads(response.data)
#         self.assertEqual(data["Code"], 400)
#         self.assertIn("No fields to update provided", data["Message"])

#     def test_update_department_duplicate_name(self):
#         """Test update department with name that already exists."""
#         # Clean up any existing test data first
#         self.cleanup_test_data()
        
#         # First, create two departments
#         dept1_response = self.client.post('/departments', json={
#             "name": "Department 1"
#         })
#         self.assertEqual(dept1_response.status_code, 201)
        
#         dept2_response = self.client.post('/departments', json={
#             "name": "Department 2"
#         })
#         self.assertEqual(dept2_response.status_code, 201)
#         dept2_data = json.loads(dept2_response.data)
#         dept2_id = dept2_data["data"]["id"]
        
#         # Try to update dept2 with dept1's name
#         response = self.client.put(f'/departments/{dept2_id}', json={
#             "name": "Department 1"
#         })
        
#         # Assertions
#         self.assertEqual(response.status_code, 400)
#         data = json.loads(response.data)
#         self.assertEqual(data["Code"], 400)
#         self.assertIn("already exists", data["Message"])

#     def test_update_department_empty_name(self):
#         """Test update department with empty name."""
#         # Clean up any existing test data first
#         self.cleanup_test_data()
        
#         # First, create a department
#         create_response = self.client.post('/departments', json={
#             "name": "Test Department"
#         })
#         self.assertEqual(create_response.status_code, 201)
#         create_data = json.loads(create_response.data)
#         dept_id = create_data["data"]["id"]
        
#         # Make request with empty name
#         response = self.client.put(f'/departments/{dept_id}', json={
#             "name": ""
#         })
        
#         # Assertions
#         self.assertEqual(response.status_code, 400)
#         data = json.loads(response.data)
#         self.assertEqual(data["Code"], 400)
#         self.assertIn("Department name cannot be empty", data["Message"])

#     def test_update_department_name_trimmed(self):
#         """Test update department trims whitespace from name."""
#         # Clean up any existing test data first
#         self.cleanup_test_data()
        
#         # First, create a department
#         create_response = self.client.post('/departments', json={
#             "name": "Original Department"
#         })
#         self.assertEqual(create_response.status_code, 201)
#         create_data = json.loads(create_response.data)
#         dept_id = create_data["data"]["id"]
        
#         # Make request with name that has leading/trailing whitespace
#         response = self.client.put(f'/departments/{dept_id}', json={
#             "name": "  Trimmed Updated Department  "
#         })
        
#         # Assertions
#         self.assertEqual(response.status_code, 200)
#         data = json.loads(response.data)
#         self.assertEqual(data["Code"], 200)
#         self.assertEqual(data["data"]["name"], "Trimmed Updated Department")  # Should be trimmed

#     # ==================== delete_department Tests ====================
    
#     def test_delete_department_success(self):
#         """Test successful department deletion."""
#         # Clean up any existing test data first
#         self.cleanup_test_data()
        
#         # First, create a department
#         create_response = self.client.post('/departments', json={
#             "name": "Department to Delete"
#         })
#         self.assertEqual(create_response.status_code, 201)
#         create_data = json.loads(create_response.data)
#         dept_id = create_data["data"]["id"]
        
#         # Make delete request
#         response = self.client.delete(f'/departments/{dept_id}')
        
#         # Assertions
#         self.assertEqual(response.status_code, 200)
#         data = json.loads(response.data)
#         self.assertEqual(data["Code"], 200)
#         self.assertIn("deleted successfully", data["Message"])
#         self.assertIn(str(dept_id), data["Message"])

#     def test_delete_department_not_found(self):
#         """Test delete department when department doesn't exist."""
#         # Clean up any existing test data first
#         self.cleanup_test_data()
        
#         # Make request with non-existent department
#         response = self.client.delete('/departments/999')
        
#         # Assertions
#         self.assertEqual(response.status_code, 404)
#         data = json.loads(response.data)
#         self.assertEqual(data["Code"], 404)
#         self.assertIn("Department with ID 999 not found", data["Message"])

#     def test_delete_department_invalid_id(self):
#         """Test delete department with invalid ID format."""
#         # Make request with invalid ID
#         response = self.client.delete('/departments/invalid')
        
#         # Assertions - Flask should return 404 for invalid route
#         self.assertEqual(response.status_code, 404)

#     # ==================== get_department_with_teams Tests ====================
    
#     def test_get_department_with_teams_success(self):
#         """Test successfully retrieving department with teams."""
#         # Clean up any existing test data first
#         self.cleanup_test_data()
        
#         # First, create a department
#         create_response = self.client.post('/departments', json={
#             "name": "Department with Teams"
#         })
#         self.assertEqual(create_response.status_code, 201)
#         create_data = json.loads(create_response.data)
#         dept_id = create_data["data"]["id"]
        
#         # Make request
#         response = self.client.get(f'/departments/{dept_id}/teams')
        
#         # Assertions
#         self.assertEqual(response.status_code, 200)
#         data = json.loads(response.data)
#         self.assertEqual(data["Code"], 200)
#         self.assertIn("Department with teams retrieved successfully", data["Message"])
#         self.assertIn("data", data)
#         self.assertEqual(data["data"]["id"], dept_id)
#         self.assertEqual(data["data"]["name"], "Department with Teams")

#     def test_get_department_with_teams_not_found(self):
#         """Test get department with teams when department doesn't exist."""
#         # Clean up any existing test data first
#         self.cleanup_test_data()
        
#         # Make request with non-existent department
#         response = self.client.get('/departments/999/teams')
        
#         # Assertions
#         self.assertEqual(response.status_code, 404)
#         data = json.loads(response.data)
#         self.assertEqual(data["Code"], 404)
#         self.assertIn("Department with ID 999 not found", data["Message"])

#     # ==================== Error Handling Tests ====================
    
#     def test_database_connection_error_handling(self):
#         """Test error handling when database connection fails."""
#         # This test would require mocking the repository to simulate connection failure
#         # For now, we'll test that the service handles errors gracefully
#         pass

#     def test_invalid_json_format(self):
#         """Test handling of invalid JSON in request body."""
#         response = self.client.post('/departments',
#             data="invalid json data",
#             content_type='application/json'
#         )
        
#         # Assertions
#         self.assertEqual(response.status_code, 400)
#         data = json.loads(response.data)
#         self.assertEqual(data["Code"], 400)

#     def test_malformed_request_data(self):
#         """Test handling of malformed request data."""
#         response = self.client.post('/departments',
#             data="name=Test&invalid=data",
#             content_type='application/x-www-form-urlencoded'
#         )
        
#         # This should still work as form data
#         self.assertEqual(response.status_code, 201)


if __name__ == "__main__":
    unittest.main()
