import asyncio
import json
import time
import uuid
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict, deque
from .base_agent import BaseAgent, AgentMessage, AgentCommunicationProtocol, AgentError
from ..database import get_database
from ..config import settings

class CommunicationOrchestrator(BaseAgent):
    """
    Central communication orchestrator that manages inter-agent communication,
    message routing, workflow coordination, and system monitoring.
    """
    
    def __init__(self):
        super().__init__(
            agent_id=AgentCommunicationProtocol.COMMUNICATION_ORCHESTRATOR,
            name="Communication Orchestrator",
            version="1.0"
        )
        self.db = None
        self.agent_registry = {}
        self.message_queue = asyncio.Queue()
        self.workflow_state = {}
        self.message_history = deque(maxlen=1000)
        self.agent_performance = defaultdict(dict)
        self.active_workflows = {}
        
    async def initialize(self):
        """Initialize the communication orchestrator"""
        try:
            self.db = get_database()
            
            # Start background tasks
            asyncio.create_task(self._message_routing_task())
            asyncio.create_task(self._workflow_monitoring_task())
            asyncio.create_task(self._agent_health_monitoring_task())
            asyncio.create_task(self._performance_monitoring_task())
            
            self.logger.info("Communication Orchestrator initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Communication Orchestrator: {e}")
            raise AgentError(self.agent_id, f"Initialization failed: {e}")
    
    async def cleanup(self):
        """Cleanup resources"""
        # Save final state and metrics
        await self._save_performance_metrics()
        await self._save_workflow_state()
    
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process incoming messages and route them appropriately"""
        try:
            # Log message for monitoring
            self._log_message(message)
            
            # Route message based on type and receiver
            await self._route_message(message)
            
            # Update workflow state if needed
            await self._update_workflow_state(message)
            
            return None  # Orchestrator typically doesn't send direct responses
            
        except Exception as e:
            self.logger.error(f"Error processing message {message.id}: {e}")
            return AgentMessage(
                sender=self.agent_id,
                receiver=message.sender,
                message_type=AgentCommunicationProtocol.ERROR,
                payload={"error": str(e), "original_message_id": message.id},
                correlation_id=message.correlation_id
            )
    
    async def register_agent(self, agent_id: str, agent_info: Dict[str, Any]):
        """Register an agent with the orchestrator"""
        self.agent_registry[agent_id] = {
            "info": agent_info,
            "registered_at": datetime.utcnow(),
            "last_heartbeat": datetime.utcnow(),
            "status": "active",
            "message_count": 0,
            "error_count": 0
        }
        
        self.logger.info(f"Registered agent: {agent_id}")
    
    async def unregister_agent(self, agent_id: str):
        """Unregister an agent"""
        if agent_id in self.agent_registry:
            self.agent_registry[agent_id]["status"] = "inactive"
            self.agent_registry[agent_id]["unregistered_at"] = datetime.utcnow()
            self.logger.info(f"Unregistered agent: {agent_id}")
    
    async def start_workflow(self, workflow_type: str, workflow_data: Dict[str, Any]) -> str:
        """Start a new multi-agent workflow"""
        workflow_id = str(uuid.uuid4())
        
        workflow = {
            "id": workflow_id,
            "type": workflow_type,
            "data": workflow_data,
            "status": "started",
            "created_at": datetime.utcnow(),
            "steps": [],
            "current_step": 0,
            "agents_involved": [],
            "messages": [],
            "result": None,
            "error": None
        }
        
        self.active_workflows[workflow_id] = workflow
        
        # Start the workflow based on type
        await self._execute_workflow(workflow_id)
        
        return workflow_id
    
    async def _execute_workflow(self, workflow_id: str):
        """Execute a specific workflow"""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return
        
        workflow_type = workflow["type"]
        
        try:
            if workflow_type == "volunteer_matching":
                await self._execute_volunteer_matching_workflow(workflow_id)
            elif workflow_type == "skill_analysis":
                await self._execute_skill_analysis_workflow(workflow_id)
            elif workflow_type == "event_optimization":
                await self._execute_event_optimization_workflow(workflow_id)
            elif workflow_type == "availability_check":
                await self._execute_availability_check_workflow(workflow_id)
            else:
                raise ValueError(f"Unknown workflow type: {workflow_type}")
                
        except Exception as e:
            self.logger.error(f"Error executing workflow {workflow_id}: {e}")
            workflow["status"] = "error"
            workflow["error"] = str(e)
            workflow["completed_at"] = datetime.utcnow()
    
    async def _execute_volunteer_matching_workflow(self, workflow_id: str):
        """Execute volunteer matching workflow involving multiple agents"""
        workflow = self.active_workflows[workflow_id]
        event_id = workflow["data"].get("event_id")
        
        try:
            # Step 1: Get event details and analyze requirements
            workflow["steps"].append({
                "step": 1,
                "description": "Analyze event requirements",
                "agent": AgentCommunicationProtocol.SKILL_PROFILER,
                "started_at": datetime.utcnow()
            })
            
            # Send message to skill profiler
            skill_analysis_msg = AgentMessage(
                sender=self.agent_id,
                receiver=AgentCommunicationProtocol.SKILL_PROFILER,
                message_type=AgentCommunicationProtocol.SKILL_ANALYSIS_REQUEST,
                payload={
                    "analysis_type": "event_requirements",
                    "event_data": {"event_id": event_id},
                    "workflow_id": workflow_id
                },
                correlation_id=workflow_id
            )
            
            await self._route_message(skill_analysis_msg)
            workflow["agents_involved"].append(AgentCommunicationProtocol.SKILL_PROFILER)
            workflow["messages"].append(skill_analysis_msg.to_dict())
            
            # Wait for response and continue workflow...
            # (Implementation would continue with event matcher and availability tracker)
            
        except Exception as e:
            self.logger.error(f"Error in volunteer matching workflow: {e}")
            workflow["status"] = "error"
            workflow["error"] = str(e)
    
    async def _execute_skill_analysis_workflow(self, workflow_id: str):
        """Execute skill analysis workflow"""
        workflow = self.active_workflows[workflow_id]
        volunteer_id = workflow["data"].get("volunteer_id")
        
        # Implementation for skill analysis workflow
        workflow["status"] = "completed"
        workflow["completed_at"] = datetime.utcnow()
    
    async def _execute_event_optimization_workflow(self, workflow_id: str):
        """Execute event optimization workflow"""
        workflow = self.active_workflows[workflow_id]
        
        # Implementation for event optimization workflow
        workflow["status"] = "completed"
        workflow["completed_at"] = datetime.utcnow()
    
    async def _execute_availability_check_workflow(self, workflow_id: str):
        """Execute availability check workflow"""
        workflow = self.active_workflows[workflow_id]
        
        # Implementation for availability check workflow
        workflow["status"] = "completed"
        workflow["completed_at"] = datetime.utcnow()
    
    async def _route_message(self, message: AgentMessage):
        """Route message to appropriate agent"""
        receiver = message.receiver
        
        if receiver in self.agent_registry:
            # Update agent statistics
            self.agent_registry[receiver]["message_count"] += 1
            self.agent_registry[receiver]["last_message"] = datetime.utcnow()
            
            # In a real implementation, this would use a message broker
            # For now, we'll add to our internal queue
            await self.message_queue.put(message)
            
            self.logger.debug(f"Routed message {message.id} to {receiver}")
        else:
            self.logger.warning(f"Unknown receiver: {receiver}")
            
            # Send error back to sender
            error_msg = AgentMessage(
                sender=self.agent_id,
                receiver=message.sender,
                message_type=AgentCommunicationProtocol.ERROR,
                payload={
                    "error": f"Unknown receiver: {receiver}",
                    "original_message_id": message.id
                },
                correlation_id=message.correlation_id
            )
            await self.message_queue.put(error_msg)
    
    async def _update_workflow_state(self, message: AgentMessage):
        """Update workflow state based on message"""
        correlation_id = message.correlation_id
        
        if correlation_id in self.active_workflows:
            workflow = self.active_workflows[correlation_id]
            
            # Add message to workflow history
            workflow["messages"].append(message.to_dict())
            
            # Update workflow based on message type
            if message.message_type == AgentCommunicationProtocol.SKILL_ANALYSIS_RESPONSE:
                await self._handle_skill_analysis_response(workflow, message)
            elif message.message_type == AgentCommunicationProtocol.EVENT_MATCHING_RESPONSE:
                await self._handle_event_matching_response(workflow, message)
            elif message.message_type == AgentCommunicationProtocol.AVAILABILITY_CHECK_RESPONSE:
                await self._handle_availability_response(workflow, message)
            elif message.message_type == AgentCommunicationProtocol.ERROR:
                await self._handle_workflow_error(workflow, message)
    
    async def _handle_skill_analysis_response(self, workflow: Dict, message: AgentMessage):
        """Handle skill analysis response in workflow"""
        if workflow["type"] == "volunteer_matching":
            # Move to next step: event matching
            await self._continue_volunteer_matching_workflow(workflow, message.payload)
    
    async def _handle_event_matching_response(self, workflow: Dict, message: AgentMessage):
        """Handle event matching response in workflow"""
        if workflow["type"] == "volunteer_matching":
            # Move to next step: availability checking
            await self._continue_to_availability_check(workflow, message.payload)
    
    async def _handle_availability_response(self, workflow: Dict, message: AgentMessage):
        """Handle availability response in workflow"""
        if workflow["type"] == "volunteer_matching":
            # Final step: compile results
            await self._complete_volunteer_matching_workflow(workflow, message.payload)
    
    async def _handle_workflow_error(self, workflow: Dict, message: AgentMessage):
        """Handle workflow error"""
        workflow["status"] = "error"
        workflow["error"] = message.payload.get("error", "Unknown error")
        workflow["completed_at"] = datetime.utcnow()
    
    async def _continue_volunteer_matching_workflow(self, workflow: Dict, skill_analysis: Dict):
        """Continue volunteer matching workflow with event matching"""
        # Send request to event matcher
        matching_msg = AgentMessage(
            sender=self.agent_id,
            receiver=AgentCommunicationProtocol.EVENT_MATCHER,
            message_type=AgentCommunicationProtocol.EVENT_MATCHING_REQUEST,
            payload={
                "request_type": "find_volunteers_for_event",
                "event_id": workflow["data"]["event_id"],
                "skill_analysis": skill_analysis,
                "workflow_id": workflow["id"]
            },
            correlation_id=workflow["id"]
        )
        
        await self._route_message(matching_msg)
        workflow["agents_involved"].append(AgentCommunicationProtocol.EVENT_MATCHER)
        workflow["current_step"] += 1
    
    async def _continue_to_availability_check(self, workflow: Dict, matching_results: Dict):
        """Continue to availability checking"""
        # Send request to availability tracker
        availability_msg = AgentMessage(
            sender=self.agent_id,
            receiver=AgentCommunicationProtocol.AVAILABILITY_TRACKER,
            message_type=AgentCommunicationProtocol.AVAILABILITY_CHECK_REQUEST,
            payload={
                "request_type": "bulk_availability_check",
                "matches": matching_results.get("matches", []),
                "workflow_id": workflow["id"]
            },
            correlation_id=workflow["id"]
        )
        
        await self._route_message(availability_msg)
        workflow["agents_involved"].append(AgentCommunicationProtocol.AVAILABILITY_TRACKER)
        workflow["current_step"] += 1
    
    async def _complete_volunteer_matching_workflow(self, workflow: Dict, availability_results: Dict):
        """Complete volunteer matching workflow"""
        workflow["status"] = "completed"
        workflow["completed_at"] = datetime.utcnow()
        workflow["result"] = {
            "matches_found": len(availability_results.get("results", [])),
            "recommendations": availability_results.get("recommendations", []),
            "processing_time": (datetime.utcnow() - workflow["created_at"]).total_seconds()
        }
        
        # Store final results in database
        await self._store_workflow_results(workflow)
    
    async def _store_workflow_results(self, workflow: Dict):
        """Store workflow results in database"""
        try:
            await self.db.workflow_results.insert_one({
                "workflow_id": workflow["id"],
                "type": workflow["type"],
                "status": workflow["status"],
                "result": workflow["result"],
                "agents_involved": workflow["agents_involved"],
                "processing_time": (workflow.get("completed_at", datetime.utcnow()) - workflow["created_at"]).total_seconds(),
                "created_at": workflow["created_at"],
                "completed_at": workflow.get("completed_at")
            })
        except Exception as e:
            self.logger.error(f"Error storing workflow results: {e}")
    
    def _log_message(self, message: AgentMessage):
        """Log message for monitoring and debugging"""
        self.message_history.append({
            "id": message.id,
            "sender": message.sender,
            "receiver": message.receiver,
            "type": message.message_type,
            "timestamp": message.timestamp.isoformat(),
            "correlation_id": message.correlation_id,
            "processed": message.processed
        })
    
    async def _message_routing_task(self):
        """Background task for message routing"""
        while self.is_active:
            try:
                # Process messages in queue
                while not self.message_queue.empty():
                    message = await self.message_queue.get()
                    await self._deliver_message_to_agent(message)
                
                await asyncio.sleep(0.1)  # Short delay to prevent busy waiting
                
            except Exception as e:
                self.logger.error(f"Error in message routing task: {e}")
                await asyncio.sleep(1)
    
    async def _deliver_message_to_agent(self, message: AgentMessage):
        """Deliver message to target agent (simulation)"""
        # In a real implementation, this would deliver to actual agent instances
        # For now, we'll just log the delivery
        self.logger.debug(f"Delivered message {message.id} to {message.receiver}")
        
        # Update performance metrics
        self._update_agent_performance(message.receiver, "message_delivered")
    
    async def _workflow_monitoring_task(self):
        """Background task for monitoring workflows"""
        while self.is_active:
            try:
                current_time = datetime.utcnow()
                
                # Check for stuck workflows
                for workflow_id, workflow in list(self.active_workflows.items()):
                    if workflow["status"] == "started":
                        elapsed = current_time - workflow["created_at"]
                        if elapsed > timedelta(minutes=30):  # Timeout after 30 minutes
                            workflow["status"] = "timeout"
                            workflow["error"] = "Workflow timeout"
                            workflow["completed_at"] = current_time
                            self.logger.warning(f"Workflow {workflow_id} timed out")
                
                # Clean up completed workflows older than 24 hours
                cutoff_time = current_time - timedelta(hours=24)
                for workflow_id, workflow in list(self.active_workflows.items()):
                    if (workflow["status"] in ["completed", "error", "timeout"] and 
                        workflow.get("completed_at", current_time) < cutoff_time):
                        del self.active_workflows[workflow_id]
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in workflow monitoring task: {e}")
                await asyncio.sleep(60)
    
    async def _agent_health_monitoring_task(self):
        """Background task for monitoring agent health"""
        while self.is_active:
            try:
                current_time = datetime.utcnow()
                
                for agent_id, agent_info in self.agent_registry.items():
                    # Check for inactive agents
                    last_heartbeat = agent_info.get("last_heartbeat", current_time)
                    if current_time - last_heartbeat > timedelta(minutes=5):
                        if agent_info["status"] == "active":
                            agent_info["status"] = "inactive"
                            self.logger.warning(f"Agent {agent_id} appears to be inactive")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in agent health monitoring: {e}")
                await asyncio.sleep(30)
    
    async def _performance_monitoring_task(self):
        """Background task for monitoring system performance"""
        while self.is_active:
            try:
                # Calculate and log performance metrics
                await self._calculate_performance_metrics()
                await asyncio.sleep(300)  # Every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in performance monitoring: {e}")
                await asyncio.sleep(300)
    
    def _update_agent_performance(self, agent_id: str, metric: str):
        """Update agent performance metrics"""
        if agent_id not in self.agent_performance:
            self.agent_performance[agent_id] = defaultdict(int)
        
        self.agent_performance[agent_id][metric] += 1
        self.agent_performance[agent_id]["last_update"] = datetime.utcnow()
    
    async def _calculate_performance_metrics(self):
        """Calculate system performance metrics"""
        metrics = {
            "total_agents": len(self.agent_registry),
            "active_agents": len([a for a in self.agent_registry.values() if a["status"] == "active"]),
            "total_workflows": len(self.active_workflows),
            "completed_workflows": len([w for w in self.active_workflows.values() if w["status"] == "completed"]),
            "messages_processed": len(self.message_history),
            "average_workflow_time": self._calculate_average_workflow_time(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Store metrics in database
        try:
            await self.db.system_metrics.insert_one(metrics)
        except Exception as e:
            self.logger.error(f"Error storing performance metrics: {e}")
    
    def _calculate_average_workflow_time(self) -> float:
        """Calculate average workflow completion time"""
        completed_workflows = [w for w in self.active_workflows.values() 
                             if w["status"] == "completed" and "completed_at" in w]
        
        if not completed_workflows:
            return 0.0
        
        total_time = sum(
            (w["completed_at"] - w["created_at"]).total_seconds() 
            for w in completed_workflows
        )
        
        return total_time / len(completed_workflows)
    
    async def _save_performance_metrics(self):
        """Save final performance metrics"""
        final_metrics = {
            "agent_registry": dict(self.agent_registry),
            "agent_performance": dict(self.agent_performance),
            "message_history": list(self.message_history),
            "active_workflows": dict(self.active_workflows),
            "shutdown_time": datetime.utcnow().isoformat()
        }
        
        try:
            await self.db.orchestrator_state.insert_one(final_metrics)
        except Exception as e:
            self.logger.error(f"Error saving performance metrics: {e}")
    
    async def _save_workflow_state(self):
        """Save current workflow state"""
        try:
            for workflow_id, workflow in self.active_workflows.items():
                await self.db.workflow_state.update_one(
                    {"workflow_id": workflow_id},
                    {"$set": workflow},
                    upsert=True
                )
        except Exception as e:
            self.logger.error(f"Error saving workflow state: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            "agents": dict(self.agent_registry),
            "active_workflows": len([w for w in self.active_workflows.values() 
                                   if w["status"] == "started"]),
            "completed_workflows": len([w for w in self.active_workflows.values() 
                                      if w["status"] == "completed"]),
            "messages_in_queue": self.message_queue.qsize(),
            "messages_processed": len(self.message_history),
            "uptime": (datetime.utcnow() - self.last_heartbeat).total_seconds() if self.last_heartbeat else 0
        } 