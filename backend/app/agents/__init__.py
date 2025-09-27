"""
Intelligent Agents Package for Volunteer Matching System

This package contains AI-powered agents that handle various aspects of the volunteer matching system:

- SkillProfilerAgent: Analyzes and profiles volunteer skills using NLP and ML
- EventMatcherAgent: Matches volunteers with events based on multiple criteria
- AvailabilityTrackerAgent: Tracks and manages volunteer availability
- CommunicationOrchestrator: Handles multi-channel communication and notifications
- BaseAgent: Base class for all agents with common functionality

Each agent is designed to work independently while communicating with other agents
through a standardized communication protocol.
"""

# Import base agent components
from .base_agent import (
    BaseAgent,
    AgentMessage,
    AgentCommunicationProtocol,
    AgentStatus,
    AgentCapabilities
)

# Import specific agents
from .skill_profiler import SkillProfilerAgent
from .event_matcher import EventMatcherAgent
from .availability_tracker import AvailabilityTrackerAgent
from .communication_orchestrator import CommunicationOrchestrator

# Agent registry for dynamic loading
AGENT_REGISTRY = {
    "skill_profiler": SkillProfilerAgent,
    "event_matcher": EventMatcherAgent,
    "availability_tracker": AvailabilityTrackerAgent,
    "communication_orchestrator": CommunicationOrchestrator
}

def get_agent(agent_name: str) -> BaseAgent:
    """Get an agent instance by name"""
    if agent_name not in AGENT_REGISTRY:
        raise ValueError(f"Unknown agent: {agent_name}")
    
    agent_class = AGENT_REGISTRY[agent_name]
    return agent_class()

def list_available_agents() -> list:
    """List all available agent names"""
    return list(AGENT_REGISTRY.keys())

def get_agent_capabilities(agent_name: str) -> dict:
    """Get capabilities of a specific agent"""
    if agent_name not in AGENT_REGISTRY:
        raise ValueError(f"Unknown agent: {agent_name}")
    
    agent_class = AGENT_REGISTRY[agent_name]
    return agent_class.get_capabilities()

# Export all public components
__all__ = [
    # Base components
    "BaseAgent",
    "AgentMessage", 
    "AgentCommunicationProtocol",
    "AgentStatus",
    "AgentCapabilities",
    
    # Specific agents
    "SkillProfilerAgent",
    "EventMatcherAgent",
    "AvailabilityTrackerAgent",
    "CommunicationOrchestrator",
    
    # Registry and utilities
    "AGENT_REGISTRY",
    "get_agent",
    "list_available_agents",
    "get_agent_capabilities"
]
