from datetime import datetime, date, time
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from bson import ObjectId
from .user import PyObjectId

class AvailabilitySlot(BaseModel):
    day_of_week: str = Field(..., regex='^(monday|tuesday|wednesday|thursday|friday|saturday|sunday)$')
    start_time: str = Field(..., regex='^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    end_time: str = Field(..., regex='^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    is_available: bool = Field(default=True)
    
    @validator('end_time')
    def validate_time_range(cls, v, values):
        if 'start_time' in values:
            start = datetime.strptime(values['start_time'], '%H:%M').time()
            end = datetime.strptime(v, '%H:%M').time()
            if end <= start:
                raise ValueError('End time must be after start time')


class AvailabilityPeriod(BaseModel):
    start_date: date
    end_date: Optional[date] = None
    slots: List[AvailabilitySlot] = Field(..., min_items=1)
    is_recurring: bool = Field(default=False)
    recurring_pattern: Optional[str] = Field(default=None, regex='^(weekly|monthly)$')
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        if v and 'start_date' in values and v < values['start_date']:
            raise ValueError('End date must be after start date')


class AvailabilityCreate(BaseModel):
    volunteer_id: PyObjectId
    periods: List[AvailabilityPeriod] = Field(..., min_items=1)
    notes: Optional[str] = Field(default='', max_length=500)

class AvailabilityUpdate(BaseModel):
    periods: Optional[List[AvailabilityPeriod]] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class AvailabilityInDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    volunteer_id: PyObjectId
    periods: List[AvailabilityPeriod]
    notes: str = Field(default='')
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_checked: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class AvailabilityResponse(BaseModel):
    id: str
    volunteer_id: str
    periods: List[AvailabilityPeriod]
    notes: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_checked: Optional[datetime] = None

class AvailabilityStats(BaseModel):
    total_slots: int
    active_slots: int
    weekly_hours: float
    most_available_day: Optional[str] = None
    least_available_day: Optional[str] = None


class AvailabilityCreate(BaseModel):
    volunteer_id: PyObjectId
    periods: List[AvailabilityPeriod] = Field(..., min_items=1)
    notes: Optional[str] = Field(default='', max_length=500)

class AvailabilityUpdate(BaseModel):
    periods: Optional[List[AvailabilityPeriod]] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class AvailabilityInDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    volunteer_id: PyObjectId
    periods: List[AvailabilityPeriod]
    notes: str = Field(default='')
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_checked: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class AvailabilityResponse(BaseModel):
    id: str
    volunteer_id: str
    periods: List[AvailabilityPeriod]
    notes: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_checked: Optional[datetime] = None

class AvailabilityStats(BaseModel):
    total_slots: int
    active_slots: int
    weekly_hours: float
    most_available_day: Optional[str] = None
    least_available_day: Optional[str] = None
