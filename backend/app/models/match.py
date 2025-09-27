from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId
from .user import PyObjectId

class SkillMatch(BaseModel):
    skill_name: str
    volunteer_level: str
    required_level: str
    match_score: float = Field(..., ge=0.0, le=1.0)
    weight: float = Field(default=1.0, ge=0.0, le=1.0)

class AvailabilityMatch(BaseModel):
    day: str
    event_time_start: str
    event_time_end: str
    volunteer_time_start: str
    volunteer_time_end: str
    overlap_hours: float = Field(..., ge=0.0)
    match_score: float = Field(..., ge=0.0, le=1.0)

class LocationMatch(BaseModel):
    distance_km: float = Field(..., ge=0.0)
    volunteer_max_distance: float = Field(..., ge=0.0)
    match_score: float = Field(..., ge=0.0, le=1.0)
    transportation_provided: bool = Field(default=False)

class MatchAnalysis(BaseModel):
    skill_matches: List[SkillMatch] = Field(default_factory=list)
    availability_match: Optional[AvailabilityMatch] = None
    location_match: Optional[LocationMatch] = None
    overall_compatibility: float = Field(..., ge=0.0, le=1.0)
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    reasoning: str = Field(default="")
    recommendations: List[str] = Field(default_factory=list)

class MatchBase(BaseModel):
    volunteer_id: PyObjectId
    event_id: PyObjectId
    match_score: float = Field(..., ge=0.0, le=1.0)
    skill_compatibility: float = Field(..., ge=0.0, le=1.0)
    availability_compatibility: float = Field(..., ge=0.0, le=1.0)
    location_compatibility: float = Field(..., ge=0.0, le=1.0)
    analysis: MatchAnalysis
    ai_explanation: str = Field(default="")
    recommended_role: Optional[str] = None

class MatchCreate(MatchBase):
    pass

class MatchUpdate(BaseModel):
    match_score: Optional[float] = None
    status: Optional[str] = None
    volunteer_response: Optional[str] = None
    organization_response: Optional[str] = None
    feedback: Optional[str] = None

class MatchInDB(MatchBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    status: str = Field(default="pending", regex="^(pending|accepted|declined|expired|completed)$")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    volunteer_response: Optional[str] = None
    volunteer_responded_at: Optional[datetime] = None
    organization_response: Optional[str] = None
    organization_responded_at: Optional[datetime] = None
    feedback: Optional[str] = None
    rating: Optional[float] = Field(default=None, ge=0.0, le=5.0)
    completed_at: Optional[datetime] = None
    
    # Agent tracking
    created_by_agent: str = Field(default="event_matcher")
    processing_time_ms: Optional[int] = None
    agent_version: str = Field(default="1.0")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Match(MatchBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    status: str = Field(default="pending")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    volunteer_response: Optional[str] = None
    organization_response: Optional[str] = None
    feedback: Optional[str] = None
    rating: Optional[float] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class MatchRequest(BaseModel):
    volunteer_id: Optional[PyObjectId] = None
    event_id: Optional[PyObjectId] = None
    max_matches: int = Field(default=10, ge=1, le=50)
    min_match_score: float = Field(default=0.6, ge=0.0, le=1.0)
    include_location_filter: bool = Field(default=True)
    include_availability_filter: bool = Field(default=True)
    priority_skills: List[str] = Field(default_factory=list)

class MatchResponse(BaseModel):
    matches: List[Match]
    total_found: int
    processing_time_ms: int
    agent_insights: Dict[str, Any] = Field(default_factory=dict)

class MatchStats(BaseModel):
    total_matches_created: int
    successful_matches: int
    pending_matches: int
    declined_matches: int
    expired_matches: int
    average_match_score: float
    average_response_time_hours: float
    top_matching_skills: List[Dict[str, Any]]
    match_success_rate: float

class BatchMatchRequest(BaseModel):
    event_ids: List[PyObjectId] = Field(..., min_items=1, max_items=10)
    max_matches_per_event: int = Field(default=5, ge=1, le=20)
    min_match_score: float = Field(default=0.7, ge=0.0, le=1.0)
    priority_urgent_events: bool = Field(default=True)

class BatchMatchResponse(BaseModel):
    results: Dict[str, MatchResponse]
    total_processing_time_ms: int
    successful_events: int
    failed_events: int
    agent_performance: Dict[str, Any] 