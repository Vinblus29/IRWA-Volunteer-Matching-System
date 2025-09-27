import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from ..agents.skill_profiler import SkillProfilerAgent
from ..agents.event_matcher import EventMatcherAgent
from ..agents.availability_tracker import AvailabilityTrackerAgent
from ..agents.communication_orchestrator import CommunicationOrchestrator
from ..agents.base_agent import AgentMessage, AgentCommunicationProtocol

class TestSkillProfilerAgent:
    """Test cases for Skill Profiler Agent"""
    
    @pytest.fixture
    async def skill_profiler(self):
        agent = SkillProfilerAgent()
        with patch.object(agent, '_load_skill_taxonomy'), \
             patch.object(agent, '_load_skill_synonyms'):
            await agent.initialize()
        yield agent
        await agent.cleanup()
    
    @pytest.mark.asyncio
    async def test_skill_analysis_request(self, skill_profiler):
        """Test skill analysis request processing"""
        message = AgentMessage(
            sender="test_sender",
            receiver=AgentCommunicationProtocol.SKILL_PROFILER,
            message_type=AgentCommunicationProtocol.SKILL_ANALYSIS_REQUEST,
            payload={
                "analysis_type": "volunteer_skills",
                "volunteer_data": {
                    "skills": [{"name": "Python", "level": "advanced"}],
                    "profile": {"bio": "Software developer with 5 years experience"}
                }
            }
        )
        
        with patch.object(skill_profiler, '_analyze_volunteer_skills') as mock_analyze:
            mock_analyze.return_value = {
                "enhanced_skills": [{"name": "Python", "level": "advanced", "category": "programming"}],
                "skill_score": 0.85
            }
            
            response = await skill_profiler.process_message(message)
            
            assert response is not None
            assert response.message_type == AgentCommunicationProtocol.SKILL_ANALYSIS_RESPONSE
            assert "enhanced_skills" in response.payload
    
    @pytest.mark.asyncio
    async def test_skill_extraction(self, skill_profiler):
        """Test skill extraction from text"""
        text = "I have 5 years experience in Python, JavaScript, and machine learning"
        
        with patch.object(skill_profiler.nlp_service, 'extract_skills_from_text') as mock_extract:
            mock_extract.return_value = ["Python", "JavaScript", "machine learning"]
            
            skills = await skill_profiler._extract_skills_from_text(text)
            
            assert len(skills) == 3
            assert "Python" in skills

class TestEventMatcherAgent:
    """Test cases for Event Matcher Agent"""
    
    @pytest.fixture
    async def event_matcher(self):
        agent = EventMatcherAgent()
        with patch.object(agent, 'db'), \
             patch.object(agent, 'vector_service'):
            await agent.initialize()
        yield agent
        await agent.cleanup()
    
    @pytest.mark.asyncio
    async def test_find_volunteers_for_event(self, event_matcher):
        """Test finding volunteers for an event"""
        message = AgentMessage(
            sender="test_sender",
            receiver=AgentCommunicationProtocol.EVENT_MATCHER,
            message_type=AgentCommunicationProtocol.EVENT_MATCHING_REQUEST,
            payload={
                "request_type": "find_volunteers_for_event",
                "event_data": {
                    "title": "Beach Cleanup",
                    "requirements": [{"skill": {"name": "Environmental Awareness"}}]
                }
            }
        )
        
        with patch.object(event_matcher, '_find_volunteers_for_event') as mock_find:
            mock_find.return_value = {
                "matches": [{"volunteer_id": "123", "match_score": 0.85}],
                "total_found": 1
            }
            
            response = await event_matcher.process_message(message)
            
            assert response is not None
            assert "matches" in response.payload
            assert len(response.payload["matches"]) == 1

class TestAvailabilityTrackerAgent:
    """Test cases for Availability Tracker Agent"""
    
    @pytest.fixture
    async def availability_tracker(self):
        agent = AvailabilityTrackerAgent()
        with patch.object(agent, 'db'), \
             patch.object(agent, 'notification_service'):
            await agent.initialize()
        yield agent
        await agent.cleanup()
    
    @pytest.mark.asyncio
    async def test_availability_check(self, availability_tracker):
        """Test availability checking"""
        message = AgentMessage(
            sender="test_sender",
            receiver=AgentCommunicationProtocol.AVAILABILITY_TRACKER,
            message_type=AgentCommunicationProtocol.AVAILABILITY_CHECK_REQUEST,
            payload={
                "request_type": "check_volunteer_availability",
                "volunteer_id": "123",
                "event_id": "456"
            }
        )
        
        with patch.object(availability_tracker, '_check_volunteer_availability') as mock_check:
            mock_check.return_value = {
                "available": True,
                "availability_score": 0.9,
                "conflicts": []
            }
            
            response = await availability_tracker.process_message(message)
            
            assert response is not None
            assert response.payload["available"] is True
            assert response.payload["availability_score"] == 0.9
    
    @pytest.mark.asyncio
    async def test_conflict_detection(self, availability_tracker):
        """Test scheduling conflict detection"""
        volunteer_data = {
            "availability": [{"day": "monday", "start_time": "09:00", "end_time": "17:00"}]
        }
        event_data = {
            "schedule": {
                "start_date": "2024-01-15",  # Monday
                "start_time": "14:00",
                "end_time": "16:00"
            }
        }
        
        overlap = await availability_tracker._calculate_availability_overlap(
            volunteer_data["availability"], 
            event_data["schedule"]
        )
        
        assert overlap["overlap_hours"] == 2.0
        assert overlap["overlap_percentage"] == 100.0

class TestCommunicationOrchestrator:
    """Test cases for Communication Orchestrator"""
    
    @pytest.fixture
    async def orchestrator(self):
        agent = CommunicationOrchestrator()
        with patch.object(agent, 'db'):
            await agent.initialize()
        yield agent
        await agent.cleanup()
    
    @pytest.mark.asyncio
    async def test_agent_registration(self, orchestrator):
        """Test agent registration"""
        agent_info = {
            "name": "Test Agent",
            "version": "1.0",
            "capabilities": ["test"]
        }
        
        await orchestrator.register_agent("test_agent", agent_info)
        
        assert "test_agent" in orchestrator.agent_registry
        assert orchestrator.agent_registry["test_agent"]["info"] == agent_info
    
    @pytest.mark.asyncio
    async def test_workflow_creation(self, orchestrator):
        """Test workflow creation and execution"""
        workflow_data = {
            "event_id": "123",
            "requirements": ["skill1", "skill2"]
        }
        
        with patch.object(orchestrator, '_execute_workflow') as mock_execute:
            workflow_id = await orchestrator.start_workflow("volunteer_matching", workflow_data)
            
            assert workflow_id in orchestrator.active_workflows
            assert orchestrator.active_workflows[workflow_id]["type"] == "volunteer_matching"
            mock_execute.assert_called_once_with(workflow_id)

class TestAgentCommunication:
    """Test inter-agent communication"""
    
    @pytest.mark.asyncio
    async def test_message_routing(self):
        """Test message routing between agents"""
        orchestrator = CommunicationOrchestrator()
        
        # Create a test message
        message = AgentMessage(
            sender=AgentCommunicationProtocol.SKILL_PROFILER,
            receiver=AgentCommunicationProtocol.EVENT_MATCHER,
            message_type=AgentCommunicationProtocol.SKILL_ANALYSIS_RESPONSE,
            payload={"test": "data"}
        )
        
        with patch.object(orchestrator, '_route_message') as mock_route:
            await orchestrator.process_message(message)
            mock_route.assert_called_once_with(message)
    
    @pytest.mark.asyncio
    async def test_message_correlation(self):
        """Test message correlation for workflows"""
        message1 = AgentMessage(
            sender="agent1",
            receiver="agent2",
            message_type="test_type",
            payload={},
            correlation_id="workflow_123"
        )
        
        message2 = AgentMessage(
            sender="agent2",
            receiver="agent1",
            message_type="test_response",
            payload={},
            correlation_id="workflow_123"
        )
        
        assert message1.correlation_id == message2.correlation_id

@pytest.mark.asyncio
async def test_agent_lifecycle():
    """Test agent startup and shutdown"""
    agent = SkillProfilerAgent()
    
    # Test initialization
    with patch.object(agent, '_load_skill_taxonomy'), \
         patch.object(agent, '_load_skill_synonyms'):
        await agent.initialize()
        assert agent.is_active is True
    
    # Test cleanup
    await agent.cleanup()
    assert agent.is_active is False

@pytest.mark.asyncio
async def test_agent_error_handling():
    """Test agent error handling"""
    agent = SkillProfilerAgent()
    
    # Create invalid message
    message = AgentMessage(
        sender="test",
        receiver=agent.agent_id,
        message_type="invalid_type",
        payload={}
    )
    
    with patch.object(agent, '_load_skill_taxonomy'), \
         patch.object(agent, '_load_skill_synonyms'):
        await agent.initialize()
        
        response = await agent.process_message(message)
        
        # Should return error response
        assert response is not None
        assert response.message_type == AgentCommunicationProtocol.ERROR
    
    await agent.cleanup()

# Integration tests
class TestAgentIntegration:
    """Integration tests for agent system"""
    
    @pytest.mark.asyncio
    async def test_full_matching_workflow(self):
        """Test complete volunteer matching workflow"""
        # This would be a comprehensive test of the entire system
        # involving all agents working together
        pass
    
    @pytest.mark.asyncio
    async def test_performance_metrics(self):
        """Test agent performance monitoring"""
        agent = SkillProfilerAgent()
        
        with patch.object(agent, '_load_skill_taxonomy'), \
             patch.object(agent, '_load_skill_synonyms'):
            await agent.initialize()
            
            # Process some messages
            for i in range(10):
                message = AgentMessage(
                    sender="test",
                    receiver=agent.agent_id,
                    message_type=AgentCommunicationProtocol.SKILL_ANALYSIS_REQUEST,
                    payload={"analysis_type": "test"}
                )
                await agent.process_message(message)
            
            metrics = agent.get_performance_metrics()
            assert metrics["messages_processed"] == 10
        
        await agent.cleanup()

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 