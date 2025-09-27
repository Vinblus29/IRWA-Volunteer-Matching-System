from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from ..models.availability import (
    AvailabilityCreate, AvailabilityUpdate, AvailabilityResponse, 
    AvailabilityStats, AvailabilityPeriod, AvailabilitySlot
)
from ..models.user import User
from ..services.auth_service import auth_service
from ..services.availability_service import availability_service
from ..utils.security import sanitize_input
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=AvailabilityResponse)
async def create_availability(
    availability_data: AvailabilityCreate,
    current_user: User = Depends(auth_service.require_role("volunteer"))
):
    """Create availability for current volunteer"""
    try:
        # Set volunteer_id to current user
        availability_data.volunteer_id = current_user.id
        
        # Create availability
        availability = await availability_service.create_availability(availability_data)
        
        logger.info(f"Created availability for volunteer {current_user.id}")
        return availability
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating availability: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create availability"
        )

@router.get("/me", response_model=AvailabilityResponse)
async def get_my_availability(
    current_user: User = Depends(auth_service.require_role("volunteer"))
):
    """Get current volunteer's availability"""
    try:
        availability = await availability_service.get_availability(str(current_user.id))
        
        if not availability:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Availability not found"
            )
        
        return availability
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting availability: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get availability"
        )

@router.put("/me", response_model=AvailabilityResponse)
async def update_my_availability(
    update_data: AvailabilityUpdate,
    current_user: User = Depends(auth_service.require_role("volunteer"))
):
    """Update current volunteer's availability"""
    try:
        availability = await availability_service.update_availability(
            str(current_user.id), update_data
        )
        
        if not availability:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Availability not found"
            )
        
        logger.info(f"Updated availability for volunteer {current_user.id}")
        return availability
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating availability: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update availability"
        )

@router.delete("/me")
async def delete_my_availability(
    current_user: User = Depends(auth_service.require_role("volunteer"))
):
    """Delete current volunteer's availability"""
    try:
        success = await availability_service.delete_availability(str(current_user.id))
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Availability not found"
            )
        
        logger.info(f"Deleted availability for volunteer {current_user.id}")
        return {"message": "Availability deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting availability: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete availability"
        )

@router.get("/me/stats", response_model=AvailabilityStats)
async def get_my_availability_stats(
    current_user: User = Depends(auth_service.require_role("volunteer"))
):
    """Get current volunteer's availability statistics"""
    try:
        stats = await availability_service.get_availability_stats(str(current_user.id))
        
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Availability not found"
            )
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting availability stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get availability statistics"
        )

@router.get("/volunteer/{volunteer_id}", response_model=AvailabilityResponse)
async def get_volunteer_availability(
    volunteer_id: str,
    current_user: User = Depends(auth_service.require_role(["organization", "admin"]))
):
    """Get availability for a specific volunteer (organizations and admins only)"""
    try:
        availability = await availability_service.get_availability(volunteer_id)
        
        if not availability:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Availability not found"
            )
        
        return availability
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting volunteer availability: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get volunteer availability"
        )

@router.get("/search")
async def search_available_volunteers(
    event_date: str = Query(..., description="Event date in YYYY-MM-DD format"),
    start_time: str = Query(..., description="Start time in HH:MM format"),
    end_time: str = Query(..., description="End time in HH:MM format"),
    current_user: User = Depends(auth_service.require_role(["organization", "admin"]))
):
    """Search for volunteers available at specific time (organizations and admins only)"""
    try:
        from datetime import datetime
        
        # Validate date format
        try:
            event_date_obj = datetime.strptime(event_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
        
        # Validate time format
        try:
            datetime.strptime(start_time, "%H:%M")
            datetime.strptime(end_time, "%H:%M")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid time format. Use HH:MM"
            )
        
        # Find available volunteers
        volunteer_ids = await availability_service.find_available_volunteers(
            event_date_obj, start_time, end_time
        )
        
        return {
            "event_date": event_date,
            "start_time": start_time,
            "end_time": end_time,
            "available_volunteers": volunteer_ids,
            "count": len(volunteer_ids)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching available volunteers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search available volunteers"
        )

@router.post("/bulk-update")
async def bulk_update_availability(
    periods: List[AvailabilityPeriod],
    notes: Optional[str] = None,
    current_user: User = Depends(auth_service.require_role("volunteer"))
):
    """Bulk update availability periods for current volunteer"""
    try:
        update_data = AvailabilityUpdate(
            periods=periods,
            notes=notes
        )
        
        availability = await availability_service.update_availability(
            str(current_user.id), update_data
        )
        
        if not availability:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Availability not found"
            )
        
        logger.info(f"Bulk updated availability for volunteer {current_user.id}")
        return availability
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error bulk updating availability: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to bulk update availability"
        )
