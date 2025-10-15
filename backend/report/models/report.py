from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime, UTC
import json

@dataclass
class Report:
    """Saved report entity for database persistence"""
    id: Optional[int] = field(default=None, init=False)
    report_type: str = ""  # 'personal', 'team', 'department'
    generated_by: int = 0  # User ID who generated the report
    report_title: str = ""
    report_data: Dict[str, Any] = field(default_factory=dict)  # JSON data
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    team_id: Optional[int] = None
    dept_id: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Report object to dictionary"""
        result = {
            'report_type': self.report_type,
            'generated_by': self.generated_by,
            'report_title': self.report_title,
            'report_data': self.report_data,
            'created_at': self.created_at,
            'team_id': self.team_id,
            'dept_id': self.dept_id
        }
        
        # Include ID if it exists
        if self.id is not None:
            result['id'] = self.id
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Report':
        """Create Report object from dictionary"""
        # Handle report_data - ensure it's a dict
        report_data = data.get('report_data', {})
        if isinstance(report_data, str):
            try:
                report_data = json.loads(report_data)
            except json.JSONDecodeError:
                report_data = {}
        
        # Create report instance
        report = cls(
            report_type=str(data.get('report_type', '')),
            generated_by=int(data.get('generated_by', 0)),
            report_title=str(data.get('report_title', '')),
            report_data=report_data,
            created_at=str(data.get('created_at', datetime.now(UTC).isoformat())),
            team_id=int(data['team_id']) if data.get('team_id') not in (None, '') else None,
            dept_id=int(data['dept_id']) if data.get('dept_id') not in (None, '') else None
        )
        
        # Set ID if provided (since it's init=False)
        if 'id' in data and data['id'] is not None:
            report.id = int(data['id'])
            
        return report

@dataclass
class ReportData:
    """Data structure for holding report metrics"""
    user_id: int
    user_name: str
    user_role: str
    
    # Task statistics
    task_stats: Dict[str, int] = field(default_factory=dict)  # {status: count}
    total_tasks: int = 0
    completed_tasks: int = 0
    overdue_tasks: int = 0
    
    # Task details for comprehensive reporting
    task_details: List[Dict[str, Any]] = field(default_factory=list)
    
    # Project statistics
    project_stats: List[Dict[str, Any]] = field(default_factory=list)
    projects_breakdown: List[Dict[str, Any]] = field(default_factory=list)  # Tasks organized by project
    total_projects: int = 0
    
    # Time-based metrics
    average_task_duration: Optional[float] = None  # in days
    projected_completion_dates: List[Dict[str, Any]] = field(default_factory=list)
    
    # Additional metrics
    completion_percentage: float = 0.0
    overdue_percentage: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ReportData object to dictionary"""
        return {
            'user_id': self.user_id,
            'user_name': self.user_name,
            'user_role': self.user_role,
            'task_stats': self.task_stats,
            'total_tasks': self.total_tasks,
            'completed_tasks': self.completed_tasks,
            'overdue_tasks': self.overdue_tasks,
            'task_details': self.task_details,
            'project_stats': self.project_stats,
            'projects_breakdown': self.projects_breakdown,
            'total_projects': self.total_projects,
            'average_task_duration': self.average_task_duration,
            'projected_completion_dates': self.projected_completion_dates,
            'completion_percentage': self.completion_percentage,
            'overdue_percentage': self.overdue_percentage
        }

@dataclass
class TeamReportData:
    """Data structure for team/department reports"""
    team_id: Optional[int] = None
    dept_id: Optional[int] = None
    team_name: Optional[str] = None
    dept_name: Optional[str] = None
    
    member_reports: List[ReportData] = field(default_factory=list)
    
    # Aggregated statistics
    total_team_tasks: int = 0
    total_team_projects: int = 0
    team_completion_percentage: float = 0.0
    team_overdue_percentage: float = 0.0
    team_average_task_duration: Optional[float] = None
    
    # Detailed aggregated data (like personal reports)
    team_task_stats: Dict[str, int] = field(default_factory=dict)
    team_task_details: List[Dict[str, Any]] = field(default_factory=list)
    team_project_stats: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert TeamReportData object to dictionary"""
        return {
            'team_id': self.team_id,
            'dept_id': self.dept_id,
            'team_name': self.team_name,
            'dept_name': self.dept_name,
            'member_reports': [report.to_dict() for report in self.member_reports],
            'total_team_tasks': self.total_team_tasks,
            'total_team_projects': self.total_team_projects,
            'team_completion_percentage': self.team_completion_percentage,
            'team_overdue_percentage': self.team_overdue_percentage,
            'team_average_task_duration': self.team_average_task_duration,
            'team_task_stats': self.team_task_stats,
            'team_task_details': self.team_task_details,
            'team_project_stats': self.team_project_stats
        }