from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from bson import ObjectId
from .user import PyObjectId
from .volunteer import Skill, Location

class EventRequirement(BaseModel):
    skill: Skill
    required_volunteers: int = Field(..., ge=1)
    filled_positions: int = Field(default=0, ge=0)

class EventSchedule(BaseModel):
    start_date: date
    end_date: date
    start_time: str = Field(..., regex="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    end_time: str = Field(..., regex="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    recurring: bool = Field(default=False)
    recurring_pattern: Optional[str] = Field(default=None, regex="^(daily|weekly|monthly)$")
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('End date must be after start date')
        return v
    
    @validator('end_time')
    def validate_time_range(cls, v, values):
        if 'start_time' in values:
            start = datetime.strptime(values['start_time'], '%H:%M').time()
            end = datetime.strptime(v, '%H:%M').time()
            if end <= start:
                raise ValueError('End time must be after start time')
        return v

class EventBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=20, max_length=2000)
    organization_id: PyObjectId
    category: str = Field(..., min_length=2, max_length=100)
    location: Location
    schedule: EventSchedule
    requirements: List[EventRequirement] = Field(..., min_items=1)
    max_volunteers: int = Field(..., ge=1)
    current_volunteers: int = Field(default=0, ge=0)
    registration_deadline: Optional[date] = None
    is_urgent: bool = Field(default=False)
    requires_background_check: bool = Field(default=False)
    provides_training: bool = Field(default=False)
    provides_meals: bool = Field(default=False)
    provides_transportation: bool = Field(default=False)
    age_requirement: Optional[int] = Field(default=None, ge=13, le=100)
    
    @validator('registration_deadline')
    def validate_registration_deadline(cls, v, values):
        if v and 'schedule' in values:
            if v >= values['schedule'].start_date:
                raise ValueError('Registration deadline must be before event start date')
        return v

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    location: Optional[Location] = None
    schedule: Optional[EventSchedule] = None
    requirements: Optional[List[EventRequirement]] = None
    max_volunteers: Optional[int] = None
    registration_deadline: Optional[date] = None
    is_urgent: Optional[bool] = None
    requires_background_check: Optional[bool] = None
    provides_training: Optional[bool] = None
    provides_meals: Optional[bool] = None
    provides_transportation: Optional[bool] = None
    age_requirement: Optional[int] = None

class EventInDB(EventBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    status: str = Field(default="active", regex="^(draft|active|full|cancelled|completed)$")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    volunteer_registrations: List[PyObjectId] = Field(default_factory=list)
    waitlist: List[PyObjectId] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    images: List[str] = Field(default_factory=list)
    feedback_collected: bool = Field(default=False)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Event(EventBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    status: str = Field(default="active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    volunteer_registrations: List[PyObjectId] = Field(default_factory=list)
    waitlist: List[PyObjectId] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    images: List[str] = Field(default_factory=list)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class EventStats(BaseModel):
    total_events: int
    active_events: int
    completed_events: int
    cancelled_events: int
    total_volunteer_hours: int
    average_volunteers_per_event: float
    popular_categories: List[Dict[str, Any]]

class EventSearchFilters(BaseModel):
    category: Optional[str] = None
    location_radius_km: Optional[int] = Field(default=50, ge=1, le=1000)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    required_skills: Optional[List[str]] = None
    provides_training: Optional[bool] = None
    provides_meals: Optional[bool] = None
    provides_transportation: Optional[bool] = None
    is_urgent: Optional[bool] = None
    max_age_requirement: Optional[int] = None 