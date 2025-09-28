from typing import Dict, Any, Optional, List
from models.team import Team
from repo.supa_team_repo import SupabaseTeamRepo

class TeamService:
    def __init__(self, repo: Optional[SupabaseTeamRepo] = None):
        self.repo = repo or SupabaseTeamRepo()

    def create_team(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new team"""
        # Check if team name already exists within the same department
        existing = self.repo.find_by_name_and_dept(payload["name"], payload["dept_id"])
        if existing:
            return {
                "__status": 200, 
                "Message": f"Team '{payload['name']}' already exists in this department.", 
                "data": existing[0]
            }

        team = Team(
            name=payload["name"],
            dept_id=payload["dept_id"]
        )

        # Remove id field for insertion
        data = team.__dict__.copy()
        data.pop("id", None)

        created = self.repo.insert_team(data)
        return {
            "__status": 201, 
            "Message": f"Team created! Team ID: {created.get('id')}", 
            "data": created
        }

    def get_team_by_id(self, team_id: int, include_dept_info: bool = False) -> Dict[str, Any]:
        """Get team by ID"""
        if include_dept_info:
            team = self.repo.get_team_with_dept_info(team_id)
        else:
            team = self.repo.get_team(team_id)
            
        if not team:
            return {
                "__status": 404, 
                "Message": f"Team with ID {team_id} not found"
            }
        return {
            "__status": 200, 
            "Message": "Team retrieved successfully", 
            "data": team
        }

    def get_all_teams(self, include_dept_info: bool = False) -> Dict[str, Any]:
        """Get all teams"""
        if include_dept_info:
            teams = self.repo.get_teams_with_dept_info()
        else:
            teams = self.repo.get_all_teams()
            
        return {
            "__status": 200, 
            "Message": f"Retrieved {len(teams)} team(s)", 
            "data": teams
        }

    def get_teams_by_dept_id(self, dept_id: int, include_dept_info: bool = False) -> Dict[str, Any]:
        """Get teams by department ID"""
        if include_dept_info:
            teams = self.repo.get_teams_by_dept_with_info(dept_id)
        else:
            teams = self.repo.find_by_dept_id(dept_id)
            
        return {
            "__status": 200, 
            "Message": f"Retrieved {len(teams)} team(s) for department {dept_id}", 
            "data": teams
        }

    def update_team(self, team_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Update team by ID"""
        # Check if team exists
        existing_team = self.repo.get_team(team_id)
        if not existing_team:
            return {
                "__status": 404, 
                "Message": f"Team with ID {team_id} not found"
            }

        # If updating name and/or dept_id, check for duplicates
        if "name" in payload:
            # Use the dept_id from payload if provided, otherwise use existing team's dept_id
            check_dept_id = payload.get("dept_id", existing_team["dept_id"])
            existing_name = self.repo.find_by_name_and_dept(payload["name"], check_dept_id)
            # Check if another team has this name in the same department (exclude current team)
            if existing_name and existing_name[0]["id"] != team_id:
                return {
                    "__status": 400, 
                    "Message": f"Team name '{payload['name']}' already exists in this department"
                }

        updated = self.repo.update_team(team_id, payload)
        return {
            "__status": 200, 
            "Message": f"Team {team_id} updated successfully", 
            "data": updated
        }

    def delete_team(self, team_id: int) -> Dict[str, Any]:
        """Delete team by ID"""
        # Check if team exists
        existing_team = self.repo.get_team(team_id)
        if not existing_team:
            return {
                "__status": 404, 
                "Message": f"Team with ID {team_id} not found"
            }

        # TODO: Check if team has users/projects before deleting
        # This would require user/project repository integration

        success = self.repo.delete_team(team_id)
        if success:
            return {
                "__status": 200, 
                "Message": f"Team {team_id} deleted successfully"
            }
        else:
            return {
                "__status": 500, 
                "Message": f"Failed to delete team {team_id}"
            }