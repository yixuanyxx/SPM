import os
import requests
from typing import Optional, Dict, Any, List

class ReportRepo:
    def __init__(self):
        # Microservice URLs - these should be environment variables in production
        self.users_service_url = os.getenv("USERS_SERVICE_URL", "http://localhost:5003")
        self.tasks_service_url = os.getenv("TASKS_SERVICE_URL", "http://localhost:5002")
        self.projects_service_url = os.getenv("PROJECTS_SERVICE_URL", "http://localhost:5001")
        self.team_service_url = os.getenv("TEAM_SERVICE_URL", "http://localhost:5004")
        self.dept_service_url = os.getenv("DEPT_SERVICE_URL", "http://localhost:5005")

    def get_user_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user information from users microservice"""
        try:
            response = requests.get(f"{self.users_service_url}/users/{user_id}")
            if response.status_code == 200:
                return response.json().get('data')
            return None
        except Exception as e:
            print(f"Error fetching user info: {e}")
            return None

    def get_user_tasks(self, user_id: int, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """Get all tasks for a user from tasks microservice with optional date filtering
        
        Args:
            user_id: ID of the user
            start_date: Start date for filtering (YYYY-MM-DD format)
            end_date: End date for filtering (YYYY-MM-DD format)
        """
        try:
            url = f"{self.tasks_service_url}/tasks/user-task/{user_id}"
            params = {}
            if start_date:
                params['start_date'] = start_date
            if end_date:
                params['end_date'] = end_date
                
            response = requests.get(url, params=params)
            if response.status_code == 200:
                tasks = response.json().get('data', [])
                
                # If microservice doesn't support date filtering, filter here
                if (start_date or end_date) and tasks:
                    filtered_tasks = []
                    for task in tasks:
                        task_date = task.get('created_at', '')
                        if task_date:
                            # Extract date part (YYYY-MM-DD)
                            task_date = task_date[:10]
                            
                            # Check if task falls within date range
                            if start_date and task_date < start_date:
                                continue
                            if end_date and task_date > end_date:
                                continue
                                
                        filtered_tasks.append(task)
                    return filtered_tasks
                
                return tasks
            return []
        except Exception as e:
            print(f"Error fetching user tasks: {e}")
            return []

    def get_user_projects(self, user_id: int, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """Get all projects for a user from projects microservice with optional date filtering
        
        Args:
            user_id: ID of the user
            start_date: Start date for filtering (YYYY-MM-DD format)
            end_date: End date for filtering (YYYY-MM-DD format)
        """
        try:
            url = f"{self.projects_service_url}/projects/user/{user_id}"
            params = {}
            if start_date:
                params['start_date'] = start_date
            if end_date:
                params['end_date'] = end_date
                
            response = requests.get(url, params=params)
            if response.status_code == 200:
                projects = response.json().get('data', [])
                
                # If microservice doesn't support date filtering, filter here
                if (start_date or end_date) and projects:
                    filtered_projects = []
                    for project in projects:
                        project_date = project.get('created_at', '')
                        if project_date:
                            # Extract date part (YYYY-MM-DD)
                            project_date = project_date[:10]
                            
                            # Check if project falls within date range
                            if start_date and project_date < start_date:
                                continue
                            if end_date and project_date > end_date:
                                continue
                                
                        filtered_projects.append(project)
                    return filtered_projects
                
                return projects
            return []
        except Exception as e:
            print(f"Error fetching user projects: {e}")
            return []

    def get_project_tasks(self, project_id: int) -> List[Dict[str, Any]]:
        """Get all tasks for a project from tasks microservice"""
        try:
            response = requests.get(f"{self.tasks_service_url}/tasks/project/{project_id}")
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
        except Exception as e:
            print(f"Error fetching project tasks: {e}")
            return []

    def get_project_info(self, project_id: int) -> Optional[Dict[str, Any]]:
        """Get project information from projects microservice"""
        try:
            response = requests.get(f"{self.projects_service_url}/projects/{project_id}")
            if response.status_code == 200:
                return response.json().get('data')
            return None
        except Exception as e:
            print(f"Error fetching project info: {e}")
            return None

    def get_team_members(self, team_id: int) -> List[Dict[str, Any]]:
        """Get all team members from users microservice"""
        try:
            response = requests.get(f"{self.users_service_url}/users/team/{team_id}")
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
        except Exception as e:
            print(f"Error fetching team members: {e}")
            return []

    def get_dept_members(self, dept_id: int) -> List[Dict[str, Any]]:
        """Get all department members from users microservice"""
        try:
            response = requests.get(f"{self.users_service_url}/users/department/{dept_id}")
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
        except Exception as e:
            print(f"Error fetching department members: {e}")
            return []

    def get_team_info(self, team_id: int) -> Optional[Dict[str, Any]]:
        """Get team information from team microservice"""
        try:
            response = requests.get(f"{self.team_service_url}/teams/{team_id}")
            if response.status_code == 200:
                return response.json().get('data')
            return None
        except Exception as e:
            print(f"Error fetching team info: {e}")
            return None

    def get_dept_info(self, dept_id: int) -> Optional[Dict[str, Any]]:
        """Get department information from dept microservice"""
        try:
            response = requests.get(f"{self.dept_service_url}/departments/{dept_id}")
            if response.status_code == 200:
                return response.json().get('data')
            return None
        except Exception as e:
            print(f"Error fetching department info: {e}")
            return None

    def get_tasks_by_team(self, team_id: int) -> List[Dict[str, Any]]:
        """Get all tasks for team members from tasks microservice"""
        try:
            response = requests.get(f"{self.tasks_service_url}/tasks/team/{team_id}")
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
        except Exception as e:
            print(f"Error fetching team tasks: {e}")
            return []

    def get_tasks_by_department(self, dept_id: int) -> List[Dict[str, Any]]:
        """Get all tasks for department members from tasks microservice"""
        try:
            response = requests.get(f"{self.tasks_service_url}/tasks/department/{dept_id}")
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
        except Exception as e:
            print(f"Error fetching department tasks: {e}")
            return []

