from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime, UTC

@dataclass
class Notification:
    id: Optional[int] = field(default=None, init=False)                     # DB serial/bigint
    userid: int = 0                                                         # Foreign key to user table
    notification: str = ""                                                  # Notification message/content
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    is_read: bool = False                                                   # Track read/unread status
    notification_type: str = "general"                                     # Type: task_assigned, task_updated, etc.
    related_task_id: Optional[int] = None                                   # Optional reference to related task
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Notification object to dictionary"""
        result = {
            'userid': self.userid,
            'notification': self.notification,
            'created_at': self.created_at,
            'is_read': self.is_read,
            'notification_type': self.notification_type,
            'related_task_id': self.related_task_id
        }
        
        # Include ID if it exists
        if self.id is not None:
            result['id'] = self.id
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Notification':
        """Create Notification object from dictionary with proper type conversion"""
        # Helper function to safely convert to int
        def safe_int(value, default=0):
            if value is None:
                return default
            try:
                return int(value)
            except (ValueError, TypeError):
                return default
        
        # Helper function to safely convert to string
        def safe_str(value, default=''):
            if value is None:
                return default
            return str(value)
        
        # Create notification instance
        notification = cls(
            userid=safe_int(data.get('userid'), 0),
            notification=safe_str(data.get('notification'), ''),
            created_at=safe_str(data.get('created_at'), datetime.now(UTC).isoformat()),
            is_read=bool(data.get('is_read', False)),
            notification_type=safe_str(data.get('notification_type'), 'general'),
            related_task_id=safe_int(data.get('related_task_id')) if data.get('related_task_id') is not None else None
        )
        
        # Set ID if provided (since it's init=False)
        if 'id' in data and data['id'] is not None:
            notification.id = safe_int(data['id'])
            
        return notification
