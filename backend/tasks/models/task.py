from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime, UTC

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
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
# must include attachments also (PDF only)