from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from dateutil import parser as dateparser


def parse_date(date_string: Optional[str]) -> Optional[datetime]:
    """Parse date string to datetime object"""
    if not date_string:
        return None
    try:
        return dateparser.parse(date_string)
    except Exception:
        return None


def calculate_duration_days(start_date: Optional[str], end_date: Optional[str]) -> Optional[float]:
    """Calculate duration between two dates in days"""
    if not start_date or not end_date:
        return None
    
    start = parse_date(start_date)
    end = parse_date(end_date)
    
    if not start or not end:
        return None
    
    duration = (end - start).total_seconds() / 86400  # Convert seconds to days
    return duration if duration > 0 else None


def format_percentage(value: float, decimal_places: int = 1) -> str:
    """Format a number as percentage string"""
    return f"{value:.{decimal_places}f}%"


def safe_divide(numerator: int, denominator: int, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is 0"""
    return (numerator / denominator) if denominator > 0 else default


def aggregate_task_stats(task_list: list) -> Dict[str, int]:
    """Aggregate task statistics by status"""
    stats = {}
    for task in task_list:
        status = task.get('status', 'Unknown')
        stats[status] = stats.get(status, 0) + 1
    return stats


def estimate_completion_date(remaining_tasks: int, avg_duration: float) -> Optional[str]:
    """Estimate project completion date based on remaining tasks and average duration"""
    if remaining_tasks <= 0 or not avg_duration or avg_duration <= 0:
        return None
    
    estimated_days = remaining_tasks * avg_duration
    completion_date = datetime.now() + timedelta(days=estimated_days)
    return completion_date.isoformat()


def validate_user_role(role: str, allowed_roles: list) -> bool:
    """Validate if user role is in allowed roles list"""
    return role.lower() in [r.lower() for r in allowed_roles]


def format_duration(days: Optional[float]) -> str:
    """Format duration in days to human readable string"""
    if days is None:
        return "N/A"
    
    if days < 1:
        hours = int(days * 24)
        return f"{hours} hour{'s' if hours != 1 else ''}"
    elif days < 30:
        return f"{days:.1f} day{'s' if days != 1 else ''}"
    else:
        weeks = int(days / 7)
        return f"{weeks} week{'s' if weeks != 1 else ''}"