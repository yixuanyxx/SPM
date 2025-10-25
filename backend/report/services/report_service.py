from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dateutil import parser as dateparser
import statistics

from models.report import ReportData, TeamReportData
from repo.report_repo import ReportRepo


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

            # Generate personal reports for all department members (including managers, excluding director)
            member_reports = []
            for member in dept_members:
                # Skip only the requesting director
                if member['userid'] == director_user_id:
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
                member_report.team_name = 'Unknown Team'  # Default fallback
                
                if member.get('team_id'):
                    team_info = self.repo.get_team_info(member.get('team_id'))
                    if team_info and team_info.get('name'):
                        member_report.team_name = team_info.get('name')
                    else:
                        # Fallback: Use team_id if name not available
                        member_report.team_name = f'Team {member.get("team_id")}'
                else:
                    member_report.team_name = 'No Team Assigned'
                
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
            
            # Get all tasks for this project from the task service
            project_tasks = self.repo.get_project_tasks(project_id) if project_id else []
            if project_tasks is None:
                project_tasks = []
            
            # Process each task in the project
            project_task_details = []
            project_completed_tasks = 0
            project_ongoing_tasks = 0
            project_under_review_tasks = 0
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
                
                # Normalize status and count tasks by status
                normalized_status = status.lower()
                
                # Count tasks by status
                if normalized_status == 'completed':
                    project_completed_tasks += 1
                elif normalized_status == 'ongoing':
                    project_ongoing_tasks += 1
                elif normalized_status == 'under review':
                    project_under_review_tasks += 1
                
                if normalized_status == 'completed':
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
                    'collaborator_ids': collaborators,  # Keep the original IDs for highlighting logic
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
                'in_progress_tasks': project_ongoing_tasks,
                'under_review_tasks': project_under_review_tasks,
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
                'in_progress_tasks': project_breakdown['in_progress_tasks'],
                'under_review_tasks': project_breakdown['under_review_tasks'],
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
        task_stats = {}
        for project_breakdown in projects_breakdown:
            for task in project_breakdown['task_details']:
                task_copy = task.copy()
                task_copy['project_name'] = project_breakdown['project_name']
                all_task_details.append(task_copy)
                
                # Count task statuses
                task_status = task.get('status', 'unknown')
                if isinstance(task_status, int):
                    # Map integer status to string
                    status_map = {1: 'ongoing', 2: 'ongoing', 3: 'completed', 4: 'under review'}
                    task_status = status_map.get(task_status, 'unknown')
                elif isinstance(task_status, str):
                    task_status = task_status.lower()
                    # Normalize legacy status names
                    if task_status in ['pending', 'in progress']:
                        task_status = 'ongoing'
                
                task_stats[task_status] = task_stats.get(task_status, 0) + 1
        
        report_data.task_details = all_task_details
        report_data.task_stats = task_stats

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

        # Aggregate all project details from team members (fixing double-counting)
        # Use a dict to track which projects we've already processed to avoid double-counting tasks
        all_projects_dict = {}
        
        for member_idx, member_report in enumerate(team_report.member_reports, 1):
            projects_breakdown = getattr(member_report, 'projects_breakdown', []) or []
            
            for project_breakdown in projects_breakdown:
                if not project_breakdown:
                    continue
                    
                project_id = project_breakdown.get('project_id')
                if not project_id:
                    continue
                
                # If we haven't seen this project yet, add it with full task details
                if project_id not in all_projects_dict:
                    # Get all tasks for this project from the repo (to avoid double-counting)
                    project_tasks = self.repo.get_project_tasks(project_id) if project_id else []
                    if project_tasks is None:
                        project_tasks = []
                    
                    # Build member involvement map for this project
                    member_involvement = {}  # {member_id: {'name': name, 'role': role, 'involved_tasks': [task_ids]}}
                    
                    # FIRST: Add the current member as involved (since this project is in their breakdown)
                    current_member_id = member_report.user_id
                    member_involvement[current_member_id] = {
                        'name': member_report.user_name,
                        'role': member_report.user_role,
                        'involved_tasks': []
                    }
                    
                    # THEN: Track task ownership and collaboration
                    # Also enrich tasks with owner names, collaborator names, and completion days
                    for task in project_tasks:
                        owner_id = task.get('owner_id')
                        collaborators = task.get('collaborators', []) or []
                        
                        # Enrich task with owner name if not present
                        if owner_id and not task.get('owner_name'):
                            owner_info = self.repo.get_user_info(owner_id)
                            if owner_info:
                                task['owner_name'] = owner_info.get('name', f'User {owner_id}')
                            else:
                                task['owner_name'] = f'User {owner_id}'
                        
                        # Enrich task with collaborator names
                        collab_names = []
                        if isinstance(collaborators, list):
                            for collab_id in collaborators:
                                collab_info = self.repo.get_user_info(collab_id)
                                if collab_info:
                                    collab_names.append(collab_info.get('name', f'User {collab_id}'))
                                else:
                                    collab_names.append(f'User {collab_id}')
                        task['collaborator_names'] = collab_names  # Add to task data
                        
                        # Calculate and enrich task with completion_days if not present
                        if not task.get('completion_days'):
                            status = task.get('status', '').lower()
                            if status == 'completed':
                                created_at = task.get('created_at')
                                completed_at = task.get('completed_at')
                                if created_at and completed_at:
                                    try:
                                        created_date = dateparser.parse(created_at)
                                        completed_date = dateparser.parse(completed_at)
                                        duration_days = (completed_date - created_date).days
                                        task['completion_days'] = max(duration_days, 1) if duration_days >= 0 else None
                                    except:
                                        pass
                        
                        # Track owner
                        if owner_id:
                            if owner_id not in member_involvement:
                                owner_info = self.repo.get_user_info(owner_id)
                                member_involvement[owner_id] = {
                                    'name': owner_info.get('name', f'User {owner_id}') if owner_info else f'User {owner_id}',
                                    'role': owner_info.get('role', 'Unknown') if owner_info else 'Unknown',
                                    'involved_tasks': []
                                }
                            member_involvement[owner_id]['involved_tasks'].append(task.get('id'))
                        
                        # Track collaborators
                        if isinstance(collaborators, list):
                            for collab_id in collaborators:
                                if collab_id not in member_involvement:
                                    collab_info = self.repo.get_user_info(collab_id)
                                    member_involvement[collab_id] = {
                                        'name': collab_info.get('name', f'User {collab_id}') if collab_info else f'User {collab_id}',
                                        'role': collab_info.get('role', 'Unknown') if collab_info else 'Unknown',
                                        'involved_tasks': []
                                    }
                                member_involvement[collab_id]['involved_tasks'].append(task.get('id'))
                    
                    # Calculate project metrics based on actual tasks (not duplicated)
                    total_project_tasks = len(project_tasks)
                    completed_tasks_count = sum(1 for t in project_tasks if t.get('status', '').lower() == 'completed')
                    ongoing_tasks = sum(1 for t in project_tasks if t.get('status', '').lower() == 'ongoing')
                    under_review_tasks = sum(1 for t in project_tasks if t.get('status', '').lower() == 'under review')
                    overdue_tasks = 0
                    
                    # Calculate average task duration from ALL completed tasks in project
                    task_durations = []
                    for task in project_tasks:
                        status = task.get('status', 'Unknown')
                        
                        # For completed tasks, calculate duration
                        if status.lower() == 'completed':
                            created_at = task.get('created_at')
                            completed_at = task.get('completed_at')
                            if created_at and completed_at:
                                try:
                                    created_date = dateparser.parse(created_at)
                                    completed_date = dateparser.parse(completed_at)
                                    duration_days = (completed_date - created_date).days
                                    if duration_days >= 0:
                                        task_durations.append(max(duration_days, 1))
                                except:
                                    pass
                    
                    avg_task_duration = statistics.mean(task_durations) if task_durations else None
                    
                    # Calculate projected completion date
                    projected_completion = None
                    if avg_task_duration and total_project_tasks > completed_tasks_count:
                        remaining_tasks = total_project_tasks - completed_tasks_count
                        estimated_days = int(remaining_tasks * avg_task_duration)
                        projected_completion = (datetime.now() + timedelta(days=estimated_days)).strftime('%Y-%m-%d')
                    elif total_project_tasks == completed_tasks_count:
                        projected_completion = "Completed"
                    
                    # Count overdue tasks
                    for task in project_tasks:
                        status = task.get('status', 'Unknown')
                        due_date = task.get('due_date')
                        if due_date and status not in ['Completed', 'completed']:
                            try:
                                due_date_parsed = dateparser.parse(due_date)
                                if due_date_parsed and due_date_parsed.date() < datetime.now().date():
                                    overdue_tasks += 1
                            except:
                                pass
                    
                    # Store enriched project data
                    all_projects_dict[project_id] = {
                        'project_id': project_id,
                        'project_name': project_breakdown.get('project_name', 'Unknown Project'),
                        'total_tasks': total_project_tasks,
                        'completed_tasks': completed_tasks_count,
                        'in_progress_tasks': ongoing_tasks,
                        'under_review_tasks': under_review_tasks,
                        'overdue_tasks': overdue_tasks,
                        'completion_percentage': (completed_tasks_count / total_project_tasks * 100) if total_project_tasks > 0 else 0,
                        'overdue_percentage': (overdue_tasks / total_project_tasks * 100) if total_project_tasks > 0 else 0,
                        'average_task_duration': avg_task_duration,
                        'projected_completion_date': projected_completion,
                        'all_tasks': project_tasks,  # Store all tasks for this project
                        'member_involvement': member_involvement  # Track which members are involved
                    }
                else:
                    # Project already exists, just add this member to the involvement map
                    current_member_id = member_report.user_id
                    existing_involvement = all_projects_dict[project_id]['member_involvement']
                    
                    if current_member_id not in existing_involvement:
                        # Add this member as involved
                        existing_involvement[current_member_id] = {
                            'name': member_report.user_name,
                            'role': member_report.user_role,
                            'involved_tasks': []
                        }
                        
                        # Check if this member owns or collaborates on any tasks
                        for task in all_projects_dict[project_id]['all_tasks']:
                            owner_id = task.get('owner_id')
                            collaborators = task.get('collaborators', []) or []
                            
                            if owner_id == current_member_id or current_member_id in collaborators:
                                existing_involvement[current_member_id]['involved_tasks'].append(task.get('id'))
        
        # Convert dict to list for final output
        all_project_stats = list(all_projects_dict.values())

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
