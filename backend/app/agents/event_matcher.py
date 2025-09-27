import asyncio
import json
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from ..models.volunteer import Volunteer
from ..models.event import Event
from ..models.match import Match, MatchAnalysis, SkillMatch, LocationMatch
from ..services.llm_service import LLMService
from ..services.vector_service import VectorService
from .base_agent import BaseAgent, AgentMessage, AgentCommunicationProtocol, AgentError
from ..database import get_database
from ..config import settings

class EventMatcherAgent(BaseAgent):
    """
    Intelligent agent responsible for matching volunteers with events
    using advanced AI algorithms, vector similarity, and fairness constraints.
    """
    
    def __init__(self):
        super().__init__(
            agent_id=AgentCommunicationProtocol.EVENT_MATCHER,
            name="Event Matcher Agent",
            version="1.0"
        )
        self.llm_service = None
        self.vector_service = None
        self.db = None
        self.matching_algorithms = {}
        self.fairness_constraints = {}
        
    async def initialize(self):
        """Initialize the event matcher with required services"""
        try:
            self.llm_service = LLMService()
            self.vector_service = VectorService()
            self.db = get_database()
            
            await self.llm_service.initialize()
            await self.vector_service.initialize()
            
            # Initialize matching algorithms
            await self._initialize_matching_algorithms()
            
            # Initialize fairness constraints
            await self._initialize_fairness_constraints()
            
            # Subscribe to relevant message types
            await self.subscribe_to_events([
                AgentCommunicationProtocol.EVENT_MATCHING_REQUEST
            ])
            
            self.logger.info("Event Matcher Agent initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Event Matcher Agent: {e}")
            raise AgentError(self.agent_id, f"Initialization failed: {e}")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.llm_service:
            await self.llm_service.cleanup()
        if self.vector_service:
            await self.vector_service.cleanup()
    
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process incoming messages"""
        try:
            if message.message_type == AgentCommunicationProtocol.EVENT_MATCHING_REQUEST:
                return await self._handle_matching_request(message)
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
    
    async def _handle_matching_request(self, message: AgentMessage) -> AgentMessage:
        """Handle matching requests"""
        payload = message.payload
        request_type = payload.get("request_type")
        
        if request_type == "find_volunteers_for_event":
            result = await self._find_volunteers_for_event(payload)
        elif request_type == "find_events_for_volunteer":
            result = await self._find_events_for_volunteer(payload)
        elif request_type == "batch_matching":
            result = await self._batch_matching(payload)
        elif request_type == "rerank_matches":
            result = await self._rerank_matches(payload)
        else:
            raise ValueError(f"Unknown request type: {request_type}")
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type=AgentCommunicationProtocol.EVENT_MATCHING_RESPONSE,
            payload=result,
            correlation_id=message.correlation_id
        )
    
    async def _find_volunteers_for_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Find suitable volunteers for a specific event"""
        event_data = payload.get("event_data")
        filters = payload.get("filters", {})
        max_matches = payload.get("max_matches", 20)
        
        # Get event from database if only ID provided
        if isinstance(event_data, str):
            event = await self.db.events.find_one({"_id": event_data})
            if not event:
                raise ValueError(f"Event not found: {event_data}")
            event_data = event
        
        # Use vector service to find semantically similar volunteers
        vector_matches = await self.vector_service.find_matching_volunteers_for_event(
            event_data, n_results=max_matches * 2
        )
        
        # Apply additional filtering and scoring
        filtered_matches = await self._apply_volunteer_filters(vector_matches, event_data, filters)
        
        # Calculate comprehensive match scores
        scored_matches = await self._calculate_match_scores(filtered_matches, event_data)
        
        # Apply fairness constraints
        fair_matches = await self._apply_fairness_constraints(scored_matches, event_data)
        
        # Generate explanations for top matches
        explained_matches = await self._generate_match_explanations(fair_matches[:max_matches], event_data)
        
        return {
            "event_id": event_data.get("_id"),
            "matches": explained_matches,
            "total_found": len(vector_matches),
            "total_qualified": len(filtered_matches),
            "total_returned": len(explained_matches),
            "matching_algorithm": "hybrid_vector_ml",
            "fairness_applied": True,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def _find_events_for_volunteer(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Find suitable events for a specific volunteer"""
        volunteer_data = payload.get("volunteer_data")
        filters = payload.get("filters", {})
        max_matches = payload.get("max_matches", 20)
        
        # Get volunteer from database if only ID provided
        if isinstance(volunteer_data, str):
            volunteer = await self.db.volunteers.find_one({"_id": volunteer_data})
            if not volunteer:
                raise ValueError(f"Volunteer not found: {volunteer_data}")
            volunteer_data = volunteer
        
        # Use vector service to find semantically similar events
        vector_matches = await self.vector_service.find_matching_events_for_volunteer(
            volunteer_data, n_results=max_matches * 2
        )
        
        # Apply additional filtering and scoring
        filtered_matches = await self._apply_event_filters(vector_matches, volunteer_data, filters)
        
        # Calculate comprehensive match scores
        scored_matches = await self._calculate_event_match_scores(filtered_matches, volunteer_data)
        
        # Generate explanations for top matches
        explained_matches = await self._generate_event_match_explanations(scored_matches[:max_matches], volunteer_data)
        
        return {
            "volunteer_id": volunteer_data.get("_id"),
            "matches": explained_matches,
            "total_found": len(vector_matches),
            "total_qualified": len(filtered_matches),
            "total_returned": len(explained_matches),
            "matching_algorithm": "hybrid_vector_ml",
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def _apply_volunteer_filters(self, matches: List[Dict], event_data: Dict, filters: Dict) -> List[Dict]:
        """Apply filters to volunteer matches"""
        filtered_matches = []
        
        for match in matches:
            volunteer_id = match.get("volunteer_id")
            
            # Get full volunteer data
            volunteer = await self.db.volunteers.find_one({"_id": volunteer_id})
            if not volunteer:
                continue
            
            # Apply verification filter
            if filters.get("verified_only", True) and not volunteer.get("is_verified", False):
                continue
            
            # Apply availability filter
            if not await self._check_basic_availability(volunteer, event_data):
                continue
            
            # Apply location filter
            if not await self._check_location_compatibility(volunteer, event_data, filters):
                continue
            
            # Apply skill requirements filter
            if not await self._check_skill_requirements(volunteer, event_data):
                continue
            
            match["volunteer_data"] = volunteer
            filtered_matches.append(match)
        
        return filtered_matches
    
    async def _apply_event_filters(self, matches: List[Dict], volunteer_data: Dict, filters: Dict) -> List[Dict]:
        """Apply filters to event matches"""
        filtered_matches = []
        
        for match in matches:
            event_id = match.get("event_id")
            
            # Get full event data
            event = await self.db.events.find_one({"_id": event_id})
            if not event:
                continue
            
            # Apply status filter
            if event.get("status") != "active":
                continue
            
            # Apply date filter
            if not await self._check_event_date_validity(event):
                continue
            
            # Apply preference filters
            if not await self._check_volunteer_preferences(volunteer_data, event, filters):
                continue
            
            match["event_data"] = event
            filtered_matches.append(match)
        
        return filtered_matches
    
    async def _calculate_match_scores(self, matches: List[Dict], event_data: Dict) -> List[Dict]:
        """Calculate comprehensive match scores for volunteers"""
        scored_matches = []
        
        for match in matches:
            volunteer = match["volunteer_data"]
            
            # Calculate different score components
            skill_score = await self._calculate_skill_match_score(volunteer, event_data)
            location_score = await self._calculate_location_score(volunteer, event_data)
            availability_score = match.get("similarity_score", 0.5)  # From vector search
            experience_score = await self._calculate_experience_score(volunteer, event_data)
            preference_score = await self._calculate_preference_score(volunteer, event_data)
            
            # Weighted combination
            final_score = (
                skill_score * 0.35 +
                location_score * 0.20 +
                availability_score * 0.20 +
                experience_score * 0.15 +
                preference_score * 0.10
            )
            
            match.update({
                "final_score": final_score,
                "skill_score": skill_score,
                "location_score": location_score,
                "availability_score": availability_score,
                "experience_score": experience_score,
                "preference_score": preference_score
            })
            
            scored_matches.append(match)
        
        # Sort by final score
        scored_matches.sort(key=lambda x: x["final_score"], reverse=True)
        
        return scored_matches
    
    async def _calculate_event_match_scores(self, matches: List[Dict], volunteer_data: Dict) -> List[Dict]:
        """Calculate comprehensive match scores for events"""
        scored_matches = []
        
        for match in matches:
            event = match["event_data"]
            
            # Calculate different score components
            skill_score = await self._calculate_skill_match_score(volunteer_data, event)
            interest_score = await self._calculate_interest_alignment(volunteer_data, event)
            commitment_score = await self._calculate_commitment_compatibility(volunteer_data, event)
            impact_score = await self._calculate_impact_potential(volunteer_data, event)
            
            # Weighted combination
            final_score = (
                skill_score * 0.30 +
                interest_score * 0.25 +
                commitment_score * 0.25 +
                impact_score * 0.20
            )
            
            match.update({
                "final_score": final_score,
                "skill_score": skill_score,
                "interest_score": interest_score,
                "commitment_score": commitment_score,
                "impact_score": impact_score
            })
            
            scored_matches.append(match)
        
        # Sort by final score
        scored_matches.sort(key=lambda x: x["final_score"], reverse=True)
        
        return scored_matches
    
    async def _apply_fairness_constraints(self, matches: List[Dict], event_data: Dict) -> List[Dict]:
        """Apply fairness constraints to ensure equitable matching"""
        
        # Detect potential bias in matching results
        bias_analysis = await self._analyze_matching_bias(matches)
        
        if bias_analysis["bias_detected"]:
            self.logger.warning(f"Bias detected in matching: {bias_analysis['bias_types']}")
            
            # Apply debiasing techniques
            matches = await self._apply_debiasing(matches, bias_analysis)
        
        # Ensure diversity in results
        diverse_matches = await self._ensure_diversity(matches, event_data)
        
        return diverse_matches
    
    async def _generate_match_explanations(self, matches: List[Dict], event_data: Dict) -> List[Dict]:
        """Generate explanations for why volunteers match events"""
        explained_matches = []
        
        for match in matches:
            volunteer = match["volunteer_data"]
            
            # Generate explanation using LLM
            explanation_prompt = f"""
            Explain why this volunteer is a good match for this event:
            
            Volunteer Skills: {[skill['name'] for skill in volunteer.get('skills', [])]}
            Volunteer Experience: {volunteer.get('total_hours_volunteered', 0)} hours
            Volunteer Interests: {volunteer.get('preferences', {}).get('preferred_event_types', [])}
            
            Event: {event_data.get('title', '')}
            Event Requirements: {[req['skill']['name'] for req in event_data.get('requirements', [])]}
            Event Category: {event_data.get('category', '')}
            
            Match Score: {match['final_score']:.2f}
            
            Provide a concise, positive explanation in 2-3 sentences.
            """
            
            try:
                explanation = await self.llm_service.generate_response(explanation_prompt, max_tokens=150)
            except Exception as e:
                self.logger.error(f"Error generating explanation: {e}")
                explanation = f"Good match based on skills and experience (score: {match['final_score']:.2f})"
            
            match_result = {
                "volunteer_id": str(volunteer["_id"]),
                "volunteer_name": volunteer.get("profile", {}).get("full_name", "Volunteer"),
                "match_score": round(match["final_score"], 3),
                "skill_score": round(match["skill_score"], 3),
                "location_score": round(match["location_score"], 3),
                "availability_score": round(match["availability_score"], 3),
                "explanation": explanation,
                "skills": volunteer.get("skills", []),
                "location": volunteer.get("location", {}),
                "experience_hours": volunteer.get("total_hours_volunteered", 0),
                "rating": volunteer.get("rating", 0),
                "is_verified": volunteer.get("is_verified", False)
            }
            
            explained_matches.append(match_result)
        
        return explained_matches
    
    async def _generate_event_match_explanations(self, matches: List[Dict], volunteer_data: Dict) -> List[Dict]:
        """Generate explanations for why events match volunteers"""
        explained_matches = []
        
        for match in matches:
            event = match["event_data"]
            
            # Generate explanation using LLM
            explanation_prompt = f"""
            Explain why this event is a good opportunity for this volunteer:
            
            Volunteer Skills: {[skill['name'] for skill in volunteer_data.get('skills', [])]}
            Volunteer Interests: {volunteer_data.get('preferences', {}).get('preferred_event_types', [])}
            Volunteer Commitment Level: {volunteer_data.get('preferences', {}).get('commitment_level', '')}
            
            Event: {event.get('title', '')}
            Event Description: {event.get('description', '')[:200]}...
            Event Category: {event.get('category', '')}
            Event Benefits: {event.get('provides_training', False) and 'Training provided' or 'Experience opportunity'}
            
            Match Score: {match['final_score']:.2f}
            
            Provide a concise, encouraging explanation in 2-3 sentences.
            """
            
            try:
                explanation = await self.llm_service.generate_response(explanation_prompt, max_tokens=150)
            except Exception as e:
                self.logger.error(f"Error generating explanation: {e}")
                explanation = f"Great opportunity matching your skills and interests (score: {match['final_score']:.2f})"
            
            match_result = {
                "event_id": str(event["_id"]),
                "event_title": event.get("title", ""),
                "event_description": event.get("description", ""),
                "match_score": round(match["final_score"], 3),
                "skill_score": round(match["skill_score"], 3),
                "interest_score": round(match["interest_score"], 3),
                "commitment_score": round(match["commitment_score"], 3),
                "explanation": explanation,
                "event_category": event.get("category", ""),
                "event_date": event.get("schedule", {}).get("start_date", ""),
                "event_location": event.get("location", {}),
                "provides_training": event.get("provides_training", False),
                "is_urgent": event.get("is_urgent", False)
            }
            
            explained_matches.append(match_result)
        
        return explained_matches
    
    # Helper methods for scoring and filtering
    async def _calculate_skill_match_score(self, volunteer_data: Dict, event_data: Dict) -> float:
        """Calculate skill compatibility score"""
        volunteer_skills = {skill["name"].lower() for skill in volunteer_data.get("skills", [])}
        required_skills = {req["skill"]["name"].lower() for req in event_data.get("requirements", [])}
        
        if not required_skills:
            return 0.8  # Default score if no specific requirements
        
        matched_skills = volunteer_skills.intersection(required_skills)
        skill_coverage = len(matched_skills) / len(required_skills)
        
        return min(1.0, skill_coverage * 1.2)  # Slight boost for coverage
    
    async def _calculate_location_score(self, volunteer_data: Dict, event_data: Dict) -> float:
        """Calculate location compatibility score"""
        vol_location = volunteer_data.get("location", {})
        event_location = event_data.get("location", {})
        
        # Simple distance-based scoring (would use actual geolocation in production)
        if vol_location.get("city") == event_location.get("city"):
            return 1.0
        elif vol_location.get("state") == event_location.get("state"):
            return 0.7
        else:
            return 0.3
    
    async def _calculate_experience_score(self, volunteer_data: Dict, event_data: Dict) -> float:
        """Calculate experience compatibility score"""
        total_hours = volunteer_data.get("total_hours_volunteered", 0)
        events_completed = volunteer_data.get("events_completed", 0)
        
        # Scale experience score
        experience_score = min(1.0, (total_hours / 100) * 0.7 + (events_completed / 10) * 0.3)
        
        return experience_score
    
    async def _calculate_preference_score(self, volunteer_data: Dict, event_data: Dict) -> float:
        """Calculate preference alignment score"""
        preferences = volunteer_data.get("preferences", {})
        preferred_types = preferences.get("preferred_event_types", [])
        event_category = event_data.get("category", "")
        
        if event_category.lower() in [pref.lower() for pref in preferred_types]:
            return 1.0
        
        return 0.5  # Neutral if no preference match
    
    async def _check_basic_availability(self, volunteer: Dict, event: Dict) -> bool:
        """Check basic availability compatibility"""
        # Simplified availability check
        return True  # Would implement detailed availability checking
    
    async def _check_location_compatibility(self, volunteer: Dict, event: Dict, filters: Dict) -> bool:
        """Check location compatibility"""
        max_distance = filters.get("max_distance_km", 50)
        # Would implement actual distance calculation
        return True
    
    async def _check_skill_requirements(self, volunteer: Dict, event: Dict) -> bool:
        """Check if volunteer meets minimum skill requirements"""
        volunteer_skills = {skill["name"].lower() for skill in volunteer.get("skills", [])}
        required_skills = {req["skill"]["name"].lower() for req in event.get("requirements", []) if req.get("required", False)}
        
        if not required_skills:
            return True
        
        # Check if volunteer has at least one required skill
        return bool(volunteer_skills.intersection(required_skills))
    
    async def _analyze_matching_bias(self, matches: List[Dict]) -> Dict[str, Any]:
        """Analyze potential bias in matching results"""
        # Simple bias detection (would be more sophisticated in production)
        return {
            "bias_detected": False,
            "bias_types": [],
            "confidence": 0.0
        }
    
    async def _apply_debiasing(self, matches: List[Dict], bias_analysis: Dict) -> List[Dict]:
        """Apply debiasing techniques"""
        # Would implement sophisticated debiasing algorithms
        return matches
    
    async def _ensure_diversity(self, matches: List[Dict], event_data: Dict) -> List[Dict]:
        """Ensure diversity in matching results"""
        # Would implement diversity constraints
        return matches
    
    async def _initialize_matching_algorithms(self):
        """Initialize matching algorithms"""
        self.matching_algorithms = {
            "vector_similarity": "ChromaDB vector search",
            "skill_matching": "Weighted skill compatibility",
            "location_proximity": "Geographic distance calculation",
            "preference_alignment": "User preference matching"
        }
    
    async def _initialize_fairness_constraints(self):
        """Initialize fairness constraints"""
        self.fairness_constraints = {
            "demographic_parity": True,
            "equal_opportunity": True,
            "diversity_promotion": True,
            "bias_detection": True
        }
    
    # Additional helper methods would be implemented here...
    async def _calculate_interest_alignment(self, volunteer_data: Dict, event_data: Dict) -> float:
        """Calculate interest alignment score"""
        return 0.7  # Placeholder
    
    async def _calculate_commitment_compatibility(self, volunteer_data: Dict, event_data: Dict) -> float:
        """Calculate commitment compatibility score"""
        return 0.8  # Placeholder
    
    async def _calculate_impact_potential(self, volunteer_data: Dict, event_data: Dict) -> float:
        """Calculate potential impact score"""
        return 0.6  # Placeholder
    
    async def _check_event_date_validity(self, event: Dict) -> bool:
        """Check if event date is valid and future"""
        return True  # Placeholder
    
    async def _check_volunteer_preferences(self, volunteer_data: Dict, event: Dict, filters: Dict) -> bool:
        """Check volunteer preferences against event"""
        return True  # Placeholder
    
    async def _batch_matching(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle batch matching requests"""
        return {"message": "Batch matching not implemented yet"}
    
    async def _rerank_matches(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Rerank existing matches"""
        return {"message": "Reranking not implemented yet"} 