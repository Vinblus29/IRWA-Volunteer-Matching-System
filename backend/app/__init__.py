"""
Volunteer Matching System - Main Application Package

This package contains the core components of the Volunteer Matching System:
- API endpoints and routing
- Data models and schemas
- Business logic services
- AI agents for matching and profiling
- Database connections and operations
- Utility functions and helpers
- Authentication and security
- Testing utilities

The system provides intelligent matching between volunteers and events based on:
- Skills and experience
- Availability and scheduling
- Location and proximity
- Preferences and interests
- Organization requirements

Key Features:
- AI-powered skill profiling
- Intelligent event matching
- Real-time availability tracking
- Multi-channel notifications
- Comprehensive analytics
- Secure authentication
- RESTful API design
"""

# Version information
__version__ = "1.0.0"
__author__ = "Volunteer Matching System Team"
__email__ = "support@volunteermatching.com"
__description__ = "AI-powered volunteer matching system"

# Import key components for easy access
from .config import settings
from .database import get_database, connect_to_mongo, close_mongo_connection
from .main import app

# Import models
from .models.user import User, UserCreate, UserUpdate, UserResponse
from .models.volunteer import Volunteer, VolunteerCreate, VolunteerUpdate, VolunteerResponse
from .models.event import Event, EventCreate, EventUpdate, EventResponse
from .models.organization import Organization, OrganizationCreate, OrganizationUpdate, OrganizationResponse
from .models.match import Match, MatchCreate, MatchUpdate, MatchResponse
from .models.availability import Availability, AvailabilityCreate, AvailabilityUpdate, AvailabilityResponse
from .models.notification import Notification, NotificationCreate, NotificationUpdate, NotificationResponse

# Import services
from .services.auth_service import AuthService
from .services.matching_service import MatchingService
from .services.notification_service import NotificationService
from .services.llm_service import LLMService
from .services.nlp_service import NLPService
from .services.vector_service import VectorService
from .services.availability_service import AvailabilityService
from .services.organization_service import OrganizationService

# Import agents
from .agents.base_agent import BaseAgent, AgentMessage, AgentCommunicationProtocol
from .agents.skill_profiler import SkillProfilerAgent
from .agents.event_matcher import EventMatcherAgent
from .agents.availability_tracker import AvailabilityTrackerAgent
from .agents.communication_orchestrator import CommunicationOrchestrator

# Import utilities
from .utils import (
    # Logging
    setup_logging,
    get_logger,
    
    # Validation
    validate_email,
    validate_password,
    validate_phone_number,
    validate_coordinates,
    validate_time_format,
    validate_date_format,
    validate_skill_level,
    validate_availability_slot,
    validate_event_schedule,
    validate_organization_data,
    validate_volunteer_data,
    validate_event_data,
    validate_match_data,
    
    # Security
    sanitize_input,
    sanitize_filename,
    generate_secure_token,
    hash_password,
    verify_password,
    generate_api_key,
    validate_api_key,
    escape_html,
    clean_text,
    validate_file_upload,
    check_file_type,
    generate_csrf_token,
    validate_csrf_token,
    
    # Common utilities
    generate_id,
    generate_short_id,
    format_datetime,
    parse_datetime,
    format_date,
    parse_date,
    format_time,
    parse_time,
    get_current_timestamp,
    get_current_date,
    add_days_to_date,
    add_hours_to_datetime,
    calculate_age,
    is_weekend,
    is_weekday,
    get_day_of_week,
    format_currency,
    format_percentage,
    format_file_size,
    truncate_text,
    capitalize_words,
    slugify,
    extract_emails,
    extract_phone_numbers,
    mask_email,
    mask_phone,
    calculate_distance,
    is_within_radius,
    merge_dicts,
    deep_merge_dicts,
    flatten_dict,
    chunk_list,
    remove_duplicates,
    group_by,
    sort_by_key,
    filter_by_key,
    safe_json_loads,
    safe_json_dumps,
    create_hash,
    retry_on_exception,
    measure_execution_time,
    ensure_directory_exists,
    get_file_extension,
    is_valid_file_extension,
    convert_bytes_to_mb,
    convert_mb_to_bytes,
    get_random_string,
    get_random_number,
    is_valid_url,
    extract_domain,
    normalize_phone_number,
    format_phone_number,
    calculate_percentage,
    calculate_ratio,
    round_to_decimals,
    clamp_value,
    interpolate_value
)

# Export all public components
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    
    # Core components
    "settings",
    "get_database",
    "connect_to_mongo",
    "close_mongo_connection",
    "app",
    
    # Models
    "User",
    "UserCreate", 
    "UserUpdate",
    "UserResponse",
    "Volunteer",
    "VolunteerCreate",
    "VolunteerUpdate", 
    "VolunteerResponse",
    "Event",
    "EventCreate",
    "EventUpdate",
    "EventResponse",
    "Organization",
    "OrganizationCreate",
    "OrganizationUpdate",
    "OrganizationResponse",
    "Match",
    "MatchCreate",
    "MatchUpdate",
    "MatchResponse",
    "Availability",
    "AvailabilityCreate",
    "AvailabilityUpdate",
    "AvailabilityResponse",
    "Notification",
    "NotificationCreate",
    "NotificationUpdate",
    "NotificationResponse",
    
    # Services
    "AuthService",
    "MatchingService",
    "NotificationService",
    "LLMService",
    "NLPService",
    "VectorService",
    "AvailabilityService",
    "OrganizationService",
    
    # Agents
    "BaseAgent",
    "AgentMessage",
    "AgentCommunicationProtocol",
    "SkillProfilerAgent",
    "EventMatcherAgent",
    "AvailabilityTrackerAgent",
    "CommunicationOrchestrator",
    
    # Utilities
    "setup_logging",
    "get_logger",
    "validate_email",
    "validate_password",
    "validate_phone_number",
    "validate_coordinates",
    "validate_time_format",
    "validate_date_format",
    "validate_skill_level",
    "validate_availability_slot",
    "validate_event_schedule",
    "validate_organization_data",
    "validate_volunteer_data",
    "validate_event_data",
    "validate_match_data",
    "sanitize_input",
    "sanitize_filename",
    "generate_secure_token",
    "hash_password",
    "verify_password",
    "generate_api_key",
    "validate_api_key",
    "escape_html",
    "clean_text",
    "validate_file_upload",
    "check_file_type",
    "generate_csrf_token",
    "validate_csrf_token",
    "generate_id",
    "generate_short_id",
    "format_datetime",
    "parse_datetime",
    "format_date",
    "parse_date",
    "format_time",
    "parse_time",
    "get_current_timestamp",
    "get_current_date",
    "add_days_to_date",
    "add_hours_to_datetime",
    "calculate_age",
    "is_weekend",
    "is_weekday",
    "get_day_of_week",
    "format_currency",
    "format_percentage",
    "format_file_size",
    "truncate_text",
    "capitalize_words",
    "slugify",
    "extract_emails",
    "extract_phone_numbers",
    "mask_email",
    "mask_phone",
    "calculate_distance",
    "is_within_radius",
    "merge_dicts",
    "deep_merge_dicts",
    "flatten_dict",
    "chunk_list",
    "remove_duplicates",
    "group_by",
    "sort_by_key",
    "filter_by_key",
    "safe_json_loads",
    "safe_json_dumps",
    "create_hash",
    "retry_on_exception",
    "measure_execution_time",
    "ensure_directory_exists",
    "get_file_extension",
    "is_valid_file_extension",
    "convert_bytes_to_mb",
    "convert_mb_to_bytes",
    "get_random_string",
    "get_random_number",
    "is_valid_url",
    "extract_domain",
    "normalize_phone_number",
    "format_phone_number",
    "calculate_percentage",
    "calculate_ratio",
    "round_to_decimals",
    "clamp_value",
    "interpolate_value"
]
