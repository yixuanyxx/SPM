from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime, UTC

@dataclass
class Project:
    id: Optional[int] = field(default=None, init=False)                     # DB serial/bigint or UUID; adapt to your schema
    owner_id: int = 0
    proj_name: str = ""
    collaborators: Optional[List[int]] = field(default_factory=lambda: None)
    tasks: Optional[List[int]] = field(default_factory=lambda: None)         # List of task IDs (JSONB in Supabase)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
