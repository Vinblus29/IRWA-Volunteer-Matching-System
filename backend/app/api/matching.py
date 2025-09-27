from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from ..models.match import Match, MatchCreate, MatchUpdate, MatchRequest, MatchResponse, MatchStats
from ..models.user import User
from ..services.auth_service import auth_service
from ..database import get_database
from ..agents.communication_orchestrator import CommunicationOrchestrator
from ..agents.base_agent import AgentMessage, AgentCommunicationProtocol
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize communication orchestrator (would be dependency injected in production)
orchestrator = CommunicationOrchestrator()

@router.post("/find-volunteers", response_model=MatchResponse)
async def find_volunteers_for_event(
    request: MatchRequest,
    current_user: User = Depends(auth_service.require_role("organization"))
):
    """Find suitable volunteers for an event"""
    try:
        db = get_database()
        
        # Verify event exists and user owns it
        event = await db.events.find_one({"_id": ObjectId(request.event_id)})
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        if event["organization_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to find volunteers for this event"
            )
        
        # Start volunteer matching workflow
        workflow_data = {
            "event_id": request.event_id,
            "max_matches": request.max_matches or 20,
            "filters": request.filters or {}
        }
        
        workflow_id = await orchestrator.start_workflow("volunteer_matching", workflow_data)
        
        # For demo purposes, return a mock response
        # In production, this would wait for the workflow to complete
        mock_matches = [
            {
                "volunteer_id": "mock_volunteer_1",
                "volunteer_name": "John Doe",
                "match_score": 0.92,
                "skill_score": 0.95,
                "location_score": 0.85,
                "availability_score": 0.95,
                "explanation": "Excellent match with strong skills in required areas and perfect availability.",
                "skills": [{"name": "Event Management", "level": "advanced"}],
                "location": {"city": "New York", "state": "NY"},
                "experience_hours": 150,
                "rating": 4.8,
                "is_verified": True
            }
        ]
        
        return MatchResponse(
            event_id=request.event_id,
            matches=mock_matches,
            total_found=1,
            workflow_id=workflow_id,
            generated_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding volunteers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error finding volunteers for event"
        )

@router.post("/find-events", response_model=MatchResponse)
async def find_events_for_volunteer(
    volunteer_id: Optional[str] = None,
    max_matches: int = Query(20, ge=1, le=50),
    current_user: User = Depends(auth_service.require_role("volunteer"))
):
    """Find suitable events for a volunteer"""
    try:
        db = get_database()
        
        # Use current user's volunteer profile if no ID provided
        if not volunteer_id:
            volunteer = await db.volunteers.find_one({"user_id": current_user.id})
            if not volunteer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Volunteer profile not found"
                )
            volunteer_id = str(volunteer["_id"])
        
        # Verify volunteer exists
        volunteer = await db.volunteers.find_one({"_id": ObjectId(volunteer_id)})
        if not volunteer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Volunteer not found"
            )
        
        # Check authorization
        if volunteer["user_id"] != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to find events for this volunteer"
            )
        
        # Mock response for demo
        mock_matches = [
            {
                "event_id": "mock_event_1",
                "event_title": "Beach Cleanup Drive",
                "event_description": "Join us for a community beach cleanup to protect marine life...",
                "match_score": 0.88,
                "skill_score": 0.90,
                "interest_score": 0.85,
                "commitment_score": 0.90,
                "explanation": "Perfect match for your environmental interests and weekend availability.",
                "event_category": "Environmental",
                "event_date": "2024-02-15",
                "event_location": {"city": "Santa Monica", "state": "CA"},
                "provides_training": True,
                "is_urgent": False
            }
        ]
        
        return MatchResponse(
            volunteer_id=volunteer_id,
            matches=mock_matches,
            total_found=1,
            generated_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error finding events for volunteer"
        )

@router.get("/matches", response_model=List[Match])
async def get_matches(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, description="Filter by match status"),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get matches for current user"""
    try:
        db = get_database()
        
        # Build query based on user role
        query = {}
        
        if current_user.role == "volunteer":
            # Get volunteer ID
            volunteer = await db.volunteers.find_one({"user_id": current_user.id})
            if volunteer:
                query["volunteer_id"] = volunteer["_id"]
        elif current_user.role == "organization":
            # Get events created by this organization
            events = await db.events.find({"organization_id": current_user.id}).to_list(None)
            event_ids = [event["_id"] for event in events]
            query["event_id"] = {"$in": event_ids}
        elif current_user.role == "admin":
            # Admin can see all matches
            pass
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view matches"
            )
        
        if status_filter:
            query["status"] = status_filter
        
        # Get matches
        matches = await db.matches.find(query)\
            .sort("created_at", -1)\
            .skip(skip)\
            .limit(limit)\
            .to_list(None)
        
        return [Match(**match) for match in matches]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting matches: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving matches"
        )

@router.get("/matches/{match_id}", response_model=Match)
async def get_match(
    match_id: str,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get specific match by ID"""
    try:
        db = get_database()
        
        # Validate ObjectId
        try:
            match_object_id = ObjectId(match_id)
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid match ID"
            )
        
        match = await db.matches.find_one({"_id": match_object_id})
        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match not found"
            )
        
        # Check authorization
        authorized = False
        
        if current_user.role == "admin":
            authorized = True
        elif current_user.role == "volunteer":
            volunteer = await db.volunteers.find_one({"user_id": current_user.id})
            if volunteer and match["volunteer_id"] == volunteer["_id"]:
                authorized = True
        elif current_user.role == "organization":
            event = await db.events.find_one({"_id": match["event_id"]})
            if event and event["organization_id"] == current_user.id:
                authorized = True
        
        if not authorized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this match"
            )
        
        return Match(**match)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting match: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving match"
        )

@router.post("/matches/{match_id}/accept")
async def accept_match(
    match_id: str,
    current_user: User = Depends(auth_service.require_role("volunteer"))
):
    """Accept a volunteer match"""
    try:
        db = get_database()
        
        # Validate ObjectId
        try:
            match_object_id = ObjectId(match_id)
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid match ID"
            )
        
        # Get match
        match = await db.matches.find_one({"_id": match_object_id})
        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match not found"
            )
        
        # Check authorization
        volunteer = await db.volunteers.find_one({"user_id": current_user.id})
        if not volunteer or match["volunteer_id"] != volunteer["_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to accept this match"
            )
        
        # Check if match is in correct status
        if match["status"] != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Match cannot be accepted in current status"
            )
        
        # Update match status
        await db.matches.update_one(
            {"_id": match_object_id},
            {"$set": {
                "status": "accepted",
                "accepted_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }}
        )
        
        # Send notification to organization
        # await notification_service.send_match_accepted_notification(...)
        
        return {"message": "Match accepted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error accepting match: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error accepting match"
        )

@router.post("/matches/{match_id}/decline")
async def decline_match(
    match_id: str,
    reason: Optional[str] = None,
    current_user: User = Depends(auth_service.require_role("volunteer"))
):
    """Decline a volunteer match"""
    try:
        db = get_database()
        
        # Validate ObjectId
        try:
            match_object_id = ObjectId(match_id)
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid match ID"
            )
        
        # Get match
        match = await db.matches.find_one({"_id": match_object_id})
        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match not found"
            )
        
        # Check authorization
        volunteer = await db.volunteers.find_one({"user_id": current_user.id})
        if not volunteer or match["volunteer_id"] != volunteer["_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to decline this match"
            )
        
        # Check if match is in correct status
        if match["status"] not in ["pending", "accepted"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Match cannot be declined in current status"
            )
        
        # Update match status
        update_data = {
            "status": "declined",
            "declined_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        if reason:
            update_data["decline_reason"] = reason
        
        await db.matches.update_one(
            {"_id": match_object_id},
            {"$set": update_data}
        )
        
        return {"message": "Match declined successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error declining match: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error declining match"
        )

@router.post("/matches/{match_id}/rate")
async def rate_match(
    match_id: str,
    rating: int = Query(..., ge=1, le=5, description="Rating from 1 to 5"),
    feedback: Optional[str] = None,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Rate a completed match"""
    try:
        db = get_database()
        
        # Validate ObjectId
        try:
            match_object_id = ObjectId(match_id)
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid match ID"
            )
        
        # Get match
        match = await db.matches.find_one({"_id": match_object_id})
        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match not found"
            )
        
        # Check if match is completed
        if match["status"] != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only rate completed matches"
            )
        
        # Check authorization and determine rating type
        rating_type = None
        
        if current_user.role == "volunteer":
            volunteer = await db.volunteers.find_one({"user_id": current_user.id})
            if volunteer and match["volunteer_id"] == volunteer["_id"]:
                rating_type = "volunteer_rating"
        elif current_user.role == "organization":
            event = await db.events.find_one({"_id": match["event_id"]})
            if event and event["organization_id"] == current_user.id:
                rating_type = "organization_rating"
        
        if not rating_type:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to rate this match"
            )
        
        # Update match with rating
        update_data = {
            f"{rating_type}": rating,
            f"{rating_type.replace('rating', 'feedback')}": feedback,
            f"{rating_type.replace('rating', 'rated_at')}": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.matches.update_one(
            {"_id": match_object_id},
            {"$set": update_data}
        )
        
        # Update overall ratings
        await _update_overall_ratings(db, match, rating_type, rating)
        
        return {"message": "Rating submitted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rating match: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error submitting rating"
        )

@router.get("/stats/overview", response_model=MatchStats)
async def get_match_stats(
    current_user: User = Depends(auth_service.require_role("admin"))
):
    """Get matching statistics (admin only)"""
    try:
        db = get_database()
        
        # Get basic counts
        total_matches = await db.matches.count_documents({})
        pending_matches = await db.matches.count_documents({"status": "pending"})
        accepted_matches = await db.matches.count_documents({"status": "accepted"})
        completed_matches = await db.matches.count_documents({"status": "completed"})
        declined_matches = await db.matches.count_documents({"status": "declined"})
        
        # Calculate average match score
        score_pipeline = [
            {"$group": {"_id": None, "avg_score": {"$avg": "$match_score"}}}
        ]
        score_result = await db.matches.aggregate(score_pipeline).to_list(None)
        average_match_score = score_result[0]["avg_score"] if score_result else 0.0
        
        # Calculate success rate
        total_decided = accepted_matches + declined_matches
        success_rate = (accepted_matches / total_decided * 100) if total_decided > 0 else 0.0
        
        return MatchStats(
            total_matches=total_matches,
            pending_matches=pending_matches,
            accepted_matches=accepted_matches,
            completed_matches=completed_matches,
            declined_matches=declined_matches,
            average_match_score=round(average_match_score, 3),
            success_rate=round(success_rate, 2)
        )
        
    except Exception as e:
        logger.error(f"Error getting match stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving match statistics"
        )

async def _update_overall_ratings(db, match: dict, rating_type: str, rating: int):
    """Update overall ratings for volunteer or organization"""
    try:
        if rating_type == "volunteer_rating":
            # Update volunteer's average rating
            volunteer_id = match["volunteer_id"]
            
            # Get all ratings for this volunteer
            ratings_pipeline = [
                {"$match": {"volunteer_id": volunteer_id, "organization_rating": {"$exists": True}}},
                {"$group": {"_id": None, "avg_rating": {"$avg": "$organization_rating"}, "count": {"$sum": 1}}}
            ]
            
            result = await db.matches.aggregate(ratings_pipeline).to_list(None)
            if result:
                avg_rating = result[0]["avg_rating"]
                rating_count = result[0]["count"]
                
                # Update volunteer's rating
                await db.volunteers.update_one(
                    {"_id": volunteer_id},
                    {"$set": {
                        "rating": round(avg_rating, 2),
                        "rating_count": rating_count,
                        "updated_at": datetime.utcnow()
                    }}
                )
        
        elif rating_type == "organization_rating":
            # Update organization's average rating
            event = await db.events.find_one({"_id": match["event_id"]})
            if event:
                organization_id = event["organization_id"]
                
                # Get all organization events and their ratings
                org_events = await db.events.find({"organization_id": organization_id}).to_list(None)
                event_ids = [event["_id"] for event in org_events]
                
                ratings_pipeline = [
                    {"$match": {"event_id": {"$in": event_ids}, "volunteer_rating": {"$exists": True}}},
                    {"$group": {"_id": None, "avg_rating": {"$avg": "$volunteer_rating"}, "count": {"$sum": 1}}}
                ]
                
                result = await db.matches.aggregate(ratings_pipeline).to_list(None)
                if result:
                    avg_rating = result[0]["avg_rating"]
                    rating_count = result[0]["count"]
                    
                    # Update organization's rating (would need organization collection)
                    # await db.organizations.update_one(...)
                    
    except Exception as e:
        logger.error(f"Error updating overall ratings: {e}")

@router.post("/batch-match")
async def batch_match_volunteers(
    event_ids: List[str],
    max_matches_per_event: int = Query(10, ge=1, le=50),
    current_user: User = Depends(auth_service.require_any_role(["organization", "admin"]))
):
    """Batch match volunteers to multiple events"""
    try:
        # This would implement batch matching logic
        return {"message": "Batch matching initiated", "event_count": len(event_ids)}
        
    except Exception as e:
        logger.error(f"Error in batch matching: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error in batch matching"
        ) 