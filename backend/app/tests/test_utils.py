"""
Test utilities for the Volunteer Matching System
This module provides utility functions and classes for testing
"""

import pytest
import asyncio
import json
import hashlib
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, date, time, timedelta
from bson import ObjectId
from unittest.mock import Mock, AsyncMock, patch
import httpx
from fastapi.testclient import TestClient

# Test data factories
class TestDataFactory:
    """Factory class for creating test data"""
    
    @staticmethod
    def create_user(
        email: str = "test@example.com",
        username: str = "testuser",
        full_name: str = "Test User",
        role: str = "volunteer",
        is_active: bool = True
    ) -> Dict[str, Any]:
        """Create a test user"""
        return {
            "email": email,
            "username": username,
            "full_name": full_name,
            "password": "testpassword123",
            "role": role,
            "is_active": is_active,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    
    @staticmethod
    def create_volunteer(
        user_id: Optional[ObjectId] = None,
        skills: Optional[List[Dict]] = None,
        availability: Optional[List[Dict]] = None,
        is_verified: bool = True
    ) -> Dict[str, Any]:
        """Create a test volunteer"""
        if user_id is None:
            user_id = ObjectId()
        
        if skills is None:
            skills = [
                {
                    "name": "Teaching",
                    "level": "intermediate",
                    "years_experience": 2,
                    "certifications": ["Teaching Certificate"]
                }
            ]
        
        if availability is None:
            availability = [
                {
                    "day": "monday",
                    "start_time": "09:00",
                    "end_time": "17:00"
                }
            ]
        
        return {
            "user_id": user_id,
            "skills": skills,
            "availability": availability,
            "is_verified": is_verified,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    
    @staticmethod
    def create_organization(
        name: str = "Test Organization",
        user_id: Optional[ObjectId] = None,
        is_verified: bool = True
    ) -> Dict[str, Any]:
        """Create a test organization"""
        if user_id is None:
            user_id = ObjectId()
        
        return {
            "name": name,
            "legal_name": f"{name} Inc",
            "user_id": user_id,
            "contact": {
                "name": "John Doe",
                "title": "Manager",
                "email": "john@testorg.com",
                "phone": "+1234567890",
                "is_primary": True
            },
            "location": {
                "address": "456 Org St",
                "city": "Test City",
                "state": "Test State",
                "country": "Test Country",
                "postal_code": "12345",
                "coordinates": [-74.006, 40.7128]
            },
            "is_verified": is_verified,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    
    @staticmethod
    def create_event(
        title: str = "Test Event",
        organization_id: Optional[ObjectId] = None,
        category: str = "Education",
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Create a test event"""
        if organization_id is None:
            organization_id = ObjectId()
        
        if start_date is None:
            start_date = date.today() + timedelta(days=7)
        
        if end_date is None:
            end_date = start_date
        
        return {
            "title": title,
            "description": f"Description for {title}",
            "organization_id": organization_id,
            "category": category,
            "location": {
                "address": "123 Main St",
                "city": "Test City",
                "state": "Test State",
                "country": "Test Country",
                "postal_code": "12345",
                "coordinates": [-74.006, 40.7128]
            },
            "schedule": {
                "start_date": start_date,
                "end_date": end_date,
                "start_time": "10:00",
                "end_time": "14:00",
                "recurring": False
            },
            "requirements": [
                {
                    "skill": {
                        "name": "Teaching",
                        "level": "intermediate"
                    },
                    "required_volunteers": 2,
                    "filled_positions": 0
                }
            ],
            "max_volunteers": 5,
            "current_volunteers": 0,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    
    @staticmethod
    def create_availability(
        volunteer_id: Optional[ObjectId] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Create test availability data"""
        if volunteer_id is None:
            volunteer_id = ObjectId()
        
        if start_date is None:
            start_date = date.today()
        
        if end_date is None:
            end_date = start_date + timedelta(days=30)
        
        return {
            "volunteer_id": volunteer_id,
            "periods": [
                {
                    "start_date": start_date,
                    "end_date": end_date,
                    "slots": [
                        {
                            "day_of_week": "monday",
                            "start_time": "09:00",
                            "end_time": "17:00",
                            "is_available": True
                        },
                        {
                            "day_of_week": "tuesday",
                            "start_time": "09:00",
                            "end_time": "17:00",
                            "is_available": True
                        }
                    ],
                    "is_recurring": True,
                    "recurring_pattern": "weekly"
                }
            ],
            "notes": "Available weekdays",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    
    @staticmethod
    def create_notification(
        user_id: Optional[ObjectId] = None,
        notification_type: str = "event",
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """Create test notification data"""
        if user_id is None:
            user_id = ObjectId()
        
        return {
            "user_id": user_id,
            "type": notification_type,
            "priority": priority,
            "channel": "push",
            "data": {
                "title": "Test Notification",
                "message": "This is a test notification",
                "action_url": "/test",
                "action_text": "View",
                "metadata": {}
            },
            "is_read": False,
            "is_sent": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    
    @staticmethod
    def create_match(
        event_id: Optional[ObjectId] = None,
        volunteer_id: Optional[ObjectId] = None,
        match_score: float = 0.85,
        status: str = "pending"
    ) -> Dict[str, Any]:
        """Create test match data"""
        if event_id is None:
            event_id = ObjectId()
        
        if volunteer_id is None:
            volunteer_id = ObjectId()
        
        return {
            "event_id": event_id,
            "volunteer_id": volunteer_id,
            "match_score": match_score,
            "status": status,
            "match_reasons": [
                "Excellent skill match",
                "Available during event time",
                "Close to event location"
            ],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

# Test database utilities
class TestDatabaseManager:
    """Utility class for managing test database operations"""
    
    def __init__(self, database_name: str = "volunteer_matching_test"):
        self.database_name = database_name
        self.collections = {}
    
    async def setup(self):
        """Setup test database"""
        # This would connect to test database
        pass
    
    async def cleanup(self):
        """Cleanup test database"""
        # This would clear test database
        pass
    
    async def insert_test_data(self, collection: str, data: Union[Dict, List[Dict]]):
        """Insert test data into collection"""
        if isinstance(data, dict):
            data = [data]
        # This would insert data into test collection
        return [ObjectId() for _ in data]
    
    async def clear_collection(self, collection: str):
        """Clear test collection"""
        # This would clear the collection
        pass
    
    async def find_documents(self, collection: str, query: Dict = None):
        """Find documents in test collection"""
        if query is None:
            query = {}
        # This would find documents
        return []
    
    async def count_documents(self, collection: str, query: Dict = None):
        """Count documents in test collection"""
        if query is None:
            query = {}
        # This would count documents
        return 0

# Test client utilities
class TestAPIClient:
    """Utility class for making API requests in tests"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.headers = {}
        self.cookies = {}
    
    def set_auth_token(self, token: str):
        """Set authorization token"""
        self.headers["Authorization"] = f"Bearer {token}"
    
    def set_cookie(self, name: str, value: str):
        """Set cookie"""
        self.cookies[name] = value
    
    async def get(self, endpoint: str, params: Dict = None):
        """Make GET request"""
        url = f"{self.base_url}{endpoint}"
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=self.headers,
                cookies=self.cookies,
                params=params
            )
            return response
    
    async def post(self, endpoint: str, data: Dict[str, Any]):
        """Make POST request"""
        url = f"{self.base_url}{endpoint}"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=self.headers,
                cookies=self.cookies,
                json=data
            )
            return response
    
    async def put(self, endpoint: str, data: Dict[str, Any]):
        """Make PUT request"""
        url = f"{self.base_url}{endpoint}"
        async with httpx.AsyncClient() as client:
            response = await client.put(
                url,
                headers=self.headers,
                cookies=self.cookies,
                json=data
            )
            return response
    
    async def delete(self, endpoint: str):
        """Make DELETE request"""
        url = f"{self.base_url}{endpoint}"
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                url,
                headers=self.headers,
                cookies=self.cookies
            )
            return response

# Test assertion utilities
class TestAssertions:
    """Custom assertion utilities for tests"""
    
    @staticmethod
    def assert_valid_object_id(value: str) -> bool:
        """Assert that value is a valid ObjectId"""
        try:
            ObjectId(value)
            return True
        except:
            return False
    
    @staticmethod
    def assert_valid_email(email: str) -> bool:
        """Assert that email is valid"""
        import re
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None
    
    @staticmethod
    def assert_valid_phone(phone: str) -> bool:
        """Assert that phone number is valid"""
        import re
        pattern = r"^\+?[1-9]\d{1,14}$"
        return re.match(pattern, phone) is not None
    
    @staticmethod
    def assert_valid_coordinates(coordinates: list) -> bool:
        """Assert that coordinates are valid"""
        if len(coordinates) != 2:
            return False
        longitude, latitude = coordinates
        return -180 <= longitude <= 180 and -90 <= latitude <= 90
    
    @staticmethod
    def assert_valid_time_format(time_str: str) -> bool:
        """Assert that time format is valid"""
        import re
        pattern = r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$"
        return re.match(pattern, time_str) is not None
    
    @staticmethod
    def assert_valid_date_format(date_str: str) -> bool:
        """Assert that date format is valid"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except:
            return False
    
    @staticmethod
    def assert_response_success(response):
        """Assert that response is successful"""
        assert response.status_code >= 200 and response.status_code < 300
    
    @staticmethod
    def assert_response_error(response, expected_status: int = None):
        """Assert that response is an error"""
        if expected_status:
            assert response.status_code == expected_status
        else:
            assert response.status_code >= 400
    
    @staticmethod
    def assert_json_response(response, expected_keys: List[str] = None):
        """Assert that response is valid JSON with expected keys"""
        assert response.headers.get("content-type", "").startswith("application/json")
        data = response.json()
        if expected_keys:
            for key in expected_keys:
                assert key in data
        return data

# Mock utilities
class MockUtilities:
    """Utilities for creating mocks in tests"""
    
    @staticmethod
    def create_mock_user(user_id: str = None, role: str = "volunteer"):
        """Create a mock user object"""
        if user_id is None:
            user_id = str(ObjectId())
        
        mock_user = Mock()
        mock_user.id = user_id
        mock_user.email = "test@example.com"
        mock_user.username = "testuser"
        mock_user.full_name = "Test User"
        mock_user.role = role
        mock_user.is_active = True
        return mock_user
    
    @staticmethod
    def create_mock_database():
        """Create a mock database"""
        mock_db = Mock()
        mock_collection = Mock()
        mock_collection.find.return_value = []
        mock_collection.find_one.return_value = None
        mock_collection.insert_one.return_value = Mock(inserted_id=ObjectId())
        mock_collection.update_one.return_value = Mock(modified_count=1)
        mock_collection.delete_one.return_value = Mock(deleted_count=1)
        mock_collection.count_documents.return_value = 0
        
        mock_db.__getitem__ = Mock(return_value=mock_collection)
        return mock_db
    
    @staticmethod
    def create_mock_llm_service():
        """Create a mock LLM service"""
        mock_llm = Mock()
        mock_llm.generate_response = AsyncMock(return_value="Mock response")
        mock_llm.analyze_text = AsyncMock(return_value={"sentiment": "positive"})
        mock_llm.extract_skills = AsyncMock(return_value=["Teaching", "Communication"])
        return mock_llm
    
    @staticmethod
    def create_mock_notification_service():
        """Create a mock notification service"""
        mock_notification = Mock()
        mock_notification.send_notification = AsyncMock(return_value=True)
        mock_notification.send_bulk_notifications = AsyncMock(return_value=5)
        mock_notification.get_user_notifications = AsyncMock(return_value=[])
        return mock_notification

# Test decorators
def async_test(func):
    """Decorator for async test functions"""
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(func(*args, **kwargs))
        finally:
            loop.close()
    return wrapper

def skip_if_no_database(func):
    """Decorator to skip test if database is not available"""
    def wrapper(*args, **kwargs):
        try:
            # Check if database is available
            return func(*args, **kwargs)
        except Exception:
            pytest.skip("Database not available")
    return wrapper

def mock_database(func):
    """Decorator to mock database for test"""
    def wrapper(*args, **kwargs):
        with patch("app.database.get_database") as mock_db:
            mock_db.return_value = MockUtilities.create_mock_database()
            return func(*args, **kwargs)
    return wrapper

def mock_llm_service(func):
    """Decorator to mock LLM service for test"""
    def wrapper(*args, **kwargs):
        with patch("app.services.llm_service.LLMService") as mock_llm:
            mock_llm.return_value = MockUtilities.create_mock_llm_service()
            return func(*args, **kwargs)
    return wrapper

# Test data generators
def generate_test_users(count: int = 5) -> List[Dict[str, Any]]:
    """Generate multiple test users"""
    users = []
    for i in range(count):
        users.append(TestDataFactory.create_user(
            email=f"test{i}@example.com",
            username=f"testuser{i}",
            full_name=f"Test User {i}",
            role="volunteer" if i % 2 == 0 else "organization"
        ))
    return users

def generate_test_events(count: int = 5) -> List[Dict[str, Any]]:
    """Generate multiple test events"""
    events = []
    categories = ["Education", "Healthcare", "Environment", "Community", "Sports"]
    for i in range(count):
        events.append(TestDataFactory.create_event(
            title=f"Test Event {i}",
            category=categories[i % len(categories)],
            start_date=date.today() + timedelta(days=7 + i)
        ))
    return events

def generate_test_volunteers(count: int = 5) -> List[Dict[str, Any]]:
    """Generate multiple test volunteers"""
    volunteers = []
    for i in range(count):
        volunteers.append(TestDataFactory.create_volunteer(
            user_id=ObjectId(),
            skills=[{
                "name": f"Skill {i}",
                "level": "intermediate",
                "years_experience": i + 1,
                "certifications": [f"Cert {i}"]
            }]
        ))
    return volunteers

# Test fixtures
@pytest.fixture
def test_data_factory():
    """Fixture for test data factory"""
    return TestDataFactory

@pytest.fixture
def test_database():
    """Fixture for test database manager"""
    return TestDatabaseManager()

@pytest.fixture
def test_client():
    """Fixture for test API client"""
    return TestAPIClient()

@pytest.fixture
def test_assertions():
    """Fixture for test assertions"""
    return TestAssertions

@pytest.fixture
def mock_utilities():
    """Fixture for mock utilities"""
    return MockUtilities

# Test markers
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.database = pytest.mark.database
pytest.mark.api = pytest.mark.api
pytest.mark.slow = pytest.mark.slow
pytest.mark.async_test = pytest.mark.async_test
