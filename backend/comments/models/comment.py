from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime, UTC

@dataclass
class Comment:
    id: Optional[int] = field(default=None, init=False)
    task_id: int = 0
    user_id: int = 0
    user_name: str = ""
    user_role: str = ""
    content: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Comment object to dictionary"""
        result = {
            'task_id': self.task_id,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'user_role': self.user_role,
            'content': self.content,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
        if self.id is not None:
            result['id'] = self.id
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Comment':
        """Create Comment object from dictionary"""
        comment = cls(
            task_id=int(data.get('task_id', 0)),
            user_id=int(data.get('user_id', 0)),
            user_name=str(data.get('user_name', '')),
            user_role=str(data.get('user_role', '')),
            content=str(data.get('content', '')),
            created_at=str(data.get('created_at', datetime.now(UTC).isoformat())),
            updated_at=str(data.get('updated_at', datetime.now(UTC).isoformat()))
        )
        
        if 'id' in data and data['id'] is not None:
            comment.id = int(data['id'])
            
        return comment