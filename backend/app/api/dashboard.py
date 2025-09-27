from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from ..models.user import User
from ..services.auth_service import auth_service
from ..database import get_database
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/volunteer")
async def get_volunteer_dashboard(
    current_user: User = Depends(auth_service.require_role("volunteer"))
) -> Dict[str, Any]:
    """Get volunteer dashboard data"""
    try:
        db = get_database()
        
        # Get volunteer profile
        volunteer = await db.volunteers.find_one({"user_id": current_user.id})
        if not volunteer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Volunteer profile not found"
            )
        
        volunteer_id = volunteer["_id"]
        
        # Get match statistics
        total_matches = await db.matches.count_documents({"volunteer_id": volunteer_id})
        pending_matches = await db.matches.count_documents({
            "volunteer_id": volunteer_id, 
            "status": "pending"
        })
        accepted_matches = await db.matches.count_documents({
            "volunteer_id": volunteer_id, 
            "status": "accepted"
        })
        completed_matches = await db.matches.count_documents({
            "volunteer_id": volunteer_id, 
            "status": "completed"
        })
        
        # Get recent matches
        recent_matches = await db.matches.find({
            "volunteer_id": volunteer_id
        }).sort("created_at", -1).limit(5).to_list(None)
        
        # Get upcoming events
        upcoming_events = []
        for match in recent_matches:
            if match["status"] == "accepted":
                event = await db.events.find_one({"_id": match["event_id"]})
                if event and event["schedule"]["start_date"] >= datetime.utcnow().date().isoformat():
                    upcoming_events.append({
                        "event_id": str(event["_id"]),
                        "title": event["title"],
                        "date": event["schedule"]["start_date"],
                        "time": event["schedule"]["start_time"],
                        "location": event["location"],
                        "match_id": str(match["_id"])
                    })
        
        # Get skill recommendations
        skill_recommendations = await _get_skill_recommendations(volunteer)
        
        # Get volunteer stats
        total_hours = volunteer.get("total_hours_volunteered", 0)
        events_completed = volunteer.get("events_completed", 0)
        rating = volunteer.get("rating", 0)
        
        return {
            "profile": {
                "volunteer_id": str(volunteer_id),
                "name": volunteer.get("profile", {}).get("full_name", ""),
                "total_hours": total_hours,
                "events_completed": events_completed,
                "rating": rating,
                "is_verified": volunteer.get("is_verified", False),
                "skills_count": len(volunteer.get("skills", []))
            },
            "statistics": {
                "total_matches": total_matches,
                "pending_matches": pending_matches,
                "accepted_matches": accepted_matches,
                "completed_matches": completed_matches,
                "success_rate": (accepted_matches / total_matches * 100) if total_matches > 0 else 0
            },
            "upcoming_events": upcoming_events[:3],
            "recent_matches": [
                {
                    "match_id": str(match["_id"]),
                    "event_title": "Event Title",  # Would fetch from event
                    "match_score": match.get("match_score", 0),
                    "status": match["status"],
                    "created_at": match["created_at"].isoformat()
                } for match in recent_matches[:3]
            ],
            "skill_recommendations": skill_recommendations,
            "notifications_count": await _get_unread_notifications_count(current_user.id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting volunteer dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving dashboard data"
        )

@router.get("/organization")
async def get_organization_dashboard(
    current_user: User = Depends(auth_service.require_role("organization"))
) -> Dict[str, Any]:
    """Get organization dashboard data"""
    try:
        db = get_database()
        
        # Get organization events
        total_events = await db.events.count_documents({"organization_id": current_user.id})
        active_events = await db.events.count_documents({
            "organization_id": current_user.id, 
            "status": "active"
        })
        completed_events = await db.events.count_documents({
            "organization_id": current_user.id, 
            "status": "completed"
        })
        
        # Get recent events
        recent_events = await db.events.find({
            "organization_id": current_user.id
        }).sort("created_at", -1).limit(5).to_list(None)
        
        # Get match statistics for organization events
        org_event_ids = [event["_id"] for event in recent_events]
        total_matches = await db.matches.count_documents({"event_id": {"$in": org_event_ids}})
        pending_matches = await db.matches.count_documents({
            "event_id": {"$in": org_event_ids}, 
            "status": "pending"
        })
        accepted_matches = await db.matches.count_documents({
            "event_id": {"$in": org_event_ids}, 
            "status": "accepted"
        })
        
        # Get events needing attention
        events_needing_attention = []
        for event in recent_events:
            if event["status"] == "active":
                event_matches = await db.matches.count_documents({
                    "event_id": event["_id"],
                    "status": "pending"
                })
                if event_matches > 0:
                    events_needing_attention.append({
                        "event_id": str(event["_id"]),
                        "title": event["title"],
                        "pending_matches": event_matches,
                        "date": event["schedule"]["start_date"]
                    })
        
        # Get upcoming events
        today = datetime.utcnow().date().isoformat()
        upcoming_events = await db.events.find({
            "organization_id": current_user.id,
            "status": "active",
            "schedule.start_date": {"$gte": today}
        }).sort("schedule.start_date", 1).limit(3).to_list(None)
        
        # Get volunteer engagement stats
        volunteer_stats = await _get_volunteer_engagement_stats(org_event_ids, db)
        
        return {
            "organization": {
                "organization_id": current_user.id,
                "name": current_user.full_name,
                "total_events": total_events,
                "active_events": active_events,
                "completed_events": completed_events
            },
            "statistics": {
                "total_matches": total_matches,
                "pending_matches": pending_matches,
                "accepted_matches": accepted_matches,
                "match_rate": (total_matches / active_events) if active_events > 0 else 0,
                "acceptance_rate": (accepted_matches / total_matches * 100) if total_matches > 0 else 0
            },
            "upcoming_events": [
                {
                    "event_id": str(event["_id"]),
                    "title": event["title"],
                    "date": event["schedule"]["start_date"],
                    "time": event["schedule"]["start_time"],
                    "location": event["location"],
                    "status": event["status"]
                } for event in upcoming_events
            ],
            "events_needing_attention": events_needing_attention[:5],
            "recent_events": [
                {
                    "event_id": str(event["_id"]),
                    "title": event["title"],
                    "status": event["status"],
                    "created_at": event["created_at"].isoformat(),
                    "volunteers_matched": 0  # Would calculate actual count
                } for event in recent_events[:3]
            ],
            "volunteer_engagement": volunteer_stats,
            "notifications_count": await _get_unread_notifications_count(current_user.id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting organization dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving dashboard data"
        )

@router.get("/admin")
async def get_admin_dashboard(
    current_user: User = Depends(auth_service.require_role("admin"))
) -> Dict[str, Any]:
    """Get admin dashboard data"""
    try:
        db = get_database()
        
        # System overview statistics
        total_users = await db.users.count_documents({})
        total_volunteers = await db.volunteers.count_documents({})
        total_organizations = await db.users.count_documents({"role": "organization"})
        total_events = await db.events.count_documents({})
        total_matches = await db.matches.count_documents({})
        
        # Active counts
        active_volunteers = await db.volunteers.count_documents({"is_active": True})
        active_events = await db.events.count_documents({"status": "active"})
        pending_matches = await db.matches.count_documents({"status": "pending"})
        
        # Recent activity
        recent_users = await db.users.find({}).sort("created_at", -1).limit(5).to_list(None)
        recent_events = await db.events.find({}).sort("created_at", -1).limit(5).to_list(None)
        recent_matches = await db.matches.find({}).sort("created_at", -1).limit(5).to_list(None)
        
        # System health metrics
        system_health = await _get_system_health_metrics(db)
        
        # Growth metrics (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        new_users_month = await db.users.count_documents({
            "created_at": {"$gte": thirty_days_ago}
        })
        new_events_month = await db.events.count_documents({
            "created_at": {"$gte": thirty_days_ago}
        })
        new_matches_month = await db.matches.count_documents({
            "created_at": {"$gte": thirty_days_ago}
        })
        
        # Top performing metrics
        top_volunteers = await _get_top_volunteers(db)
        top_organizations = await _get_top_organizations(db)
        
        return {
            "system_overview": {
                "total_users": total_users,
                "total_volunteers": total_volunteers,
                "total_organizations": total_organizations,
                "total_events": total_events,
                "total_matches": total_matches,
                "active_volunteers": active_volunteers,
                "active_events": active_events,
                "pending_matches": pending_matches
            },
            "growth_metrics": {
                "new_users_month": new_users_month,
                "new_events_month": new_events_month,
                "new_matches_month": new_matches_month,
                "user_growth_rate": (new_users_month / total_users * 100) if total_users > 0 else 0
            },
            "system_health": system_health,
            "recent_activity": {
                "recent_users": [
                    {
                        "user_id": str(user["_id"]),
                        "name": user["full_name"],
                        "role": user["role"],
                        "created_at": user["created_at"].isoformat()
                    } for user in recent_users
                ],
                "recent_events": [
                    {
                        "event_id": str(event["_id"]),
                        "title": event["title"],
                        "status": event["status"],
                        "created_at": event["created_at"].isoformat()
                    } for event in recent_events
                ],
                "recent_matches": [
                    {
                        "match_id": str(match["_id"]),
                        "status": match["status"],
                        "match_score": match.get("match_score", 0),
                        "created_at": match["created_at"].isoformat()
                    } for match in recent_matches
                ]
            },
            "top_performers": {
                "top_volunteers": top_volunteers,
                "top_organizations": top_organizations
            },
            "notifications_count": await _get_unread_notifications_count(current_user.id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting admin dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving dashboard data"
        )

async def _get_skill_recommendations(volunteer: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get skill recommendations for volunteer"""
    # Mock implementation - would use AI to analyze and recommend skills
    current_skills = {skill["name"] for skill in volunteer.get("skills", [])}
    
    recommendations = [
        {
            "skill": "Project Management",
            "reason": "Complements your organizational skills",
            "demand": "High demand in current events"
        },
        {
            "skill": "Digital Marketing",
            "reason": "Growing need in non-profit sector",
            "demand": "Medium demand"
        }
    ]
    
    # Filter out skills volunteer already has
    return [rec for rec in recommendations if rec["skill"] not in current_skills]

async def _get_unread_notifications_count(user_id: str) -> int:
    """Get count of unread notifications for user"""
    # Mock implementation
    return 3

async def _get_volunteer_engagement_stats(event_ids: List, db) -> Dict[str, Any]:
    """Get volunteer engagement statistics for organization events"""
    if not event_ids:
        return {
            "total_volunteers": 0,
            "avg_rating": 0,
            "repeat_volunteers": 0,
            "engagement_rate": 0
        }
    
    # Get unique volunteers who matched with organization events
    volunteer_matches = await db.matches.find({
        "event_id": {"$in": event_ids},
        "status": {"$in": ["accepted", "completed"]}
    }).to_list(None)
    
    unique_volunteers = len(set(match["volunteer_id"] for match in volunteer_matches))
    
    # Calculate average rating
    ratings = [match.get("volunteer_rating", 0) for match in volunteer_matches if match.get("volunteer_rating")]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    
    return {
        "total_volunteers": unique_volunteers,
        "avg_rating": round(avg_rating, 2),
        "repeat_volunteers": 0,  # Would calculate actual repeat volunteers
        "engagement_rate": 85  # Mock engagement rate
    }

async def _get_system_health_metrics(db) -> Dict[str, Any]:
    """Get system health metrics"""
    # Mock implementation - would check actual system health
    return {
        "database_status": "healthy",
        "api_response_time": 150,  # ms
        "active_agents": 4,
        "system_load": 65,  # percentage
        "error_rate": 0.5,  # percentage
        "uptime": 99.9  # percentage
    }

async def _get_top_volunteers(db) -> List[Dict[str, Any]]:
    """Get top performing volunteers"""
    # Would implement actual ranking algorithm
    return [
        {
            "volunteer_id": "mock_id_1",
            "name": "John Doe",
            "total_hours": 120,
            "events_completed": 8,
            "rating": 4.9
        },
        {
            "volunteer_id": "mock_id_2", 
            "name": "Jane Smith",
            "total_hours": 95,
            "events_completed": 6,
            "rating": 4.8
        }
    ]

async def _get_top_organizations(db) -> List[Dict[str, Any]]:
    """Get top performing organizations"""
    # Would implement actual ranking algorithm
    return [
        {
            "organization_id": "mock_org_1",
            "name": "Green Earth Initiative",
            "total_events": 15,
            "volunteer_satisfaction": 4.7,
            "match_success_rate": 92
        },
        {
            "organization_id": "mock_org_2",
            "name": "Community Helpers",
            "total_events": 12,
            "volunteer_satisfaction": 4.6,
            "match_success_rate": 88
        }
    ] 