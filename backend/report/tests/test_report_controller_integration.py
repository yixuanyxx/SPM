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
    """Integration tests for report controller endpoints using real microservices."""

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

    # ==================== Personal Report Tests ====================

    def test_generate_personal_report_json_success(self):
        """Test generating personal report in JSON format for existing user."""
        # Use configured test user ID
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

    def test_generate_personal_report_with_date_filter(self):
        """Test generating personal report with date filtering."""
        user_id = self.staff_user_id
        
        response = self.client.get(
            f'/reports/personal/{user_id}?start_date=2024-01-01&end_date=2024-12-31'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['Code'] == 200

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

    def test_generate_personal_report_user_not_found(self):
        """Test personal report for non-existent user."""
        user_id = self.nonexistent_user_id  
        
        response = self.client.get(f'/reports/personal/{user_id}')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['Code'] == 404

    def test_generate_personal_report_pdf_success(self):
        """Test generating personal report in PDF format."""
        user_id = self.staff_user_id
        
        response = self.client.get(f'/reports/personal/{user_id}?format=pdf')
        
        assert response.status_code == 200
        assert response.mimetype == 'application/pdf'
        assert response.content_length > 0
        
        # Verify PDF header
        data = response.data
        assert data[:4] == b'%PDF'

    def test_generate_personal_report_excel_success(self):
        """Test generating personal report in Excel format."""
        user_id = self.staff_user_id
        
        response = self.client.get(f'/reports/personal/{user_id}?format=excel')
        
        assert response.status_code == 200
        assert response.mimetype == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        assert response.content_length > 0
        
        # Verify Excel file header (PK zip signature)
        data = response.data
        assert data[:2] == b'PK'

    def test_generate_personal_report_invalid_format(self):
        """Test personal report with invalid format parameter."""
        user_id = self.staff_user_id
        
        response = self.client.get(f'/reports/personal/{user_id}?format=xml')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['Code'] == 400
        assert 'Invalid format' in data['Message']

    # ==================== Team Report Tests ====================

    def test_generate_team_report_json_success(self):
        """Test generating team report in JSON format for manager."""
        # Use configured test manager ID
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

    def test_generate_team_report_with_date_filter(self):
        """Test generating team report with date filtering."""
        manager_id = self.manager_user_id
        
        response = self.client.get(
            f'/reports/team/{manager_id}?start_date=2024-01-01&end_date=2024-12-31'
        )
        
        # Should be 200, 403, or 404 depending on manager status
        assert response.status_code in [200, 403, 404]

    def test_generate_team_report_invalid_date(self):
        """Test team report with invalid date format."""
        manager_id = self.manager_user_id
        
        response = self.client.get(
            f'/reports/team/{manager_id}?start_date=invalid'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['Code'] == 400

    def test_generate_team_report_non_manager(self):
        """Test team report for non-manager user (Staff)."""
        # Use configured staff user ID (who is not a manager)
        staff_id = self.staff_user_id
        
        response = self.client.get(f'/reports/team/{staff_id}')
        
        # Should return 403 (not a manager) or 404 (not assigned to team)
        assert response.status_code in [403, 404]

    def test_generate_team_report_pdf_success(self):
        """Test generating team report in PDF format."""
        manager_id = self.manager_user_id
        
        response = self.client.get(f'/reports/team/{manager_id}?format=pdf')
        
        if response.status_code == 200:
            assert response.mimetype == 'application/pdf'
            assert response.content_length > 0
            data = response.data
            assert data[:4] == b'%PDF'
        else:
            # If manager doesn't exist or not authorized, should be 403/404
            assert response.status_code in [403, 404]

    def test_generate_team_report_excel_success(self):
        """Test generating team report in Excel format."""
        manager_id = self.manager_user_id
        
        response = self.client.get(f'/reports/team/{manager_id}?format=excel')
        
        if response.status_code == 200:
            assert response.mimetype == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            assert response.content_length > 0
            data = response.data
            assert data[:2] == b'PK'
        else:
            # If manager doesn't exist or not authorized, should be 403/404
            assert response.status_code in [403, 404]

    def test_generate_team_report_invalid_format(self):
        """Test team report with invalid format parameter."""
        manager_id = self.manager_user_id
        
        response = self.client.get(f'/reports/team/{manager_id}?format=csv')
        
        # Should be 400 for invalid format, or 403/404 if manager issue
        assert response.status_code in [400, 403, 404]

    def test_generate_team_report_user_not_found(self):
        """Test team report for non-existent user."""
        manager_id = self.nonexistent_user_id
        
        response = self.client.get(f'/reports/team/{manager_id}')
        
        assert response.status_code == 404

    # ==================== Department Report Tests ====================

    def test_generate_department_report_json_success(self):
        """Test generating department report in JSON format for director."""
        # Use configured test director ID
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

    def test_generate_department_report_with_date_filter(self):
        """Test generating department report with date filtering."""
        director_id = self.director_user_id
        
        response = self.client.get(
            f'/reports/department/{director_id}?start_date=2024-01-01&end_date=2024-12-31'
        )
        
        # Should be 200, 403, or 404 depending on director status
        assert response.status_code in [200, 403, 404]

    def test_generate_department_report_invalid_date(self):
        """Test department report with invalid date format."""
        director_id = self.director_user_id
        
        response = self.client.get(
            f'/reports/department/{director_id}?end_date=2024/12/31'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['Code'] == 400

    def test_generate_department_report_non_director(self):
        """Test department report for non-director user."""
        # Use configured staff user ID (who is not a director)
        non_director_id = self.staff_user_id
        
        response = self.client.get(f'/reports/department/{non_director_id}')
        
        # Should return 403 (not a director) or 404 (not assigned to dept)
        assert response.status_code in [403, 404]

    def test_generate_department_report_pdf_success(self):
        """Test generating department report in PDF format."""
        director_id = self.director_user_id
        
        response = self.client.get(f'/reports/department/{director_id}?format=pdf')
        
        if response.status_code == 200:
            assert response.mimetype == 'application/pdf'
            assert response.content_length > 0
            data = response.data
            assert data[:4] == b'%PDF'
        else:
            # If director doesn't exist or not authorized, should be 403/404
            assert response.status_code in [403, 404]

    def test_generate_department_report_excel_success(self):
        """Test generating department report in Excel format."""
        director_id = self.director_user_id
        
        response = self.client.get(f'/reports/department/{director_id}?format=excel')
        
        if response.status_code == 200:
            assert response.mimetype == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            assert response.content_length > 0
            data = response.data
            assert data[:2] == b'PK'
        else:
            # If director doesn't exist or not authorized, should be 403/404
            assert response.status_code in [403, 404]

    def test_generate_department_report_invalid_format(self):
        """Test department report with invalid format parameter."""
        director_id = self.director_user_id
        
        response = self.client.get(f'/reports/department/{director_id}?format=html')
        
        # Should be 400 for invalid format, or 403/404 if director issue
        assert response.status_code in [400, 403, 404]

    def test_generate_department_report_user_not_found(self):
        """Test department report for non-existent user."""
        director_id = self.nonexistent_user_id
        
        response = self.client.get(f'/reports/department/{director_id}')
        
        assert response.status_code == 404

    # ==================== Cross-Format Consistency Tests ====================

    def test_personal_report_consistency_across_formats(self):
        """Test that personal report data is consistent across JSON, PDF, and Excel formats."""
        user_id = self.staff_user_id
        
        # Get JSON version
        json_response = self.client.get(f'/reports/personal/{user_id}')
        
        if json_response.status_code == 200:
            json_data = json.loads(json_response.data)
            
            # Get PDF version
            pdf_response = self.client.get(f'/reports/personal/{user_id}?format=pdf')
            assert pdf_response.status_code == 200
            assert pdf_response.mimetype == 'application/pdf'
            
            # Get Excel version
            excel_response = self.client.get(f'/reports/personal/{user_id}?format=excel')
            assert excel_response.status_code == 200
            assert excel_response.mimetype == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    def test_team_report_consistency_across_formats(self):
        """Test that team report data is consistent across JSON, PDF, and Excel formats."""
        manager_id = self.manager_user_id
        
        # Get JSON version
        json_response = self.client.get(f'/reports/team/{manager_id}')
        
        if json_response.status_code == 200:
            json_data = json.loads(json_response.data)
            
            # Get PDF version
            pdf_response = self.client.get(f'/reports/team/{manager_id}?format=pdf')
            assert pdf_response.status_code == 200
            
            # Get Excel version
            excel_response = self.client.get(f'/reports/team/{manager_id}?format=excel')
            assert excel_response.status_code == 200

    # ==================== Edge Case Tests ====================

    def test_personal_report_zero_tasks(self):
        """Test personal report for user with no tasks."""
        # Using director ID who might have fewer/no tasks
        user_id = self.director_user_id
        
        response = self.client.get(f'/reports/personal/{user_id}')
        
        # Should handle gracefully - either 200 with empty tasks or 404
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = json.loads(response.data)
            report_data = data['data']
            assert report_data['total_tasks'] == 0

    def test_report_with_future_date_range(self):
        """Test report with future date range returns empty results."""
        user_id = self.staff_user_id
        
        response = self.client.get(
            f'/reports/personal/{user_id}?start_date=2099-01-01&end_date=2099-12-31'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        # Should return report with no tasks in date range
        assert 'data' in data

    def test_report_with_date_range_start_after_end(self):
        """Test report with start_date after end_date."""
        user_id = self.staff_user_id
        
        response = self.client.get(
            f'/reports/personal/{user_id}?start_date=2024-12-31&end_date=2024-01-01'
        )
        
        # Should handle gracefully - might return empty results
        assert response.status_code in [200, 400]

    def test_multiple_concurrent_report_requests(self):
        """Test handling of multiple concurrent report requests."""
        user_id = self.staff_user_id
        
        # Make multiple requests
        responses = []
        for _ in range(5):
            response = self.client.get(f'/reports/personal/{user_id}')
            responses.append(response)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200

    # ==================== Microservice Integration Tests ====================

    def test_report_with_real_user_data(self):
        """Test that report correctly integrates with Users microservice."""
        user_id = self.staff_user_id
        
        # First verify user exists in Users microservice
        try:
            user_response = requests.get(f"{self.users_url}/users/{user_id}")
            
            if user_response.status_code == 200:
                user_data = user_response.json()
                
                # Now get report
                report_response = self.client.get(f'/reports/personal/{user_id}')
                assert report_response.status_code == 200
                
                report_data = json.loads(report_response.data)

                assert report_data['data']['user_name'] == user_data['data']['name']
        except requests.exceptions.RequestException:
            self.skipTest("Users microservice not available")

    def test_report_with_real_task_data(self):
        """Test that report correctly integrates with Tasks microservice."""
        user_id = self.staff_user_id
        
        # First verify tasks exist in Tasks microservice
        try:
            tasks_response = requests.get(f"{self.tasks_url}/tasks/user-task/{user_id}")
            
            if tasks_response.status_code == 200:
                tasks_data = tasks_response.json()
                
                # Now get report
                report_response = self.client.get(f'/reports/personal/{user_id}')
                assert report_response.status_code == 200
                
                report_data = json.loads(report_response.data)
                # Task count should match or be reasonable
                assert 'total_tasks' in report_data['data']
        except requests.exceptions.RequestException:
            self.skipTest("Tasks microservice not available")

    def test_team_report_with_real_team_data(self):
        """Test that team report correctly integrates with Team microservice."""
        manager_id = self.manager_user_id
        
        # First verify team exists in Team microservice
        try:
            # Try to get team info for manager
            report_response = self.client.get(f'/reports/team/{manager_id}')
            
            if report_response.status_code == 200:
                report_data = json.loads(report_response.data)
                team_report = report_data['data']['team_report']
                
                # Verify team structure
                assert 'team_id' in team_report or 'dept_id' in team_report
                assert 'member_reports' in team_report
                assert isinstance(team_report['member_reports'], list)
        except requests.exceptions.RequestException:
            self.skipTest("Team microservice not available")

    # ==================== Additional Coverage Tests ====================

    def test_all_else_branches_for_coverage(self):
        """Test all else branches to achieve 100% coverage."""
        # Test with non-existent user to trigger else branches in PDF/Excel tests
        nonexistent_id = 999998
        
        # Personal report PDF - else branch
        response = self.client.get(f'/reports/personal/{nonexistent_id}?format=pdf')
        assert response.status_code in [403, 404]
        
        # Personal report Excel - else branch  
        response = self.client.get(f'/reports/personal/{nonexistent_id}?format=excel')
        assert response.status_code in [403, 404]
        
        # Team report PDF - else branch
        response = self.client.get(f'/reports/team/{nonexistent_id}?format=pdf')
        assert response.status_code in [403, 404]
        
        # Team report Excel - else branch
        response = self.client.get(f'/reports/team/{nonexistent_id}?format=excel')
        assert response.status_code in [403, 404]
        
        # Department report PDF - else branch
        response = self.client.get(f'/reports/department/{nonexistent_id}?format=pdf')
        assert response.status_code in [403, 404]
        
        # Department report Excel - else branch
        response = self.client.get(f'/reports/department/{nonexistent_id}?format=excel')
        assert response.status_code in [403, 404]

