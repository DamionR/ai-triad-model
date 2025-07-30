"""
A2A Broker Implementation

Central broker for agent-to-agent communication with constitutional oversight
and Westminster parliamentary principles.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid
import logfire

from .models import (
    TaskRequest, TaskResponse, AgentMessage, ConversationContext,
    BroadcastMessage, MessageQueue, MessageType, ConstitutionalPriority
)
from .storage import A2AStorage


class A2ABroker:
    """
    Central broker for agent-to-agent communication.
    
    Manages message routing, constitutional oversight,
    and parliamentary accountability for all inter-agent communication.
    """
    
    def __init__(self, storage: A2AStorage, logfire_logger: logfire):
        self.storage = storage
        self.logfire_logger = logfire_logger
        self.active_conversations: Dict[str, ConversationContext] = {}
        self.agent_queues: Dict[str, MessageQueue] = {}
        self.message_handlers: Dict[str, callable] = {}
        self.constitutional_monitor_active = True
        
        # Initialize agent queues for core agents
        self._initialize_agent_queues()
    
    def _initialize_agent_queues(self):
        """Initialize message queues for core agents."""
        core_agents = ["planner_agent", "executor_agent", "evaluator_agent", "overwatch_agent"]
        
        for agent in core_agents:
            self.agent_queues[agent] = MessageQueue(
                agent_name=agent,
                max_queue_size=200 if agent == "overwatch_agent" else 100,
                priority_processing=True
            )
    
    async def send_task_request(
        self,
        request: TaskRequest
    ) -> Dict[str, Any]:
        """
        Send task request to another agent with constitutional oversight.
        """
        with logfire.span("a2a_task_request") as span:
            span.set_attribute("requesting_agent", request.requesting_agent)
            span.set_attribute("target_agent", request.target_agent)
            span.set_attribute("priority", request.priority.value)
            
            # Constitutional validation
            if request.requires_constitutional_review():
                constitutional_check = await self._validate_constitutional_authority(request)
                if not constitutional_check["valid"]:
                    return {
                        "success": False,
                        "error": "Constitutional authority validation failed",
                        "violations": constitutional_check["violations"]
                    }
            
            # Store request
            await self.storage.store_task_request(request)
            
            # Route to target agent
            routing_result = await self._route_message_to_agent(request.target_agent, {
                "type": "task_request",
                "request": request.model_dump(),
                "priority": request.priority.value
            })
            
            # Log to parliamentary record if required
            if request.parliamentary_oversight:
                await self._log_to_parliamentary_record(
                    "task_request_sent",
                    {
                        "request_id": request.request_id,
                        "requesting_agent": request.requesting_agent,
                        "target_agent": request.target_agent,
                        "task_type": request.task_type,
                        "constitutional_oversight": request.constitutional_authority_required
                    }
                )
            
            # Notify Crown if required
            if request.crown_notification:
                await self._notify_crown_of_request(request)
            
            await self.logfire_logger.info(
                "Task request sent via A2A",
                request_id=request.request_id,
                routing_success=routing_result["success"]
            )
            
            return {
                "success": routing_result["success"],
                "request_id": request.request_id,
                "queued_at": datetime.now(timezone.utc).isoformat(),
                "parliamentary_recorded": request.parliamentary_oversight,
                "constitutional_validated": request.requires_constitutional_review()
            }
    
    async def send_task_response(
        self,
        response: TaskResponse
    ) -> Dict[str, Any]:
        """
        Send task response back to requesting agent.
        """
        with logfire.span("a2a_task_response") as span:
            span.set_attribute("response_id", response.response_id)
            span.set_attribute("responding_agent", response.responding_agent)
            
            # Get original request
            original_request = await self.storage.get_task_request(response.request_id)
            if not original_request:
                return {
                    "success": False,
                    "error": "Original request not found"
                }
            
            # Validate ministerial responsibility
            if not response.ministerial_responsibility_accepted:
                await self._trigger_ministerial_accountability(response)
            
            # Store response
            await self.storage.store_task_response(response)
            
            # Route back to requesting agent
            routing_result = await self._route_message_to_agent(original_request.requesting_agent, {
                "type": "task_response",
                "response": response.model_dump(),
                "original_request_id": response.request_id
            })
            
            # Check if validation required
            if response.validation_required:
                await self._request_evaluator_validation(response)
            
            # Log completion
            await self._log_to_parliamentary_record(
                "task_response_received",
                {
                    "response_id": response.response_id,
                    "request_id": response.request_id,
                    "success": response.is_successful(),
                    "constitutional_compliance": response.constitutional_compliance
                }
            )
            
            return {
                "success": routing_result["success"],
                "response_id": response.response_id,
                "delivered_at": datetime.now(timezone.utc).isoformat()
            }
    
    async def broadcast_event(
        self,
        event: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Broadcast event to all relevant agents.
        """
        with logfire.span("a2a_broadcast") as span:
            broadcast_id = f"broadcast_{uuid.uuid4().hex[:8]}"
            span.set_attribute("broadcast_id", broadcast_id)
            span.set_attribute("event_type", event.get("event_type", "unknown"))
            
            broadcast = BroadcastMessage(
                broadcast_id=broadcast_id,
                message_type=MessageType.STATUS_UPDATE,
                sender_agent=event.get("sender", "system"),
                subject=f"System Event: {event.get('event_type', 'Unknown')}",
                content=event.get("description", str(event)),
                priority=ConstitutionalPriority.PARLIAMENTARY if event.get("constitutional_impact") else ConstitutionalPriority.ROUTINE,
                immediate_action_required=event.get("urgent", False)
            )
            
            # Determine target agents
            target_agents = event.get("target_agents", list(self.agent_queues.keys()))
            broadcast.target_agents = target_agents
            
            delivery_results = {}
            
            # Send to each target agent
            for agent in target_agents:
                try:
                    result = await self._route_message_to_agent(agent, {
                        "type": "broadcast",
                        "broadcast": broadcast.model_dump(),
                        "requires_acknowledgment": broadcast.acknowledgment_required
                    })
                    delivery_results[agent] = result["success"]
                    
                    if result["success"]:
                        broadcast.delivered_to.append(agent)
                        
                except Exception as e:
                    delivery_results[agent] = False
                    await self.logfire_logger.error(
                        "Broadcast delivery failed",
                        agent=agent,
                        error=str(e)
                    )
            
            # Store broadcast record
            await self.storage.store_broadcast(broadcast)
            
            # Log to parliamentary record
            await self._log_to_parliamentary_record(
                "system_broadcast",
                {
                    "broadcast_id": broadcast_id,
                    "event_type": event.get("event_type"),
                    "delivery_rate": broadcast.get_delivery_rate(),
                    "agents_reached": len(broadcast.delivered_to)
                }
            )
            
            return {
                "broadcast_id": broadcast_id,
                "delivery_results": delivery_results,
                "successful_deliveries": len(broadcast.delivered_to),
                "total_targets": len(target_agents),
                "delivery_rate": broadcast.get_delivery_rate()
            }
    
    async def broadcast_status_update(
        self,
        status: Dict[str, Any]
    ) -> None:
        """Broadcast status update to interested agents."""
        await self.broadcast_event({
            "event_type": "status_update",
            "sender": status.get("agent", "system"),
            "description": f"Status update: {status.get('status', 'unknown')}",
            "data": status
        })
    
    async def broadcast_emergency(
        self,
        emergency: Dict[str, Any]
    ) -> None:
        """Broadcast emergency message with highest priority."""
        await self.broadcast_event({
            "event_type": "emergency",
            "sender": emergency.get("sender", "overwatch_agent"),
            "description": f"EMERGENCY: {emergency.get('description', 'Critical system event')}",
            "urgent": True,
            "constitutional_impact": True,
            "data": emergency
        })
    
    async def initiate_conversation(
        self,
        conversation_type: str,
        participants: List[str],
        initiated_by: str,
        topic: str
    ) -> ConversationContext:
        """
        Initiate multi-agent conversation with parliamentary oversight.
        """
        with logfire.span("a2a_conversation_init") as span:
            context = ConversationContext(
                conversation_type=conversation_type,
                participants=participants,
                initiated_by=initiated_by,
                current_topic=topic
            )
            
            span.set_attribute("context_id", context.context_id)
            span.set_attribute("participants_count", len(participants))
            
            # Determine constitutional oversight requirements
            if conversation_type in ["collective_decision", "constitutional_review", "crisis_management"]:
                context.constitutional_oversight = True
                context.crown_monitoring = True
            
            self.active_conversations[context.context_id] = context
            
            # Notify participants
            for participant in participants:
                if participant != initiated_by:
                    await self._route_message_to_agent(participant, {
                        "type": "conversation_invitation",
                        "context": context.model_dump(),
                        "initiated_by": initiated_by
                    })
            
            await self.storage.store_conversation_context(context)
            
            await self.logfire_logger.info(
                "Conversation initiated",
                context_id=context.context_id,
                conversation_type=conversation_type,
                participants=participants
            )
            
            return context
    
    async def send_message_in_conversation(
        self,
        context_id: str,
        message: AgentMessage
    ) -> Dict[str, Any]:
        """
        Send message within existing conversation context.
        """
        context = self.active_conversations.get(context_id)
        if not context:
            return {
                "success": False,
                "error": "Conversation context not found"
            }
        
        # Update conversation activity
        context.update_activity()
        
        # Route message to participants
        delivery_results = {}
        for participant in context.participants:
            if participant != message.sender_agent:
                result = await self._route_message_to_agent(participant, {
                    "type": "conversation_message",
                    "message": message.model_dump(),
                    "context_id": context_id
                })
                delivery_results[participant] = result["success"]
        
        # Store message
        await self.storage.store_agent_message(message)
        
        # Log to parliamentary record if required
        if context.parliamentary_record:
            await self._log_to_parliamentary_record(
                "conversation_message",
                {
                    "context_id": context_id,
                    "sender": message.sender_agent,
                    "message_type": message.message_type.value,
                    "constitutional_oversight": context.constitutional_oversight
                }
            )
        
        return {
            "success": True,
            "delivery_results": delivery_results,
            "message_id": message.message_id
        }
    
    async def register_cache_coordination(
        self,
        config: Dict[str, Any]
    ) -> None:
        """Register cache coordination configuration."""
        # Store cache configuration
        await self.storage.store_cache_config(config)
        
        # Broadcast cache configuration to agents
        await self.broadcast_event({
            "event_type": "cache_coordination_update",
            "sender": "a2a_broker",
            "description": "Cache coordination configuration updated",
            "config": config
        })
    
    async def _route_message_to_agent(
        self,
        agent_name: str,
        message: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Route message to specific agent queue.
        """
        if agent_name not in self.agent_queues:
            return {
                "success": False,
                "error": f"Agent {agent_name} not found"
            }
        
        queue = self.agent_queues[agent_name]
        
        # Check if queue is full
        if queue.is_full():
            return {
                "success": False,
                "error": "Agent message queue is full"
            }
        
        # Generate message ID and add to queue
        message_id = f"msg_{uuid.uuid4().hex[:8]}"
        message["message_id"] = message_id
        message["queued_at"] = datetime.now(timezone.utc).isoformat()
        
        queue.pending_messages.append(message_id)
        
        # Store message for retrieval
        await self.storage.store_queued_message(message_id, message)
        
        return {
            "success": True,
            "message_id": message_id,
            "queue_position": len(queue.pending_messages)
        }
    
    async def _validate_constitutional_authority(
        self,
        request: TaskRequest
    ) -> Dict[str, Any]:
        """
        Validate constitutional authority for task request.
        """
        violations = []
        
        # Check agent authority mapping
        authority_map = {
            "planner_agent": ["planning", "policy", "legislation"],
            "executor_agent": ["execution", "implementation", "operation"],  
            "evaluator_agent": ["validation", "compliance", "review"],
            "overwatch_agent": ["monitoring", "oversight", "emergency"]
        }
        
        allowed_tasks = authority_map.get(request.requesting_agent, [])
        
        if request.task_type not in allowed_tasks and request.task_type not in ["communication", "status", "query"]:
            violations.append(f"Agent {request.requesting_agent} lacks authority for task type {request.task_type}")
        
        # Check separation of powers
        if (request.requesting_agent == "planner_agent" and 
            request.target_agent == "executor_agent" and 
            request.task_type == "execution"):
            # This is allowed - legislative directing executive
            pass
        elif (request.requesting_agent == "executor_agent" and 
              request.target_agent == "evaluator_agent" and 
              request.task_type == "validation"):
            # This is allowed - executive requesting judicial review
            pass
        else:
            # Check for potential violations
            if (request.requesting_agent in ["planner_agent", "executor_agent"] and 
                request.target_agent == "evaluator_agent" and 
                request.task_type in ["override", "ignore"]):
                violations.append("Cannot override judicial decisions")
        
        return {
            "valid": len(violations) == 0,
            "violations": violations
        }
    
    async def _log_to_parliamentary_record(
        self,
        event_type: str,
        data: Dict[str, Any]
    ) -> None:
        """Log event to parliamentary record (Hansard)."""
        parliamentary_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "data": data,
            "recorded_by": "a2a_broker",
            "constitutional_oversight": True
        }
        
        await self.storage.store_parliamentary_record(parliamentary_entry)
    
    async def _notify_crown_of_request(
        self,
        request: TaskRequest
    ) -> None:
        """Notify Crown (Overwatch) of important request."""
        crown_notification = {
            "type": "crown_notification",
            "notification_type": "task_request",
            "request_summary": {
                "request_id": request.request_id,
                "requesting_agent": request.requesting_agent,
                "task_type": request.task_type,
                "priority": request.priority.value,
                "constitutional_authority_required": request.constitutional_authority_required
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        await self._route_message_to_agent("overwatch_agent", crown_notification)
    
    async def _trigger_ministerial_accountability(
        self,
        response: TaskResponse
    ) -> None:
        """Trigger ministerial accountability process."""
        accountability_event = {
            "event_type": "ministerial_accountability_triggered",
            "response_id": response.response_id,
            "responding_agent": response.responding_agent,
            "responsibility_declined": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Notify Crown of ministerial responsibility issue
        await self._route_message_to_agent("overwatch_agent", {
            "type": "constitutional_alert",
            "alert_type": "ministerial_responsibility",
            "data": accountability_event
        })
    
    async def _request_evaluator_validation(
        self,
        response: TaskResponse
    ) -> None:
        """Request validation from Evaluator agent."""
        validation_request = TaskRequest(
            requesting_agent="a2a_broker",
            target_agent="evaluator_agent", 
            task_type="validation",
            task_description=f"Validate response {response.response_id}",
            task_parameters={"response_data": response.model_dump()},
            priority=ConstitutionalPriority.CONSTITUTIONAL,
            constitutional_authority_required=True
        )
        
        await self.send_task_request(validation_request)
    
    async def get_agent_queue_status(
        self,
        agent_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get status of agent's message queue."""
        if agent_name not in self.agent_queues:
            return None
        
        queue = self.agent_queues[agent_name]
        return queue.get_queue_health()
    
    async def get_conversation_status(
        self,
        context_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get status of conversation."""
        context = self.active_conversations.get(context_id)
        if not context:
            return None
        
        return {
            "context_id": context_id,
            "status": context.status,
            "participants": context.participants,
            "message_count": context.message_count,
            "last_activity": context.last_activity.isoformat(),
            "constitutional_oversight": context.constitutional_oversight
        }
    
    async def close(self) -> None:
        """Clean shutdown of A2A broker."""
        # Store final state
        for context in self.active_conversations.values():
            await self.storage.store_conversation_context(context)
        
        # Clear active conversations
        self.active_conversations.clear()
        
        await self.logfire_logger.info("A2A broker shutdown completed")