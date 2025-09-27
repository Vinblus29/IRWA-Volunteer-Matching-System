import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
import uvicorn

from .config import settings
from .database import connect_to_mongo, close_mongo_connection
from .api import auth, volunteers, events, matching, dashboard, skill_profiler, event_matcher, availability, organization, notification
from .agents.skill_profiler import SkillProfilerAgent
from .agents.event_matcher import EventMatcherAgent
from .utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global agent instances
agents = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting Volunteer Matching System...")
    
    try:
        # Connect to MongoDB
        await connect_to_mongo()
        
        # Initialize and start agents
        agents["skill_profiler"] = SkillProfilerAgent()
        agents["event_matcher"] = EventMatcherAgent()
        
        # Start agents
        for agent_name, agent in agents.items():
            await agent.start()
            logger.info(f"Started {agent_name} agent")
        
        logger.info("All systems initialized successfully")
        
        yield
        
    finally:
        # Shutdown
        logger.info("Shutting down Volunteer Matching System...")
        
        # Stop agents
        for agent_name, agent in agents.items():
            await agent.stop()
            logger.info(f"Stopped {agent_name} agent")
        
        # Close database connection
        await close_mongo_connection()
        
        logger.info("Shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Intelligent Volunteer Matching System",
    description="AI-powered volunteer matching system using multi-agent architecture",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Security
security = HTTPBearer()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
if settings.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts
    )

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(volunteers.router, prefix="/api/volunteers", tags=["Volunteers"])
app.include_router(events.router, prefix="/api/events", tags=["Events"])
app.include_router(matching.router, prefix="/api/matching", tags=["Matching"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(skill_profiler.router, prefix="/api/skill-profiler", tags=["Skill Profiler"])
app.include_router(event_matcher.router, prefix="/api/event-matcher", tags=["Event Matcher"])
app.include_router(availability.router, prefix="/api/availability", tags=["Availability"])
app.include_router(organization.router, prefix="/api/organizations", tags=["Organizations"])
app.include_router(notification.router, prefix="/api/notifications", tags=["Notifications"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Intelligent Volunteer Matching System API",
        "version": "1.0.0",
        "docs": "/docs",
        "agents_status": {
            name: agent.get_status() 
            for name, agent in agents.items()
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        from .database import get_database
        db = get_database()
        await db.command("ping")
        
        # Check agent status
        agent_status = {
            name: agent.is_active 
            for name, agent in agents.items()
        }
        
        return {
            "status": "healthy",
            "database": "connected",
            "agents": agent_status,
            "environment": settings.environment
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.get("/api/agents/status")
async def get_agents_status():
    """Get detailed status of all agents"""
    return {
        name: agent.get_status() 
        for name, agent in agents.items()
    }

# Custom exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP {exc.status_code}: {exc.detail}")
    return {"error": exc.detail, "status_code": exc.status_code}

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return {"error": "Internal server error", "status_code": 500}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower()
    )
