import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import openai
from ..models.volunteer import Skill, Volunteer
from ..models.event import Event, EventRequirement
from ..services.llm_service import LLMService
from ..services.nlp_service import NLPService
from .base_agent import BaseAgent, AgentMessage, AgentCommunicationProtocol, AgentError
from ..config import settings

class SkillProfilerAgent(BaseAgent):
    """
    Intelligent agent responsible for analyzing and profiling volunteer skills.
    Uses NLP and LLM capabilities to extract, categorize, and match skills.
    """
    
    def __init__(self):
        super().__init__(
            agent_id=AgentCommunicationProtocol.SKILL_PROFILER,
            name="Skill Profiler Agent",
            version="1.0"
        )
        self.llm_service = None
        self.nlp_service = None
        self.skill_taxonomy = {}
        self.skill_synonyms = {}
        
    async def initialize(self):
        """Initialize the skill profiler with LLM and NLP services"""
        try:
            self.llm_service = LLMService()
            self.nlp_service = NLPService()
            
            # Load skill taxonomy and synonyms
            await self._load_skill_taxonomy()
            await self._load_skill_synonyms()
            
            # Subscribe to relevant message types
            await self.subscribe_to_events([
                AgentCommunicationProtocol.SKILL_ANALYSIS_REQUEST
            ])
            
            self.logger.info("Skill Profiler Agent initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Skill Profiler Agent: {e}")
            raise AgentError(self.agent_id, f"Initialization failed: {e}")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.llm_service:
            await self.llm_service.cleanup()
        if self.nlp_service:
            await self.nlp_service.cleanup()
    
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process incoming messages"""
        try:
            if message.message_type == AgentCommunicationProtocol.SKILL_ANALYSIS_REQUEST:
                return await self._handle_skill_analysis_request(message)
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
    
    async def _handle_skill_analysis_request(self, message: AgentMessage) -> AgentMessage:
        """Handle skill analysis requests"""
        payload = message.payload
        analysis_type = payload.get("analysis_type")
        
        if analysis_type == "volunteer_skills":
            result = await self._analyze_volunteer_skills(payload.get("volunteer_data"))
        elif analysis_type == "event_requirements":
            result = await self._analyze_event_requirements(payload.get("event_data"))
        elif analysis_type == "skill_matching":
            result = await self._match_skills(
                payload.get("volunteer_skills"),
                payload.get("required_skills")
            )
        elif analysis_type == "skill_extraction":
            result = await self._extract_skills_from_text(payload.get("text"))
        else:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type=AgentCommunicationProtocol.SKILL_ANALYSIS_RESPONSE,
            payload=result,
            correlation_id=message.correlation_id
        )
    
    async def _analyze_volunteer_skills(self, volunteer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and enhance volunteer skill profiles"""
        volunteer_id = volunteer_data.get("volunteer_id")
        skills = volunteer_data.get("skills", [])
        bio = volunteer_data.get("bio", "")
        
        # Extract additional skills from bio using NLP
        extracted_skills = await self._extract_skills_from_text(bio)
        
        # Enhance existing skills with AI insights
        enhanced_skills = []
        for skill in skills:
            enhanced_skill = await self._enhance_skill_profile(skill)
            enhanced_skills.append(enhanced_skill)
        
        # Merge extracted skills with existing ones
        merged_skills = await self._merge_skills(enhanced_skills, extracted_skills)
        
        # Generate skill recommendations
        recommendations = await self._generate_skill_recommendations(merged_skills)
        
        # Calculate skill profile completeness
        completeness_score = await self._calculate_profile_completeness(merged_skills)
        
        return {
            "volunteer_id": volunteer_id,
            "enhanced_skills": merged_skills,
            "extracted_skills": extracted_skills,
            "recommendations": recommendations,
            "completeness_score": completeness_score,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "agent_version": self.version
        }
    
    async def _analyze_event_requirements(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze event skill requirements and suggest improvements"""
        event_id = event_data.get("event_id")
        description = event_data.get("description", "")
        requirements = event_data.get("requirements", [])
        
        # Extract skills from event description
        extracted_skills = await self._extract_skills_from_text(description)
        
        # Analyze existing requirements
        analyzed_requirements = []
        for req in requirements:
            analyzed_req = await self._analyze_skill_requirement(req)
            analyzed_requirements.append(analyzed_req)
        
        # Suggest missing skill requirements
        suggested_skills = await self._suggest_missing_requirements(
            description, analyzed_requirements
        )
        
        # Generate requirement optimization suggestions
        optimizations = await self._optimize_requirements(analyzed_requirements)
        
        return {
            "event_id": event_id,
            "analyzed_requirements": analyzed_requirements,
            "extracted_skills": extracted_skills,
            "suggested_skills": suggested_skills,
            "optimizations": optimizations,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "agent_version": self.version
        }
    
    async def _match_skills(self, volunteer_skills: List[Dict], required_skills: List[Dict]) -> Dict[str, Any]:
        """Match volunteer skills against event requirements"""
        matches = []
        unmatched_requirements = []
        volunteer_surplus = []
        
        # Create skill mapping using LLM for semantic matching
        skill_matches = await self._semantic_skill_matching(volunteer_skills, required_skills)
        
        for req_skill in required_skills:
            best_match = await self._find_best_skill_match(req_skill, volunteer_skills, skill_matches)
            
            if best_match:
                match_score = await self._calculate_match_score(req_skill, best_match)
                matches.append({
                    "required_skill": req_skill,
                    "volunteer_skill": best_match,
                    "match_score": match_score,
                    "match_type": best_match["match_type"],
                    "confidence": best_match["confidence"]
                })
            else:
                unmatched_requirements.append(req_skill)
        
        # Find surplus volunteer skills
        matched_volunteer_skills = {match["volunteer_skill"]["name"] for match in matches}
        volunteer_surplus = [
            skill for skill in volunteer_skills 
            if skill["name"] not in matched_volunteer_skills
        ]
        
        # Calculate overall match quality
        overall_score = await self._calculate_overall_match_score(matches, required_skills)
        
        return {
            "matches": matches,
            "unmatched_requirements": unmatched_requirements,
            "volunteer_surplus": volunteer_surplus,
            "overall_match_score": overall_score,
            "total_required_skills": len(required_skills),
            "total_matched_skills": len(matches),
            "match_percentage": len(matches) / len(required_skills) * 100 if required_skills else 0,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    
    async def _extract_skills_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract skills from free text using NLP and LLM"""
        if not text.strip():
            return []
        
        # Use NLP service for named entity recognition
        entities = await self.nlp_service.extract_entities(text)
        
        # Use LLM for semantic skill extraction
        prompt = f"""
        Analyze the following text and extract any skills, competencies, or abilities mentioned.
        Focus on technical skills, soft skills, certifications, and professional experience.
        
        Text: {text}
        
        Return the results as a JSON array of skills with the following structure:
        [
            {{
                "name": "skill_name",
                "category": "technical|soft|certification|experience",
                "confidence": 0.0-1.0,
                "context": "relevant_context_from_text"
            }}
        ]
        """
        
        try:
            llm_response = await self.llm_service.generate_response(prompt)
            extracted_skills = json.loads(llm_response)
            
            # Enhance with NLP entities
            enhanced_skills = await self._enhance_with_nlp_entities(extracted_skills, entities)
            
            # Normalize and categorize skills
            normalized_skills = await self._normalize_skills(enhanced_skills)
            
            return normalized_skills
            
        except Exception as e:
            self.logger.error(f"Error extracting skills from text: {e}")
            return []
    
    async def _enhance_skill_profile(self, skill: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance a skill profile with AI insights"""
        skill_name = skill.get("name", "")
        skill_level = skill.get("level", "")
        years_experience = skill.get("years_experience", 0)
        
        # Get skill categorization and standardization
        enhanced_skill = await self._standardize_skill(skill_name)
        
        # Validate skill level against experience
        validated_level = await self._validate_skill_level(skill_level, years_experience)
        
        # Generate skill improvement suggestions
        improvements = await self._suggest_skill_improvements(skill_name, skill_level)
        
        # Find related skills
        related_skills = await self._find_related_skills(skill_name)
        
        return {
            "name": enhanced_skill["standardized_name"],
            "original_name": skill_name,
            "level": validated_level,
            "years_experience": years_experience,
            "category": enhanced_skill["category"],
            "subcategory": enhanced_skill["subcategory"],
            "certifications": skill.get("certifications", []),
            "improvements": improvements,
            "related_skills": related_skills,
            "market_demand": enhanced_skill.get("market_demand", "unknown"),
            "confidence": enhanced_skill.get("confidence", 0.8)
        }
    
    async def _semantic_skill_matching(self, volunteer_skills: List[Dict], required_skills: List[Dict]) -> Dict[str, Any]:
        """Perform semantic skill matching using LLM"""
        prompt = f"""
        Perform semantic matching between volunteer skills and required skills.
        Consider synonyms, related skills, skill hierarchies, and transferable skills.
        
        Volunteer Skills: {json.dumps(volunteer_skills, indent=2)}
        Required Skills: {json.dumps(required_skills, indent=2)}
        
        Return a JSON object mapping each required skill to potential volunteer skill matches:
        {{
            "required_skill_name": [
                {{
                    "volunteer_skill": "skill_name",
                    "match_type": "exact|semantic|transferable|related",
                    "confidence": 0.0-1.0,
                    "reasoning": "explanation"
                }}
            ]
        }}
        """
        
        try:
            response = await self.llm_service.generate_response(prompt)
            return json.loads(response)
        except Exception as e:
            self.logger.error(f"Error in semantic skill matching: {e}")
            return {}
    
    async def _load_skill_taxonomy(self):
        """Load skill taxonomy for categorization"""
        # In a real implementation, this would load from a database or file
        self.skill_taxonomy = {
            "technical": {
                "programming": ["python", "javascript", "java", "c++", "react", "nodejs"],
                "data_analysis": ["sql", "excel", "tableau", "power_bi", "r", "statistics"],
                "design": ["photoshop", "illustrator", "figma", "sketch", "ui_design", "ux_design"],
                "marketing": ["seo", "sem", "social_media", "content_marketing", "analytics"]
            },
            "soft": {
                "communication": ["public_speaking", "writing", "presentation", "negotiation"],
                "leadership": ["team_management", "project_management", "mentoring", "coaching"],
                "interpersonal": ["teamwork", "collaboration", "empathy", "customer_service"]
            },
            "domain": {
                "healthcare": ["nursing", "first_aid", "cpr", "medical_assistance"],
                "education": ["teaching", "tutoring", "curriculum_development", "child_care"],
                "environment": ["conservation", "sustainability", "gardening", "wildlife_protection"],
                "social_services": ["counseling", "social_work", "community_outreach", "advocacy"]
            }
        }
    
    async def _load_skill_synonyms(self):
        """Load skill synonyms for better matching"""
        self.skill_synonyms = {
            "programming": ["coding", "software_development", "development"],
            "javascript": ["js", "node", "nodejs"],
            "photoshop": ["ps", "photo_editing", "image_editing"],
            "public_speaking": ["presentation", "speaking", "oratory"],
            "project_management": ["pm", "project_coordination", "project_planning"]
        }
    
    async def _standardize_skill(self, skill_name: str) -> Dict[str, Any]:
        """Standardize skill name and categorize it"""
        skill_lower = skill_name.lower().replace(" ", "_")
        
        # Check for exact matches in taxonomy
        for category, subcategories in self.skill_taxonomy.items():
            for subcategory, skills in subcategories.items():
                if skill_lower in skills:
                    return {
                        "standardized_name": skill_lower,
                        "category": category,
                        "subcategory": subcategory,
                        "confidence": 1.0
                    }
        
        # Check for synonyms
        for standard_skill, synonyms in self.skill_synonyms.items():
            if skill_lower in synonyms:
                # Find the category for the standard skill
                for category, subcategories in self.skill_taxonomy.items():
                    for subcategory, skills in subcategories.items():
                        if standard_skill in skills:
                            return {
                                "standardized_name": standard_skill,
                                "category": category,
                                "subcategory": subcategory,
                                "confidence": 0.9
                            }
        
        # If no match found, use LLM for categorization
        return await self._llm_categorize_skill(skill_name)
    
    async def _llm_categorize_skill(self, skill_name: str) -> Dict[str, Any]:
        """Use LLM to categorize an unknown skill"""
        prompt = f"""
        Categorize the skill "{skill_name}" into one of these categories:
        - technical (programming, data_analysis, design, marketing)
        - soft (communication, leadership, interpersonal)
        - domain (healthcare, education, environment, social_services)
        
        Return JSON:
        {{
            "standardized_name": "standardized_skill_name",
            "category": "category",
            "subcategory": "subcategory", 
            "confidence": 0.0-1.0
        }}
        """
        
        try:
            response = await self.llm_service.generate_response(prompt)
            return json.loads(response)
        except Exception as e:
            self.logger.error(f"Error categorizing skill {skill_name}: {e}")
            return {
                "standardized_name": skill_name.lower().replace(" ", "_"),
                "category": "unknown",
                "subcategory": "unknown",
                "confidence": 0.5
            }
    
    async def _validate_skill_level(self, level: str, years_experience: int) -> str:
        """Validate skill level against years of experience"""
        level_mapping = {
            "beginner": (0, 2),
            "intermediate": (1, 5),
            "advanced": (3, 10),
            "expert": (5, float('inf'))
        }
        
        if level.lower() not in level_mapping:
            return "intermediate"  # Default
        
        min_years, max_years = level_mapping[level.lower()]
        
        if years_experience < min_years:
            # Suggest lower level
            for lvl, (min_yr, max_yr) in level_mapping.items():
                if min_yr <= years_experience <= max_yr:
                    return lvl
        
        return level.lower()
    
    async def _calculate_match_score(self, required_skill: Dict, volunteer_skill: Dict) -> float:
        """Calculate match score between required and volunteer skill"""
        # Base score from semantic matching confidence
        base_score = volunteer_skill.get("confidence", 0.5)
        
        # Adjust for skill level compatibility
        level_score = await self._calculate_level_compatibility(
            required_skill.get("level", "intermediate"),
            volunteer_skill.get("level", "beginner")
        )
        
        # Adjust for experience
        experience_score = await self._calculate_experience_score(
            required_skill.get("min_years_experience", 0),
            volunteer_skill.get("years_experience", 0)
        )
        
        # Weighted final score
        final_score = (base_score * 0.4) + (level_score * 0.35) + (experience_score * 0.25)
        
        return min(1.0, max(0.0, final_score))
    
    async def _calculate_level_compatibility(self, required_level: str, volunteer_level: str) -> float:
        """Calculate compatibility between skill levels"""
        level_values = {"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}
        
        req_value = level_values.get(required_level.lower(), 2)
        vol_value = level_values.get(volunteer_level.lower(), 1)
        
        if vol_value >= req_value:
            return 1.0
        elif vol_value == req_value - 1:
            return 0.8
        elif vol_value == req_value - 2:
            return 0.5
        else:
            return 0.2
    
    async def _calculate_experience_score(self, required_years: int, volunteer_years: int) -> float:
        """Calculate score based on years of experience"""
        if volunteer_years >= required_years:
            return 1.0
        elif volunteer_years >= required_years * 0.75:
            return 0.8
        elif volunteer_years >= required_years * 0.5:
            return 0.6
        else:
            return 0.3 