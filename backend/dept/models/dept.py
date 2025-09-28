from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Optional, List

@dataclass
class Department:
    id: Optional[int] = field(default=None, init=False)   # serial/bigint (Supabase will autogen)
    name: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
