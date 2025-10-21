import unittest
import json
import sys
import os
from datetime import datetime, UTC
from unittest.mock import Mock, patch

# Add parent directory to path to find modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.report import Report, ReportData, TeamReportData
from services.report_service import ReportService
from services.export_service import ExportService
from repo.report_repo import ReportRepo


class TestReportModel(unittest.TestCase):
    """Unit tests for Report model."""

    def test_report_creation_with_required_fields(self):
        """Test creating a Report with only required fields."""
        report = Report(
            report_type="personal",
            generated_by=999,  
            report_title="Test Report"
        )
        
        assert report.report_type == "personal"
        assert report.generated_by == 999
        assert report.report_title == "Test Report"
        assert report.report_data == {}
        assert report.id is None
        assert report.team_id is None
        assert report.dept_id is None

    def test_report_creation_with_all_fields(self):
        """Test creating a Report with all fields."""
        test_data = {"key": "value"}
        report = Report(
            report_type="team",
            generated_by=888,  
            report_title="Team Report",
            report_data=test_data,
            team_id=555,  
            dept_id=None
        )
        
        assert report.report_type == "team"
        assert report.generated_by == 888
        assert report.report_title == "Team Report"
        assert report.report_data == test_data
        assert report.team_id == 555
        assert report.dept_id is None

    def test_report_to_dict_without_id(self):
        """Test converting Report to dict when id is None."""
        report = Report(
            report_type="personal",
            generated_by=777,  
            report_title="Test"
        )
        
        result = report.to_dict()
        
        assert 'id' not in result
        assert result['report_type'] == "personal"
        assert result['generated_by'] == 777
        assert result['report_title'] == "Test"
        assert result['report_data'] == {}

    def test_report_to_dict_with_id(self):
        """Test converting Report to dict when id is set."""
        report = Report(
            report_type="personal",
            generated_by=666,  
            report_title="Test"
        )
        report.id = 42  
        
        result = report.to_dict()
        
        assert result['id'] == 42
        assert result['report_type'] == "personal"

    def test_report_to_dict_with_team_and_dept(self):
        """Test converting Report to dict with team_id and dept_id."""
        report = Report(
            report_type="department",
            generated_by=555,  
            report_title="Dept Report",
            team_id=444,  
            dept_id=333  
        )
        
        result = report.to_dict()
        
        assert result['team_id'] == 444
        assert result['dept_id'] == 333

    def test_report_from_dict_minimal(self):
        """Test creating Report from dict with minimal data."""
        data = {
            'report_type': 'personal',
            'generated_by': 888,  
            'report_title': 'Test'
        }
        
        report = Report.from_dict(data)
        
        assert report.report_type == "personal"
        assert report.generated_by == 888
        assert report.report_title == "Test"
        assert report.report_data == {}
        assert report.id is None

    def test_report_from_dict_with_id(self):
        """Test creating Report from dict with id."""
        data = {
            'id': 99,  
            'report_type': 'personal',
            'generated_by': 777,  
            'report_title': 'Test'
        }
        
        report = Report.from_dict(data)
        
        assert report.id == 99

    def test_report_from_dict_with_json_string_report_data(self):
        """Test creating Report from dict when report_data is JSON string."""
        data = {
            'report_type': 'personal',
            'generated_by': 666,  
            'report_title': 'Test',
            'report_data': '{"key": "value"}'
        }
        
        report = Report.from_dict(data)
        
        assert report.report_data == {"key": "value"}

    def test_report_from_dict_with_dict_report_data(self):
        """Test creating Report from dict when report_data is already a dict."""
        data = {
            'report_type': 'personal',
            'generated_by': 555,  
            'report_title': 'Test',
            'report_data': {"key": "value"}
        }
        
        report = Report.from_dict(data)
        
        assert report.report_data == {"key": "value"}

    def test_report_from_dict_with_invalid_json_string(self):
        """Test creating Report from dict with invalid JSON string."""
        data = {
            'report_type': 'personal',
            'generated_by': 444,  
            'report_title': 'Test',
            'report_data': 'invalid json'
        }
        
        report = Report.from_dict(data)
        
        assert report.report_data == {}

    def test_report_from_dict_with_team_and_dept_ids(self):
        """Test creating Report from dict with team_id and dept_id."""
        data = {
            'report_type': 'department',
            'generated_by': 333,  
            'report_title': 'Dept Report',
            'team_id': 222,  
            'dept_id': 111  
        }
        
        report = Report.from_dict(data)
        
        assert report.team_id == 222
        assert report.dept_id == 111

    def test_report_from_dict_with_none_team_id(self):
        """Test creating Report from dict with None team_id."""
        data = {
            'report_type': 'personal',
            'generated_by': 999,  
            'report_title': 'Test',
            'team_id': None
        }
        
        report = Report.from_dict(data)
        
        assert report.team_id is None

    def test_report_from_dict_with_empty_string_team_id(self):
        """Test creating Report from dict with empty string team_id."""
        data = {
            'report_type': 'personal',
            'generated_by': 888,  
            'report_title': 'Test',
            'team_id': ''
        }
        
        report = Report.from_dict(data)
        
        assert report.team_id is None

    def test_report_roundtrip_conversion(self):
        """Test converting Report to dict and back maintains data."""
        original = Report(
            report_type="team",
            generated_by=777,  
            report_title="Original Report",
            report_data={"tasks": 10},
            team_id=555,  
            dept_id=None
        )
        original.id = 123  
        
        dict_form = original.to_dict()
        restored = Report.from_dict(dict_form)
        
        assert restored.id == original.id
        assert restored.report_type == original.report_type
        assert restored.generated_by == original.generated_by
        assert restored.report_title == original.report_title
        assert restored.report_data == original.report_data
        assert restored.team_id == original.team_id
        assert restored.dept_id == original.dept_id

    def test_report_created_at_auto_generation(self):
        """Test that created_at is auto-generated."""
        report = Report(
            report_type="personal",
            generated_by=999,  
            report_title="Test"
        )
        
        assert report.created_at is not None
        assert isinstance(report.created_at, str)


class TestReportDataModel(unittest.TestCase):
    """Unit tests for ReportData model."""

    def test_report_data_creation_minimal(self):
        """Test creating ReportData with minimal required fields."""
        data = ReportData(
            user_id=1,
            user_name="John Doe",
            user_role="Staff"
        )
        
        assert data.user_id == 1
        assert data.user_name == "John Doe"
        assert data.user_role == "Staff"
        assert data.task_stats == {}
        assert data.total_tasks == 0
        assert data.completed_tasks == 0

    def test_report_data_creation_with_all_fields(self):
        """Test creating ReportData with all fields."""
        task_stats = {"Completed": 5, "Pending": 3}
        task_details = [{"id": 1, "name": "Task 1"}]
        project_stats = [{"id": 1, "tasks": 8}]
        
        data = ReportData(
            user_id=1,
            user_name="John Doe",
            user_role="Manager",
            task_stats=task_stats,
            total_tasks=8,
            completed_tasks=5,
            overdue_tasks=2,
            task_details=task_details,
            project_stats=project_stats,
            total_projects=1,
            average_task_duration=5.5,
            completion_percentage=62.5,
            overdue_percentage=25.0,
            team_id=10,
            team_name="Engineering"
        )
        
        assert data.user_id == 1
        assert data.user_name == "John Doe"
        assert data.user_role == "Manager"
        assert data.task_stats == task_stats
        assert data.total_tasks == 8
        assert data.completed_tasks == 5
        assert data.overdue_tasks == 2
        assert data.task_details == task_details
        assert data.project_stats == project_stats
        assert data.total_projects == 1
        assert data.average_task_duration == 5.5
        assert data.completion_percentage == 62.5
        assert data.overdue_percentage == 25.0
        assert data.team_id == 10
        assert data.team_name == "Engineering"

    def test_report_data_to_dict(self):
        """Test converting ReportData to dict."""
        data = ReportData(
            user_id=1,
            user_name="John Doe",
            user_role="Staff",
            total_tasks=5,
            team_id=3,
            team_name="Sales"
        )
        
        result = data.to_dict()
        
        assert result['user_id'] == 1
        assert result['user_name'] == "John Doe"
        assert result['user_role'] == "Staff"
        assert result['total_tasks'] == 5
        assert result['team_id'] == 3
        assert result['team_name'] == "Sales"
        assert 'task_stats' in result
        assert 'task_details' in result

    def test_report_data_to_dict_with_none_values(self):
        """Test converting ReportData to dict with None values."""
        data = ReportData(
            user_id=1,
            user_name="John Doe",
            user_role="Staff",
            average_task_duration=None,
            team_id=None,
            team_name=None
        )
        
        result = data.to_dict()
        
        assert result['average_task_duration'] is None
        assert result['team_id'] is None
        assert result['team_name'] is None

    def test_report_data_with_empty_lists(self):
        """Test ReportData with empty list fields."""
        data = ReportData(
            user_id=1,
            user_name="John Doe",
            user_role="Staff",
            task_details=[],
            project_stats=[],
            projects_breakdown=[],
            projected_completion_dates=[]
        )
        
        assert data.task_details == []
        assert data.project_stats == []
        assert data.projects_breakdown == []
        assert data.projected_completion_dates == []

    def test_report_data_with_complex_task_details(self):
        """Test ReportData with complex task details."""
        task_details = [
            {
                "id": 1,
                "task_name": "Task 1",
                "status": "Completed",
                "owner_name": "John Doe",
                "collaborator_names": ["Jane Smith"]
            },
            {
                "id": 2,
                "task_name": "Task 2",
                "status": "Ongoing",
                "owner_name": "John Doe",
                "collaborator_names": []
            }
        ]
        
        data = ReportData(
            user_id=1,
            user_name="John Doe",
            user_role="Manager",
            task_details=task_details,
            total_tasks=2
        )
        
        assert len(data.task_details) == 2
        assert data.task_details[0]['task_name'] == "Task 1"
        assert data.task_details[1]['status'] == "Ongoing"

    def test_report_data_percentage_calculations(self):
        """Test ReportData with percentage fields."""
        data = ReportData(
            user_id=1,
            user_name="John Doe",
            user_role="Staff",
            total_tasks=10,
            completed_tasks=7,
            overdue_tasks=2,
            completion_percentage=70.0,
            overdue_percentage=20.0
        )
        
        assert data.completion_percentage == 70.0
        assert data.overdue_percentage == 20.0

    def test_report_data_with_project_breakdown(self):
        """Test ReportData with projects_breakdown."""
        projects_breakdown = [
            {
                "project_id": 1,
                "project_name": "Project A",
                "tasks": [{"id": 1, "name": "Task 1"}]
            }
        ]
        
        data = ReportData(
            user_id=1,
            user_name="John Doe",
            user_role="Manager",
            projects_breakdown=projects_breakdown
        )
        
        assert len(data.projects_breakdown) == 1
        assert data.projects_breakdown[0]['project_name'] == "Project A"

    def test_report_data_from_dict_minimal(self):
        """Test creating ReportData from dict with minimal data."""
        data_dict = {
            'user_id': 1,
            'user_name': 'Jane Doe',
            'user_role': 'Staff'
        }
        
        data = ReportData.from_dict(data_dict)
        
        assert data.user_id == 1
        assert data.user_name == 'Jane Doe'
        assert data.user_role == 'Staff'
        assert data.total_tasks == 0
        assert data.task_stats == {}

    def test_report_data_from_dict_complete(self):
        """Test creating ReportData from dict with all fields."""
        data_dict = {
            'user_id': 5,
            'user_name': 'Bob Smith',
            'user_role': 'Manager',
            'task_stats': {'Completed': 10, 'Pending': 5},
            'total_tasks': 15,
            'completed_tasks': 10,
            'overdue_tasks': 2,
            'task_details': [{'id': 1, 'name': 'Task 1'}],
            'project_stats': [{'id': 1, 'tasks': 15}],
            'projects_breakdown': [],
            'total_projects': 1,
            'average_task_duration': 3.5,
            'projected_completion_dates': [],
            'completion_percentage': 66.7,
            'overdue_percentage': 13.3,
            'team_id': 5,
            'team_name': 'Sales'
        }
        
        data = ReportData.from_dict(data_dict)
        
        assert data.user_id == 5
        assert data.user_name == 'Bob Smith'
        assert data.total_tasks == 15
        assert data.completed_tasks == 10
        assert data.average_task_duration == 3.5
        assert data.team_id == 5
        assert data.team_name == 'Sales'

    def test_report_data_from_dict_with_none_values(self):
        """Test creating ReportData from dict with None values."""
        data_dict = {
            'user_id': 1,
            'user_name': 'Test User',
            'user_role': 'Staff',
            'average_task_duration': None,
            'team_id': None,
            'team_name': None
        }
        
        data = ReportData.from_dict(data_dict)
        
        assert data.average_task_duration is None
        assert data.team_id is None
        assert data.team_name is None

    def test_report_data_roundtrip_conversion(self):
        """Test ReportData to_dict and from_dict roundtrip."""
        original = ReportData(
            user_id=10,
            user_name='Alice',
            user_role='Director',
            total_tasks=20,
            completed_tasks=15,
            completion_percentage=75.0,
            team_id=3,
            team_name='Engineering'
        )
        
        dict_form = original.to_dict()
        restored = ReportData.from_dict(dict_form)
        
        assert restored.user_id == original.user_id
        assert restored.user_name == original.user_name
        assert restored.user_role == original.user_role
        assert restored.total_tasks == original.total_tasks
        assert restored.completed_tasks == original.completed_tasks
        assert restored.completion_percentage == original.completion_percentage
        assert restored.team_id == original.team_id
        assert restored.team_name == original.team_name


class TestTeamReportDataModel(unittest.TestCase):
    """Unit tests for TeamReportData model."""

    def test_team_report_data_creation_empty(self):
        """Test creating TeamReportData with default values."""
        data = TeamReportData()
        
        assert data.team_id is None
        assert data.dept_id is None
        assert data.team_name is None
        assert data.dept_name is None
        assert data.member_reports == []
        assert data.total_team_tasks == 0
        assert data.total_team_projects == 0

    def test_team_report_data_creation_team_type(self):
        """Test creating TeamReportData for team report."""
        data = TeamReportData(
            team_id=5,
            team_name="Engineering",
            total_team_tasks=20,
            total_team_projects=3
        )
        
        assert data.team_id == 5
        assert data.team_name == "Engineering"
        assert data.dept_id is None
        assert data.dept_name is None
        assert data.total_team_tasks == 20
        assert data.total_team_projects == 3

    def test_team_report_data_creation_dept_type(self):
        """Test creating TeamReportData for department report."""
        data = TeamReportData(
            dept_id=10,
            dept_name="Sales Department",
            total_team_tasks=50,
            total_team_projects=8
        )
        
        assert data.dept_id == 10
        assert data.dept_name == "Sales Department"
        assert data.team_id is None
        assert data.team_name is None
        assert data.total_team_tasks == 50
        assert data.total_team_projects == 8

    def test_team_report_data_with_member_reports(self):
        """Test TeamReportData with member reports."""
        member1 = ReportData(
            user_id=1,
            user_name="John Doe",
            user_role="Manager",
            total_tasks=10
        )
        member2 = ReportData(
            user_id=2,
            user_name="Jane Smith",
            user_role="Staff",
            total_tasks=8
        )
        
        data = TeamReportData(
            team_id=5,
            team_name="Engineering",
            member_reports=[member1, member2]
        )
        
        assert len(data.member_reports) == 2
        assert data.member_reports[0].user_name == "John Doe"
        assert data.member_reports[1].user_name == "Jane Smith"

    def test_team_report_data_to_dict(self):
        """Test converting TeamReportData to dict."""
        data = TeamReportData(
            team_id=5,
            team_name="Engineering",
            total_team_tasks=20,
            team_completion_percentage=75.0
        )
        
        result = data.to_dict()
        
        assert result['team_id'] == 5
        assert result['team_name'] == "Engineering"
        assert result['total_team_tasks'] == 20
        assert result['team_completion_percentage'] == 75.0
        assert result['member_reports'] == []

    def test_team_report_data_to_dict_with_members(self):
        """Test converting TeamReportData to dict with member reports."""
        member = ReportData(
            user_id=1,
            user_name="John Doe",
            user_role="Manager",
            total_tasks=10
        )
        
        data = TeamReportData(
            team_id=5,
            team_name="Engineering",
            member_reports=[member]
        )
        
        result = data.to_dict()
        
        assert len(result['member_reports']) == 1
        assert result['member_reports'][0]['user_name'] == "John Doe"

    def test_team_report_data_with_aggregated_stats(self):
        """Test TeamReportData with all aggregated statistics."""
        task_stats = {"Completed": 15, "Pending": 5}
        task_details = [{"id": 1, "name": "Task 1"}]
        project_stats = [{"id": 1, "tasks": 20}]
        
        data = TeamReportData(
            team_id=5,
            team_name="Engineering",
            total_team_tasks=20,
            total_team_projects=3,
            team_completion_percentage=75.0,
            team_overdue_percentage=10.0,
            team_average_task_duration=4.5,
            team_task_stats=task_stats,
            team_task_details=task_details,
            team_project_stats=project_stats
        )
        
        assert data.team_completion_percentage == 75.0
        assert data.team_overdue_percentage == 10.0
        assert data.team_average_task_duration == 4.5
        assert data.team_task_stats == task_stats
        assert data.team_task_details == task_details
        assert data.team_project_stats == project_stats

    def test_team_report_data_to_dict_complete(self):
        """Test converting complete TeamReportData to dict."""
        member = ReportData(
            user_id=1,
            user_name="John Doe",
            user_role="Manager",
            total_tasks=10
        )
        
        data = TeamReportData(
            team_id=5,
            team_name="Engineering",
            member_reports=[member],
            total_team_tasks=20,
            total_team_projects=3,
            team_completion_percentage=75.0,
            team_overdue_percentage=10.0,
            team_average_task_duration=4.5,
            team_task_stats={"Completed": 15},
            team_task_details=[{"id": 1}],
            team_project_stats=[{"id": 1}]
        )
        
        result = data.to_dict()
        
        assert result['team_id'] == 5
        assert result['team_name'] == "Engineering"
        assert len(result['member_reports']) == 1
        assert result['total_team_tasks'] == 20
        assert result['total_team_projects'] == 3
        assert result['team_completion_percentage'] == 75.0
        assert result['team_overdue_percentage'] == 10.0
        assert result['team_average_task_duration'] == 4.5
        assert 'team_task_stats' in result
        assert 'team_task_details' in result
        assert 'team_project_stats' in result

    def test_team_report_data_with_dept_and_team(self):
        """Test TeamReportData with both dept and team (department report with team grouping)."""
        data = TeamReportData(
            dept_id=10,
            dept_name="Sales Department",
            team_id=5,
            team_name="Sales Team A"
        )
        
        assert data.dept_id == 10
        assert data.dept_name == "Sales Department"
        assert data.team_id == 5
        assert data.team_name == "Sales Team A"

    def test_team_report_data_roundtrip_conversion(self):
        """Test converting TeamReportData to dict and back maintains member data."""
        member = ReportData(
            user_id=1,
            user_name="John Doe",
            user_role="Manager",
            total_tasks=10,
            team_id=5,
            team_name="Engineering"
        )
        
        original = TeamReportData(
            team_id=5,
            team_name="Engineering",
            member_reports=[member],
            total_team_tasks=10
        )
        
        dict_form = original.to_dict()
        
        # Verify dict has correct structure
        assert dict_form['team_id'] == 5
        assert dict_form['team_name'] == "Engineering"
        assert len(dict_form['member_reports']) == 1
        assert dict_form['member_reports'][0]['user_name'] == "John Doe"

    def test_team_report_data_from_dict_minimal(self):
        """Test creating TeamReportData from dict with minimal data."""
        data_dict = {
            'team_id': 5,
            'team_name': 'Sales Team'
        }
        
        data = TeamReportData.from_dict(data_dict)
        
        assert data.team_id == 5
        assert data.team_name == 'Sales Team'
        assert data.dept_id is None
        assert data.member_reports == []
        assert data.total_team_tasks == 0

    def test_team_report_data_from_dict_complete(self):
        """Test creating TeamReportData from dict with all fields."""
        member_dict = {
            'user_id': 1,
            'user_name': 'John Doe',
            'user_role': 'Staff',
            'total_tasks': 5
        }
        
        data_dict = {
            'team_id': 10,
            'dept_id': 20,
            'team_name': 'Engineering Team',
            'dept_name': 'Engineering Dept',
            'member_reports': [member_dict],
            'total_team_tasks': 50,
            'total_team_projects': 5,
            'team_completion_percentage': 80.0,
            'team_overdue_percentage': 10.0,
            'team_average_task_duration': 4.5,
            'team_task_stats': {'Completed': 40},
            'team_task_details': [{'id': 1}],
            'team_project_stats': [{'id': 1}]
        }
        
        data = TeamReportData.from_dict(data_dict)
        
        assert data.team_id == 10
        assert data.dept_id == 20
        assert data.team_name == 'Engineering Team'
        assert data.dept_name == 'Engineering Dept'
        assert len(data.member_reports) == 1
        assert data.member_reports[0].user_name == 'John Doe'
        assert data.total_team_tasks == 50
        assert data.team_completion_percentage == 80.0

    def test_team_report_data_from_dict_with_none_values(self):
        """Test creating TeamReportData from dict with None values."""
        data_dict = {
            'team_id': None,
            'dept_id': 5,
            'team_name': None,
            'dept_name': 'Sales',
            'team_average_task_duration': None
        }
        
        data = TeamReportData.from_dict(data_dict)
        
        assert data.team_id is None
        assert data.dept_id == 5
        assert data.team_name is None
        assert data.dept_name == 'Sales'
        assert data.team_average_task_duration is None

    def test_team_report_data_from_dict_roundtrip(self):
        """Test TeamReportData to_dict and from_dict roundtrip."""
        member = ReportData(
            user_id=1,
            user_name="Alice",
            user_role="Manager",
            total_tasks=10
        )
        
        original = TeamReportData(
            team_id=5,
            team_name="Sales",
            member_reports=[member],
            total_team_tasks=10,
            team_completion_percentage=75.0
        )
        
        dict_form = original.to_dict()
        restored = TeamReportData.from_dict(dict_form)
        
        assert restored.team_id == original.team_id
        assert restored.team_name == original.team_name
        assert len(restored.member_reports) == len(original.member_reports)
        assert restored.member_reports[0].user_name == original.member_reports[0].user_name
        assert restored.total_team_tasks == original.total_team_tasks
        assert restored.team_completion_percentage == original.team_completion_percentage

    def test_team_report_data_from_dict_with_reportdata_objects(self):
        """Test creating TeamReportData from dict where member_reports contains ReportData objects."""
        # Create actual ReportData objects (not dicts)
        member1 = ReportData(
            user_id=111,
            user_name="Bob",
            user_role="Staff",
            total_tasks=5
        )
        member2 = ReportData(
            user_id=222,
            user_name="Carol",
            user_role="Manager",
            total_tasks=8
        )
        
        # Create dict with ReportData objects in member_reports
        # This tests the elif isinstance(member_data, ReportData) branch
        data_dict = {
            'team_id': 999,
            'team_name': 'Test Team',
            'member_reports': [member1, member2],  # ReportData objects, not dicts!
            'total_team_tasks': 13
        }
        
        data = TeamReportData.from_dict(data_dict)
        
        assert data.team_id == 999
        assert data.team_name == 'Test Team'
        assert len(data.member_reports) == 2
        assert data.member_reports[0].user_name == "Bob"
        assert data.member_reports[0].user_id == 111
        assert data.member_reports[1].user_name == "Carol"
        assert data.member_reports[1].user_id == 222
        assert data.total_team_tasks == 13

class TestReportServiceErrorPaths(unittest.TestCase):
    """Test error paths in ReportService using mocked dependencies"""
    
    def setUp(self):
        """Set up test fixtures"""
        from unittest.mock import Mock
        from repo.report_repo import ReportRepo
        self.mock_repo = Mock(spec=ReportRepo)
        self.service = ReportService(repo=self.mock_repo)
    
    def test_generate_personal_report_user_not_found(self):
        """Test personal report when user doesn't exist"""
        self.mock_repo.get_user_info.return_value = None
        
        result = self.service.generate_personal_report(999999)
        
        assert result['status'] == 404
        assert 'not found' in result['message'].lower()
    
    def test_generate_personal_report_exception(self):
        """Test personal report handles exceptions"""
        self.mock_repo.get_user_info.side_effect = Exception("Database error")
        
        result = self.service.generate_personal_report(101)
        
        assert result['status'] == 500
        assert 'error' in result['message'].lower()
    
    def test_generate_team_report_manager_not_found(self):
        """Test team report when manager doesn't exist"""
        self.mock_repo.get_user_info.return_value = None
        
        result = self.service.generate_team_report(999999)
        
        assert result['status'] == 404
    
    def test_generate_team_report_not_manager(self):
        """Test team report by non-manager"""
        self.mock_repo.get_user_info.return_value = {
            'userid': 101,
            'name': 'Test User',
            'role': 'staff',
            'team_id': 5
        }
        
        result = self.service.generate_team_report(101)
        
        assert result['status'] == 403
    
    def test_generate_team_report_no_team(self):
        """Test team report when manager not assigned to team"""
        self.mock_repo.get_user_info.return_value = {
            'userid': 352,
            'name': 'Test Manager',
            'role': 'manager',
            'team_id': None
        }
        
        result = self.service.generate_team_report(352)
        
        assert result['status'] == 400
    
    def test_generate_team_report_exception(self):
        """Test team report handles exceptions"""
        self.mock_repo.get_user_info.side_effect = Exception("Database error")
        
        result = self.service.generate_team_report(352)
        
        assert result['status'] == 500
    
    def test_generate_department_report_director_not_found(self):
        """Test department report when director doesn't exist"""
        self.mock_repo.get_user_info.return_value = None
        
        result = self.service.generate_department_report(999999)
        
        assert result['status'] == 404
    
    def test_generate_department_report_not_director(self):
        """Test department report by non-director"""
        self.mock_repo.get_user_info.return_value = {
            'userid': 101,
            'name': 'Test User',
            'role': 'staff',
            'dept_id': 4
        }
        
        result = self.service.generate_department_report(101)
        
        assert result['status'] == 403
    
    def test_generate_department_report_no_dept(self):
        """Test department report when director not assigned to department"""
        self.mock_repo.get_user_info.return_value = {
            'userid': 399,
            'name': 'Test Director',
            'role': 'director',
            'dept_id': None
        }
        
        result = self.service.generate_department_report(399)
        
        assert result['status'] == 400
    
    def test_generate_department_report_exception(self):
        """Test department report handles exceptions"""
        self.mock_repo.get_user_info.side_effect = Exception("Database error")
        
        result = self.service.generate_department_report(399)
        
        assert result['status'] == 500


class TestExportServiceCoverage(unittest.TestCase):
    """Test export service edge cases"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.export_service = ExportService()
    
    def test_export_personal_report_pdf_comprehensive(self):
        """Test PDF export with comprehensive data"""
        report_data = ReportData(user_id=101, user_name='Test User', user_role='staff')
        report_data.total_tasks = 10
        report_data.completed_tasks = 7
        report_data.overdue_tasks = 2
        report_data.total_projects = 3
        report_data.completion_percentage = 70.0
        report_data.average_task_duration = 3.5
        report_data.projects_breakdown = [
            {
                'project_id': 1,
                'project_name': 'Project Alpha',
                'total_tasks': 5,
                'completed_tasks': 4,
                'overdue_tasks': 1,
                'completion_percentage': 80.0,
                'average_task_duration': 3.0,
                'projected_completion_date': '2025-11-01',
                'task_details': [
                    {
                        'task_id': 1,
                        'task_name': 'Task 1',
                        'status': 'Completed',
                        'owner_name': 'Test User',
                        'collaborators': ['Other User'],
                        'due_date': '2025-01-10T00:00:00Z',
                        'is_overdue': False,
                        'was_completed_late': False
                    }
                ]
            }
        ]
        
        pdf_bytes = self.export_service.export_personal_report_pdf(report_data)
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 1000
        assert pdf_bytes.startswith(b'%PDF')
    
    def test_export_personal_report_excel_comprehensive(self):
        """Test Excel export with comprehensive data"""
        report_data = ReportData(user_id=101, user_name='Test User', user_role='staff')
        report_data.total_tasks = 10
        report_data.projects_breakdown = [
            {
                'project_id': 1,
                'project_name': 'Project Alpha',
                'total_tasks': 5,
                'task_details': [{'task_name': 'Task 1', 'status': 'Completed'}]
            }
        ]
        
        excel_bytes = self.export_service.export_personal_report_excel(report_data)
        
        assert excel_bytes is not None
        assert len(excel_bytes) > 1000
    
    def test_export_team_report_pdf_comprehensive(self):
        """Test team PDF export with comprehensive data"""
        member1 = ReportData(user_id=101, user_name='User 1', user_role='staff')
        member1.total_tasks = 10
        member1.completed_tasks = 7
        member1.projects_breakdown = []
        
        team_report = TeamReportData(team_id=5, team_name='Test Team', member_reports=[member1])
        team_report.total_team_tasks = 10
        team_report.team_completion_percentage = 70.0
        
        pdf_bytes = self.export_service.export_team_report_pdf(None, team_report, None)
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 1000
        assert pdf_bytes.startswith(b'%PDF')
    
    def test_export_team_report_excel_comprehensive(self):
        """Test team Excel export with comprehensive data"""
        member1 = ReportData(user_id=101, user_name='User 1', user_role='staff')
        member1.total_tasks = 10
        
        team_report = TeamReportData(team_id=5, team_name='Test Team', member_reports=[member1])
        team_report.total_team_tasks = 10
        
        excel_bytes = self.export_service.export_team_report_excel(None, team_report, None)
        
        assert excel_bytes is not None
        assert len(excel_bytes) > 1000


class TestReportRepoCoverage(unittest.TestCase):
    """Test repo error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.repo = ReportRepo()
    
    @patch('requests.get')
    def test_get_user_info_error(self, mock_get):
        """Test get_user_info handles errors"""
        mock_get.side_effect = Exception("Connection error")
        
        result = self.repo.get_user_info(101)
        
        assert result is None
    
    @patch('requests.get')
    def test_get_user_tasks_error(self, mock_get):
        """Test get_user_tasks handles errors"""
        mock_get.side_effect = Exception("Connection error")
        
        result = self.repo.get_user_tasks(101)
        
        assert result == []
    
    @patch('requests.get')
    def test_get_user_projects_error(self, mock_get):
        """Test get_user_projects handles errors"""
        mock_get.side_effect = Exception("Connection error")
        
        result = self.repo.get_user_projects(101)
        
        assert result == []
    
    @patch('requests.get')
    def test_get_project_tasks_error(self, mock_get):
        """Test get_project_tasks handles errors"""
        mock_get.side_effect = Exception("Connection error")
        
        result = self.repo.get_project_tasks(1)
        
        assert result == []
    
    @patch('requests.get')
    def test_get_project_info_error(self, mock_get):
        """Test get_project_info handles errors"""
        mock_get.side_effect = Exception("Connection error")
        
        result = self.repo.get_project_info(1)
        
        assert result is None
    
    @patch('requests.get')
    def test_get_team_members_error(self, mock_get):
        """Test get_team_members handles errors"""
        mock_get.side_effect = Exception("Connection error")
        
        result = self.repo.get_team_members(1)
        
        assert result == []
    
    @patch('requests.get')
    def test_get_dept_members_error(self, mock_get):
        """Test get_dept_members handles errors"""
        mock_get.side_effect = Exception("Connection error")
        
        result = self.repo.get_dept_members(1)
        
        assert result == []
    
    @patch('requests.get')
    def test_get_team_info_error(self, mock_get):
        """Test get_team_info handles errors"""
        mock_get.side_effect = Exception("Connection error")
        
        result = self.repo.get_team_info(1)
        
        assert result is None
    
    @patch('requests.get')
    def test_get_dept_info_error(self, mock_get):
        """Test get_dept_info handles errors"""
        mock_get.side_effect = Exception("Connection error")
        
        result = self.repo.get_dept_info(1)
        
        assert result is None
    
    @patch('requests.get')
    def test_get_tasks_by_team_success(self, mock_get):
        """Test get_tasks_by_team success path"""
        from unittest.mock import Mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': [{'id': 1, 'task_name': 'Task 1'}]}
        mock_get.return_value = mock_response
        
        result = self.repo.get_tasks_by_team(5)
        
        assert result == [{'id': 1, 'task_name': 'Task 1'}]
    
    @patch('requests.get')
    def test_get_tasks_by_team_error(self, mock_get):
        """Test get_tasks_by_team handles errors"""
        mock_get.side_effect = Exception("Connection error")
        
        result = self.repo.get_tasks_by_team(5)
        
        assert result == []
    
    @patch('requests.get')
    def test_get_tasks_by_department_success(self, mock_get):
        """Test get_tasks_by_department success path"""
        from unittest.mock import Mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': [{'id': 1, 'task_name': 'Task 1'}]}
        mock_get.return_value = mock_response
        
        result = self.repo.get_tasks_by_department(4)
        
        assert result == [{'id': 1, 'task_name': 'Task 1'}]
    
    @patch('requests.get')
    def test_get_tasks_by_department_error(self, mock_get):
        """Test get_tasks_by_department handles errors"""
        mock_get.side_effect = Exception("Connection error")
        
        result = self.repo.get_tasks_by_department(4)
        
        assert result == []


if __name__ == '__main__': # pragma: no cover
    unittest.main() # pragma: no cover
