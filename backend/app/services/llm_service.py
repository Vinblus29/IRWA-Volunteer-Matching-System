import logging
import openai
from typing import List, Dict, Any, Optional
import asyncio
import json
from ..config import settings

logger = logging.getLogger(__name__)

class LLMService:
    """Service for Large Language Model interactions using OpenAI API"""
    
    def __init__(self):
        self.client = None
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize the LLM service"""
        try:
            # Initialize OpenAI client with API key
            self.client = openai.OpenAI(api_key=settings.openai_api_key)
            
            self.is_initialized = True
            logger.info("LLM Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM Service: {e}")
            raise
    
    async def generate_response(self, prompt: str, max_tokens: int = 1000, 
                              temperature: float = 0.7, model: str = "gpt-3.5-turbo") -> str:
        """Generate text response using OpenAI API"""
        
        if not self.is_initialized:
            await self.initialize()
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return f"Error: Unable to generate response - {str(e)}"
    
    async def generate_embedding(self, text: str, model: str = "text-embedding-ada-002") -> List[float]:
        """Generate text embedding using OpenAI API"""
        
        if not self.is_initialized:
            await self.initialize()
        
        try:
            response = await asyncio.to_thread(
                self.client.embeddings.create,
                model=model,
                input=text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []
    
    async def chat_completion(self, messages: List[Dict[str, str]], 
                            model: str = "gpt-3.5-turbo", 
                            temperature: float = 0.7) -> str:
        """Multi-turn chat completion"""
        
        if not self.is_initialized:
            await self.initialize()
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=model,
                messages=messages,
                temperature=temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            return f"Error: Unable to complete chat - {str(e)}"
    
    async def cleanup(self):
        """Cleanup resources"""
        self.is_initialized = False
        logger.info("LLM Service cleaned up") 