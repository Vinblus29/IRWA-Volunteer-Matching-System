import re
import html
import secrets
import string
from typing import Any, Dict, List
import bleach
from urllib.parse import quote, unquote

def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input to prevent XSS and injection attacks"""
    if not isinstance(text, str):
        return str(text)
    
    # Limit length
    text = text[:max_length]
    
    # HTML escape
    text = html.escape(text)
    
    # Remove potential script tags and dangerous characters
    text = bleach.clean(text, tags=[], attributes={}, strip=True)
    
    # Remove null bytes and control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\t\n\r')
    
    return text.strip()

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove or replace dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Limit length
    filename = filename[:255]
    
    # Ensure it's not empty
    if not filename:
        filename = "file"
    
    return filename

def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_secure_password(length: int = 12) -> str:
    """Generate a secure password"""
    # Ensure we have at least one character from each category
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    symbols = "!@#$%^&*"
    
    # Ensure at least one character from each category
    password = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits),
        secrets.choice(symbols)
    ]
    
    # Fill the rest randomly
    all_chars = lowercase + uppercase + digits + symbols
    for _ in range(length - 4):
        password.append(secrets.choice(all_chars))
    
    # Shuffle the password list
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password)

def validate_url(url: str) -> bool:
    """Validate if URL is safe and well-formed"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(url):
        return False
    
    # Check for dangerous protocols
    dangerous_protocols = ['javascript:', 'data:', 'vbscript:', 'file:']
    for protocol in dangerous_protocols:
        if url.lower().startswith(protocol):
            return False
    
    return True

def sanitize_sql_input(text: str) -> str:
    """Sanitize input to prevent SQL injection (though we use MongoDB)"""
    # Remove SQL metacharacters
    dangerous_chars = ["'", '"', ';', '--', '/*', '*/', 'xp_', 'sp_']
    
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text

def validate_email_domain(email: str, allowed_domains: List[str] = None) -> bool:
    """Validate email domain against whitelist"""
    if not allowed_domains:
        return True
    
    domain = email.split('@')[-1].lower()
    return domain in [d.lower() for d in allowed_domains]

def rate_limit_key(identifier: str, action: str) -> str:
    """Generate rate limiting key"""
    sanitized_identifier = re.sub(r'[^a-zA-Z0-9_.-]', '_', identifier)
    sanitized_action = re.sub(r'[^a-zA-Z0-9_.-]', '_', action)
    return f"rate_limit:{sanitized_action}:{sanitized_identifier}"

def sanitize_search_query(query: str) -> str:
    """Sanitize search query to prevent injection attacks"""
    # Remove MongoDB operators
    dangerous_operators = ['$where', '$regex', '$ne', '$gt', '$lt', '$in', '$nin']
    
    for operator in dangerous_operators:
        query = query.replace(operator, '')
    
    # Remove special regex characters
    query = re.sub(r'[.*+?^${}()|[\]\\]', '', query)
    
    # Limit length
    query = query[:100]
    
    return query.strip()

def validate_file_type(filename: str, allowed_extensions: List[str]) -> bool:
    """Validate file type based on extension"""
    if not filename or '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in [ext.lower() for ext in allowed_extensions]

def sanitize_json_data(data: Dict[str, Any], max_depth: int = 10) -> Dict[str, Any]:
    """Recursively sanitize JSON data"""
    def _sanitize_value(value, depth=0):
        if depth > max_depth:
            return None
        
        if isinstance(value, str):
            return sanitize_input(value)
        elif isinstance(value, dict):
            return {
                sanitize_input(k): _sanitize_value(v, depth + 1) 
                for k, v in value.items()
            }
        elif isinstance(value, list):
            return [_sanitize_value(item, depth + 1) for item in value]
        else:
            return value
    
    return _sanitize_value(data)

def check_password_strength(password: str) -> Dict[str, Any]:
    """Check password strength and return score with feedback"""
    score = 0
    feedback = []
    
    # Length check
    if len(password) >= 8:
        score += 1
    else:
        feedback.append("Password should be at least 8 characters long")
    
    # Uppercase check
    if re.search(r'[A-Z]', password):
        score += 1
    else:
        feedback.append("Password should contain uppercase letters")
    
    # Lowercase check
    if re.search(r'[a-z]', password):
        score += 1
    else:
        feedback.append("Password should contain lowercase letters")
    
    # Digit check
    if re.search(r'\d', password):
        score += 1
    else:
        feedback.append("Password should contain numbers")
    
    # Special character check
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    else:
        feedback.append("Password should contain special characters")
    
    # Common password check
    common_passwords = ['password', '123456', 'qwerty', 'admin', 'letmein']
    if password.lower() in common_passwords:
        score -= 2
        feedback.append("Password is too common")
    
    # Determine strength
    if score >= 4:
        strength = "strong"
    elif score >= 2:
        strength = "medium"
    else:
        strength = "weak"
    
    return {
        "score": max(0, score),
        "strength": strength,
        "feedback": feedback
    }

def generate_csrf_token() -> str:
    """Generate CSRF token"""
    return generate_secure_token(32)

def validate_csrf_token(token: str, expected_token: str) -> bool:
    """Validate CSRF token"""
    return secrets.compare_digest(token, expected_token)

def escape_regex(text: str) -> str:
    """Escape special characters for regex"""
    return re.escape(text)

def sanitize_phone_number(phone: str) -> str:
    """Sanitize and format phone number"""
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Validate length (assuming international format)
    if len(digits) < 10 or len(digits) > 15:
        return ""
    
    return digits

def validate_coordinate(lat: float, lon: float) -> bool:
    """Validate geographic coordinates"""
    return -90 <= lat <= 90 and -180 <= lon <= 180 