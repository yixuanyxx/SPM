from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
# from datetime import datetime, UTC
import uuid

@dataclass
class User:
    id: uuid.UUID                   # DB serial/bigint or UUID; adapt to your schema
    userid: int = 0
    role: str = ""
    name: str = ""
    email: str = ""
    team_id: Optional[int] = None
    dept_id: Optional[int] = None
    notification_preferences: Dict[str, Any] = field(default_factory=lambda: {"in_app": True, "email": True})
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert User object to dictionary"""
        return {
            'id': str(self.id),
            'userid': self.userid,
            'role': self.role,
            'name': self.name,
            'email': self.email,
            'team_id': self.team_id,
            'dept_id': self.dept_id,
            'notification_preferences': self.notification_preferences
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create User object from dictionary"""
        # Handle notification preferences
        notification_preferences = data.get('notification_preferences')
        if notification_preferences is None:
            notification_preferences = {"in_app": True, "email": True}
        elif isinstance(notification_preferences, str):
            # If it's a JSON string, parse it
            import json
            try:
                notification_preferences = json.loads(notification_preferences)
            except json.JSONDecodeError:
                notification_preferences = {"in_app": True, "email": True}
        
        return cls(
            id=uuid.UUID(data['id']) if isinstance(data['id'], str) else data['id'],
            userid=data.get('userid', 0),
            role=data.get('role', ''),
            name=data.get('name', ''),
            email=data.get('email', ''),
            team_id=data.get('team_id'),
            dept_id=data.get('dept_id'),
            notification_preferences=notification_preferences
        )
    