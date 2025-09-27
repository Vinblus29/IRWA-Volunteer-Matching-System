from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from ..models.event import Event, EventCreate, EventUpdate, EventStats, EventSearchFilters
from ..models.user import User
from ..services.auth_service import auth_service
from ..database import get_database
from ..utils.security import sanitize_input
from ..utils.validators import validate_date_range, validate_coordinates
from bson import ObjectId
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=Event)
async def create_event(
    event_data: EventCreate,
    current_user: User = Depends(auth_service.require_role("organization"))
):
    """Create a new volunteer event"""
    try:
        db = get_database()
        
        # Validate event dates
        if not validate_date_range(event_data.schedule.start_date, event_data.schedule.end_date):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date range"
            )
        
        # Validate location coordinates if provided
        if event_data.location.coordinates:
            if not validate_coordinates(event_data.location.coordinates):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid coordinates"
                )
        
        # Create event
        event_dict = event_data.dict()
        event_dict["organization_id"] = current_user.id
        event_dict["created_at"] = datetime.utcnow()
        event_dict["updated_at"] = datetime.utcnow()
        event_dict["status"] = "active"
        
        result = await db.events.insert_one(event_dict)
        
        # Get created event
        created_event = await db.events.find_one({"_id": result.inserted_id})
        
        return Event(**created_event)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating event"
        )

@router.get("/", response_model=List[Event])
async def list_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None, description="Filter by category"),
    location: Optional[str] = Query(None, description="Filter by location"),
    status: Optional[str] = Query(None, description="Filter by status"),
    is_urgent: Optional[bool] = Query(None, description="Filter urgent events"),
    provides_training: Optional[bool] = Query(None, description="Events that provide training"),
    start_date_from: Optional[str] = Query(None, description="Events starting from date (YYYY-MM-DD)"),
    start_date_to: Optional[str] = Query(None, description="Events starting to date (YYYY-MM-DD)"),
    current_user: User = Depends(auth_service.get_current_user_optional)
):
    """List volunteer events with filtering options"""
    try:
        db = get_database()
        
        # Build query
        query = {}
        
        if category:
            query["category"] = {"$regex": category, "$options": "i"}
        
        if location:
            query["$or"] = [
                {"location.city": {"$regex": location, "$options": "i"}},
                {"location.state": {"$regex": location, "$options": "i"}},
                {"location.address": {"$regex": location, "$options": "i"}}
            ]
        
        if status:
            query["status"] = status
        else:
            query["status"] = "active"  # Default to active events
        
        if is_urgent is not None:
            query["is_urgent"] = is_urgent
        
        if provides_training is not None:
            query["provides_training"] = provides_training
        
        # Date range filtering
        if start_date_from or start_date_to:
            date_filter = {}
            if start_date_from:
                date_filter["$gte"] = start_date_from
            if start_date_to:
                date_filter["$lte"] = start_date_to
            query["schedule.start_date"] = date_filter
        
        # Get events
        events = await db.events.find(query)\
            .sort("schedule.start_date", 1)\
            .skip(skip)\
            .limit(limit)\
            .to_list(None)
        
        return [Event(**event) for event in events]
        
    except Exception as e:
        logger.error(f"Error listing events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving events"
        )

@router.get("/{event_id}", response_model=Event)
async def get_event(
    event_id: str,
    current_user: User = Depends(auth_service.get_current_user_optional)
):
    """Get event by ID"""
    try:
        db = get_database()
        
        # Validate ObjectId
        try:
            event_object_id = ObjectId(event_id)
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid event ID"
            )
        
        event = await db.events.find_one({"_id": event_object_id})
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        return Event(**event)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving event"
        )

@router.put("/{event_id}", response_model=Event)
async def update_event(
    event_id: str,
    event_update: EventUpdate,
    current_user: User = Depends(auth_service.require_role("organization"))
):
    """Update an event (organization owner only)"""
    try:
        db = get_database()
        
        # Validate ObjectId
        try:
            event_object_id = ObjectId(event_id)
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid event ID"
            )
        
        # Check if event exists and user is owner
        existing_event = await db.events.find_one({"_id": event_object_id})
        if not existing_event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        if existing_event["organization_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this event"
            )
        
        # Prepare update data
        update_data = event_update.dict(exclude_unset=True)
        
        # Validate dates if being updated
        if "schedule" in update_data:
            schedule = update_data["schedule"]
            if "start_date" in schedule and "end_date" in schedule:
                if not validate_date_range(schedule["start_date"], schedule["end_date"]):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid date range"
                    )
        
        update_data["updated_at"] = datetime.utcnow()
        
        # Update event
        await db.events.update_one(
            {"_id": event_object_id},
            {"$set": update_data}
        )
        
        # Get updated event
        updated_event = await db.events.find_one({"_id": event_object_id})
        
        return Event(**updated_event)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating event"
        )

@router.delete("/{event_id}")
async def delete_event(
    event_id: str,
    current_user: User = Depends(auth_service.require_any_role(["organization", "admin"]))
):
    """Delete an event"""
    try:
        db = get_database()
        
        # Validate ObjectId
        try:
            event_object_id = ObjectId(event_id)
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid event ID"
            )
        
        # Check if event exists
        existing_event = await db.events.find_one({"_id": event_object_id})
        if not existing_event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        # Check authorization
        if current_user.role != "admin" and existing_event["organization_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this event"
            )
        
        # Check for active matches
        active_matches = await db.matches.count_documents({
            "event_id": event_object_id,
            "status": {"$in": ["pending", "accepted"]}
        })
        
        if active_matches > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete event with active volunteer matches"
            )
        
        # Soft delete by updating status
        await db.events.update_one(
            {"_id": event_object_id},
            {"$set": {
                "status": "deleted",
                "deleted_at": datetime.utcnow(),
                "deleted_by": current_user.id
            }}
        )
        
        return {"message": "Event deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting event"
        )

@router.get("/my-events", response_model=List[Event])
async def get_my_events(
    current_user: User = Depends(auth_service.require_role("organization")),
    status_filter: Optional[str] = Query(None, description="Filter by status")
):
    """Get events created by current organization"""
    try:
        db = get_database()
        
        # Build query
        query = {"organization_id": current_user.id}
        
        if status_filter:
            query["status"] = status_filter
        
        events = await db.events.find(query)\
            .sort("created_at", -1)\
            .to_list(None)
        
        return [Event(**event) for event in events]
        
    except Exception as e:
        logger.error(f"Error getting user events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving your events"
        )

@router.get("/search", response_model=List[Event])
async def search_events(
    q: str = Query(..., description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    location: Optional[str] = Query(None, description="Filter by location"),
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(auth_service.get_current_user_optional)
):
    """Search events by text query"""
    try:
        db = get_database()
        
        # Build search query
        search_query = {
            "$text": {"$search": q},
            "status": "active"
        }
        
        if category:
            search_query["category"] = {"$regex": category, "$options": "i"}
        
        if location:
            search_query["$or"] = [
                {"location.city": {"$regex": location, "$options": "i"}},
                {"location.state": {"$regex": location, "$options": "i"}}
            ]
        
        # Execute search
        events = await db.events.find(search_query)\
            .sort([("score", {"$meta": "textScore"})])\
            .limit(limit)\
            .to_list(None)
        
        return [Event(**event) for event in events]
        
    except Exception as e:
        logger.error(f"Error searching events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching events"
        )

@router.get("/stats/overview", response_model=EventStats)
async def get_event_stats(
    current_user: User = Depends(auth_service.require_role("admin"))
):
    """Get event statistics (admin only)"""
    try:
        db = get_database()
        
        # Get basic counts
        total_events = await db.events.count_documents({})
        active_events = await db.events.count_documents({"status": "active"})
        completed_events = await db.events.count_documents({"status": "completed"})
        urgent_events = await db.events.count_documents({"is_urgent": True, "status": "active"})
        
        # Get events by category
        category_pipeline = [
            {"$match": {"status": "active"}},
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        category_result = await db.events.aggregate(category_pipeline).to_list(None)
        events_by_category = [{"category": item["_id"], "count": item["count"]} for item in category_result]
        
        # Get upcoming events count
        today = datetime.utcnow().date().isoformat()
        upcoming_events = await db.events.count_documents({
            "status": "active",
            "schedule.start_date": {"$gte": today}
        })
        
        return EventStats(
            total_events=total_events,
            active_events=active_events,
            completed_events=completed_events,
            urgent_events=urgent_events,
            upcoming_events=upcoming_events,
            events_by_category=events_by_category
        )
        
    except Exception as e:
        logger.error(f"Error getting event stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving event statistics"
        )

@router.post("/{event_id}/publish")
async def publish_event(
    event_id: str,
    current_user: User = Depends(auth_service.require_role("organization"))
):
    """Publish an event (make it active)"""
    try:
        db = get_database()
        
        # Validate ObjectId
        try:
            event_object_id = ObjectId(event_id)
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid event ID"
            )
        
        # Check authorization
        event = await db.events.find_one({"_id": event_object_id})
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        if event["organization_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to publish this event"
            )
        
        # Update status
        await db.events.update_one(
            {"_id": event_object_id},
            {"$set": {
                "status": "active",
                "published_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }}
        )
        
        return {"message": "Event published successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error publishing event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error publishing event"
        )

@router.post("/{event_id}/cancel")
async def cancel_event(
    event_id: str,
    reason: str = Query(..., description="Cancellation reason"),
    current_user: User = Depends(auth_service.require_role("organization"))
):
    """Cancel an event"""
    try:
        db = get_database()
        
        # Validate ObjectId
        try:
            event_object_id = ObjectId(event_id)
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid event ID"
            )
        
        # Check authorization
        event = await db.events.find_one({"_id": event_object_id})
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        if event["organization_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to cancel this event"
            )
        
        # Update status
        await db.events.update_one(
            {"_id": event_object_id},
            {"$set": {
                "status": "cancelled",
                "cancellation_reason": sanitize_input(reason),
                "cancelled_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }}
        )
        
        # Notify volunteers (would integrate with notification service)
        # await self._notify_volunteers_of_cancellation(event_object_id, reason)
        
        return {"message": "Event cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error cancelling event"
        ) 