import asyncio
import json
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
from ..config import settings

logger = logging.getLogger(__name__)

class AgentMessage:
    """Standard message format for agent communication"""
    def __init__(self, sender: str, receiver: str, message_type: str, 
                 payload: Dict[str, Any], correlation_id: str = None):
        self.id = str(uuid.uuid4())
        self.sender = sender
        self.receiver = receiver
        self.message_type = message_type
        self.payload = payload
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.timestamp = datetime.utcnow()
        self.processed = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "sender": self.sender,
            "receiver": self.receiver,
            "message_type": self.message_type,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat(),
            "processed": self.processed
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMessage':
        msg = cls(
            sender=data["sender"],
            receiver=data["receiver"],
            message_type=data["message_type"],
            payload=data["payload"],
            correlation_id=data["correlation_id"]
        )
        msg.id = data["id"]
        msg.timestamp = datetime.fromisoformat(data["timestamp"])
        msg.processed = data["processed"]
        return msg

class BaseAgent(ABC):
    """Base class for all intelligent agents in the volunteer matching system"""
    
    def __init__(self, agent_id: str, name: str, version: str = "1.0"):
        self.agent_id = agent_id
        self.name = name
        self.version = version
        self.is_active = False
        self.last_heartbeat = None
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.subscriptions: List[str] = []
        self.performance_metrics = {
            "messages_processed": 0,
            "errors_count": 0,
            "average_processing_time": 0.0,
            "last_activity": None
        }
        self.logger = logging.getLogger(f"agent.{self.agent_id}")
        
    async def start(self):
        """Start the agent and begin processing messages"""
        self.is_active = True
        self.last_heartbeat = datetime.utcnow()
        self.logger.info(f"Agent {self.name} ({self.agent_id}) started")
        
        # Start message processing loop
        asyncio.create_task(self._message_processing_loop())
        
        # Start heartbeat
        asyncio.create_task(self._heartbeat_loop())
        
        await self.initialize()

    async def stop(self):
        """Stop the agent gracefully"""
        self.is_active = False
        await self.cleanup()
        self.logger.info(f"Agent {self.name} ({self.agent_id}) stopped")

    @abstractmethod
    async def initialize(self):
        """Initialize agent-specific resources"""
        pass

    @abstractmethod
    async def cleanup(self):
        """Cleanup agent-specific resources"""
        pass

    @abstractmethod
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process incoming message and optionally return a response"""
        pass

    async def send_message(self, receiver: str, message_type: str, 
                          payload: Dict[str, Any], correlation_id: str = None) -> str:
        """Send a message to another agent"""
        message = AgentMessage(
            sender=self.agent_id,
            receiver=receiver,
            message_type=message_type,
            payload=payload,
            correlation_id=correlation_id
        )
        
        # In a real implementation, this would send to a message broker
        # For now, we'll simulate direct delivery
        await self._deliver_message(message)
        
        self.logger.debug(f"Sent message {message.id} to {receiver}")
        return message.id

    async def _deliver_message(self, message: AgentMessage):
        """Simulate message delivery (would use Redis/RabbitMQ in production)"""
        # This is a simplified implementation
        # In production, you'd use a proper message broker
        pass

    async def receive_message(self, message: AgentMessage):
        """Receive a message from another agent"""
        await self.message_queue.put(message)

    async def _message_processing_loop(self):
        """Main message processing loop"""
        while self.is_active:
            try:
                # Wait for message with timeout
                message = await asyncio.wait_for(
                    self.message_queue.get(), 
                    timeout=1.0
                )
                
                start_time = time.time()
                
                # Process the message
                response = await self.process_message(message)
                
                # Update performance metrics
                processing_time = time.time() - start_time
                self._update_performance_metrics(processing_time)
                
                # Send response if generated
                if response:
                    await self._deliver_message(response)
                
                # Mark message as processed
                message.processed = True
                
            except asyncio.TimeoutError:
                # No message received, continue
                continue
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")
                self.performance_metrics["errors_count"] += 1

    async def _heartbeat_loop(self):
        """Send periodic heartbeat signals"""
        while self.is_active:
            self.last_heartbeat = datetime.utcnow()
            await asyncio.sleep(30)  # Heartbeat every 30 seconds

    def _update_performance_metrics(self, processing_time: float):
        """Update agent performance metrics"""
        self.performance_metrics["messages_processed"] += 1
        self.performance_metrics["last_activity"] = datetime.utcnow()
        
        # Calculate rolling average processing time
        current_avg = self.performance_metrics["average_processing_time"]
        msg_count = self.performance_metrics["messages_processed"]
        
        new_avg = ((current_avg * (msg_count - 1)) + processing_time) / msg_count
        self.performance_metrics["average_processing_time"] = new_avg

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "version": self.version,
            "is_active": self.is_active,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "performance_metrics": self.performance_metrics,
            "queue_size": self.message_queue.qsize()
        }

    async def subscribe_to_events(self, event_types: List[str]):
        """Subscribe to specific event types"""
        self.subscriptions.extend(event_types)
        self.logger.info(f"Subscribed to events: {event_types}")

    async def unsubscribe_from_events(self, event_types: List[str]):
        """Unsubscribe from specific event types"""
        for event_type in event_types:
            if event_type in self.subscriptions:
                self.subscriptions.remove(event_type)
        self.logger.info(f"Unsubscribed from events: {event_types}")

    def can_handle_message(self, message: AgentMessage) -> bool:
        """Check if this agent can handle the given message type"""
        return message.message_type in self.subscriptions or message.receiver == self.agent_id

class AgentCommunicationProtocol:
    """Defines the communication protocol between agents"""
    
    # Message types
    SKILL_ANALYSIS_REQUEST = "skill_analysis_request"
    SKILL_ANALYSIS_RESPONSE = "skill_analysis_response"
    EVENT_MATCHING_REQUEST = "event_matching_request"
    EVENT_MATCHING_RESPONSE = "event_matching_response"
    AVAILABILITY_CHECK_REQUEST = "availability_check_request"
    AVAILABILITY_CHECK_RESPONSE = "availability_check_response"
    NOTIFICATION_REQUEST = "notification_request"
    HEARTBEAT = "heartbeat"
    ERROR = "error"
    
    # Agent identifiers
    SKILL_PROFILER = "skill_profiler"
    EVENT_MATCHER = "event_matcher"
    AVAILABILITY_TRACKER = "availability_tracker"
    COMMUNICATION_ORCHESTRATOR = "communication_orchestrator"

class AgentError(Exception):
    """Custom exception for agent-related errors"""
    def __init__(self, agent_id: str, message: str, error_code: str = None):
        self.agent_id = agent_id
        self.error_code = error_code
        super().__init__(f"Agent {agent_id}: {message}") 