import re
from typing import Any, List, Dict
from datetime import datetime, date
import phonenumbers
from email_validator import validate_email as email_validate, EmailNotValidError

def validate_email(email: str) -> bool:
    """Validate email format"""
    try:
        # Use email-validator library for comprehensive validation
        email_validate(email)
        return True
    except EmailNotValidError:
        return False

def validate_password(password: str) -> bool:
    """Validate password strength"""
    if len(password) < 8:
        return False
    
    # Check for at least one letter and one number
    has_letter = re.search(r'[a-zA-Z]', password) is not None
    has_number = re.search(r'\d', password) is not None
    
    return has_letter and has_number

def validate_phone_number(phone: str) -> bool:
    """Validate phone number format"""
    try:
        # Parse phone number
        parsed = phonenumbers.parse(phone, None)
        return phonenumbers.is_valid_number(parsed)
    except phonenumbers.NumberParseException:
        # Fallback to simple regex validation
        phone_pattern = re.compile(r'^\+?[\d\s\-\(\)]{10,15}$')
        return bool(phone_pattern.match(phone))

def validate_username(username: str) -> bool:
    """Validate username format"""
    if not username or len(username) < 3 or len(username) > 50:
        return False
    
    # Allow letters, numbers, underscores, and hyphens
    username_pattern = re.compile(r'^[a-zA-Z0-9_-]+$')
    return bool(username_pattern.match(username))

def validate_name(name: str) -> bool:
    """Validate name format"""
    if not name or len(name) < 2 or len(name) > 100:
        return False
    
    # Allow letters, spaces, hyphens, and apostrophes
    name_pattern = re.compile(r"^[a-zA-Z\s\-']+$")
    return bool(name_pattern.match(name))

def validate_skill_level(level: str) -> bool:
    """Validate skill level"""
    valid_levels = ['beginner', 'intermediate', 'advanced', 'expert']
    return level.lower() in valid_levels

def validate_coordinates(latitude: float, longitude: float) -> bool:
    """Validate geographic coordinates"""
    return (
        isinstance(latitude, (int, float)) and 
        isinstance(longitude, (int, float)) and
        -90 <= latitude <= 90 and 
        -180 <= longitude <= 180
    )

def validate_date_range(start_date: date, end_date: date) -> bool:
    """Validate date range"""
    return start_date <= end_date

def validate_time_range(start_time: str, end_time: str) -> bool:
    """Validate time range in HH:MM format"""
    time_pattern = re.compile(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    
    if not (time_pattern.match(start_time) and time_pattern.match(end_time)):
        return False
    
    # Convert to minutes for comparison
    start_minutes = time_to_minutes(start_time)
    end_minutes = time_to_minutes(end_time)
    
    return start_minutes < end_minutes

def time_to_minutes(time_str: str) -> int:
    """Convert HH:MM time to minutes"""
    try:
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes
    except ValueError:
        return 0

def validate_url(url: str) -> bool:
    """Validate URL format"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP address
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))

def validate_postal_code(postal_code: str, country: str = 'US') -> bool:
    """Validate postal code format based on country"""
    patterns = {
        'US': r'^\d{5}(-\d{4})?$',  # 12345 or 12345-6789
        'UK': r'^[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}$',  # UK postcode
        'CA': r'^[A-Z]\d[A-Z]\s*\d[A-Z]\d$',  # Canadian postal code
        'DE': r'^\d{5}$',  # German postal code
        'FR': r'^\d{5}$',  # French postal code
    }
    
    pattern = patterns.get(country.upper(), r'^\w{3,10}$')  # Generic pattern
    return bool(re.match(pattern, postal_code.upper()))

def validate_age(age: int, min_age: int = 13, max_age: int = 120) -> bool:
    """Validate age within reasonable range"""
    return isinstance(age, int) and min_age <= age <= max_age

def validate_event_category(category: str) -> bool:
    """Validate event category"""
    valid_categories = [
        'environment', 'education', 'healthcare', 'social_services',
        'community_development', 'arts_culture', 'sports_recreation',
        'disaster_relief', 'animal_welfare', 'technology', 'other'
    ]
    return category.lower() in valid_categories

def validate_commitment_level(level: str) -> bool:
    """Validate commitment level"""
    valid_levels = ['low', 'flexible', 'high']
    return level.lower() in valid_levels

def validate_event_status(status: str) -> bool:
    """Validate event status"""
    valid_statuses = ['draft', 'active', 'full', 'cancelled', 'completed']
    return status.lower() in valid_statuses

def validate_match_status(status: str) -> bool:
    """Validate match status"""
    valid_statuses = ['pending', 'accepted', 'declined', 'expired', 'completed']
    return status.lower() in valid_statuses

def validate_role(role: str) -> bool:
    """Validate user role"""
    valid_roles = ['volunteer', 'organization', 'admin']
    return role.lower() in valid_roles

def validate_file_size(file_size: int, max_size_mb: int = 10) -> bool:
    """Validate file size"""
    max_size_bytes = max_size_mb * 1024 * 1024
    return 0 < file_size <= max_size_bytes

def validate_list_length(items: List[Any], min_length: int = 0, max_length: int = 100) -> bool:
    """Validate list length"""
    return min_length <= len(items) <= max_length

def validate_string_length(text: str, min_length: int = 0, max_length: int = 1000) -> bool:
    """Validate string length"""
    return min_length <= len(text) <= max_length

def validate_rating(rating: float) -> bool:
    """Validate rating value (0-5)"""
    return isinstance(rating, (int, float)) and 0 <= rating <= 5

def validate_percentage(value: float) -> bool:
    """Validate percentage value (0-100)"""
    return isinstance(value, (int, float)) and 0 <= value <= 100

def validate_positive_number(value: Any) -> bool:
    """Validate positive number"""
    try:
        num = float(value)
        return num > 0
    except (ValueError, TypeError):
        return False

def validate_non_negative_number(value: Any) -> bool:
    """Validate non-negative number"""
    try:
        num = float(value)
        return num >= 0
    except (ValueError, TypeError):
        return False

def validate_integer_range(value: int, min_val: int, max_val: int) -> bool:
    """Validate integer within range"""
    return isinstance(value, int) and min_val <= value <= max_val

def validate_json_structure(data: Dict[str, Any], required_fields: List[str]) -> tuple[bool, List[str]]:
    """Validate JSON structure has required fields"""
    missing_fields = []
    
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    
    return len(missing_fields) == 0, missing_fields

def validate_language_code(code: str) -> bool:
    """Validate ISO 639-1 language code"""
    # Common language codes
    valid_codes = [
        'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko',
        'ar', 'hi', 'th', 'vi', 'nl', 'sv', 'no', 'da', 'fi', 'pl'
    ]
    return code.lower() in valid_codes

def validate_timezone(timezone: str) -> bool:
    """Validate timezone string"""
    # Simple validation for common timezone formats
    timezone_pattern = re.compile(r'^[A-Z][a-z_]+/[A-Z][a-z_]+$')
    return bool(timezone_pattern.match(timezone))

def validate_skills_list(skills: List[Dict[str, Any]]) -> tuple[bool, List[str]]:
    """Validate skills list structure"""
    errors = []
    
    if not isinstance(skills, list):
        return False, ["Skills must be a list"]
    
    if len(skills) > 50:  # Reasonable limit
        errors.append("Too many skills (max 50)")
    
    for i, skill in enumerate(skills):
        if not isinstance(skill, dict):
            errors.append(f"Skill {i+1} must be an object")
            continue
        
        if 'name' not in skill or not skill['name']:
            errors.append(f"Skill {i+1} missing name")
        
        if 'level' in skill and not validate_skill_level(skill['level']):
            errors.append(f"Skill {i+1} has invalid level")
        
        if 'years_experience' in skill and not validate_non_negative_number(skill['years_experience']):
            errors.append(f"Skill {i+1} has invalid years_experience")
    
    return len(errors) == 0, errors

def validate_availability_list(availability: List[Dict[str, Any]]) -> tuple[bool, List[str]]:
    """Validate availability list structure"""
    errors = []
    
    if not isinstance(availability, list):
        return False, ["Availability must be a list"]
    
    valid_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    
    for i, avail in enumerate(availability):
        if not isinstance(avail, dict):
            errors.append(f"Availability {i+1} must be an object")
            continue
        
        if 'day' not in avail or avail['day'].lower() not in valid_days:
            errors.append(f"Availability {i+1} has invalid day")
        
        if 'start_time' not in avail or 'end_time' not in avail:
            errors.append(f"Availability {i+1} missing time fields")
            continue
        
        if not validate_time_range(avail['start_time'], avail['end_time']):
            errors.append(f"Availability {i+1} has invalid time range")
    
    return len(errors) == 0, errors 