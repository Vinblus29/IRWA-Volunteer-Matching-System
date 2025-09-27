from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from ..models.user import User
from ..models.event import Event
from ..models.volunteer import Volunteer
from ..services.auth_service import auth_service
from ..services.matching_service import matching_service
from ..agents.event_matcher import EventMatcherAgent
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize event matcher agent
event_matcher_agent = EventMatcherAgent()

@router.post("/match-event/{event_id}")
async def match_event_with_volunteers(
    event_id: str,
    max_matches: int = Query(default=10, ge=1, le=50),
    current_user: User = Depends(auth_service.require_role(["organization", "admin"]))
):
    """Match an event with suitable volunteers using AI"""
    try:
        # Get event details
        event = await matching_service.get_event(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        # Use AI agent to find matches
        matches = await event_matcher_agent.find_matches(
            event_id=event_id,
            max_matches=max_matches
        )
        
        return {
            "event_id": event_id,
            "matches": matches,
            "total_matches": len(matches),
            "message": "Event matched successfully with volunteers"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error matching event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to match event with volunteers"
        )

@router.post("/match-volunteer/{volunteer_id}")
async def match_volunteer_with_events(
    volunteer_id: str,
    max_matches: int = Query(default=10, ge=1, le=50),
    current_user: User = Depends(auth_service.require_role(["volunteer", "admin"]))
):
    """Match a volunteer with suitable events using AI"""
    try:
        # Check if user can access this volunteer
        if current_user.role == "volunteer" and str(current_user.id) != volunteer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get volunteer details
        volunteer = await matching_service.get_volunteer(volunteer_id)
        if not volunteer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Volunteer not found"
            )
        
        # Use AI agent to find matches
        matches = await event_matcher_agent.find_volunteer_matches(
            volunteer_id=volunteer_id,
            max_matches=max_matches
        )
        
        return {
            "volunteer_id": volunteer_id,
            "matches": matches,
            "total_matches": len(matches),
            "message": "Volunteer matched successfully with events"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error matching volunteer: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to match volunteer with events"
        )

@router.get("/suggestions/event/{event_id}")
async def get_event_suggestions(
    event_id: str,
    current_user: User = Depends(auth_service.require_role(["organization", "admin"]))
):
    """Get AI-powered suggestions for improving event matching"""
    try:
        # Get event details
        event = await matching_service.get_event(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        # Get AI suggestions
        suggestions = await event_matcher_agent.get_event_suggestions(event_id)
        
        return {
            "event_id": event_id,
            "suggestions": suggestions,
            "message": "AI suggestions generated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting event suggestions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get event suggestions"
        )

@router.get("/suggestions/volunteer/{volunteer_id}")
async def get_volunteer_suggestions(
    volunteer_id: str,
    current_user: User = Depends(auth_service.require_role(["volunteer", "admin"]))
):
    """Get AI-powered suggestions for improving volunteer matching"""
    try:
        # Check if user can access this volunteer
        if current_user.role == "volunteer" and str(current_user.id) != volunteer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get volunteer details
        volunteer = await matching_service.get_volunteer(volunteer_id)
        if not volunteer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Volunteer not found"
            )
        
        # Get AI suggestions
        suggestions = await event_matcher_agent.get_volunteer_suggestions(volunteer_id)
        
        return {
            "volunteer_id": volunteer_id,
            "suggestions": suggestions,
            "message": "AI suggestions generated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting volunteer suggestions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get volunteer suggestions"
        )

@router.post("/batch-match")
async def batch_match_events(
    event_ids: List[str],
    max_matches_per_event: int = Query(default=5, ge=1, le=20),
    current_user: User = Depends(auth_service.require_role(["organization", "admin"]))
):
    """Batch match multiple events with volunteers"""
    try:
        results = []
        
        for event_id in event_ids:
            try:
                matches = await event_matcher_agent.find_matches(
                    event_id=event_id,
                    max_matches=max_matches_per_event
                )
                results.append({
                    "event_id": event_id,
                    "matches": matches,
                    "status": "success"
                })
            except Exception as e:
                results.append({
                    "event_id": event_id,
                    "matches": [],
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "results": results,
            "total_events": len(event_ids),
            "successful_matches": len([r for r in results if r["status"] == "success"]),
            "message": "Batch matching completed"
        }
        
    except Exception as e:
        logger.error(f"Error in batch matching: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform batch matching"
        )

@router.get("/match-quality/{event_id}")
async def get_match_quality_score(
    event_id: str,
    current_user: User = Depends(auth_service.require_role(["organization", "admin"]))
):
    """Get AI-powered match quality score for an event"""
    try:
        # Get event details
        event = await matching_service.get_event(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        # Get match quality score
        quality_score = await event_matcher_agent.get_match_quality_score(event_id)
        
        return {
            "event_id": event_id,
            "quality_score": quality_score,
            "message": "Match quality score calculated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting match quality score: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get match quality score"
        )

@router.get("/agent-status")
async def get_event_matcher_agent_status(
    current_user: User = Depends(auth_service.require_role(["admin"]))
):
    """Get status of the event matcher AI agent (admin only)"""
    try:
        status = event_matcher_agent.get_status()
        return {
            "agent_name": "EventMatcherAgent",
            "status": status,
            "message": "Agent status retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get agent status"
        )
