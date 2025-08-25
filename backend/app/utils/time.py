from datetime import datetime, timezone, timedelta
from typing import Optional, Union
import pytz

def now() -> datetime:
    """Get current UTC datetime"""
    return datetime.now(timezone.utc)

def parse_datetime(date_string: str, timezone_name: str = "UTC") -> Optional[datetime]:
    """Parse datetime string with timezone support"""
    try:
        # Try parsing ISO format first
        dt = datetime.fromisoformat(date_string.replace("Z", "+00:00"))
        return dt
    except ValueError:
        try:
            # Try parsing common formats
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%d %H:%M:%S%z"
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_string, fmt)
                    if dt.tzinfo is None:
                        # Assume UTC if no timezone info
                        dt = dt.replace(tzinfo=timezone.utc)
                    return dt
                except ValueError:
                    continue
            
            return None
        except Exception:
            return None

def format_datetime(dt: datetime, format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.strftime(format_string)

def format_relative_time(dt: datetime) -> str:
    """Format datetime as relative time (e.g., '2 hours ago')"""
    now_dt = now()
    diff = now_dt - dt
    
    if diff.total_seconds() < 60:
        return "just now"
    elif diff.total_seconds() < 3600:
        minutes = int(diff.total_seconds() / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif diff.total_seconds() < 86400:
        hours = int(diff.total_seconds() / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.total_seconds() < 2592000:
        days = int(diff.total_seconds() / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    else:
        return format_datetime(dt, "%Y-%m-%d")

def calculate_duration(start_time: datetime, end_time: datetime) -> Optional[int]:
    """Calculate duration in seconds between two datetimes"""
    try:
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=timezone.utc)
        
        duration = end_time - start_time
        return int(duration.total_seconds())
    except Exception:
        return None

def is_recent(dt: datetime, threshold_minutes: int = 60) -> bool:
    """Check if datetime is within recent threshold"""
    now_dt = now()
    diff = now_dt - dt
    return diff.total_seconds() < (threshold_minutes * 60)

def get_timezone_offset(timezone_name: str = "UTC") -> int:
    """Get timezone offset in seconds from UTC"""
    try:
        tz = pytz.timezone(timezone_name)
        offset = tz.utcoffset(now())
        return int(offset.total_seconds())
    except Exception:
        return 0
