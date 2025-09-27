"""
Demo script showing how to use the utility functions
"""

# Example usage of utility functions
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, date
from typing import Dict, List

# Example utility functions (these would normally be imported from the utils package)
def generate_id() -> str:
    import uuid
    return str(uuid.uuid4())

def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    return dt.strftime(format_str)

def validate_email(email: str) -> bool:
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
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

def mask_email(email: str) -> str:
    if '@' not in email:
        return email
    
    local, domain = email.split('@', 1)
    if len(local) <= 2:
        masked_local = local[0] + '*' * (len(local) - 1)
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
    
    return f"{masked_local}@{domain}"

def format_currency(amount: float, currency: str = "USD") -> str:
    if currency == "USD":
        return f""
    return f"{amount:,.2f} {currency}"

def slugify(text: str) -> str:
    import re
    # Convert to lowercase and replace spaces with hyphens
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def main():
    print("=== Volunteer Matching System - Utility Functions Demo ===\n")
    
    # ID Generation
    print("1. ID Generation:")
    unique_id = generate_id()
    print(f"   Generated ID: {unique_id}")
    print()
    
    # Date/Time Formatting
    print("2. Date/Time Formatting:")
    now = datetime.now()
    formatted_date = format_datetime(now)
    print(f"   Current time: {formatted_date}")
    print()
    
    # Email Validation
    print("3. Email Validation:")
    test_emails = ["test@example.com", "invalid-email", "user@domain.org"]
    for email in test_emails:
        is_valid = validate_email(email)
        print(f"   {email}: {'Valid' if is_valid else 'Invalid'}")
    print()
    
    # Email Masking
    print("4. Email Masking:")
    test_email = "john.doe@example.com"
    masked = mask_email(test_email)
    print(f"   Original: {test_email}")
    print(f"   Masked:   {masked}")
    print()
    
    # Currency Formatting
    print("5. Currency Formatting:")
    amounts = [1234.56, 999.99, 1000000.00]
    for amount in amounts:
        formatted = format_currency(amount)
        print(f"    -> {formatted}")
    print()
    
    # Distance Calculation
    print("6. Distance Calculation:")
    # New York to Los Angeles coordinates
    ny_lat, ny_lon = 40.7128, -74.0060
    la_lat, la_lon = 34.0522, -118.2437
    distance = calculate_distance(ny_lat, ny_lon, la_lat, la_lon)
    print(f"   Distance from NYC to LA: {distance:.2f} km")
    print()
    
    # Text Processing
    print("7. Text Processing:")
    text = "Community Teaching Event 2024!"
    slug = slugify(text)
    print(f"   Original: {text}")
    print(f"   Slug:     {slug}")
    print()
    
    # List Operations
    print("8. List Operations:")
    numbers = list(range(1, 11))
    chunks = chunk_list(numbers, 3)
    print(f"   Original list: {numbers}")
    print(f"   Chunked (size 3): {chunks}")
    print()
    
    print("=== Demo Complete ===")

if __name__ == "__main__":
    main()
