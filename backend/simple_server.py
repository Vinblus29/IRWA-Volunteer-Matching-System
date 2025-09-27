"""
Simple FastAPI Server for Volunteer Matching System

This is a simplified version of the main server for development and testing purposes.
It provides basic endpoints and functionality without the full complexity of the main application.
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
import os
from pathlib import Path

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Volunteer Matching System - Simple Server",
    description="A simplified version of the Volunteer Matching System for development and testing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "message": "Volunteer Matching System - Simple Server",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "volunteer-matching-simple-server"
    }

# Basic API endpoints
@app.get("/api/status")
async def api_status():
    """API status endpoint"""
    return {
        "api_status": "operational",
        "endpoints_available": [
            "/",
            "/health", 
            "/api/status",
            "/api/test",
            "/docs",
            "/redoc"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/test")
async def test_endpoint():
    """Test endpoint for basic functionality"""
    return {
        "message": "Test endpoint working",
        "data": {
            "test_id": "simple-server-test-001",
            "server_type": "simple",
            "features": [
                "basic_routing",
                "cors_support",
                "health_checks",
                "api_documentation"
            ]
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"The requested endpoint {request.url.path} was not found",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An internal server error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Simple Volunteer Matching Server starting up...")
    logger.info("Server will be available at: http://localhost:8000")
    logger.info("API documentation available at: http://localhost:8000/docs")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Simple Volunteer Matching Server shutting down...")

def main():
    """Main function to run the server"""
    # Get configuration from environment variables
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Reload mode: {reload}")
    
    # Run the server
    uvicorn.run(
        "simple_server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    main()
