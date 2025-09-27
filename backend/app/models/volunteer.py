from datetime import datetime, time
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from bson import ObjectId
from .user import PyObjectId

class Skill(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    level: str = Field(..., regex="^(beginner|intermediate|advanced|expert)$")
    years_experience: Optional[int] = Field(default=0, ge=0)
    certifications: List[str] = Field(default_factory=list)

class Availability(BaseModel):
    day: str = Field(..., regex="^(monday|tuesday|wednesday|thursday|friday|saturday|sunday)$")
    start_time: str = Field(..., regex="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    end_time: str = Field(..., regex="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    
    @validator('end_time')
    def validate_time_range(cls, v, values):
        if 'start_time' in values:
            start = datetime.strptime(values['start_time'], '%H:%M').time()
            end = datetime.strptime(v, '%H:%M').time()
            if end <= start:
                raise ValueError('End time must be after start time')
        return v

class Location(BaseModel):
    address: str = Field(..., min_length=5, max_length=200)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    country: str = Field(..., min_length=2, max_length=100)
    postal_code: str = Field(..., min_length=3, max_length=20)
    coordinates: List[float] = Field(..., min_items=2, max_items=2)  # [longitude, latitude]
    
    @validator('coordinates')
    def validate_coordinates(cls, v):
        if len(v) != 2:
            raise ValueError('Coordinates must contain exactly 2 values: [longitude, latitude]')
        longitude, latitude = v
        if not (-180 <= longitude <= 180):
            raise ValueError('Longitude must be between -180 and 180')
        if not (-90 <= latitude <= 90):
            raise ValueError('Latitude must be between -90 and 90')
        return v

class VolunteerProfile(BaseModel):
    bio: Optional[str] = Field(default="", max_length=1000)
    motivation: Optional[str] = Field(default="", max_length=500)
    languages: List[str] = Field(default_factory=list)
    transportation: bool = Field(default=False)
    emergency_contact: Optional[Dict[str, str]] = None
    dietary_restrictions: List[str] = Field(default_factory=list)
    medical_conditions: List[str] = Field(default_factory=list)

class VolunteerPreferences(BaseModel):
    preferred_event_types: List[str] = Field(default_factory=list)
    max_distance_km: int = Field(default=50, ge=1, le=1000)
    notification_preferences: Dict[str, bool] = Field(default_factory=lambda: {
        "email": True,
        "sms": False,
        "push": True
    })
    commitment_level: str = Field(default="flexible", regex="^(low|flexible|high)$")

class VolunteerBase(BaseModel):
    user_id: PyObjectId
    skills: List[Skill] = Field(default_factory=list)
    availability: List[Availability] = Field(default_factory=list)
    location: Optional[Location] = None
    profile: VolunteerProfile = Field(default_factory=VolunteerProfile)
    preferences: VolunteerPreferences = Field(default_factory=VolunteerPreferences)
    is_verified: bool = Field(default=False)
    verification_documents: List[str] = Field(default_factory=list)

class VolunteerCreate(VolunteerBase):
    pass

class VolunteerUpdate(BaseModel):
    skills: Optional[List[Skill]] = None
    availability: Optional[List[Availability]] = None
    location: Optional[Location] = None
    profile: Optional[VolunteerProfile] = None
    preferences: Optional[VolunteerPreferences] = None
    is_verified: Optional[bool] = None
    verification_documents: Optional[List[str]] = None

class VolunteerInDB(VolunteerBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: Optional[datetime] = None
    total_hours_volunteered: int = Field(default=0)
    events_completed: int = Field(default=0)
    rating: float = Field(default=0.0, ge=0.0, le=5.0)
    reviews: List[Dict[str, Any]] = Field(default_factory=list)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Volunteer(VolunteerBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: Optional[datetime] = None
    total_hours_volunteered: int = Field(default=0)
    events_completed: int = Field(default=0)
    rating: float = Field(default=0.0)
    reviews: List[Dict[str, Any]] = Field(default_factory=list)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class VolunteerStats(BaseModel):
    total_volunteers: int
    active_volunteers: int
    verified_volunteers: int
    average_rating: float
    total_hours_volunteered: int
    top_skills: List[Dict[str, Any]] 