from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime, UTC
from dateutil import parser as dateparser

@dataclass
class Task:
    id: Optional[int] = field(default=None, init=False)                     # DB serial/bigint or UUID; adapt to your schema
    owner_id: int = 0
    task_name: str = ""
    due_date: Optional[datetime] = None
    description: str = ""
    collaborators: Optional[List[int]] = field(default_factory=lambda: None)
    status: Optional[str] = None         # Unassigned|Ongoing|Under Review|Completed (Unassigned exist only for mgrs and directors)
    project_id: Optional[int] = None
    parent_task: Optional[int] = None   # References parent task ID, null if this is a parent task
    type: str = "parent"                # Either "parent" or "subtask" default is parent
    subtasks: Optional[List[int]] = field(default_factory=lambda: None)  # List of subtask IDs (JSONB in Supabase)
    attachments: Optional[List[Dict[str, str]]] = field(default_factory=lambda: None)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    attachments: Optional[List[Dict[str, str]]] = field(default_factory=lambda: None)  # PDF attachments
    priority: Optional[int] = None       # Priority level (optional integer)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Task object to dictionary"""
        result = {
            'owner_id': self.owner_id,
            'task_name': self.task_name,
            'description': self.description,
            'status': self.status,
            'project_id': self.project_id,
            'parent_task': self.parent_task,
            'type': self.type,
            'collaborators': self.collaborators,
            'subtasks': self.subtasks,
            'created_at': self.created_at,
            'attachments': self.attachments,
            'priority': self.priority
        }
        
        # Include ID if it exists
        if self.id is not None:
            result['id'] = self.id
            
        # Convert datetime to ISO string for database
        if self.due_date is not None:
            if isinstance(self.due_date, datetime):
                result['due_date'] = self.due_date.isoformat()
            else:
                result['due_date'] = self.due_date
        else:
            result['due_date'] = None
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create Task object from dictionary with proper type conversion"""
        # Handle due_date conversion
        due_date = data.get('due_date')
        if due_date is not None and isinstance(due_date, str):
            try:
                due_date = dateparser.parse(due_date)
            except Exception:
                due_date = None
        
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
        
        # Handle subtasks - ensure it's a list of integers
        subtasks = data.get('subtasks')
        if subtasks is not None:
            if isinstance(subtasks, str) and subtasks.strip():
                # Parse comma-separated string
                subtasks = [int(s.strip()) for s in subtasks.split(",") if s.strip()]
            elif isinstance(subtasks, list):
                # Ensure all elements are integers
                subtasks = [int(x) for x in subtasks if x is not None]
            else:
                subtasks = None
        
        # Handle attachments - ensure proper format
        attachments = data.get('attachments')
        if attachments is not None and not isinstance(attachments, list):
            attachments = None
        
        # Handle priority - ensure it's an integer or None
        priority = data.get('priority')
        if priority is not None:
            try:
                priority = int(priority)
            except (ValueError, TypeError):
                priority = None
        
        # Create task instance
        task = cls(
            owner_id=int(data.get('owner_id', 0)),
            task_name=str(data.get('task_name', '')),
            due_date=due_date,
            description=str(data.get('description', '')),
            collaborators=collaborators,
            status=data.get('status'),
            project_id=int(data['project_id']) if data.get('project_id') not in (None, '') else None,
            parent_task=int(data['parent_task']) if data.get('parent_task') not in (None, '') else None,
            type=str(data.get('type', 'parent')),
            subtasks=subtasks,
            created_at=str(data.get('created_at', datetime.now(UTC).isoformat())),
            attachments=attachments,
            priority=priority
        )
        
        # Set ID if provided (since it's init=False)
        if 'id' in data and data['id'] is not None:
            task.id = int(data['id'])
            
        return task