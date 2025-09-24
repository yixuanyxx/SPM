from dataclasses import dataclass, field
from typing import Optional, List
# from datetime import datetime, UTC
import uuid

class User:
    id: uuid.UUID                   # DB serial/bigint or UUID; adapt to your schema
    userid: int = 0
    role: str = ""
    name: str = ""
    email: str = ""
    team_id: Optional[int] = None
    dept_id: Optional[int] = None
    