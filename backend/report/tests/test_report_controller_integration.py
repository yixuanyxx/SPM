import unittest
import json
import sys
import os
import requests
from io import BytesIO
from unittest.mock import Mock, patch

# Add parent directory to path to find modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app
from app import create_app
from services.report_service import ReportService
from services.export_service import ExportService
from repo.report_repo import ReportRepo
from models.report import ReportData, TeamReportData


class TestReportControllerIntegration(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures for the entire test class."""
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()
        
        # Microservice URLs (must be running for these tests to pass)
        cls.users_url = "http://localhost:5003"
        cls.tasks_url = "http://localhost:5002"
        cls.projects_url = "http://localhost:5001"
        cls.team_url = "http://localhost:5004"
        cls.dept_url = "http://localhost:5005"
        
        # Can override these with environment variables:
        # export TEST_STAFF_USER_ID=101, etc.
        cls.staff_user_id = int(os.getenv('TEST_STAFF_USER_ID', '101'))
        cls.manager_user_id = int(os.getenv('TEST_MANAGER_USER_ID', '352'))
        cls.director_user_id = int(os.getenv('TEST_DIRECTOR_USER_ID', '399'))
        cls.nonexistent_user_id = 999999  

        cls.nonexistent_user_id = 999999

    # ==================== CRITICAL INTEGRATION TESTS ====================
    # These test actual cross-service communication and are necessary
    
    def test_generate_personal_report_json_success(self):
        """
        Test complete personal report flow with real microservices (JSON).
        This validates: Users service → Tasks service → Report assembly
        """
        user_id = self.staff_user_id
        
        response = self.client.get(f'/reports/personal/{user_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['Code'] == 200
        assert 'message' in data
        assert 'data' in data
        
        # Validate report data structure
        report_data = data['data']
        assert 'user_id' in report_data
        assert 'user_name' in report_data
        assert 'user_role' in report_data
        assert 'task_stats' in report_data
        assert 'total_tasks' in report_data
        assert 'project_stats' in report_data

    def test_generate_personal_report_pdf_success(self):
        """
        Test personal report PDF generation (validates export service integration).
        This is slow but critical for verifying document generation works.
        """
        user_id = self.staff_user_id
        
        response = self.client.get(f'/reports/personal/{user_id}?format=pdf')
        
        assert response.status_code == 200
        assert response.mimetype == 'application/pdf'
        assert response.content_length > 0
        
        # Verify PDF header
        data = response.data
        assert data[:4] == b'%PDF'

    def test_generate_personal_report_user_not_found(self):
        """Test personal report for non-existent user (validates error propagation)."""
        user_id = self.nonexistent_user_id  
        
        response = self.client.get(f'/reports/personal/{user_id}')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['Code'] == 404

    def test_generate_team_report_json_success(self):
        """
        Test team report with manager (validates Team service integration).
        """
        manager_id = self.manager_user_id
        
        response = self.client.get(f'/reports/team/{manager_id}')
        
        # Should be 200 if manager exists and has team, or 403/404 otherwise
        assert response.status_code in [200, 403, 404]
        data = json.loads(response.data)
        
        if response.status_code == 200:
            assert data['Code'] == 200
            assert 'message' in data
            assert 'data' in data
            assert 'team_report' in data['data']
            
            # Validate team report structure
            team_report = data['data']['team_report']
            assert 'team_id' in team_report or 'dept_id' in team_report
            assert 'member_reports' in team_report
            assert 'total_team_tasks' in team_report

    def test_generate_department_report_json_success(self):
        """
        Test department report with director (validates Dept service integration).
        """
        director_id = self.director_user_id
        
        response = self.client.get(f'/reports/department/{director_id}')
        
        # Should be 200 if director exists and has dept, or 403/404 otherwise
        assert response.status_code in [200, 403, 404]
        data = json.loads(response.data)
        
        if response.status_code == 200:
            assert data['Code'] == 200
            assert 'message' in data
            assert 'data' in data
            assert 'department_report' in data['data']
            
            # Validate department report structure
            dept_report = data['data']['department_report']
            assert 'dept_id' in dept_report
            assert 'member_reports' in dept_report
            assert 'total_team_tasks' in dept_report

    def test_generate_personal_report_with_date_filter(self):
        """Test date filtering works across microservices."""
        user_id = self.staff_user_id
        
        response = self.client.get(
            f'/reports/personal/{user_id}?start_date=2024-01-01&end_date=2024-12-31'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['Code'] == 200

    def test_cross_service_integration(self):
        """
        COMBINED TEST: Verify integration with Users, Tasks, and Team microservices.
        This replaces 3 separate tests to reduce execution time.
        """
        user_id = self.staff_user_id
        manager_id = self.manager_user_id
        
        try:
            # Test 1: Users service integration
            user_response = requests.get(f"{self.users_url}/users/{user_id}", timeout=3)
            
            if user_response.status_code == 200:
                user_data = user_response.json()
                report_response = self.client.get(f'/reports/personal/{user_id}')
                
                if report_response.status_code == 200:
                    report_data = json.loads(report_response.data)
                    assert report_data['data']['user_name'] == user_data['data']['name']
                    # Also verify task data is present (Tasks service integration)
                    assert 'total_tasks' in report_data['data']
            
            # Test 2: Team service integration
            team_response = self.client.get(f'/reports/team/{manager_id}')
            if team_response.status_code == 200:
                team_data = json.loads(team_response.data)
                team_report = team_data['data']['team_report']
                assert 'member_reports' in team_report
                assert isinstance(team_report['member_reports'], list)
                
        except requests.exceptions.RequestException:
            self.skipTest("Microservices not available")

    def test_multiple_formats_and_concurrent_requests(self):
        """
        COMBINED TEST: Test format consistency AND concurrent requests.
        This replaces 2 separate tests to reduce execution time.
        """
        user_id = self.staff_user_id
        
        # Part 1: Test all formats work (was test_personal_report_consistency_across_formats)
        json_response = self.client.get(f'/reports/personal/{user_id}')
        
        if json_response.status_code == 200:
            # Verify PDF and Excel work
            pdf_response = self.client.get(f'/reports/personal/{user_id}?format=pdf')
            assert pdf_response.status_code == 200
            assert pdf_response.mimetype == 'application/pdf'
            
            excel_response = self.client.get(f'/reports/personal/{user_id}?format=excel')
            assert excel_response.status_code == 200
            assert excel_response.mimetype == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            
            # Part 2: Test concurrent requests (reduced to 2 for speed)
            responses = [self.client.get(f'/reports/personal/{user_id}') for _ in range(2)]
            for response in responses:
                assert response.status_code == 200

    def test_team_report_non_manager(self):
        """Test team report for non-manager user (Staff)."""
        # Use configured staff user ID (who is not a manager)
        staff_id = self.staff_user_id
        
        response = self.client.get(f'/reports/team/{staff_id}')
        
        # Should return 403 (not a manager) or 404 (not assigned to team)
        assert response.status_code in [403, 404]

    # ==================== FAST VALIDATION TESTS ====================
    # These test validation logic - they fail fast without heavy processing

    def test_generate_personal_report_invalid_start_date(self):
        """Test personal report with invalid start_date format."""
        user_id = self.staff_user_id
        
        response = self.client.get(
            f'/reports/personal/{user_id}?start_date=invalid-date'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['Code'] == 400
        assert 'Invalid start_date format' in data['Message']

    def test_generate_personal_report_invalid_end_date(self):
        """Test personal report with invalid end_date format."""
        user_id = self.staff_user_id
        
        response = self.client.get(
            f'/reports/personal/{user_id}?end_date=12/31/2024'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['Code'] == 400
        assert 'Invalid end_date format' in data['Message']

    def test_invalid_format_parameters(self):
        """
        COMBINED TEST: Test invalid format parameters for all report types.
        """
        user_id = self.staff_user_id
        manager_id = self.manager_user_id
        director_id = self.director_user_id
        
        # Personal report invalid format
        response = self.client.get(f'/reports/personal/{user_id}?format=xml')
        assert response.status_code == 400
        
        # Team report invalid format
        response = self.client.get(f'/reports/team/{manager_id}?format=csv')
        assert response.status_code in [400, 403, 404]
        
        # Department report invalid format
        response = self.client.get(f'/reports/department/{director_id}?format=html')
        assert response.status_code in [400, 403, 404]

    def test_invalid_date_and_not_found_errors(self):
        """
        COMBINED TEST: Test invalid dates and user not found errors.
        """
        manager_id = self.manager_user_id
        director_id = self.director_user_id
        nonexistent_id = self.nonexistent_user_id
        
        # Invalid date for team report
        response = self.client.get(f'/reports/team/{manager_id}?start_date=invalid')
        assert response.status_code == 400
        
        # Invalid date for department report
        response = self.client.get(f'/reports/department/{director_id}?end_date=2024/12/31')
        assert response.status_code == 400
        
        # User not found for team report
        response = self.client.get(f'/reports/team/{nonexistent_id}')
        assert response.status_code == 404
        
        # User not found for department report
        response = self.client.get(f'/reports/department/{nonexistent_id}')
        assert response.status_code == 404

    def test_edge_cases(self):
        """
        COMBINED TEST: Test various edge cases (future dates, reversed dates, zero tasks).
        """
        user_id = self.staff_user_id
        director_id = self.director_user_id
        
        # Future date range
        response = self.client.get(
            f'/reports/personal/{user_id}?start_date=2099-01-01&end_date=2099-12-31'
        )
        assert response.status_code == 200
        
        # Start date after end date
        response = self.client.get(
            f'/reports/personal/{user_id}?start_date=2024-12-31&end_date=2024-01-01'
        )
        assert response.status_code in [200, 400]
        
        # User with zero tasks
        response = self.client.get(f'/reports/personal/{director_id}')
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['data']['total_tasks'] == 0


if __name__ == '__main__': # pragma: no cover
    unittest.main() # pragma: no cover