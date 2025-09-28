from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime, UTC

@dataclass
class Team:
    id: Optional[int] = field(default=None, init=False)
    dept_id: int = 0                               
    name: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
