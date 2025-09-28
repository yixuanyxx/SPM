from typing import Dict, Any, Optional, List
from models.dept import Department
from repo.supa_dept_repo import SupabaseDeptRepo

class DeptService:
    def __init__(self, repo: Optional[SupabaseDeptRepo] = None):
        self.repo = repo or SupabaseDeptRepo()

    def create_dept(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new department"""
        # Check if department name already exists
        existing = self.repo.find_by_name(payload["name"])
        if existing:
            return {
                "__status": 200, 
                "Message": f"Department '{payload['name']}' already exists.", 
                "data": existing[0]
            }

        dept = Department(
            name=payload["name"]
        )

        # Remove id field for insertion
        data = dept.__dict__.copy()
        data.pop("id", None)

        created = self.repo.insert_dept(data)
        return {
            "__status": 201, 
            "Message": f"Department created! Department ID: {created.get('id')}", 
            "data": created
        }

    def get_dept_by_id(self, dept_id: int) -> Dict[str, Any]:
        """Get department by ID"""
        dept = self.repo.get_dept(dept_id)
        if not dept:
            return {
                "__status": 404, 
                "Message": f"Department with ID {dept_id} not found"
            }
        return {
            "__status": 200, 
            "Message": "Department retrieved successfully", 
            "data": dept
        }

    def get_all_depts(self) -> Dict[str, Any]:
        """Get all departments"""
        depts = self.repo.get_all_depts()
        return {
            "__status": 200, 
            "Message": f"Retrieved {len(depts)} department(s)", 
            "data": depts
        }

    def update_dept(self, dept_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Update department by ID"""
        # Check if department exists
        existing_dept = self.repo.get_dept(dept_id)
        if not existing_dept:
            return {
                "__status": 404, 
                "Message": f"Department with ID {dept_id} not found"
            }

        # If updating name, check for duplicates
        if "name" in payload:
            existing_name = self.repo.find_by_name(payload["name"])
            # Check if another department has this name (exclude current dept)
            if existing_name and existing_name[0]["id"] != dept_id:
                return {
                    "__status": 400, 
                    "Message": f"Department name '{payload['name']}' already exists"
                }

        updated = self.repo.update_dept(dept_id, payload)
        return {
            "__status": 200, 
            "Message": f"Department {dept_id} updated successfully", 
            "data": updated
        }

    def delete_dept(self, dept_id: int) -> Dict[str, Any]:
        """Delete department by ID"""
        # Check if department exists
        existing_dept = self.repo.get_dept(dept_id)
        if not existing_dept:
            return {
                "__status": 404, 
                "Message": f"Department with ID {dept_id} not found"
            }

        # TODO: Check if department has teams before deleting
        # This would require team repository integration

        success = self.repo.delete_dept(dept_id)
        if success:
            return {
                "__status": 200, 
                "Message": f"Department {dept_id} deleted successfully"
            }
        else:
            return {
                "__status": 500, 
                "Message": f"Failed to delete department {dept_id}"
            }

    def get_dept_with_teams(self, dept_id: int) -> Dict[str, Any]:
        """Get department by ID with its teams"""
        # This method would need to be implemented when team integration is available
        # For now, it just returns the department info
        return self.get_dept_by_id(dept_id)