from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from ..models.volunteer import Volunteer, VolunteerCreate, VolunteerUpdate, VolunteerStats
from ..models.user import User
from ..services.auth_service import auth_service
from ..database import get_database
from ..utils.security import sanitize_input
from ..utils.validators import validate_skills_list, validate_availability_list
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=Volunteer)
async def create_volunteer_profile(
    volunteer_data: VolunteerCreate,
    current_user: User = Depends(auth_service.require_role("volunteer"))
):
    """Create volunteer profile"""
    try:
        db = get_database()
        
        # Check if volunteer profile already exists
        existing_profile = await db.volunteers.find_one({"user_id": current_user.id})
        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Volunteer profile already exists"
            )
        
        # Validate skills
        if volunteer_data.skills:
            valid, errors = validate_skills_list([skill.dict() for skill in volunteer_data.skills])
            if not valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid skills: {', '.join(errors)}"
                )
        
        # Validate availability
        if volunteer_data.availability:
            valid, errors = validate_availability_list([avail.dict() for avail in volunteer_data.availability])
            if not valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid availability: {', '.join(errors)}"
                )
        
        # Create volunteer profile
        volunteer_dict = volunteer_data.dict()
        volunteer_dict["user_id"] = current_user.id
        volunteer_dict["created_at"] = datetime.utcnow()
        volunteer_dict["updated_at"] = datetime.utcnow()
        
        result = await db.volunteers.insert_one(volunteer_dict)
        
        # Get created volunteer
        created_volunteer = await db.volunteers.find_one({"_id": result.inserted_id})
        
        return Volunteer(**created_volunteer)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating volunteer profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating volunteer profile"
        )

@router.get("/me", response_model=Volunteer)
async def get_my_volunteer_profile(
    current_user: User = Depends(auth_service.require_role("volunteer"))
):
    """Get current user's volunteer profile"""
    try:
        db = get_database()
        
        volunteer = await db.volunteers.find_one({"user_id": current_user.id})
        if not volunteer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Volunteer profile not found"
            )
        
        return Volunteer(**volunteer)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting volunteer profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving volunteer profile"
        )

@router.put("/me", response_model=Volunteer)
async def update_my_volunteer_profile(
    volunteer_update: VolunteerUpdate,
    current_user: User = Depends(auth_service.require_role("volunteer"))
):
    """Update current user's volunteer profile"""
    try:
        db = get_database()
        
        # Get existing profile
        existing_volunteer = await db.volunteers.find_one({"user_id": current_user.id})
        if not existing_volunteer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Volunteer profile not found"
            )
        
        # Prepare update data
        update_data = volunteer_update.dict(exclude_unset=True)
        
        # Validate skills if provided
        if "skills" in update_data and update_data["skills"]:
            valid, errors = validate_skills_list([skill.dict() for skill in update_data["skills"]])
            if not valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid skills: {', '.join(errors)}"
                )
        
        # Validate availability if provided
        if "availability" in update_data and update_data["availability"]:
            valid, errors = validate_availability_list([avail.dict() for avail in update_data["availability"]])
            if not valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid availability: {', '.join(errors)}"
                )
        
        update_data["updated_at"] = datetime.utcnow()
        
        # Update volunteer profile
        await db.volunteers.update_one(
            {"user_id": current_user.id},
            {"$set": update_data}
        )
        
        # Get updated volunteer
        updated_volunteer = await db.volunteers.find_one({"user_id": current_user.id})
        
        return Volunteer(**updated_volunteer)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating volunteer profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating volunteer profile"
        )

@router.get("/", response_model=List[Volunteer])
async def list_volunteers(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    skills: Optional[str] = Query(None, description="Filter by skills (comma-separated)"),
    location: Optional[str] = Query(None, description="Filter by location"),
    availability: Optional[str] = Query(None, description="Filter by availability day"),
    verified_only: bool = Query(False, description="Show only verified volunteers"),
    current_user: User = Depends(auth_service.require_any_role(["organization", "admin"]))
):
    """List volunteers (for organizations and admins)"""
    try:
        db = get_database()
        
        # Build query
        query = {}
        
        if verified_only:
            query["is_verified"] = True
        
        if skills:
            skill_list = [skill.strip() for skill in skills.split(",")]
            query["skills.name"] = {"$in": skill_list}
        
        if location:
            query["location.city"] = {"$regex": location, "$options": "i"}
        
        if availability:
            query["availability.day"] = availability.lower()
        
        # Get volunteers
        volunteers = await db.volunteers.find(query)\
            .skip(skip)\
            .limit(limit)\
            .to_list(None)
        
        return [Volunteer(**volunteer) for volunteer in volunteers]
        
    except Exception as e:
        logger.error(f"Error listing volunteers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving volunteers"
        )

@router.get("/{volunteer_id}", response_model=Volunteer)
async def get_volunteer(
    volunteer_id: str,
    current_user: User = Depends(auth_service.require_any_role(["organization", "admin"]))
):
    """Get volunteer by ID (for organizations and admins)"""
    try:
        db = get_database()
        
        # Validate ObjectId
        try:
            volunteer_object_id = ObjectId(volunteer_id)
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid volunteer ID"
            )
        
        volunteer = await db.volunteers.find_one({"_id": volunteer_object_id})
        if not volunteer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Volunteer not found"
            )
        
        return Volunteer(**volunteer)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting volunteer: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving volunteer"
        )

@router.get("/search/skills")
async def search_volunteers_by_skills(
    skills: str = Query(..., description="Skills to search for (comma-separated)"),
    location_radius: Optional[float] = Query(None, description="Search radius in km"),
    latitude: Optional[float] = Query(None, description="Latitude for location search"),
    longitude: Optional[float] = Query(None, description="Longitude for location search"),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(auth_service.require_any_role(["organization", "admin"]))
):
    """Search volunteers by skills and location"""
    try:
        db = get_database()
        
        # Parse skills
        skill_list = [skill.strip() for skill in skills.split(",")]
        
        # Build aggregation pipeline
        pipeline = []
        
        # Match skills
        pipeline.append({
            "$match": {
                "skills.name": {"$in": skill_list},
                "is_verified": True
            }
        })
        
        # Add location filter if provided
        if location_radius and latitude is not None and longitude is not None:
            pipeline.append({
                "$match": {
                    "location.coordinates": {
                        "$near": {
                            "$geometry": {
                                "type": "Point",
                                "coordinates": [longitude, latitude]
                            },
                            "$maxDistance": location_radius * 1000  # Convert km to meters
                        }
                    }
                }
            })
        
        # Add skill matching score
        pipeline.append({
            "$addFields": {
                "skill_match_count": {
                    "$size": {
                        "$filter": {
                            "input": "$skills",
                            "cond": {"$in": ["$$this.name", skill_list]}
                        }
                    }
                }
            }
        })
        
        # Sort by skill match count
        pipeline.append({"$sort": {"skill_match_count": -1, "rating": -1}})
        
        # Limit results
        pipeline.append({"$limit": limit})
        
        volunteers = await db.volunteers.aggregate(pipeline).to_list(None)
        
        return [Volunteer(**volunteer) for volunteer in volunteers]
        
    except Exception as e:
        logger.error(f"Error searching volunteers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching volunteers"
        )

@router.get("/stats/overview", response_model=VolunteerStats)
async def get_volunteer_stats(
    current_user: User = Depends(auth_service.require_role("admin"))
):
    """Get volunteer statistics (admin only)"""
    try:
        db = get_database()
        
        # Get basic counts
        total_volunteers = await db.volunteers.count_documents({})
        active_volunteers = await db.volunteers.count_documents({"is_active": True})
        verified_volunteers = await db.volunteers.count_documents({"is_verified": True})
        
        # Calculate average rating
        rating_pipeline = [
            {"$group": {"_id": None, "avg_rating": {"$avg": "$rating"}}}
        ]
        rating_result = await db.volunteers.aggregate(rating_pipeline).to_list(None)
        average_rating = rating_result[0]["avg_rating"] if rating_result else 0.0
        
        # Get total hours volunteered
        hours_pipeline = [
            {"$group": {"_id": None, "total_hours": {"$sum": "$total_hours_volunteered"}}}
        ]
        hours_result = await db.volunteers.aggregate(hours_pipeline).to_list(None)
        total_hours_volunteered = hours_result[0]["total_hours"] if hours_result else 0
        
        # Get top skills
        skills_pipeline = [
            {"$unwind": "$skills"},
            {"$group": {"_id": "$skills.name", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        skills_result = await db.volunteers.aggregate(skills_pipeline).to_list(None)
        top_skills = [{"skill": item["_id"], "count": item["count"]} for item in skills_result]
        
        return VolunteerStats(
            total_volunteers=total_volunteers,
            active_volunteers=active_volunteers,
            verified_volunteers=verified_volunteers,
            average_rating=round(average_rating, 2),
            total_hours_volunteered=total_hours_volunteered,
            top_skills=top_skills
        )
        
    except Exception as e:
        logger.error(f"Error getting volunteer stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving volunteer statistics"
        )

@router.post("/{volunteer_id}/verify")
async def verify_volunteer(
    volunteer_id: str,
    current_user: User = Depends(auth_service.require_role("admin"))
):
    """Verify a volunteer (admin only)"""
    try:
        db = get_database()
        
        # Validate ObjectId
        try:
            volunteer_object_id = ObjectId(volunteer_id)
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid volunteer ID"
            )
        
        # Update volunteer verification status
        result = await db.volunteers.update_one(
            {"_id": volunteer_object_id},
            {"$set": {
                "is_verified": True,
                "verified_at": datetime.utcnow(),
                "verified_by": current_user.id,
                "updated_at": datetime.utcnow()
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Volunteer not found"
            )
        
        return {"message": "Volunteer verified successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying volunteer: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error verifying volunteer"
        )

@router.delete("/{volunteer_id}")
async def delete_volunteer(
    volunteer_id: str,
    current_user: User = Depends(auth_service.require_role("admin"))
):
    """Delete volunteer profile (admin only)"""
    try:
        db = get_database()
        
        # Validate ObjectId
        try:
            volunteer_object_id = ObjectId(volunteer_id)
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid volunteer ID"
            )
        
        # Check if volunteer has active matches
        active_matches = await db.matches.count_documents({
            "volunteer_id": volunteer_object_id,
            "status": {"$in": ["pending", "accepted"]}
        })
        
        if active_matches > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete volunteer with active matches"
            )
        
        # Delete volunteer profile
        result = await db.volunteers.delete_one({"_id": volunteer_object_id})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Volunteer not found"
            )
        
        return {"message": "Volunteer profile deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting volunteer: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting volunteer"
        ) 