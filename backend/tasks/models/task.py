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
    collaborators: List[int] = field(default_factory=list)
    status: str = "Unassigned"                    # Unassigned|In Progress|Under Review|Completed
    project_id: Optional[int] = None
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
