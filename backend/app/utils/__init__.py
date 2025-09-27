"""
Utilities package for the Volunteer Matching System
This module provides common utility functions and imports from specialized utility modules
"""

import re
import json
import hashlib
import secrets
import string
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime, date, time, timedelta
from decimal import Decimal
import uuid
from pathlib import Path
import asyncio
from functools import wraps

# Import from existing utility modules
from .logger import setup_logging, get_logger
from .validators import (
    validate_email,
    validate_password,
    validate_phone_number,
    validate_coordinates,
    validate_time_format,
    validate_date_format,
    validate_skill_level,
    validate_availability_slot,
    validate_event_schedule,
    validate_organization_data,
    validate_volunteer_data,
    validate_event_data,
    validate_match_data
)
from .security import (
    sanitize_input,
    sanitize_filename,
    generate_secure_token,
    hash_password,
    verify_password,
    generate_api_key,
    validate_api_key,
    escape_html,
    clean_text,
    validate_file_upload,
    check_file_type,
    generate_csrf_token,
    validate_csrf_token
)

# Common utility functions
def generate_id() -> str:
    """Generate a unique ID string"""
    return str(uuid.uuid4())

def generate_short_id(length: int = 8) -> str:
    """Generate a short unique ID"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))

def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime object to string"""
    return dt.strftime(format_str)

def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """Parse string to datetime object"""
    try:
        return datetime.strptime(date_str, format_str)
    except ValueError:
        return None

def format_date(d: date, format_str: str = "%Y-%m-%d") -> str:
    """Format date object to string"""
    return d.strftime(format_str)

def parse_date(date_str: str, format_str: str = "%Y-%m-%d") -> Optional[date]:
    """Parse string to date object"""
    try:
        return datetime.strptime(date_str, format_str).date()
    except ValueError:
        return None

def format_time(t: time, format_str: str = "%H:%M") -> str:
    """Format time object to string"""
    return t.strftime(format_str)

def parse_time(time_str: str, format_str: str = "%H:%M") -> Optional[time]:
    """Parse string to time object"""
    try:
        return datetime.strptime(time_str, format_str).time()
    except ValueError:
        return None

def get_current_timestamp() -> datetime:
    """Get current UTC timestamp"""
    return datetime.utcnow()

def get_current_date() -> date:
    """Get current date"""
    return date.today()

def add_days_to_date(d: date, days: int) -> date:
    """Add days to a date"""
    return d + timedelta(days=days)

def add_hours_to_datetime(dt: datetime, hours: int) -> datetime:
    """Add hours to a datetime"""
    return dt + timedelta(hours=hours)

def calculate_age(birth_date: date) -> int:
    """Calculate age from birth date"""
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def is_weekend(d: date) -> bool:
    """Check if date is weekend"""
    return d.weekday() >= 5

def is_weekday(d: date) -> bool:
    """Check if date is weekday"""
    return d.weekday() < 5

def get_day_of_week(d: date) -> str:
    """Get day of week name"""
    return d.strftime("%A").lower()

def format_currency(amount: Union[float, Decimal], currency: str = "USD") -> str:
    """Format amount as currency"""
    if currency == "USD":
        return f"${amount:,.2f}"
    return f"{amount:,.2f} {currency}"

def format_percentage(value: float, decimals: int = 1) -> str:
    """Format value as percentage"""
    return f"{value * 100:.{decimals}f}%"

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def capitalize_words(text: str) -> str:
    """Capitalize first letter of each word"""
    return ' '.join(word.capitalize() for word in text.split())

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    # Convert to lowercase and replace spaces with hyphens
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

def extract_emails(text: str) -> List[str]:
    """Extract email addresses from text"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, text)

def extract_phone_numbers(text: str) -> List[str]:
    """Extract phone numbers from text"""
    phone_pattern = r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
    return re.findall(phone_pattern, text)

def mask_email(email: str) -> str:
    """Mask email address for privacy"""
    if '@' not in email:
        return email
    
    local, domain = email.split('@', 1)
    if len(local) <= 2:
        masked_local = local[0] + '*' * (len(local) - 1)
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
    
    return f"{masked_local}@{domain}"

def mask_phone(phone: str) -> str:
    """Mask phone number for privacy"""
    if len(phone) < 4:
        return phone
    
    return phone[:-4] + '****'

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in kilometers (Haversine formula)"""
    from math import radians, cos, sin, asin, sqrt
    
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    return c * r

def is_within_radius(lat1: float, lon1: float, lat2: float, lon2: float, radius_km: float) -> bool:
    """Check if two coordinates are within specified radius"""
    distance = calculate_distance(lat1, lon1, lat2, lon2)
    return distance <= radius_km

def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple dictionaries"""
    result = {}
    for d in dicts:
        result.update(d)
    return result

def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result

def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """Flatten nested dictionary"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks of specified size"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def remove_duplicates(lst: List[Any]) -> List[Any]:
    """Remove duplicates from list while preserving order"""
    seen = set()
    return [x for x in lst if not (x in seen or seen.add(x))]

def group_by(lst: List[Dict[str, Any]], key: str) -> Dict[str, List[Dict[str, Any]]]:
    """Group list of dictionaries by key"""
    result = {}
    for item in lst:
        group_key = item.get(key)
        if group_key not in result:
            result[group_key] = []
        result[group_key].append(item)
    return result

def sort_by_key(lst: List[Dict[str, Any]], key: str, reverse: bool = False) -> List[Dict[str, Any]]:
    """Sort list of dictionaries by key"""
    return sorted(lst, key=lambda x: x.get(key, ''), reverse=reverse)

def filter_by_key(lst: List[Dict[str, Any]], key: str, value: Any) -> List[Dict[str, Any]]:
    """Filter list of dictionaries by key-value pair"""
    return [item for item in lst if item.get(key) == value]

def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely parse JSON string"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default

def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """Safely serialize object to JSON string"""
    try:
        return json.dumps(obj, default=str)
    except (TypeError, ValueError):
        return default

def create_hash(data: str, algorithm: str = "sha256") -> str:
    """Create hash of data"""
    if algorithm == "md5":
        return hashlib.md5(data.encode()).hexdigest()
    elif algorithm == "sha1":
        return hashlib.sha1(data.encode()).hexdigest()
    elif algorithm == "sha256":
        return hashlib.sha256(data.encode()).hexdigest()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

def retry_on_exception(max_retries: int = 3, delay: float = 1.0, exceptions: Tuple = (Exception,)):
    """Decorator to retry function on exception"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries - 1:
                        raise e
                    await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
            return None
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries - 1:
                        raise e
                    import time
                    time.sleep(delay * (2 ** attempt))  # Exponential backoff
            return None
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def measure_execution_time(func):
    """Decorator to measure function execution time"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = datetime.utcnow()
        result = await func(*args, **kwargs)
        end_time = datetime.utcnow()
        execution_time = (end_time - start_time).total_seconds()
        print(f"{func.__name__} executed in {execution_time:.4f} seconds")
        return result
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = datetime.utcnow()
        result = func(*args, **kwargs)
        end_time = datetime.utcnow()
        execution_time = (end_time - start_time).total_seconds()
        print(f"{func.__name__} executed in {execution_time:.4f} seconds")
        return result
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper

def ensure_directory_exists(path: Union[str, Path]) -> Path:
    """Ensure directory exists, create if it doesn't"""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return Path(filename).suffix.lower()

def is_valid_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """Check if file has allowed extension"""
    extension = get_file_extension(filename)
    return extension in allowed_extensions

def convert_bytes_to_mb(bytes_size: int) -> float:
    """Convert bytes to megabytes"""
    return bytes_size / (1024 * 1024)

def convert_mb_to_bytes(mb_size: float) -> int:
    """Convert megabytes to bytes"""
    return int(mb_size * 1024 * 1024)

def get_random_string(length: int = 10) -> str:
    """Generate random string of specified length"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))

def get_random_number(min_val: int = 0, max_val: int = 100) -> int:
    """Generate random number within range"""
    return secrets.randbelow(max_val - min_val + 1) + min_val

def is_valid_url(url: str) -> bool:
    """Check if string is valid URL"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None

def extract_domain(url: str) -> Optional[str]:
    """Extract domain from URL"""
    if not is_valid_url(url):
        return None
    
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return parsed.netloc

def normalize_phone_number(phone: str) -> str:
    """Normalize phone number to standard format"""
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Handle US phone numbers
    if len(digits) == 10:
        return f"+1{digits}"
    elif len(digits) == 11 and digits.startswith('1'):
        return f"+{digits}"
    elif len(digits) > 11:
        return f"+{digits}"
    else:
        return phone  # Return original if can't normalize

def format_phone_number(phone: str, format_style: str = "US") -> str:
    """Format phone number in specified style"""
    normalized = normalize_phone_number(phone)
    
    if format_style == "US" and normalized.startswith("+1") and len(normalized) == 12:
        digits = normalized[2:]
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    
    return normalized

def calculate_percentage(part: float, total: float) -> float:
    """Calculate percentage"""
    if total == 0:
        return 0.0
    return (part / total) * 100

def calculate_ratio(numerator: float, denominator: float) -> float:
    """Calculate ratio"""
    if denominator == 0:
        return 0.0
    return numerator / denominator

def round_to_decimals(value: float, decimals: int = 2) -> float:
    """Round value to specified decimal places"""
    return round(value, decimals)

def clamp_value(value: float, min_val: float, max_val: float) -> float:
    """Clamp value between min and max"""
    return max(min_val, min(value, max_val))

def interpolate_value(start: float, end: float, factor: float) -> float:
    """Interpolate between two values"""
    return start + (end - start) * factor

# Export all utility functions
__all__ = [
    # From logger module
    "setup_logging",
    "get_logger",
    
    # From validators module
    "validate_email",
    "validate_password",
    "validate_phone_number",
    "validate_coordinates",
    "validate_time_format",
    "validate_date_format",
    "validate_skill_level",
    "validate_availability_slot",
    "validate_event_schedule",
    "validate_organization_data",
    "validate_volunteer_data",
    "validate_event_data",
    "validate_match_data",
    
    # From security module
    "sanitize_input",
    "sanitize_filename",
    "generate_secure_token",
    "hash_password",
    "verify_password",
    "generate_api_key",
    "validate_api_key",
    "escape_html",
    "clean_text",
    "validate_file_upload",
    "check_file_type",
    "generate_csrf_token",
    "validate_csrf_token",
    
    # Common utility functions
    "generate_id",
    "generate_short_id",
    "format_datetime",
    "parse_datetime",
    "format_date",
    "parse_date",
    "format_time",
    "parse_time",
    "get_current_timestamp",
    "get_current_date",
    "add_days_to_date",
    "add_hours_to_datetime",
    "calculate_age",
    "is_weekend",
    "is_weekday",
    "get_day_of_week",
    "format_currency",
    "format_percentage",
    "format_file_size",
    "truncate_text",
    "capitalize_words",
    "slugify",
    "extract_emails",
    "extract_phone_numbers",
    "mask_email",
    "mask_phone",
    "calculate_distance",
    "is_within_radius",
    "merge_dicts",
    "deep_merge_dicts",
    "flatten_dict",
    "chunk_list",
    "remove_duplicates",
    "group_by",
    "sort_by_key",
    "filter_by_key",
    "safe_json_loads",
    "safe_json_dumps",
    "create_hash",
    "retry_on_exception",
    "measure_execution_time",
    "ensure_directory_exists",
    "get_file_extension",
    "is_valid_file_extension",
    "convert_bytes_to_mb",
    "convert_mb_to_bytes",
    "get_random_string",
    "get_random_number",
    "is_valid_url",
    "extract_domain",
    "normalize_phone_number",
    "format_phone_number",
    "calculate_percentage",
    "calculate_ratio",
    "round_to_decimals",
    "clamp_value",
    "interpolate_value"
]
