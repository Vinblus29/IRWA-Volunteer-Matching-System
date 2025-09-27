"""
Demo test file to show how to use the test utilities
"""

import pytest
from test_utils import TestDataFactory, TestAssertions, MockUtilities

class TestDemoUtilities:
    """Demo tests showing how to use the test utilities"""
    
    def test_data_factory_creation(self):
        """Test that data factory creates valid test data"""
        # Create test user
        user = TestDataFactory.create_user()
        assert user["email"] == "test@example.com"
        assert user["role"] == "volunteer"
        assert user["is_active"] is True
        
        # Create test volunteer
        volunteer = TestDataFactory.create_volunteer()
        assert "user_id" in volunteer
        assert "skills" in volunteer
        assert "availability" in volunteer
        assert volunteer["is_verified"] is True
        
        # Create test organization
        org = TestDataFactory.create_organization()
        assert org["name"] == "Test Organization"
        assert "contact" in org
        assert "location" in org
        assert org["is_verified"] is True
        
        # Create test event
        event = TestDataFactory.create_event()
        assert event["title"] == "Test Event"
        assert "organization_id" in event
        assert "schedule" in event
        assert "requirements" in event
        assert event["is_active"] is True
    
    def test_assertions_utilities(self):
        """Test that assertion utilities work correctly"""
        # Test email validation
        assert TestAssertions.assert_valid_email("test@example.com") is True
        assert TestAssertions.assert_valid_email("invalid-email") is False
        
        # Test phone validation
        assert TestAssertions.assert_valid_phone("+1234567890") is True
        assert TestAssertions.assert_valid_phone("invalid-phone") is False
        
        # Test coordinates validation
        assert TestAssertions.assert_valid_coordinates([-74.006, 40.7128]) is True
        assert TestAssertions.assert_valid_coordinates([200, 100]) is False
        
        # Test time format validation
        assert TestAssertions.assert_valid_time_format("09:00") is True
        assert TestAssertions.assert_valid_time_format("25:00") is False
        
        # Test date format validation
        assert TestAssertions.assert_valid_date_format("2024-01-15") is True
        assert TestAssertions.assert_valid_date_format("invalid-date") is False
    
    def test_mock_utilities(self):
        """Test that mock utilities work correctly"""
        # Create mock user
        mock_user = MockUtilities.create_mock_user()
        assert mock_user.email == "test@example.com"
        assert mock_user.role == "volunteer"
        assert mock_user.is_active is True
        
        # Create mock database
        mock_db = MockUtilities.create_mock_database()
        assert mock_db is not None
        
        # Create mock LLM service
        mock_llm = MockUtilities.create_mock_llm_service()
        assert mock_llm is not None
        
        # Create mock notification service
        mock_notification = MockUtilities.create_mock_notification_service()
        assert mock_notification is not None

if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
