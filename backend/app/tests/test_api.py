import pytest
import asyncio
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from ..main import app
from ..services.auth_service import auth_service
from ..database import get_database

# Test configuration
TEST_DATABASE_URL = "mongodb://localhost:27017/volunteer_matching_test"

@pytest.fixture
async def client():
    """Create test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def auth_headers():
    """Create authentication headers for testing"""
    # Mock JWT token for testing
    token = "test_jwt_token"
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
async def mock_user():
    """Mock user for testing"""
    return {
        "id": "test_user_id",
        "email": "test@example.com",
        "full_name": "Test User",
        "role": "volunteer",
        "is_active": True
    }

class TestAuthAPI:
    """Test authentication endpoints"""
    
    @pytest.mark.asyncio
    async def test_register_volunteer(self, client):
        """Test volunteer registration"""
        register_data = {
            "email": "newvolunteer@example.com",
            "password": "securepassword123",
            "full_name": "New Volunteer",
            "role": "volunteer"
        }
        
        with patch('app.services.auth_service.auth_service.register_user') as mock_register:
            mock_register.return_value = {
                "user": register_data,
                "message": "User registered successfully"
            }
            
            response = await client.post("/api/auth/register", json=register_data)
            
            assert response.status_code == 200
            assert "user" in response.json()
            mock_register.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_login_user(self, client):
        """Test user login"""
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        with patch('app.services.auth_service.auth_service.authenticate_user') as mock_auth:
            mock_auth.return_value = {
                "access_token": "test_token",
                "token_type": "bearer",
                "user": {"id": "test_id", "email": "test@example.com"}
            }
            
            response = await client.post("/api/auth/login", json=login_data)
            
            assert response.status_code == 200
            assert "access_token" in response.json()
            mock_auth.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_current_user(self, client, auth_headers, mock_user):
        """Test getting current user"""
        with patch.object(auth_service, 'get_current_user', return_value=mock_user):
            response = await client.get("/api/auth/me", headers=auth_headers)
            
            assert response.status_code == 200
            assert response.json()["email"] == mock_user["email"]
    
    @pytest.mark.asyncio
    async def test_change_password(self, client, auth_headers, mock_user):
        """Test password change"""
        password_data = {
            "current_password": "oldpassword",
            "new_password": "newpassword123"
        }
        
        with patch.object(auth_service, 'get_current_user', return_value=mock_user), \
             patch('app.services.auth_service.auth_service.change_password') as mock_change:
            mock_change.return_value = True
            
            response = await client.post(
                "/api/auth/change-password", 
                json=password_data, 
                headers=auth_headers
            )
            
            assert response.status_code == 200
            mock_change.assert_called_once()

class TestVolunteersAPI:
    """Test volunteer endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_volunteer_profile(self, client, auth_headers, mock_user):
        """Test creating volunteer profile"""
        profile_data = {
            "profile": {
                "full_name": "John Doe",
                "bio": "Passionate about community service",
                "phone": "+1234567890"
            },
            "skills": [
                {
                    "name": "Event Management",
                    "level": "intermediate",
                    "years_experience": 3
                }
            ],
            "availability": [
                {
                    "day": "saturday",
                    "start_time": "09:00",
                    "end_time": "17:00"
                }
            ],
            "location": {
                "city": "New York",
                "state": "NY",
                "postal_code": "10001"
            }
        }
        
        with patch.object(auth_service, 'require_role') as mock_auth, \
             patch('app.database.get_database') as mock_db:
            
            mock_auth.return_value = mock_user
            mock_db.return_value.volunteers.find_one.return_value = None
            mock_db.return_value.volunteers.insert_one.return_value = AsyncMock(inserted_id="test_id")
            mock_db.return_value.volunteers.find_one.return_value = {**profile_data, "_id": "test_id"}
            
            response = await client.post(
                "/api/volunteers/", 
                json=profile_data, 
                headers=auth_headers
            )
            
            assert response.status_code == 200
            assert "skills" in response.json()
    
    @pytest.mark.asyncio
    async def test_get_volunteer_profile(self, client, auth_headers, mock_user):
        """Test getting volunteer profile"""
        mock_profile = {
            "_id": "test_volunteer_id",
            "user_id": mock_user["id"],
            "profile": {"full_name": "John Doe"},
            "skills": []
        }
        
        with patch.object(auth_service, 'require_role', return_value=mock_user), \
             patch('app.database.get_database') as mock_db:
            
            mock_db.return_value.volunteers.find_one.return_value = mock_profile
            
            response = await client.get("/api/volunteers/me", headers=auth_headers)
            
            assert response.status_code == 200
            assert response.json()["user_id"] == mock_user["id"]
    
    @pytest.mark.asyncio
    async def test_list_volunteers(self, client, auth_headers):
        """Test listing volunteers"""
        mock_volunteers = [
            {
                "_id": "vol1",
                "profile": {"full_name": "Volunteer 1"},
                "skills": [],
                "is_verified": True
            },
            {
                "_id": "vol2", 
                "profile": {"full_name": "Volunteer 2"},
                "skills": [],
                "is_verified": True
            }
        ]
        
        with patch.object(auth_service, 'require_any_role') as mock_auth, \
             patch('app.database.get_database') as mock_db:
            
            mock_auth.return_value = {"role": "organization"}
            mock_db.return_value.volunteers.find.return_value.skip.return_value.limit.return_value.to_list.return_value = mock_volunteers
            
            response = await client.get("/api/volunteers/", headers=auth_headers)
            
            assert response.status_code == 200
            assert len(response.json()) == 2

class TestEventsAPI:
    """Test event endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_event(self, client, auth_headers, mock_user):
        """Test creating an event"""
        event_data = {
            "title": "Beach Cleanup",
            "description": "Help clean up the local beach",
            "category": "Environmental",
            "schedule": {
                "start_date": "2024-06-15",
                "end_date": "2024-06-15",
                "start_time": "09:00",
                "end_time": "13:00"
            },
            "location": {
                "address": "Main Beach",
                "city": "Santa Monica",
                "state": "CA",
                "postal_code": "90401"
            },
            "requirements": [
                {
                    "skill": {"name": "Physical Labor"},
                    "required": True
                }
            ]
        }
        
        with patch.object(auth_service, 'require_role', return_value=mock_user), \
             patch('app.database.get_database') as mock_db:
            
            mock_db.return_value.events.insert_one.return_value = AsyncMock(inserted_id="test_event_id")
            mock_db.return_value.events.find_one.return_value = {**event_data, "_id": "test_event_id"}
            
            response = await client.post(
                "/api/events/", 
                json=event_data, 
                headers=auth_headers
            )
            
            assert response.status_code == 200
            assert response.json()["title"] == event_data["title"]
    
    @pytest.mark.asyncio
    async def test_list_events(self, client):
        """Test listing events"""
        mock_events = [
            {
                "_id": "event1",
                "title": "Event 1",
                "status": "active",
                "schedule": {"start_date": "2024-06-15"}
            },
            {
                "_id": "event2",
                "title": "Event 2", 
                "status": "active",
                "schedule": {"start_date": "2024-06-16"}
            }
        ]
        
        with patch('app.database.get_database') as mock_db:
            mock_db.return_value.events.find.return_value.sort.return_value.skip.return_value.limit.return_value.to_list.return_value = mock_events
            
            response = await client.get("/api/events/")
            
            assert response.status_code == 200
            assert len(response.json()) == 2
    
    @pytest.mark.asyncio
    async def test_get_event_by_id(self, client):
        """Test getting event by ID"""
        mock_event = {
            "_id": "test_event_id",
            "title": "Test Event",
            "description": "Test event description",
            "status": "active"
        }
        
        with patch('app.database.get_database') as mock_db:
            mock_db.return_value.events.find_one.return_value = mock_event
            
            response = await client.get("/api/events/test_event_id")
            
            assert response.status_code == 200
            assert response.json()["title"] == mock_event["title"]

class TestMatchingAPI:
    """Test matching endpoints"""
    
    @pytest.mark.asyncio
    async def test_find_volunteers_for_event(self, client, auth_headers, mock_user):
        """Test finding volunteers for an event"""
        request_data = {
            "event_id": "test_event_id",
            "max_matches": 20,
            "filters": {}
        }
        
        mock_event = {
            "_id": "test_event_id",
            "organization_id": mock_user["id"],
            "title": "Test Event"
        }
        
        with patch.object(auth_service, 'require_role', return_value=mock_user), \
             patch('app.database.get_database') as mock_db, \
             patch('app.agents.communication_orchestrator.CommunicationOrchestrator') as mock_orch:
            
            mock_db.return_value.events.find_one.return_value = mock_event
            mock_orch.return_value.start_workflow.return_value = "workflow_123"
            
            response = await client.post(
                "/api/matching/find-volunteers",
                json=request_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            assert "matches" in response.json()
    
    @pytest.mark.asyncio
    async def test_accept_match(self, client, auth_headers, mock_user):
        """Test accepting a match"""
        mock_match = {
            "_id": "test_match_id",
            "volunteer_id": "test_volunteer_id",
            "status": "pending"
        }
        
        mock_volunteer = {
            "_id": "test_volunteer_id",
            "user_id": mock_user["id"]
        }
        
        with patch.object(auth_service, 'require_role', return_value=mock_user), \
             patch('app.database.get_database') as mock_db:
            
            mock_db.return_value.matches.find_one.return_value = mock_match
            mock_db.return_value.volunteers.find_one.return_value = mock_volunteer
            mock_db.return_value.matches.update_one.return_value = AsyncMock()
            
            response = await client.post(
                "/api/matching/matches/test_match_id/accept",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            assert "accepted" in response.json()["message"]

class TestDashboardAPI:
    """Test dashboard endpoints"""
    
    @pytest.mark.asyncio
    async def test_volunteer_dashboard(self, client, auth_headers, mock_user):
        """Test volunteer dashboard"""
        mock_volunteer = {
            "_id": "test_volunteer_id",
            "user_id": mock_user["id"],
            "profile": {"full_name": "Test Volunteer"},
            "total_hours_volunteered": 50,
            "events_completed": 5,
            "rating": 4.5,
            "skills": []
        }
        
        with patch.object(auth_service, 'require_role', return_value=mock_user), \
             patch('app.database.get_database') as mock_db:
            
            mock_db.return_value.volunteers.find_one.return_value = mock_volunteer
            mock_db.return_value.matches.count_documents.return_value = 10
            mock_db.return_value.matches.find.return_value.sort.return_value.limit.return_value.to_list.return_value = []
            
            response = await client.get("/api/dashboard/volunteer", headers=auth_headers)
            
            assert response.status_code == 200
            assert "profile" in response.json()
            assert "statistics" in response.json()
    
    @pytest.mark.asyncio
    async def test_admin_dashboard(self, client, auth_headers):
        """Test admin dashboard"""
        admin_user = {"id": "admin_id", "role": "admin"}
        
        with patch.object(auth_service, 'require_role', return_value=admin_user), \
             patch('app.database.get_database') as mock_db:
            
            # Mock database counts
            mock_db.return_value.users.count_documents.return_value = 100
            mock_db.return_value.volunteers.count_documents.return_value = 80
            mock_db.return_value.events.count_documents.return_value = 50
            mock_db.return_value.matches.count_documents.return_value = 200
            mock_db.return_value.users.find.return_value.sort.return_value.limit.return_value.to_list.return_value = []
            mock_db.return_value.events.find.return_value.sort.return_value.limit.return_value.to_list.return_value = []
            mock_db.return_value.matches.find.return_value.sort.return_value.limit.return_value.to_list.return_value = []
            
            response = await client.get("/api/dashboard/admin", headers=auth_headers)
            
            assert response.status_code == 200
            assert "system_overview" in response.json()
            assert "growth_metrics" in response.json()

# Integration tests
class TestAPIIntegration:
    """Integration tests for API endpoints"""
    
    @pytest.mark.asyncio
    async def test_full_volunteer_workflow(self, client):
        """Test complete volunteer workflow"""
        # This would test the full flow from registration to matching
        pass
    
    @pytest.mark.asyncio 
    async def test_organization_event_workflow(self, client):
        """Test complete organization workflow"""
        # This would test event creation to volunteer matching
        pass

# Error handling tests
class TestErrorHandling:
    """Test error handling in API endpoints"""
    
    @pytest.mark.asyncio
    async def test_unauthorized_access(self, client):
        """Test unauthorized access handling"""
        response = await client.get("/api/volunteers/me")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_invalid_data_validation(self, client, auth_headers):
        """Test data validation errors"""
        invalid_data = {
            "email": "invalid-email",  # Invalid email format
            "password": "123",  # Too short password
        }
        
        response = await client.post("/api/auth/register", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_not_found_resources(self, client, auth_headers):
        """Test 404 errors for non-existent resources"""
        with patch('app.database.get_database') as mock_db:
            mock_db.return_value.events.find_one.return_value = None
            
            response = await client.get("/api/events/nonexistent_id")
            assert response.status_code == 404

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 