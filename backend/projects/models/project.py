from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime, UTC

@dataclass
class Project:
    id: Optional[int] = field(default=None, init=False)                     # DB serial/bigint or UUID; adapt to your schema
    owner_id: int = 0
    proj_name: str = ""
    collaborators: Optional[List[int]] = field(default_factory=lambda: None)
    tasks: Optional[List[int]] = field(default_factory=lambda: None)         # List of task IDs (JSONB in Supabase)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Project object to dictionary"""
        result = {
            'owner_id': self.owner_id,
            'proj_name': self.proj_name,
            'collaborators': self.collaborators,
            'tasks': self.tasks,
            'created_at': self.created_at
        }
        
        # Include ID if it exists
        if self.id is not None:
            result['id'] = self.id
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """Create Project object from dictionary with proper type conversion"""
        # Handle collaborators - ensure it's a list of integers
        collaborators = data.get('collaborators')
        if collaborators is not None:
            if isinstance(collaborators, str) and collaborators.strip():
                # Parse comma-separated string
                collaborators = [int(c.strip()) for c in collaborators.split(",") if c.strip()]
            elif isinstance(collaborators, list):
                # Ensure all elements are integers
                collaborators = [int(x) for x in collaborators if x is not None]
            else:
                collaborators = None
        
        # Handle tasks - ensure it's a list of integers
        tasks = data.get('tasks')
        if tasks is not None:
            if isinstance(tasks, str) and tasks.strip():
                # Parse comma-separated string
                tasks = [int(t.strip()) for t in tasks.split(",") if t.strip()]
            elif isinstance(tasks, list):
                # Ensure all elements are integers
                tasks = [int(x) for x in tasks if x is not None]
            else:
                tasks = None
        
        # Create project instance
        project = cls(
            owner_id=int(data.get('owner_id', 0)),
            proj_name=str(data.get('proj_name', '')),
            collaborators=collaborators,
            tasks=tasks,
            created_at=str(data.get('created_at', datetime.now(UTC).isoformat()))
        )
        
        # Set ID if provided (since it's init=False)
        if 'id' in data and data['id'] is not None:
            project.id = int(data['id'])
            
        return project
