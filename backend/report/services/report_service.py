from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dateutil import parser as dateparser
import statistics

from models.report import ReportData, TeamReportData
from repo.supa_report_repo import ReportRepo


class ReportService:
    def __init__(self, repo: Optional[ReportRepo] = None):
        self.repo = repo or ReportRepo()

    def generate_personal_report(self, user_id: int, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Generate personal report for staff showing their own stats
        
        Args:
            user_id: ID of the user requesting the report
            start_date: Start date for filtering (YYYY-MM-DD format)
            end_date: End date for filtering (YYYY-MM-DD format)
        """
        try:
            # Get user information
            user_info = self.repo.get_user_info(user_id)
            if not user_info:
                return {"status": 404, "message": f"User {user_id} not found"}

            # Get user tasks and projects with date filtering
            user_tasks = self.repo.get_user_tasks(user_id, start_date, end_date)
            user_projects = self.repo.get_user_projects(user_id, start_date, end_date)
            
            # Handle None values
            if user_tasks is None:
                print(f"Warning: user_tasks is None for user {user_id}")
                user_tasks = []
            if user_projects is None:
                print(f"Warning: user_projects is None for user {user_id}")
                user_projects = []
            
            print(f"User {user_id}: Found {len(user_tasks)} tasks and {len(user_projects)} projects")

            # Generate report data
            report_data = self._generate_user_report_data(user_info, user_tasks, user_projects)

            result = {
                "status": 200,
                "message": f"Personal report generated for {user_info.get('name', 'User')}",
                "data": report_data.to_dict()
            }

            return result

        except Exception as e:
            return {"status": 500, "message": f"Error generating personal report: {str(e)}"}

    def generate_team_report(self, manager_user_id: int, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Generate team report for managers showing their team members' stats
        
        Args:
            manager_user_id: ID of the manager requesting the report  
            start_date: Start date for filtering (YYYY-MM-DD format)
            end_date: End date for filtering (YYYY-MM-DD format)
        """
        try:
            # Get manager information
            manager_info = self.repo.get_user_info(manager_user_id)
            if not manager_info:
                return {"status": 404, "message": f"Manager {manager_user_id} not found"}

            # Check if user is a manager
            user_role = manager_info.get('role')
            if user_role is None:
                role_str = ''
            elif isinstance(user_role, int):
                # Handle case where role is stored as integer (1=staff, 2=manager, 3=director)
                role_map = {1: 'staff', 2: 'manager', 3: 'director'}
                role_str = role_map.get(user_role, '')
            else:
                role_str = str(user_role).lower()
            
            if role_str != 'manager':
                return {"status": 403, "message": "Only managers can generate team reports"}

            team_id = manager_info.get('team_id')
            if not team_id:
                return {"status": 400, "message": "Manager is not assigned to a team"}

            # Get team information
            team_info = self.repo.get_team_info(team_id)
            if not team_info:
                print(f"Warning: Team info not found for team_id {team_id}")
            
            # Get team members
            team_members = self.repo.get_team_members(team_id)
            if not team_members:
                print(f"Warning: No team members found for team_id {team_id}")

            # Generate personal reports for all team members except the manager (compilation approach)
            member_reports = []
            for member in team_members:
                # Skip the manager from their own team report
                if member['userid'] == manager_user_id:
                    continue
                    
                member_tasks = self.repo.get_user_tasks(member['userid'], start_date, end_date)
                member_projects = self.repo.get_user_projects(member['userid'], start_date, end_date)
                
                # Handle None values
                if member_tasks is None:
                    member_tasks = []
                if member_projects is None:
                    member_projects = []
                
                member_report = self._generate_user_report_data(member, member_tasks, member_projects)
                member_reports.append(member_report)

            # Create team report as compilation of personal reports
            team_report = TeamReportData(
                team_id=team_id,
                team_name=team_info.get('name', f'Team {team_id}') if team_info else f'Team {team_id}',
                member_reports=member_reports
            )

            # Calculate team aggregates
            team_report = self._calculate_team_aggregates_detailed(team_report)

            result = {
                "status": 200,
                "message": f"Team report generated for manager {manager_info.get('name', 'Manager')}",
                "data": {
                    "team_report": team_report.to_dict()
                }
            }

            return result

        except Exception as e:
            return {"status": 500, "message": f"Error generating team report: {str(e)}"}

    def generate_department_report(self, director_user_id: int, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Generate department report for director showing department-wide performance and detailed workload analysis
        
        Args:
            director_user_id: ID of the director requesting the report
            start_date: Start date for filtering (YYYY-MM-DD format)
            end_date: End date for filtering (YYYY-MM-DD format)
        """
        try:
            # Get director information
            director_info = self.repo.get_user_info(director_user_id)
            if not director_info:
                return {"status": 404, "message": f"Director {director_user_id} not found"}

            # Check if user is a director
            user_role = director_info.get('role')
            if user_role is None:
                role_str = ''
            elif isinstance(user_role, int):
                # Handle case where role is stored as integer (1=staff, 2=manager, 3=director)
                role_map = {1: 'staff', 2: 'manager', 3: 'director'}
                role_str = role_map.get(user_role, '')
            else:
                role_str = str(user_role).lower()
            
            if role_str != 'director':
                return {"status": 403, "message": "Only directors can generate department reports"}

            dept_id = director_info.get('dept_id')
            if not dept_id:
                return {"status": 400, "message": "Director is not assigned to a department"}

            # Get department information
            dept_info = self.repo.get_dept_info(dept_id)
            if not dept_info:
                print(f"Warning: Department info not found for dept_id {dept_id}")
            
            # Get department members
            dept_members = self.repo.get_dept_members(dept_id)
            if not dept_members:
                print(f"Warning: No department members found for dept_id {dept_id}")

            # Generate personal reports for all department members except directors and managers (compilation approach)
            member_reports = []
            for member in dept_members:
                # Skip directors and managers from the department report
                member_role = member.get('role')
                if member_role is None:
                    member_role_str = ''
                elif isinstance(member_role, int):
                    role_map = {1: 'staff', 2: 'manager', 3: 'director'}
                    member_role_str = role_map.get(member_role, '')
                else:
                    member_role_str = str(member_role).lower()
                
                # Skip directors and managers
                if member_role_str in ['director', 'manager']:
                    continue
                    
                member_tasks = self.repo.get_user_tasks(member['userid'], start_date, end_date)
                member_projects = self.repo.get_user_projects(member['userid'], start_date, end_date)
                
                # Handle None values
                if member_tasks is None:
                    member_tasks = []
                if member_projects is None:
                    member_projects = []
                
                member_report = self._generate_user_report_data(member, member_tasks, member_projects)
                
                # Add team information to member report for department view
                member_report.team_id = member.get('team_id')
                member_report.team_name = None
                if member.get('team_id'):
                    team_info = self.repo.get_team_info(member.get('team_id'))
                    if team_info:
                        member_report.team_name = team_info.get('name', f'Team {member.get("team_id")}')
                
                member_reports.append(member_report)

            # Create department report as compilation of personal reports
            dept_report = TeamReportData(
                dept_id=dept_id,
                dept_name=dept_info.get('name', f'Department {dept_id}') if dept_info else f'Department {dept_id}',
                member_reports=member_reports
            )

            # Calculate department aggregates
            dept_report = self._calculate_team_aggregates_detailed(dept_report)

            result = {
                "status": 200,
                "message": f"Department report generated for director {director_info.get('name', 'Director')}",
                "data": {
                    "department_report": dept_report.to_dict()
                }
            }

            return result

        except Exception as e:
            return {"status": 500, "message": f"Error generating department report: {str(e)}"}

    def _generate_user_report_data(self, user_info: Dict[str, Any], tasks: List[Dict[str, Any]], projects: List[Dict[str, Any]]) -> ReportData:
        """Generate report data for a single user organized by projects"""
        # Handle None values for safety
        if tasks is None:
            tasks = []
        if projects is None:
            projects = []
            
        # Handle role conversion from integer to string if necessary
        user_role_raw = user_info.get('role')
        if user_role_raw is None:
            user_role_str = 'Unknown'
        elif isinstance(user_role_raw, int):
            # Handle case where role is stored as integer (1=staff, 2=manager, 3=director)
            role_map = {1: 'staff', 2: 'manager', 3: 'director'}
            user_role_str = role_map.get(user_role_raw, 'Unknown')
        else:
            user_role_str = str(user_role_raw)
            
        # Initialize report data
        report_data = ReportData(
            user_id=user_info.get('userid'),
            user_name=user_info.get('name', 'Unknown'),
            user_role=user_role_str
        )

        # Get project names cache to avoid duplicate requests
        project_name_cache = {}
        for project in projects:
            project_id = project.get('id')
            project_name = project.get('proj_name', 'Unknown Project')
            if project_id:
                project_name_cache[project_id] = project_name

        # Organize report by projects that belong to the user
        projects_breakdown = []
        total_tasks = 0
        completed_tasks = 0
        overdue_tasks = 0
        all_task_durations = []

        for project in projects:
            project_id = project.get('id')
            project_name = project.get('proj_name', 'Unknown Project')
            
            print(f"Processing project {project_id}: {project_name} for user {user_info.get('name')}")
            
            # Get all tasks for this project from the task service
            project_tasks = self.repo.get_project_tasks(project_id) if project_id else []
            if project_tasks is None:
                project_tasks = []
            
            print(f"Found {len(project_tasks)} total tasks in project {project_id}")
            
            # Process each task in the project
            project_task_details = []
            project_completed_tasks = 0
            project_overdue_tasks = 0
            project_task_durations = []
            
            for task in project_tasks:
                status = task.get('status', 'Unknown')
                task_name = task.get('task_name', 'Unknown Task')
                
                # Get owner information
                owner_id = task.get('owner_id')
                owner_name = task.get('owner_name')
                if not owner_name and owner_id:
                    # Fetch owner info from user service
                    owner_info = self.repo.get_user_info(owner_id)
                    owner_name = owner_info.get('name', f'User {owner_id}') if owner_info else f'User {owner_id}'
                elif not owner_name:
                    owner_name = 'Unknown'
                
                # Get collaborators information
                collaborators = task.get('collaborators', []) or []
                collaborator_names = []
                if isinstance(collaborators, list):
                    for collab_id in collaborators:
                        # Get collaborator info from user service
                        collab_info = self.repo.get_user_info(collab_id)
                        if collab_info:
                            collaborator_names.append(collab_info.get('name', f'User {collab_id}'))
                        else:
                            collaborator_names.append(f'User {collab_id}')
                
                # Parse dates for analysis
                created_at = task.get('created_at')
                completed_at = task.get('completed_at')
                due_date = task.get('due_date')
                
                # Calculate if task is overdue
                is_overdue = False
                days_overdue = 0
                if due_date and status not in ['Completed']:
                    try:
                        due_date_parsed = dateparser.parse(due_date)
                        if due_date_parsed:
                            due_date_only = due_date_parsed.date()
                            current_date = datetime.now().date()
                            
                            if current_date > due_date_only:
                                is_overdue = True
                                days_overdue = (current_date - due_date_only).days
                                project_overdue_tasks += 1
                    except Exception as e:
                        print(f"Error parsing due date '{due_date}' for task '{task_name}': {e}")
                        pass
                
                # Calculate completion time for completed tasks
                completion_days = None
                was_completed_late = False
                if status == 'Completed':
                    project_completed_tasks += 1
                    
                    if created_at and completed_at:
                        try:
                            created_date = dateparser.parse(created_at)
                            completed_date = dateparser.parse(completed_at)
                            completion_days = (completed_date - created_date).days
                            if completion_days >= 0:
                                project_task_durations.append(max(completion_days, 1))
                                all_task_durations.append(max(completion_days, 1))
                            
                            # Check if completed late
                            if due_date:
                                due_date_parsed = dateparser.parse(due_date)
                                if completed_date > due_date_parsed:
                                    was_completed_late = True
                        except Exception as e:
                            print(f"Error parsing task dates: {e}")
                            pass
                
                # Add detailed task information
                task_detail = {
                    'task_id': task.get('id'),
                    'task_name': task_name,
                    'status': status,
                    'priority': task.get('priority', 'Normal'),
                    'owner_id': owner_id,
                    'owner_name': owner_name,
                    'collaborators': collaborator_names,
                    'created_at': created_at,
                    'due_date': due_date,
                    'completed_at': completed_at,
                    'completion_days': completion_days,
                    'is_overdue': is_overdue,
                    'days_overdue': days_overdue,
                    'was_completed_late': was_completed_late,
                    'description': task.get('description', '')
                }
                project_task_details.append(task_detail)
            
            # Calculate project statistics
            total_project_tasks = len(project_tasks)
            project_completion_percentage = (project_completed_tasks / total_project_tasks * 100) if total_project_tasks > 0 else 0
            project_overdue_percentage = (project_overdue_tasks / total_project_tasks * 100) if total_project_tasks > 0 else 0
            
            # Calculate average task duration for this project
            avg_project_duration = statistics.mean(project_task_durations) if project_task_durations else None
            
            # Estimate project completion date
            projected_completion = None
            if avg_project_duration and total_project_tasks > project_completed_tasks:
                remaining_tasks = total_project_tasks - project_completed_tasks
                estimated_days = int(remaining_tasks * avg_project_duration)
                projected_completion = (datetime.now() + timedelta(days=estimated_days)).strftime('%Y-%m-%d')
            elif total_project_tasks == project_completed_tasks:
                projected_completion = "Completed"
            
            # Create project breakdown
            project_breakdown = {
                'project_id': project_id,
                'project_name': project_name,
                'total_tasks': total_project_tasks,
                'completed_tasks': project_completed_tasks,
                'overdue_tasks': project_overdue_tasks,
                'completion_percentage': project_completion_percentage,
                'overdue_percentage': project_overdue_percentage,
                'average_task_duration': avg_project_duration,
                'projected_completion_date': projected_completion,
                'task_details': project_task_details
            }
            
            projects_breakdown.append(project_breakdown)
            
            # Update totals
            total_tasks += total_project_tasks
            completed_tasks += project_completed_tasks
            overdue_tasks += project_overdue_tasks

        # Set report data
        report_data.total_tasks = total_tasks
        report_data.completed_tasks = completed_tasks
        report_data.overdue_tasks = overdue_tasks
        report_data.completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        report_data.overdue_percentage = (overdue_tasks / total_tasks * 100) if total_tasks > 0 else 0
        report_data.average_task_duration = statistics.mean(all_task_durations) if all_task_durations else None
        report_data.total_projects = len(projects)
        
        # Set projects breakdown as the main report content
        report_data.projects_breakdown = projects_breakdown
        
        # Also maintain backward compatibility for project_stats
        project_stats = []
        for project_breakdown in projects_breakdown:
            project_stat = {
                'project_id': project_breakdown['project_id'],
                'project_name': project_breakdown['project_name'],
                'total_tasks': project_breakdown['total_tasks'],
                'completed_tasks': project_breakdown['completed_tasks'],
                'overdue_tasks': project_breakdown['overdue_tasks'],
                'completion_percentage': project_breakdown['completion_percentage'],
                'overdue_percentage': project_breakdown['overdue_percentage'],
                'average_task_duration': project_breakdown['average_task_duration'],
                'projected_completion_date': project_breakdown['projected_completion_date']
            }
            project_stats.append(project_stat)
        
        report_data.project_stats = project_stats
        
        # Create task_details list for backward compatibility
        all_task_details = []
        for project_breakdown in projects_breakdown:
            for task in project_breakdown['task_details']:
                task_copy = task.copy()
                task_copy['project_name'] = project_breakdown['project_name']
                all_task_details.append(task_copy)
        report_data.task_details = all_task_details

        return report_data

    def _calculate_team_aggregates(self, team_report: TeamReportData) -> TeamReportData:
        """Calculate aggregated statistics for team/department report"""
        if not team_report.member_reports:
            return team_report

        # Aggregate totals
        total_tasks = sum(report.total_tasks for report in team_report.member_reports)
        total_projects = sum(report.total_projects for report in team_report.member_reports)
        completed_tasks = sum(report.completed_tasks for report in team_report.member_reports)
        
        # Calculate team completion percentage
        team_completion = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Calculate average task duration across all team members
        all_durations = [report.average_task_duration for report in team_report.member_reports 
                        if report.average_task_duration is not None]
        team_avg_duration = statistics.mean(all_durations) if all_durations else None

        team_report.total_team_tasks = total_tasks
        team_report.total_team_projects = total_projects
        team_report.team_completion_percentage = team_completion
        team_report.team_average_task_duration = team_avg_duration

        return team_report

    def _calculate_team_aggregates_detailed(self, team_report: TeamReportData) -> TeamReportData:
        """Calculate detailed aggregated statistics for team/department report including task details"""
        if not team_report.member_reports:
            return team_report

        # Aggregate basic totals with error handling
        total_tasks = 0
        total_projects = 0
        completed_tasks = 0
        total_overdue = 0
        
        for report in team_report.member_reports:
            total_tasks += getattr(report, 'total_tasks', 0) or 0
            total_projects += getattr(report, 'total_projects', 0) or 0
            completed_tasks += getattr(report, 'completed_tasks', 0) or 0
            total_overdue += getattr(report, 'overdue_tasks', 0) or 0
        
        # Calculate team completion percentage
        team_completion = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        team_overdue_percentage = (total_overdue / total_tasks * 100) if total_tasks > 0 else 0
        
        # Calculate average task duration across all team members
        all_durations = []
        for report in team_report.member_reports:
            duration = getattr(report, 'average_task_duration', None)
            if duration is not None:
                all_durations.append(duration)
        team_avg_duration = statistics.mean(all_durations) if all_durations else None

        # Aggregate all task details from team members
        all_task_details = []
        team_task_stats = {}
        
        for member_report in team_report.member_reports:
            # Add member's task details to team aggregate
            member_tasks = getattr(member_report, 'task_details', []) or []
            for task in member_tasks:
                # Add member name to task for team context
                task_copy = task.copy() if task else {}
                task_copy['team_member'] = getattr(member_report, 'user_name', 'Unknown')
                task_copy['member_role'] = getattr(member_report, 'user_role', 'Unknown')
                all_task_details.append(task_copy)
            
            # Aggregate task status statistics
            task_stats = getattr(member_report, 'task_stats', {}) or {}
            for status, count in task_stats.items():
                team_task_stats[status] = team_task_stats.get(status, 0) + (count or 0)

        # Aggregate all project details from team members
        all_project_stats = []
        for member_report in team_report.member_reports:
            project_stats = getattr(member_report, 'project_stats', []) or []
            for project in project_stats:
                if not project:  # Skip None projects
                    continue
                    
                # Check if project already exists in team aggregation
                project_id = project.get('project_id')
                existing_project = next((p for p in all_project_stats if p.get('project_id') == project_id), None)
                
                if existing_project:
                    # Merge project data from multiple team members
                    existing_project['total_tasks'] = (existing_project.get('total_tasks', 0) or 0) + (project.get('total_tasks', 0) or 0)
                    existing_project['completed_tasks'] = (existing_project.get('completed_tasks', 0) or 0) + (project.get('completed_tasks', 0) or 0)
                    existing_project['overdue_tasks'] = (existing_project.get('overdue_tasks', 0) or 0) + (project.get('overdue_tasks', 0) or 0)
                    existing_project['late_completions'] = (existing_project.get('late_completions', 0) or 0) + (project.get('late_completions', 0) or 0)
                    
                    # Merge task assignees safely
                    project_assignees = project.get('task_assignees', {}) or {}
                    for owner_id, assignee_info in project_assignees.items():
                        if owner_id not in existing_project['task_assignees']:
                            existing_project['task_assignees'][owner_id] = assignee_info
                        else:
                            existing_tasks = existing_project['task_assignees'][owner_id].get('tasks', []) or []
                            new_tasks = assignee_info.get('tasks', []) or []
                            existing_project['task_assignees'][owner_id]['tasks'] = existing_tasks + new_tasks
                    
                    # Recalculate percentages
                    total_tasks_proj = existing_project.get('total_tasks', 0) or 0
                    completed_tasks_proj = existing_project.get('completed_tasks', 0) or 0
                    overdue_tasks_proj = existing_project.get('overdue_tasks', 0) or 0
                    
                    existing_project['completion_percentage'] = (completed_tasks_proj / total_tasks_proj * 100) if total_tasks_proj > 0 else 0
                    existing_project['overdue_percentage'] = (overdue_tasks_proj / total_tasks_proj * 100) if total_tasks_proj > 0 else 0
                else:
                    # Add new project to team aggregation
                    project_copy = project.copy()
                    # Ensure task_assignees exists
                    if 'task_assignees' not in project_copy:
                        project_copy['task_assignees'] = {}
                    all_project_stats.append(project_copy)

        # Set aggregated data
        team_report.total_team_tasks = total_tasks
        team_report.total_team_projects = total_projects
        team_report.team_completion_percentage = team_completion
        team_report.team_overdue_percentage = team_overdue_percentage
        team_report.team_average_task_duration = team_avg_duration
        team_report.team_task_stats = team_task_stats
        team_report.team_task_details = all_task_details
        team_report.team_project_stats = all_project_stats

        return team_report

    def _generate_detailed_workload_analysis(self, member_reports: List[Any], start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Generate detailed workload analysis for team/department members including projects and tasks breakdown
        
        Args:
            member_reports: List of ReportData objects for team/department members
            start_date: Start date for filtering (YYYY-MM-DD format)
            end_date: End date for filtering (YYYY-MM-DD format)
        
        This provides comprehensive scheduling information showing:
        - Projects each member is working on
        - Tasks per project for each member
        - Workload distribution across projects
        - Timeline and scheduling conflicts
        """
        detailed_analysis = {
            'members_workload': [],
            'project_distribution': {},
            'workload_summary': {},
            'scheduling_insights': []
        }
        
        total_member_hours = 0
        project_member_mapping = {}
        
        for member in member_reports:
            member_analysis = {
                'member_id': member.user_id,
                'member_name': member.user_name or 'Unknown',
                'member_role': member.user_role or 'Unknown',
                'projects_breakdown': [],
                'total_tasks': 0,
                'total_projects': 0,
                'workload_score': 0,
                'availability_status': 'Available',
                'scheduling_conflicts': []
            }
            
            # Group tasks by project for this member
            projects_tasks = {}
            all_member_tasks = getattr(member, 'task_details', [])
            project_name_cache = {}  # Cache project names to avoid duplicate requests
            
            for task in all_member_tasks:
                project_id = task.get('project_id')
                
                # Get proper project name
                project_name = 'No Project'
                if project_id:
                    if project_id not in project_name_cache:
                        # Fetch project info from projects service
                        project_info = self.repo.get_project_info(project_id)
                        if project_info:
                            project_name_cache[project_id] = project_info.get('proj_name', f'Project {project_id}')
                        else:
                            project_name_cache[project_id] = f'Project {project_id}'
                    project_name = project_name_cache[project_id]
                
                if project_id not in projects_tasks:
                    projects_tasks[project_id] = {
                        'project_id': project_id,
                        'project_name': project_name,
                        'tasks': [],
                        'total_tasks': 0,
                        'completed_tasks': 0,
                        'in_progress_tasks': 0,
                        'overdue_tasks': 0,
                        'estimated_hours': 0,
                        'completion_percentage': 0
                    }
                
                projects_tasks[project_id]['tasks'].append(task)
                projects_tasks[project_id]['total_tasks'] += 1
                
                # Categorize task status
                status_raw = task.get('status')
                if status_raw is None:
                    status = 'unknown'
                elif isinstance(status_raw, int):
                    # Handle case where status is stored as integer
                    status_map = {1: 'pending', 2: 'in progress', 3: 'completed', 4: 'under review'}
                    status = status_map.get(status_raw, 'unknown')
                else:
                    status = str(status_raw).lower()
                if status == 'completed':
                    projects_tasks[project_id]['completed_tasks'] += 1
                elif status == 'in progress':
                    projects_tasks[project_id]['in_progress_tasks'] += 1
                
                if task.get('is_overdue'):
                    projects_tasks[project_id]['overdue_tasks'] += 1
                
                # Estimate hours (simplified calculation)
                task_priority_raw = task.get('priority')
                if task_priority_raw is None:
                    task_priority = 'medium'
                elif isinstance(task_priority_raw, int):
                    # Handle case where priority is stored as integer (1=high, 2=medium, 3=low)
                    priority_map = {1: 'high', 2: 'medium', 3: 'low'}
                    task_priority = priority_map.get(task_priority_raw, 'medium')
                else:
                    task_priority = str(task_priority_raw).lower()
                if task_priority == 'high':
                    estimated_hours = 8
                elif task_priority == 'medium':
                    estimated_hours = 4
                else:
                    estimated_hours = 2
                    
                projects_tasks[project_id]['estimated_hours'] += estimated_hours
            
            # Calculate project-level metrics
            for project_id, project_data in projects_tasks.items():
                total_tasks = project_data['total_tasks']
                completed_tasks = project_data['completed_tasks']
                
                project_data['completion_percentage'] = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
                
                # Add to project member mapping
                if project_id not in project_member_mapping:
                    project_member_mapping[project_id] = {
                        'project_name': project_data['project_name'],
                        'members': [],
                        'total_members': 0,
                        'total_tasks_across_members': 0
                    }
                
                project_member_mapping[project_id]['members'].append({
                    'member_name': member.user_name or 'Unknown',
                    'member_role': member.user_role or 'Unknown',
                    'tasks_count': total_tasks,
                    'completion_rate': project_data['completion_percentage'],
                    'estimated_hours': project_data['estimated_hours']
                })
                project_member_mapping[project_id]['total_members'] += 1
                project_member_mapping[project_id]['total_tasks_across_members'] += total_tasks
                
                member_analysis['projects_breakdown'].append(project_data)
            
            # Calculate member-level metrics
            member_analysis['total_projects'] = len(projects_tasks)
            member_analysis['total_tasks'] = sum(p['total_tasks'] for p in projects_tasks.values())
            total_estimated_hours = sum(p['estimated_hours'] for p in projects_tasks.values())
            member_analysis['estimated_weekly_hours'] = total_estimated_hours
            
            # Calculate workload score (0-100, where 100 is maximum capacity)
            # Assuming 40 hours per week as full capacity
            workload_score = min(100, (total_estimated_hours / 40) * 100)
            member_analysis['workload_score'] = round(workload_score, 1)
            
            # Determine availability status
            if workload_score >= 90:
                member_analysis['availability_status'] = 'Overloaded'
            elif workload_score >= 70:
                member_analysis['availability_status'] = 'Busy'
            elif workload_score >= 40:
                member_analysis['availability_status'] = 'Moderate'
            else:
                member_analysis['availability_status'] = 'Available'
            
            # Check for scheduling conflicts (multiple high-priority tasks with overlapping deadlines)
            high_priority_tasks = []
            for task in all_member_tasks:
                priority_raw = task.get('priority')
                status_raw = task.get('status')
                
                # Safe priority check
                is_high_priority = False
                if isinstance(priority_raw, int) and priority_raw == 1:
                    is_high_priority = True
                elif isinstance(priority_raw, str) and priority_raw.lower() == 'high':
                    is_high_priority = True
                
                # Safe status check
                is_not_completed = True
                if isinstance(status_raw, int) and status_raw == 3:
                    is_not_completed = False
                elif isinstance(status_raw, str) and status_raw.lower() == 'completed':
                    is_not_completed = False
                
                if is_high_priority and is_not_completed:
                    high_priority_tasks.append(task)
            if len(high_priority_tasks) > 2:
                member_analysis['scheduling_conflicts'].append(f"Multiple high-priority tasks ({len(high_priority_tasks)}) may cause scheduling conflicts")
            
            overdue_count = sum(p['overdue_tasks'] for p in projects_tasks.values())
            if overdue_count > 0:
                member_analysis['scheduling_conflicts'].append(f"{overdue_count} overdue tasks affecting schedule")
            
            detailed_analysis['members_workload'].append(member_analysis)
            total_member_hours += total_estimated_hours
        
        # Generate project distribution analysis
        detailed_analysis['project_distribution'] = project_member_mapping
        
        # Generate workload summary
        if member_reports:
            avg_workload = total_member_hours / len(member_reports)
            detailed_analysis['workload_summary'] = {
                'total_estimated_hours': total_member_hours,
                'average_workload_per_member': round(avg_workload, 1),
                'total_projects': len(project_member_mapping),
                'members_count': len(member_reports),
                'high_workload_members': len([m for m in detailed_analysis['members_workload'] if m['workload_score'] >= 70]),
                'available_members': len([m for m in detailed_analysis['members_workload'] if m['workload_score'] < 40])
            }
        
        # Generate scheduling insights
        insights = []
        overloaded_members = [m for m in detailed_analysis['members_workload'] if m['availability_status'] == 'Overloaded']
        available_members = [m for m in detailed_analysis['members_workload'] if m['availability_status'] == 'Available']
        
        if overloaded_members:
            insights.append(f"{len(overloaded_members)} members are overloaded and may need task redistribution")
        
        if available_members:
            insights.append(f"{len(available_members)} members have capacity for additional tasks")
        
        # Project concentration analysis
        single_member_projects = [p for p in project_member_mapping.values() if p['total_members'] == 1]
        if single_member_projects:
            insights.append(f"{len(single_member_projects)} projects have only one assigned member (risk of bottlenecks)")
        
        detailed_analysis['scheduling_insights'] = insights
        
        return detailed_analysis

    

    def get_saved_reports(self, user_id: int, report_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all saved reports for a user"""
        try:
            if report_type:
                reports = self.repo.get_reports_by_type(report_type, user_id)
            else:
                reports = self.repo.get_reports_by_user(user_id)

            return {
                "status": 200,
                "message": f"Found {len(reports)} saved reports",
                "data": reports
            }

        except Exception as e:
            return {"status": 500, "message": f"Error retrieving saved reports: {str(e)}"}

    def get_saved_report(self, report_id: int, user_id: int) -> Dict[str, Any]:
        """Get a specific saved report"""
        try:
            report = self.repo.get_report(report_id)
            
            if not report:
                return {"status": 404, "message": f"Report {report_id} not found"}

            # Check if user has permission to view this report
            if report['generated_by'] != user_id:
                # Check if user is manager/director and report is from their team/dept
                user_info = self.repo.get_user_info(user_id)
                if not user_info:
                    return {"status": 403, "message": "Access denied"}

                user_role = (user_info.get('role') or '').lower()
                if user_role == 'manager' and report.get('team_id') == user_info.get('team_id'):
                    pass  # Manager can view team reports
                elif user_role == 'director' and report.get('dept_id') == user_info.get('dept_id'):
                    pass  # Director can view department reports
                else:
                    return {"status": 403, "message": "Access denied to this report"}

            return {
                "status": 200,
                "message": "Report retrieved successfully",
                "data": report
            }

        except Exception as e:
            return {"status": 500, "message": f"Error retrieving report: {str(e)}"}

    def delete_saved_report(self, report_id: int, user_id: int) -> Dict[str, Any]:
        """Delete a saved report"""
        try:
            # First check if report exists and user owns it
            report = self.repo.get_report(report_id)
            
            if not report:
                return {"status": 404, "message": f"Report {report_id} not found"}

            if report['generated_by'] != user_id:
                return {"status": 403, "message": "You can only delete reports you generated"}

            # Delete the report
            success = self.repo.delete_report(report_id)
            
            if success:
                return {
                    "status": 200,
                    "message": f"Report {report_id} deleted successfully"
                }
            else:
                return {"status": 500, "message": "Failed to delete report"}

        except Exception as e:
            return {"status": 500, "message": f"Error deleting report: {str(e)}"}

    def get_team_saved_reports(self, manager_user_id: int) -> Dict[str, Any]:
        """Get all saved reports for a manager's team"""
        try:
            # Get manager information
            manager_info = self.repo.get_user_info(manager_user_id)
            if not manager_info:
                return {"status": 404, "message": f"Manager {manager_user_id} not found"}

            # Check if user is a manager
            if (manager_info.get('role') or '').lower() != 'manager':
                return {"status": 403, "message": "Only managers can view team reports"}

            team_id = manager_info.get('team_id')
            if not team_id:
                return {"status": 400, "message": "Manager is not assigned to a team"}

            reports = self.repo.get_team_reports(team_id)

            return {
                "status": 200,
                "message": f"Found {len(reports)} team reports",
                "data": reports
            }

        except Exception as e:
            return {"status": 500, "message": f"Error retrieving team reports: {str(e)}"}

    def get_department_saved_reports(self, director_user_id: int) -> Dict[str, Any]:
        """Get all saved reports for a director's department"""
        try:
            # Get director information
            director_info = self.repo.get_user_info(director_user_id)
            if not director_info:
                return {"status": 404, "message": f"Director {director_user_id} not found"}

            # Check if user is a director
            if (director_info.get('role') or '').lower() != 'director':
                return {"status": 403, "message": "Only directors can view department reports"}

            dept_id = director_info.get('dept_id')
            if not dept_id:
                return {"status": 400, "message": "Director is not assigned to a department"}

            reports = self.repo.get_department_reports(dept_id)

            return {
                "status": 200,
                "message": f"Found {len(reports)} department reports",
                "data": reports
            }

        except Exception as e:
            return {"status": 500, "message": f"Error retrieving department reports: {str(e)}"}