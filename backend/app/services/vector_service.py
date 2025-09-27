import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import json
import asyncio
from ..config import settings

logger = logging.getLogger(__name__)

class VectorService:
    """Service for vector embeddings and semantic search using ChromaDB and SentenceTransformers"""
    
    def __init__(self):
        self.model = None
        self.chroma_client = None
        self.collections = {}
        self.is_initialized = False
        self.embedding_dimension = 384  # all-MiniLM-L6-v2 dimension
        
    async def initialize(self):
        """Initialize the vector service"""
        try:
            # Initialize sentence transformer model
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize ChromaDB client
            self.chroma_client = chromadb.Client(Settings(
                persist_directory="./data/chromadb",
                is_persistent=True
            ))
            
            # Create collections for different data types
            await self._create_collections()
            
            self.is_initialized = True
            logger.info("Vector Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Vector Service: {e}")
            raise
    
    async def _create_collections(self):
        """Create ChromaDB collections for different data types"""
        try:
            # Volunteers collection
            self.collections['volunteers'] = self.chroma_client.get_or_create_collection(
                name="volunteers",
                metadata={"description": "Volunteer profiles and skills"}
            )
            
            # Events collection
            self.collections['events'] = self.chroma_client.get_or_create_collection(
                name="events",
                metadata={"description": "Event descriptions and requirements"}
            )
            
            # Skills collection
            self.collections['skills'] = self.chroma_client.get_or_create_collection(
                name="skills",
                metadata={"description": "Skill descriptions and categories"}
            )
            
            logger.info("Created ChromaDB collections")
            
        except Exception as e:
            logger.error(f"Error creating collections: {e}")
            raise
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Clean and preprocess text
            cleaned_text = self._preprocess_text(text)
            
            # Generate embedding
            embedding = self.model.encode(cleaned_text, normalize_embeddings=True)
            
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return [0.0] * self.embedding_dimension
    
    async def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Clean and preprocess texts
            cleaned_texts = [self._preprocess_text(text) for text in texts]
            
            # Generate embeddings in batch
            embeddings = self.model.encode(cleaned_texts, normalize_embeddings=True)
            
            return embeddings.tolist()
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            return [[0.0] * self.embedding_dimension] * len(texts)
    
    async def add_volunteer_profile(self, volunteer_id: str, volunteer_data: Dict[str, Any]):
        """Add volunteer profile to vector database"""
        try:
            # Create text representation of volunteer
            volunteer_text = self._create_volunteer_text(volunteer_data)
            
            # Generate embedding
            embedding = await self.generate_embedding(volunteer_text)
            
            # Add to collection
            self.collections['volunteers'].add(
                embeddings=[embedding],
                documents=[volunteer_text],
                metadatas=[{
                    "volunteer_id": volunteer_id,
                    "skills": json.dumps(volunteer_data.get("skills", [])),
                    "location": json.dumps(volunteer_data.get("location", {})),
                    "created_at": volunteer_data.get("created_at", "")
                }],
                ids=[volunteer_id]
            )
            
            logger.debug(f"Added volunteer profile {volunteer_id} to vector database")
            
        except Exception as e:
            logger.error(f"Error adding volunteer profile: {e}")
    
    async def add_event_profile(self, event_id: str, event_data: Dict[str, Any]):
        """Add event profile to vector database"""
        try:
            # Create text representation of event
            event_text = self._create_event_text(event_data)
            
            # Generate embedding
            embedding = await self.generate_embedding(event_text)
            
            # Add to collection
            self.collections['events'].add(
                embeddings=[embedding],
                documents=[event_text],
                metadatas=[{
                    "event_id": event_id,
                    "title": event_data.get("title", ""),
                    "category": event_data.get("category", ""),
                    "requirements": json.dumps(event_data.get("requirements", [])),
                    "location": json.dumps(event_data.get("location", {})),
                    "created_at": event_data.get("created_at", "")
                }],
                ids=[event_id]
            )
            
            logger.debug(f"Added event profile {event_id} to vector database")
            
        except Exception as e:
            logger.error(f"Error adding event profile: {e}")
    
    async def search_similar_volunteers(self, query_text: str, n_results: int = 10,
                                      filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for similar volunteers based on query text"""
        try:
            # Generate query embedding
            query_embedding = await self.generate_embedding(query_text)
            
            # Prepare where clause for filtering
            where_clause = self._prepare_where_clause(filters) if filters else None
            
            # Search in volunteers collection
            results = self.collections['volunteers'].query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            formatted_results = []
            if results['ids']:
                for i, volunteer_id in enumerate(results['ids'][0]):
                    formatted_results.append({
                        "volunteer_id": volunteer_id,
                        "similarity_score": 1 - results['distances'][0][i],  # Convert distance to similarity
                        "document": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i]
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching similar volunteers: {e}")
            return []
    
    async def search_similar_events(self, query_text: str, n_results: int = 10,
                                   filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for similar events based on query text"""
        try:
            # Generate query embedding
            query_embedding = await self.generate_embedding(query_text)
            
            # Prepare where clause for filtering
            where_clause = self._prepare_where_clause(filters) if filters else None
            
            # Search in events collection
            results = self.collections['events'].query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            formatted_results = []
            if results['ids']:
                for i, event_id in enumerate(results['ids'][0]):
                    formatted_results.append({
                        "event_id": event_id,
                        "similarity_score": 1 - results['distances'][0][i],
                        "document": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i]
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching similar events: {e}")
            return []
    
    async def find_matching_volunteers_for_event(self, event_data: Dict[str, Any], 
                                               n_results: int = 20) -> List[Dict[str, Any]]:
        """Find volunteers that match an event's requirements"""
        try:
            # Create search query from event requirements
            query_text = self._create_event_requirements_query(event_data)
            
            # Search for matching volunteers
            results = await self.search_similar_volunteers(query_text, n_results)
            
            # Filter and rank results based on additional criteria
            filtered_results = await self._filter_volunteer_matches(results, event_data)
            
            return filtered_results
            
        except Exception as e:
            logger.error(f"Error finding matching volunteers: {e}")
            return []
    
    async def find_matching_events_for_volunteer(self, volunteer_data: Dict[str, Any], 
                                               n_results: int = 20) -> List[Dict[str, Any]]:
        """Find events that match a volunteer's skills and preferences"""
        try:
            # Create search query from volunteer skills and interests
            query_text = self._create_volunteer_skills_query(volunteer_data)
            
            # Search for matching events
            results = await self.search_similar_events(query_text, n_results)
            
            # Filter and rank results based on additional criteria
            filtered_results = await self._filter_event_matches(results, volunteer_data)
            
            return filtered_results
            
        except Exception as e:
            logger.error(f"Error finding matching events: {e}")
            return []
    
    async def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts"""
        try:
            embeddings = await self.generate_batch_embeddings([text1, text2])
            
            # Calculate cosine similarity
            embedding1 = np.array(embeddings[0])
            embedding2 = np.array(embeddings[1])
            
            similarity = np.dot(embedding1, embedding2) / (
                np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
            )
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    async def update_volunteer_profile(self, volunteer_id: str, volunteer_data: Dict[str, Any]):
        """Update volunteer profile in vector database"""
        try:
            # Delete existing profile
            await self.delete_volunteer_profile(volunteer_id)
            
            # Add updated profile
            await self.add_volunteer_profile(volunteer_id, volunteer_data)
            
        except Exception as e:
            logger.error(f"Error updating volunteer profile: {e}")
    
    async def update_event_profile(self, event_id: str, event_data: Dict[str, Any]):
        """Update event profile in vector database"""
        try:
            # Delete existing profile
            await self.delete_event_profile(event_id)
            
            # Add updated profile
            await self.add_event_profile(event_id, event_data)
            
        except Exception as e:
            logger.error(f"Error updating event profile: {e}")
    
    async def delete_volunteer_profile(self, volunteer_id: str):
        """Delete volunteer profile from vector database"""
        try:
            self.collections['volunteers'].delete(ids=[volunteer_id])
            logger.debug(f"Deleted volunteer profile {volunteer_id}")
            
        except Exception as e:
            logger.error(f"Error deleting volunteer profile: {e}")
    
    async def delete_event_profile(self, event_id: str):
        """Delete event profile from vector database"""
        try:
            self.collections['events'].delete(ids=[event_id])
            logger.debug(f"Deleted event profile {event_id}")
            
        except Exception as e:
            logger.error(f"Error deleting event profile: {e}")
    
    def _create_volunteer_text(self, volunteer_data: Dict[str, Any]) -> str:
        """Create text representation of volunteer for embedding"""
        text_parts = []
        
        # Add bio and motivation
        if volunteer_data.get("profile", {}).get("bio"):
            text_parts.append(volunteer_data["profile"]["bio"])
        
        if volunteer_data.get("profile", {}).get("motivation"):
            text_parts.append(volunteer_data["profile"]["motivation"])
        
        # Add skills
        skills = volunteer_data.get("skills", [])
        if skills:
            skill_texts = []
            for skill in skills:
                skill_text = f"{skill['name']} ({skill.get('level', 'unknown')} level)"
                if skill.get("years_experience"):
                    skill_text += f" with {skill['years_experience']} years experience"
                skill_texts.append(skill_text)
            text_parts.append("Skills: " + ", ".join(skill_texts))
        
        # Add interests and preferences
        preferences = volunteer_data.get("preferences", {})
        if preferences.get("preferred_event_types"):
            text_parts.append("Interested in: " + ", ".join(preferences["preferred_event_types"]))
        
        # Add languages
        languages = volunteer_data.get("profile", {}).get("languages", [])
        if languages:
            text_parts.append("Languages: " + ", ".join(languages))
        
        return " ".join(text_parts)
    
    def _create_event_text(self, event_data: Dict[str, Any]) -> str:
        """Create text representation of event for embedding"""
        text_parts = []
        
        # Add title and description
        if event_data.get("title"):
            text_parts.append(event_data["title"])
        
        if event_data.get("description"):
            text_parts.append(event_data["description"])
        
        # Add category
        if event_data.get("category"):
            text_parts.append(f"Category: {event_data['category']}")
        
        # Add required skills
        requirements = event_data.get("requirements", [])
        if requirements:
            req_texts = []
            for req in requirements:
                skill = req.get("skill", {})
                req_text = f"{skill.get('name', 'Unknown skill')} ({skill.get('level', 'any')} level)"
                req_texts.append(req_text)
            text_parts.append("Required skills: " + ", ".join(req_texts))
        
        # Add additional attributes
        if event_data.get("provides_training"):
            text_parts.append("Provides training")
        
        if event_data.get("is_urgent"):
            text_parts.append("Urgent opportunity")
        
        return " ".join(text_parts)
    
    def _create_event_requirements_query(self, event_data: Dict[str, Any]) -> str:
        """Create search query from event requirements"""
        query_parts = []
        
        # Add required skills
        requirements = event_data.get("requirements", [])
        for req in requirements:
            skill = req.get("skill", {})
            query_parts.append(f"{skill.get('name', '')} {skill.get('level', '')}")
        
        # Add event category and type
        if event_data.get("category"):
            query_parts.append(event_data["category"])
        
        # Add key terms from description
        description = event_data.get("description", "")
        if description:
            # Extract key terms (simplified approach)
            key_terms = [word for word in description.split() if len(word) > 4][:10]
            query_parts.extend(key_terms)
        
        return " ".join(query_parts)
    
    def _create_volunteer_skills_query(self, volunteer_data: Dict[str, Any]) -> str:
        """Create search query from volunteer skills and preferences"""
        query_parts = []
        
        # Add skills
        skills = volunteer_data.get("skills", [])
        for skill in skills:
            query_parts.append(f"{skill['name']} {skill.get('level', '')}")
        
        # Add preferred event types
        preferences = volunteer_data.get("preferences", {})
        if preferences.get("preferred_event_types"):
            query_parts.extend(preferences["preferred_event_types"])
        
        # Add bio keywords
        bio = volunteer_data.get("profile", {}).get("bio", "")
        if bio:
            # Extract key terms (simplified approach)
            key_terms = [word for word in bio.split() if len(word) > 4][:10]
            query_parts.extend(key_terms)
        
        return " ".join(query_parts)
    
    async def _filter_volunteer_matches(self, results: List[Dict[str, Any]], 
                                      event_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter and rank volunteer matches based on additional criteria"""
        filtered_results = []
        
        for result in results:
            # Apply additional filtering logic
            metadata = result["metadata"]
            
            # Check if similarity score meets threshold
            if result["similarity_score"] < 0.3:
                continue
            
            # Add additional scoring factors
            additional_score = 0.0
            
            # Location proximity bonus (if both have location data)
            try:
                volunteer_location = json.loads(metadata.get("location", "{}"))
                event_location = event_data.get("location", {})
                
                if volunteer_location and event_location:
                    # Simple distance calculation bonus (simplified)
                    additional_score += 0.1
            except:
                pass
            
            # Update final score
            final_score = min(1.0, result["similarity_score"] + additional_score)
            result["final_score"] = final_score
            
            filtered_results.append(result)
        
        # Sort by final score
        filtered_results.sort(key=lambda x: x["final_score"], reverse=True)
        
        return filtered_results
    
    async def _filter_event_matches(self, results: List[Dict[str, Any]], 
                                   volunteer_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter and rank event matches based on additional criteria"""
        filtered_results = []
        
        for result in results:
            # Apply additional filtering logic
            metadata = result["metadata"]
            
            # Check if similarity score meets threshold
            if result["similarity_score"] < 0.3:
                continue
            
            # Add additional scoring factors
            additional_score = 0.0
            
            # Category preference bonus
            volunteer_prefs = volunteer_data.get("preferences", {})
            preferred_types = volunteer_prefs.get("preferred_event_types", [])
            event_category = metadata.get("category", "")
            
            if event_category in preferred_types:
                additional_score += 0.15
            
            # Update final score
            final_score = min(1.0, result["similarity_score"] + additional_score)
            result["final_score"] = final_score
            
            filtered_results.append(result)
        
        # Sort by final score
        filtered_results.sort(key=lambda x: x["final_score"], reverse=True)
        
        return filtered_results
    
    def _prepare_where_clause(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare where clause for ChromaDB filtering"""
        where_clause = {}
        
        # Add filters based on metadata fields
        if "category" in filters:
            where_clause["category"] = filters["category"]
        
        if "location" in filters:
            # Location filtering would require more complex logic
            pass
        
        return where_clause if where_clause else None
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for embedding generation"""
        if not text:
            return ""
        
        # Basic preprocessing
        text = text.strip()
        text = " ".join(text.split())  # Normalize whitespace
        
        # Truncate if too long (model has token limits)
        max_length = 512  # Conservative limit
        if len(text) > max_length:
            text = text[:max_length]
        
        return text
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about vector collections"""
        stats = {}
        
        try:
            for name, collection in self.collections.items():
                count = collection.count()
                stats[name] = {
                    "document_count": count,
                    "collection_name": name
                }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            
        return stats
    
    async def cleanup(self):
        """Cleanup resources"""
        self.is_initialized = False
        logger.info("Vector Service cleaned up") 