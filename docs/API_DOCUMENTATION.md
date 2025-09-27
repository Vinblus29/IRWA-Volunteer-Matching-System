# API Documentation

## Overview

The Intelligent Volunteer Matching System provides a comprehensive REST API built with FastAPI. The API supports authentication, volunteer management, event management, intelligent matching, and administrative functions.

## Base URL

```
Development: http://localhost:8000
Production: https://your-domain.com
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## API Endpoints

### Authentication Endpoints

#### POST /api/auth/register
Register a new user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe",
  "role": "volunteer"  // "volunteer", "organization", or "admin"
}
```

**Response:**
```json
{
  "user": {
    "id": "user_id",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "volunteer",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z"
  },
  "message": "User registered successfully"
}
```

#### POST /api/auth/login
Authenticate user and get access token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "user_id",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "volunteer"
  }
}
```

#### GET /api/auth/me
Get current user information.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": "user_id",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "volunteer",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Volunteer Endpoints

#### POST /api/volunteers/
Create volunteer profile.

**Headers:** `Authorization: Bearer <token>` (volunteer role required)

**Request Body:**
```json
{
  "profile": {
    "full_name": "John Doe",
    "bio": "Passionate about community service",
    "phone": "+1234567890",
    "date_of_birth": "1990-01-15",
    "languages": ["English", "Spanish"]
  },
  "skills": [
    {
      "name": "Event Management",
      "level": "intermediate",
      "years_experience": 3,
      "certifications": ["Event Planning Certificate"]
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
    "address": "123 Main St",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "coordinates": [-74.0060, 40.7128]
  },
  "preferences": {
    "preferred_event_types": ["Environmental", "Education"],
    "commitment_level": "high",
    "travel_radius_km": 25
  }
}
```

#### GET /api/volunteers/me
Get current user's volunteer profile.

**Headers:** `Authorization: Bearer <token>` (volunteer role required)

#### PUT /api/volunteers/me
Update current user's volunteer profile.

**Headers:** `Authorization: Bearer <token>` (volunteer role required)

#### GET /api/volunteers/
List volunteers (for organizations and admins).

**Headers:** `Authorization: Bearer <token>` (organization or admin role required)

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Number of records to return (default: 20, max: 100)
- `skills`: Filter by skills (comma-separated)
- `location`: Filter by location
- `verified_only`: Show only verified volunteers (default: false)

### Event Endpoints

#### POST /api/events/
Create a new volunteer event.

**Headers:** `Authorization: Bearer <token>` (organization role required)

**Request Body:**
```json
{
  "title": "Beach Cleanup Drive",
  "description": "Join us for a community beach cleanup to protect marine life and keep our beaches clean.",
  "category": "Environmental",
  "schedule": {
    "start_date": "2024-06-15",
    "end_date": "2024-06-15",
    "start_time": "09:00",
    "end_time": "13:00",
    "timezone": "America/New_York"
  },
  "location": {
    "address": "Santa Monica Beach",
    "city": "Santa Monica",
    "state": "CA",
    "postal_code": "90401",
    "coordinates": [-118.4912, 34.0195]
  },
  "requirements": [
    {
      "skill": {
        "name": "Physical Labor",
        "level": "beginner"
      },
      "required": true,
      "volunteers_needed": 20
    }
  ],
  "provides_training": true,
  "is_urgent": false,
  "max_volunteers": 50
}
```

#### GET /api/events/
List volunteer events.

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Number of records to return (default: 20, max: 100)
- `category`: Filter by category
- `location`: Filter by location
- `status`: Filter by status (default: "active")
- `is_urgent`: Filter urgent events
- `provides_training`: Filter events that provide training
- `start_date_from`: Events starting from date (YYYY-MM-DD)
- `start_date_to`: Events starting to date (YYYY-MM-DD)

#### GET /api/events/{event_id}
Get event by ID.

#### PUT /api/events/{event_id}
Update an event (organization owner only).

**Headers:** `Authorization: Bearer <token>` (organization role required)

#### DELETE /api/events/{event_id}
Delete an event.

**Headers:** `Authorization: Bearer <token>` (organization or admin role required)

### Matching Endpoints

#### POST /api/matching/find-volunteers
Find suitable volunteers for an event.

**Headers:** `Authorization: Bearer <token>` (organization role required)

**Request Body:**
```json
{
  "event_id": "event_id_here",
  "max_matches": 20,
  "filters": {
    "verified_only": true,
    "min_rating": 4.0,
    "max_distance_km": 50
  }
}
```

**Response:**
```json
{
  "event_id": "event_id_here",
  "matches": [
    {
      "volunteer_id": "volunteer_id",
      "volunteer_name": "John Doe",
      "match_score": 0.92,
      "skill_score": 0.95,
      "location_score": 0.85,
      "availability_score": 0.95,
      "explanation": "Excellent match with strong skills in required areas and perfect availability.",
      "skills": [
        {
          "name": "Event Management",
          "level": "advanced"
        }
      ],
      "location": {
        "city": "New York",
        "state": "NY"
      },
      "experience_hours": 150,
      "rating": 4.8,
      "is_verified": true
    }
  ],
  "total_found": 25,
  "total_qualified": 15,
  "total_returned": 10,
  "matching_algorithm": "hybrid_vector_ml",
  "fairness_applied": true,
  "generated_at": "2024-01-15T10:30:00Z"
}
```

#### POST /api/matching/find-events
Find suitable events for a volunteer.

**Headers:** `Authorization: Bearer <token>` (volunteer role required)

**Query Parameters:**
- `volunteer_id`: Volunteer ID (optional, defaults to current user)
- `max_matches`: Maximum number of matches to return (default: 20)

#### GET /api/matching/matches
Get matches for current user.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Number of records to return (default: 20, max: 100)
- `status_filter`: Filter by match status

#### POST /api/matching/matches/{match_id}/accept
Accept a volunteer match.

**Headers:** `Authorization: Bearer <token>` (volunteer role required)

#### POST /api/matching/matches/{match_id}/decline
Decline a volunteer match.

**Headers:** `Authorization: Bearer <token>` (volunteer role required)

**Request Body:**
```json
{
  "reason": "Schedule conflict"
}
```

#### POST /api/matching/matches/{match_id}/rate
Rate a completed match.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `rating`: Rating from 1 to 5
- `feedback`: Optional feedback text

### Dashboard Endpoints

#### GET /api/dashboard/volunteer
Get volunteer dashboard data.

**Headers:** `Authorization: Bearer <token>` (volunteer role required)

**Response:**
```json
{
  "profile": {
    "volunteer_id": "volunteer_id",
    "name": "John Doe",
    "total_hours": 150,
    "events_completed": 8,
    "rating": 4.8,
    "is_verified": true,
    "skills_count": 5
  },
  "statistics": {
    "total_matches": 25,
    "pending_matches": 3,
    "accepted_matches": 18,
    "completed_matches": 4,
    "success_rate": 85.0
  },
  "upcoming_events": [
    {
      "event_id": "event_id",
      "title": "Beach Cleanup",
      "date": "2024-06-15",
      "time": "09:00",
      "location": {...},
      "match_id": "match_id"
    }
  ],
  "skill_recommendations": [
    {
      "skill": "Project Management",
      "reason": "Complements your organizational skills",
      "demand": "High demand in current events"
    }
  ],
  "notifications_count": 5
}
```

#### GET /api/dashboard/organization
Get organization dashboard data.

**Headers:** `Authorization: Bearer <token>` (organization role required)

#### GET /api/dashboard/admin
Get admin dashboard data.

**Headers:** `Authorization: Bearer <token>` (admin role required)

## Response Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

## Error Response Format

```json
{
  "detail": "Error message describing what went wrong",
  "error_code": "SPECIFIC_ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **100 requests per minute** for authenticated users
- **20 requests per minute** for unauthenticated users
- **Burst limit**: 20 additional requests

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Total requests allowed per window
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Time when the rate limit resets

## Pagination

List endpoints support pagination with the following parameters:

- `skip`: Number of records to skip (default: 0)
- `limit`: Number of records to return (default: 20, max: 100)

Pagination information is included in list responses:

```json
{
  "items": [...],
  "total": 150,
  "skip": 0,
  "limit": 20,
  "has_more": true
}
```

## Filtering and Searching

Many endpoints support filtering and searching:

### Query Parameters
- Text search: `q=search_term`
- Date ranges: `start_date_from=2024-01-01&start_date_to=2024-12-31`
- Boolean filters: `is_urgent=true`
- Categorical filters: `category=Environmental`

### Search Syntax
- Use `+` for AND operations: `environmental+cleanup`
- Use `|` for OR operations: `education|healthcare`
- Use quotes for exact phrases: `"beach cleanup"`

## Webhooks

The system supports webhooks for real-time notifications:

### Available Events
- `match.created`: New match created
- `match.accepted`: Match accepted by volunteer
- `match.declined`: Match declined by volunteer
- `event.created`: New event created
- `volunteer.registered`: New volunteer registered

### Webhook Configuration
Configure webhooks through the admin dashboard or API:

```json
{
  "url": "https://your-domain.com/webhook",
  "events": ["match.created", "match.accepted"],
  "secret": "your_webhook_secret"
}
```

## SDKs and Examples

### Python Example
```python
import requests

# Authentication
response = requests.post('http://localhost:8000/api/auth/login', json={
    'email': 'user@example.com',
    'password': 'password'
})
token = response.json()['access_token']

# Make authenticated request
headers = {'Authorization': f'Bearer {token}'}
volunteers = requests.get('http://localhost:8000/api/volunteers/', headers=headers)
```

### JavaScript Example
```javascript
// Authentication
const loginResponse = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password'
  })
});
const { access_token } = await loginResponse.json();

// Make authenticated request
const volunteersResponse = await fetch('http://localhost:8000/api/volunteers/', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const volunteers = await volunteersResponse.json();
```

## API Versioning

The API uses URL versioning:
- Current version: `v1` (default)
- Access specific version: `/api/v1/volunteers/`

## Support

For API support:
- Documentation: `/docs` (Swagger UI)
- Alternative docs: `/redoc` (ReDoc)
- Support email: api-support@volunteermatching.com
- GitHub Issues: [Project Repository] 