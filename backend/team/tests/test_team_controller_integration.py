import unittest
import json
import sys
import os

# Add parent directory to path to find modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.team_service import TeamService
from models.team import Team
from repo.supa_team_repo import SupabaseTeamRepo

# Import the controller and service
from controllers.team_controller import team_bp, service


class TestTeamControllerIntegration(unittest.TestCase):
    """Integration tests for team controller endpoints."""

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
            self.repo = SupabaseTeamRepo()
            print(f"[SUCCESS] Supabase connection successful")
        except Exception as e:
            print(f"[ERROR] Supabase connection failed: {e}")
            raise
        
        # Replace the service's repository with our real repository
        service.repo = self.repo

        # Create a test Flask app
        from flask import Flask
        self.app = Flask(__name__)
        self.app.register_blueprint(team_bp)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Clean up any existing test data
        # self.cleanup_test_data()

    # def tearDown(self):
    #     """Clean up after each test method."""
    #     self.cleanup_test_data()

    # def cleanup_test_data(self):
    #     """Clean up test data from the database."""
    #     try:
    #         # Delete test teams for common test department IDs
    #         test_dept_ids = [1, 2, 3, 999]  # Common test department IDs
    #         deleted_count = 0
            
    #         for dept_id in test_dept_ids:
    #             # Get teams for this department
    #             teams = self.repo.find_by_dept_id(dept_id)
    #             print(f"Found {len(teams)} teams for department {dept_id}")
                
    #             # Delete teams
    #             for team in teams:
    #                 team_id = team['id']
    #                 if self.repo.delete_team(team_id):
    #                     deleted_count += 1
    #                     print(f"✓ Deleted team {team_id} for department {dept_id}")
    #                 else:
    #                     print(f"✗ Failed to delete team {team_id} for department {dept_id}")
            
    #         if deleted_count > 0:
    #             print(f"Cleanup completed: {deleted_count} teams deleted")
    #         else:
    #             print("No teams found to clean up")
                
    #     except Exception as e:
    #         print(f"Warning: Could not clean up test data: {e}")
    #         import traceback
    #         traceback.print_exc()

    # ==================== get_all_teams Tests ====================
    
    def test_get_all_teams_success(self):
        """Test successfully retrieving all teams."""
        # Make request to get all teams
        response = self.client.get('/teams')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertIn("Retrieved", data["Message"])
        self.assertIn("data", data)
        self.assertIsInstance(data["data"], list)

    def test_get_all_teams_with_dept_info(self):
        """Test retrieving all teams with department information."""
        # Make request with include_dept_info=true
        response = self.client.get('/teams?include_dept_info=true')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertIn("data", data)
        
        # Check if department info is included (if dept table exists)
        if data["data"]:
            team = data["data"][0]
            # Department info might be present if dept table exists
            if "dept" in team:
                self.assertIn("id", team["dept"])
                self.assertIn("name", team["dept"])

    def test_get_all_teams_empty_database(self):
        """Test retrieving all teams when database is empty."""
        # Make request
        response = self.client.get('/teams')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertIn("Retrieved", data["Message"])
        self.assertIsInstance(data["data"], list)

    # ==================== get_team_by_id Tests ====================
    
    def test_get_team_by_id_success(self):
        """Test successfully retrieving a team by ID."""
        # Test with existing team IDs (5-9)
        test_team_ids = [5, 6, 7]
        
        for team_id in test_team_ids:
            response = self.client.get(f'/teams/{team_id}')
            if response.status_code == 200:
                data = json.loads(response.data)
                self.assertEqual(data["Code"], 200)
                self.assertEqual(data["Message"], "Team retrieved successfully")
                self.assertEqual(data["data"]["id"], team_id)
                break
        else:
            # If no existing teams found, test with a non-existent team
            response = self.client.get('/teams/999')
            # This should return 404
            self.assertEqual(response.status_code, 404)

    def test_get_team_by_id_with_dept_info(self):
        """Test retrieving a team by ID with department information."""
        # Test with existing team IDs (5-9)
        test_team_ids = [5, 6, 7]
        
        for team_id in test_team_ids:
            response = self.client.get(f'/teams/{team_id}?include_dept_info=true')
            if response.status_code == 200:
                data = json.loads(response.data)
                self.assertEqual(data["Code"], 200)
                self.assertEqual(data["data"]["id"], team_id)
                
                # Check if department info is included (if dept table exists)
                if "dept" in data["data"]:
                    self.assertIn("id", data["data"]["dept"])
                    self.assertIn("name", data["data"]["dept"])
                break
        else:
            # If no existing teams found, test with a non-existent team
            response = self.client.get('/teams/999?include_dept_info=true')
            # This should return 404
            self.assertEqual(response.status_code, 404)

    def test_get_team_by_id_not_found(self):
        """Test retrieving a team by ID when team doesn't exist."""
        # Make request with non-existent team ID
        response = self.client.get('/teams/999')
        
        # Assertions
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 404)
        self.assertIn("not found", data["Message"])

    def test_get_team_by_id_invalid_id(self):
        """Test retrieving a team with invalid ID format."""
        # Make request with invalid ID
        response = self.client.get('/teams/invalid')
        
        # Assertions - should return 404 due to Flask routing
        self.assertEqual(response.status_code, 404)

    # ==================== get_teams_by_dept_id Tests ====================
    
    def test_get_teams_by_dept_id_success(self):
        """Test successfully retrieving teams by department ID."""
        # Test with existing department IDs (5-7)
        test_dept_ids = [5, 6, 7]
        
        for dept_id in test_dept_ids:
            response = self.client.get(f'/teams/department/{dept_id}')
            if response.status_code == 200:
                data = json.loads(response.data)
                self.assertEqual(data["Code"], 200)
                self.assertIn("Retrieved", data["Message"])
                self.assertIn(f"department {dept_id}", data["Message"])
                self.assertIsInstance(data["data"], list)
                
                # Verify all returned teams belong to the department
                for team in data["data"]:
                    self.assertEqual(team["dept_id"], dept_id)
                break
        else:
            # If no existing department has teams, test with a department that should have no teams
            response = self.client.get('/teams/department/999')
            # This should return 200 with empty data
            self.assertEqual(response.status_code, 200)

    def test_get_teams_by_dept_id_with_dept_info(self):
        """Test retrieving teams by department ID with department information."""
        # Test with existing department IDs (5-7)
        test_dept_ids = [5, 6, 7]
        
        for dept_id in test_dept_ids:
            response = self.client.get(f'/teams/department/{dept_id}?include_dept_info=true')
            if response.status_code == 200:
                data = json.loads(response.data)
                self.assertEqual(data["Code"], 200)
                self.assertIn("data", data)
                
                # Check if department info is included (if dept table exists)
                if data["data"]:
                    team = data["data"][0]
                    if "dept" in team:
                        self.assertIn("id", team["dept"])
                        self.assertIn("name", team["dept"])
                break
        else:
            # If no existing department has teams, test with a department that should have no teams
            response = self.client.get('/teams/department/999?include_dept_info=true')
            # This should return 200 with empty data
            self.assertEqual(response.status_code, 200)

    def test_get_teams_by_dept_id_empty_department(self):
        """Test retrieving teams for a department with no teams."""
        # Make request for department with no teams
        response = self.client.get('/teams/department/999')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["Code"], 200)
        self.assertIn("Retrieved 0 team(s) for department 999", data["Message"])
        self.assertEqual(data["data"], [])

    def test_get_teams_by_dept_id_invalid_id(self):
        """Test retrieving teams with invalid department ID format."""
        # Make request with invalid department ID
        response = self.client.get('/teams/department/invalid')
        
        # Assertions - should return 404 due to Flask routing
        self.assertEqual(response.status_code, 404)

    # ==================== health_check Tests ====================
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get('/health')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "ok")


if __name__ == "__main__":
    unittest.main()
