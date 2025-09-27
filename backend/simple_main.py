from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(title="Volunteer Matching System API")

# Add CORS middleware with more permissive settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Pydantic models
class UserRegister(BaseModel):
    email: str
    username: str
    full_name: str
    password: str
    role: str = "volunteer"

class UserLogin(BaseModel):
    email: str
    password: str

# Mock user data
mock_users = {
    "test@example.com": {
        "id": "1",
        "email": "test@example.com",
        "username": "testuser",
        "password": "test123",
        "full_name": "Test User",
        "role": "volunteer",
        "is_active": True
    }
}

@app.get("/")
async def root():
    return {"message": "Volunteer Matching System API is running!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Authentication endpoints
@app.post("/api/auth/register")
async def register(user_data: UserRegister):
    if user_data.email in mock_users:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    new_user = {
        "id": str(len(mock_users) + 1),
        "email": user_data.email,
        "username": user_data.username,
        "password": user_data.password,  # In real app, hash this
        "full_name": user_data.full_name,
        "role": user_data.role,
        "is_active": True
    }
    mock_users[user_data.email] = new_user
    
    return {
        "message": "User registered successfully",
        "user": {
            "id": new_user["id"],
            "email": new_user["email"],
            "username": new_user["username"],
            "full_name": new_user["full_name"],
            "role": new_user["role"]
        },
        "access_token": f"mock_token_{new_user['id']}"
    }

@app.post("/api/auth/login")
async def login(credentials: UserLogin):
    if credentials.email not in mock_users:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = mock_users[credentials.email]
    if user["password"] != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {
        "message": "Login successful",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "username": user["username"],
            "full_name": user["full_name"],
            "role": user["role"]
        },
        "access_token": f"mock_token_{user['id']}"
    }

@app.get("/api/auth/me")
async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    token = authorization.replace("Bearer ", "")
    if not token.startswith("mock_token_"):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = token.replace("mock_token_", "")
    
    # Find user by ID
    for user in mock_users.values():
        if user["id"] == user_id:
            return {
                "id": user["id"],
                "email": user["email"],
                "username": user["username"],
                "full_name": user["full_name"],
                "role": user["role"],
                "is_active": user["is_active"]
            }
    
    raise HTTPException(status_code=401, detail="User not found")

@app.get("/api/events")
async def get_events():
    return {
        "events": [
            {
                "id": "1",
                "title": "Community Cleanup",
                "description": "Help clean up the local park",
                "location": {"city": "New York", "state": "NY"},
                "start_date": "2024-01-15",
                "start_time": "09:00",
                "max_volunteers": 20,
                "current_volunteers": 5,
                "event_type": "Community Service"
            }
        ],
        "message": "Events endpoint - CORS working!"
    }

# Handle OPTIONS requests explicitly
@app.options("/{path:path}")
async def options_handler(path: str):
    return JSONResponse(
        status_code=200,
        content={"message": "CORS preflight successful"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
