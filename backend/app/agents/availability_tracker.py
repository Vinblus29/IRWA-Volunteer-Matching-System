import asyncio
import json
from datetime import datetime, timedelta, time
from typing import Dict, Any, List, Optional, Tuple
from ..models.volunteer import Volunteer, Availability
from ..models.event import Event, EventSchedule
from ..services.llm_service import LLMService
from ..services.notification_service import NotificationService
from .base_agent import BaseAgent, AgentMessage, AgentCommunicationProtocol, AgentError
from ..database import get_database
from ..config import settings

class AvailabilityTrackerAgent(BaseAgent):
    """
    Intelligent agent responsible for tracking volunteer availability,
    detecting scheduling conflicts, and optimizing event scheduling.
    """
    
    def __init__(self):
        super().__init__(
            agent_id=AgentCommunicationProtocol.AVAILABILITY_TRACKER,
            name="Availability Tracker Agent",
            version="1.0"
        )
        self.llm_service = None
        self.notification_service = None
        self.db = None
        self.schedule_cache = {}
        
    async def initialize(self):
        """Initialize the availability tracker with required services"""
        try:
            self.llm_service = LLMService()
            self.notification_service = NotificationService()
            self.db = get_database()
            
            # Subscribe to relevant message types
            await self.subscribe_to_events([
                AgentCommunicationProtocol.AVAILABILITY_CHECK_REQUEST
            ])
            
            # Start background tasks
            asyncio.create_task(self._schedule_reminder_task())
            asyncio.create_task(self._conflict_detection_task())
            
            self.logger.info("Availability Tracker Agent initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Availability Tracker Agent: {e}")
            raise AgentError(self.agent_id, f"Initialization failed: {e}")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.llm_service:
            await self.llm_service.cleanup()
        if self.notification_service:
            await self.notification_service.cleanup()
    
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process incoming messages"""
        try:
            if message.message_type == AgentCommunicationProtocol.AVAILABILITY_CHECK_REQUEST:
                return await self._handle_availability_check_request(message)
            else:
                self.logger.warning(f"Unknown message type: {message.message_type}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error processing message {message.id}: {e}")
            return AgentMessage(
                sender=self.agent_id,
                receiver=message.sender,
                message_type=AgentCommunicationProtocol.ERROR,
                payload={"error": str(e), "original_message_id": message.id},
                correlation_id=message.correlation_id
            )
    
    async def _handle_availability_check_request(self, message: AgentMessage) -> AgentMessage:
        """Handle availability check requests"""
        payload = message.payload
        request_type = payload.get("request_type")
        
        if request_type == "check_volunteer_availability":
            result = await self._check_volunteer_availability(payload)
        elif request_type == "detect_conflicts":
            result = await self._detect_scheduling_conflicts(payload)
        elif request_type == "optimize_schedule":
            result = await self._optimize_event_schedule(payload)
        elif request_type == "suggest_alternatives":
            result = await self._suggest_schedule_alternatives(payload)
        elif request_type == "bulk_availability_check":
            result = await self._bulk_availability_check(payload)
        else:
            raise ValueError(f"Unknown request type: {request_type}")
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type=AgentCommunicationProtocol.AVAILABILITY_CHECK_RESPONSE,
            payload=result,
            correlation_id=message.correlation_id
        )
    
    async def _check_volunteer_availability(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Check if a volunteer is available for a specific event"""
        volunteer_id = payload.get("volunteer_id")
        event_id = payload.get("event_id")
        
        # Get volunteer and event data
        volunteer = await self.db.volunteers.find_one({"_id": volunteer_id})
        event = await self.db.events.find_one({"_id": event_id})
        
        if not volunteer or not event:
            return {
                "available": False,
                "reason": "Volunteer or event not found",
                "conflicts": [],
                "suggestions": []
            }
        
        # Check availability against volunteer's schedule
        availability_match = await self._calculate_availability_overlap(
            volunteer.get("availability", []),
            event.get("schedule", {})
        )
        
        # Check for existing commitments
        conflicts = await self._find_scheduling_conflicts(volunteer_id, event)
        
        # Generate AI-powered scheduling insights
        insights = await self._generate_scheduling_insights(volunteer, event, conflicts)
        
        # Calculate availability score
        availability_score = await self._calculate_availability_score(
            availability_match, conflicts, volunteer, event
        )
        
        return {
            "volunteer_id": volunteer_id,
            "event_id": event_id,
            "available": availability_score > 0.6,
            "availability_score": availability_score,
            "overlap_hours": availability_match.get("overlap_hours", 0),
            "conflicts": conflicts,
            "insights": insights,
            "recommendations": await self._generate_scheduling_recommendations(
                volunteer, event, conflicts
            ),
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    
    async def _calculate_availability_overlap(self, volunteer_availability: List[Dict], 
                                            event_schedule: Dict) -> Dict[str, Any]:
        """Calculate overlap between volunteer availability and event schedule"""
        
        if not volunteer_availability or not event_schedule:
            return {"overlap_hours": 0, "overlap_percentage": 0}
        
        event_start_date = datetime.fromisoformat(event_schedule.get("start_date"))
        event_end_date = datetime.fromisoformat(event_schedule.get("end_date"))
        event_start_time = event_schedule.get("start_time")
        event_end_time = event_schedule.get("end_time")
        
        # Convert event time to minutes
        event_start_minutes = self._time_to_minutes(event_start_time)
        event_end_minutes = self._time_to_minutes(event_end_time)
        event_duration_minutes = event_end_minutes - event_start_minutes
        
        # Find matching days
        event_day = event_start_date.strftime("%A").lower()
        
        best_overlap = 0
        matching_availability = None
        
        for avail in volunteer_availability:
            if avail["day"].lower() == event_day:
                vol_start_minutes = self._time_to_minutes(avail["start_time"])
                vol_end_minutes = self._time_to_minutes(avail["end_time"])
                
                # Calculate overlap
                overlap_start = max(event_start_minutes, vol_start_minutes)
                overlap_end = min(event_end_minutes, vol_end_minutes)
                
                if overlap_start < overlap_end:
                    overlap_minutes = overlap_end - overlap_start
                    if overlap_minutes > best_overlap:
                        best_overlap = overlap_minutes
                        matching_availability = avail
        
        overlap_hours = best_overlap / 60
        overlap_percentage = (best_overlap / event_duration_minutes * 100) if event_duration_minutes > 0 else 0
        
        return {
            "overlap_hours": overlap_hours,
            "overlap_percentage": overlap_percentage,
            "matching_availability": matching_availability,
            "event_duration_hours": event_duration_minutes / 60
        }
    
    async def _find_scheduling_conflicts(self, volunteer_id: str, event: Dict) -> List[Dict[str, Any]]:
        """Find scheduling conflicts for a volunteer"""
        conflicts = []
        
        event_start = datetime.fromisoformat(event["schedule"]["start_date"])
        event_end = datetime.fromisoformat(event["schedule"]["end_date"])
        
        # Check for overlapping events the volunteer is already committed to
        existing_matches = await self.db.matches.find({
            "volunteer_id": volunteer_id,
            "status": {"$in": ["accepted", "pending"]}
        }).to_list(None)
        
        for match in existing_matches:
            existing_event = await self.db.events.find_one({"_id": match["event_id"]})
            if existing_event:
                existing_start = datetime.fromisoformat(existing_event["schedule"]["start_date"])
                existing_end = datetime.fromisoformat(existing_event["schedule"]["end_date"])
                
                # Check for date overlap
                if (event_start <= existing_end and event_end >= existing_start):
                    # Check for time overlap
                    time_conflict = await self._check_time_overlap(
                        event["schedule"],
                        existing_event["schedule"]
                    )
                    
                    if time_conflict:
                        conflicts.append({
                            "type": "event_conflict",
                            "conflicting_event_id": str(existing_event["_id"]),
                            "conflicting_event_title": existing_event["title"],
                            "conflict_date": existing_start.isoformat(),
                            "severity": "high" if time_conflict["overlap_hours"] > 2 else "medium",
                            "overlap_hours": time_conflict["overlap_hours"]
                        })
        
        # Check for personal commitments (if stored)
        personal_commitments = await self.db.personal_commitments.find({
            "volunteer_id": volunteer_id,
            "$or": [
                {"date": {"$gte": event_start.date(), "$lte": event_end.date()}}
            ]
        }).to_list(None)
        
        for commitment in personal_commitments:
            conflicts.append({
                "type": "personal_commitment",
                "commitment_title": commitment.get("title", "Personal commitment"),
                "conflict_date": commitment["date"].isoformat(),
                "severity": "medium",
                "details": commitment.get("details", "")
            })
        
        return conflicts
    
    async def _check_time_overlap(self, schedule1: Dict, schedule2: Dict) -> Optional[Dict[str, Any]]:
        """Check if two event schedules have time overlap"""
        
        start1 = self._time_to_minutes(schedule1["start_time"])
        end1 = self._time_to_minutes(schedule1["end_time"])
        start2 = self._time_to_minutes(schedule2["start_time"])
        end2 = self._time_to_minutes(schedule2["end_time"])
        
        overlap_start = max(start1, start2)
        overlap_end = min(end1, end2)
        
        if overlap_start < overlap_end:
            overlap_minutes = overlap_end - overlap_start
            return {
                "has_overlap": True,
                "overlap_hours": overlap_minutes / 60,
                "overlap_start_time": self._minutes_to_time(overlap_start),
                "overlap_end_time": self._minutes_to_time(overlap_end)
            }
        
        return None
    
    async def _generate_scheduling_insights(self, volunteer: Dict, event: Dict, 
                                          conflicts: List[Dict]) -> Dict[str, Any]:
        """Generate AI-powered scheduling insights"""
        
        prompt = f"""
        Analyze the scheduling situation for this volunteer and event:
        
        Volunteer Info:
        - Availability: {volunteer.get('availability', [])}
        - Total events completed: {volunteer.get('events_completed', 0)}
        - Commitment level: {volunteer.get('preferences', {}).get('commitment_level', 'flexible')}
        
        Event Info:
        - Title: {event.get('title', '')}
        - Schedule: {event.get('schedule', {})}
        - Duration: {event.get('schedule', {}).get('start_time', '')} - {event.get('schedule', {}).get('end_time', '')}
        - Urgency: {'High' if event.get('is_urgent') else 'Normal'}
        
        Conflicts: {len(conflicts)} scheduling conflicts found
        
        Provide insights about:
        1. Schedule compatibility
        2. Potential risks or concerns
        3. Optimization opportunities
        4. Volunteer workload assessment
        
        Return JSON with insights and recommendations.
        """
        
        try:
            response = await self.llm_service.generate_response(prompt)
            insights = json.loads(response)
            return insights
        except Exception as e:
            self.logger.error(f"Error generating scheduling insights: {e}")
            return {
                "compatibility": "unknown",
                "risks": ["Unable to analyze schedule"],
                "opportunities": [],
                "workload_assessment": "Unable to assess"
            }
    
    async def _calculate_availability_score(self, availability_match: Dict, 
                                          conflicts: List[Dict], volunteer: Dict, 
                                          event: Dict) -> float:
        """Calculate overall availability score"""
        
        score = 0.0
        
        # Base score from time overlap
        if availability_match["overlap_percentage"] >= 100:
            score += 0.4
        elif availability_match["overlap_percentage"] >= 75:
            score += 0.3
        elif availability_match["overlap_percentage"] >= 50:
            score += 0.2
        elif availability_match["overlap_percentage"] >= 25:
            score += 0.1
        
        # Penalty for conflicts
        high_severity_conflicts = len([c for c in conflicts if c.get("severity") == "high"])
        medium_severity_conflicts = len([c for c in conflicts if c.get("severity") == "medium"])
        
        score -= (high_severity_conflicts * 0.3)
        score -= (medium_severity_conflicts * 0.15)
        
        # Bonus for volunteer commitment level
        commitment_level = volunteer.get("preferences", {}).get("commitment_level", "flexible")
        if commitment_level == "high":
            score += 0.1
        elif commitment_level == "flexible":
            score += 0.05
        
        # Bonus for event urgency match
        if event.get("is_urgent") and commitment_level == "high":
            score += 0.1
        
        # Penalty for overcommitment
        volunteer_workload = await self._assess_volunteer_workload(volunteer["_id"])
        if volunteer_workload > 0.8:  # High workload
            score -= 0.2
        elif volunteer_workload > 0.6:  # Medium workload
            score -= 0.1
        
        return max(0.0, min(1.0, score))
    
    async def _assess_volunteer_workload(self, volunteer_id: str) -> float:
        """Assess current workload of a volunteer (0.0 to 1.0)"""
        
        # Count active commitments in the next 30 days
        future_date = datetime.utcnow() + timedelta(days=30)
        
        active_matches = await self.db.matches.count_documents({
            "volunteer_id": volunteer_id,
            "status": {"$in": ["accepted", "pending"]},
            "created_at": {"$gte": datetime.utcnow() - timedelta(days=7)}
        })
        
        # Simple workload calculation (can be made more sophisticated)
        max_reasonable_events = 8  # per month
        workload = min(1.0, active_matches / max_reasonable_events)
        
        return workload
    
    async def _generate_scheduling_recommendations(self, volunteer: Dict, event: Dict, 
                                                 conflicts: List[Dict]) -> List[str]:
        """Generate scheduling recommendations"""
        recommendations = []
        
        if conflicts:
            recommendations.append("Review scheduling conflicts before confirming")
            
            high_conflicts = [c for c in conflicts if c.get("severity") == "high"]
            if high_conflicts:
                recommendations.append("Consider rescheduling due to high-severity conflicts")
        
        # Check volunteer workload
        workload = await self._assess_volunteer_workload(volunteer["_id"])
        if workload > 0.7:
            recommendations.append("Consider volunteer's current high workload")
        
        # Check event timing
        event_hour = int(event["schedule"]["start_time"].split(":")[0])
        if event_hour < 8 or event_hour > 18:
            recommendations.append("Event is outside typical hours - confirm volunteer availability")
        
        # Check commitment level alignment
        commitment = volunteer.get("preferences", {}).get("commitment_level", "flexible")
        if event.get("is_urgent") and commitment == "low":
            recommendations.append("Urgent event may not align with volunteer's low commitment preference")
        
        if not recommendations:
            recommendations.append("Good schedule alignment - proceed with confidence")
        
        return recommendations
    
    async def _detect_scheduling_conflicts(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Detect scheduling conflicts for multiple volunteers/events"""
        # Implementation for bulk conflict detection
        return {"conflicts_detected": 0, "details": []}
    
    async def _optimize_event_schedule(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize event schedule for better volunteer availability"""
        # Implementation for schedule optimization
        return {"optimized_schedule": {}, "improvement_score": 0.0}
    
    async def _suggest_schedule_alternatives(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest alternative schedules"""
        # Implementation for alternative schedule suggestions
        return {"alternatives": [], "recommendations": []}
    
    async def _bulk_availability_check(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Check availability for multiple volunteers against multiple events"""
        # Implementation for bulk availability checking
        return {"results": [], "summary": {}}
    
    async def _schedule_reminder_task(self):
        """Background task to send scheduling reminders"""
        while self.is_active:
            try:
                # Send reminders for upcoming events
                await self._send_upcoming_event_reminders()
                await asyncio.sleep(3600)  # Check every hour
            except Exception as e:
                self.logger.error(f"Error in reminder task: {e}")
                await asyncio.sleep(3600)
    
    async def _conflict_detection_task(self):
        """Background task to detect and resolve conflicts"""
        while self.is_active:
            try:
                # Detect and notify about conflicts
                await self._detect_and_notify_conflicts()
                await asyncio.sleep(1800)  # Check every 30 minutes
            except Exception as e:
                self.logger.error(f"Error in conflict detection task: {e}")
                await asyncio.sleep(1800)
    
    async def _send_upcoming_event_reminders(self):
        """Send reminders for upcoming events"""
        # Get events happening in the next 24 hours
        tomorrow = datetime.utcnow() + timedelta(days=1)
        
        upcoming_events = await self.db.events.find({
            "schedule.start_date": {
                "$gte": datetime.utcnow().date().isoformat(),
                "$lte": tomorrow.date().isoformat()
            },
            "status": "active"
        }).to_list(None)
        
        for event in upcoming_events:
            # Find volunteers committed to this event
            matches = await self.db.matches.find({
                "event_id": event["_id"],
                "status": "accepted"
            }).to_list(None)
            
            for match in matches:
                await self.notification_service.send_reminder(
                    match["volunteer_id"],
                    "upcoming_event",
                    {
                        "event_title": event["title"],
                        "event_date": event["schedule"]["start_date"],
                        "event_time": event["schedule"]["start_time"]
                    }
                )
    
    async def _detect_and_notify_conflicts(self):
        """Detect conflicts and notify relevant parties"""
        # Implementation for conflict detection and notification
        pass
    
    def _time_to_minutes(self, time_str: str) -> int:
        """Convert HH:MM time string to minutes since midnight"""
        try:
            hours, minutes = map(int, time_str.split(':'))
            return hours * 60 + minutes
        except ValueError:
            return 0
    
    def _minutes_to_time(self, minutes: int) -> str:
        """Convert minutes since midnight to HH:MM format"""
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}" 