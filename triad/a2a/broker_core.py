"""
A2A Broker Core Implementation

Core broker functionality for agent-to-agent communication with 
governance oversight and organizational accountability.
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


class A2ABrokerCore:
    """
    Core broker for agent-to-agent communication.
    
    Manages message routing, governance oversight,
    and organizational accountability for all inter-agent communication.
    """
    
    def __init__(self, storage: A2AStorage, logfire_logger: logfire):
        self.storage = storage
        self.logfire_logger = logfire_logger
        self.active_conversations: Dict[str, ConversationContext] = {}
        self.agent_queues: Dict[str, MessageQueue] = {}
        self.message_handlers: Dict[str, callable] = {}
        self.governance_monitor_active = True
        
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
    
    async def initialize(self) -> None:
        """Initialize the broker with governance settings."""
        await self.logfire_logger.info(
            "A2A Broker initializing",
            agent_queues=len(self.agent_queues),
            governance_monitor=self.governance_monitor_active
        )
        
        # Initialize message handlers
        self._register_message_handlers()
        
        await self.logfire_logger.info("A2A Broker initialized successfully")
    
    def _register_message_handlers(self):
        """Register message handlers for different message types."""
        self.message_handlers.update({
            MessageType.TASK_REQUEST: self._handle_task_request,
            MessageType.TASK_RESPONSE: self._handle_task_response,
            MessageType.AGENT_MESSAGE: self._handle_agent_message,
            MessageType.BROADCAST: self._handle_broadcast,
            MessageType.CONVERSATION: self._handle_conversation_message
        })
    
    async def _handle_task_request(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming task request."""
        try:
            task_request = TaskRequest(**message)
            
            # Store the request
            await self.storage.store_task_request(task_request)
            
            # Route to appropriate agent
            result = await self._route_message_to_agent(
                task_request.target_agent,
                task_request.model_dump()
            )
            
            await self.logfire_logger.info(
                "Task request handled",
                request_id=task_request.request_id,
                target_agent=task_request.target_agent
            )
            
            return result
            
        except Exception as e:
            await self.logfire_logger.error(
                "Task request handling failed",
                error=str(e),
                message=message
            )
            return {"success": False, "error": str(e)}
    
    async def _handle_task_response(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming task response."""
        try:
            task_response = TaskResponse(**message)
            
            # Store the response
            await self.storage.store_task_response(task_response)
            
            # Route back to requesting agent
            result = await self._route_message_to_agent(
                task_response.requesting_agent,
                task_response.model_dump()
            )
            
            await self.logfire_logger.info(
                "Task response handled",
                response_id=task_response.response_id,
                requesting_agent=task_response.requesting_agent
            )
            
            return result
            
        except Exception as e:
            await self.logfire_logger.error(
                "Task response handling failed",
                error=str(e),
                message=message
            )
            return {"success": False, "error": str(e)}
    
    async def _handle_agent_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general agent message."""
        try:
            agent_message = AgentMessage(**message)
            
            # Store the message
            await self.storage.store_agent_message(agent_message)
            
            # Route to target agent
            result = await self._route_message_to_agent(
                agent_message.target_agent,
                agent_message.model_dump()
            )
            
            await self.logfire_logger.info(
                "Agent message handled",
                message_id=agent_message.message_id,
                from_agent=agent_message.source_agent,
                to_agent=agent_message.target_agent
            )
            
            return result
            
        except Exception as e:
            await self.logfire_logger.error(
                "Agent message handling failed",
                error=str(e),
                message=message
            )
            return {"success": False, "error": str(e)}
    
    async def _handle_broadcast(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle broadcast message."""
        try:
            broadcast = BroadcastMessage(**message)
            
            # Store the broadcast
            await self.storage.store_broadcast(broadcast)
            
            # Route to all agents or specified targets
            targets = broadcast.target_agents or list(self.agent_queues.keys())
            results = []
            
            for target in targets:
                try:
                    result = await self._route_message_to_agent(
                        target,
                        broadcast.model_dump()
                    )
                    results.append({
                        "target": target,
                        "success": result.get("success", True)
                    })
                except Exception as e:
                    results.append({
                        "target": target,
                        "success": False,
                        "error": str(e)
                    })
            
            await self.logfire_logger.info(
                "Broadcast handled",
                broadcast_id=broadcast.broadcast_id,
                targets_count=len(targets),
                successful_deliveries=sum(1 for r in results if r["success"])
            )
            
            return {
                "success": True,
                "broadcast_id": broadcast.broadcast_id,
                "delivery_results": results
            }
            
        except Exception as e:
            await self.logfire_logger.error(
                "Broadcast handling failed",
                error=str(e),
                message=message
            )
            return {"success": False, "error": str(e)}
    
    async def _handle_conversation_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle conversation message."""
        try:
            conversation_id = message.get("conversation_id")
            if not conversation_id:
                return {"success": False, "error": "Missing conversation_id"}
            
            # Get or create conversation context
            context = self.active_conversations.get(conversation_id)
            if not context:
                return {"success": False, "error": "Conversation not found"}
            
            # Add message to conversation
            context.messages.append(message)
            context.last_activity = datetime.now(timezone.utc)
            
            # Update storage
            await self.storage.store_conversation_context(context)
            
            # Route to conversation participants
            for participant in context.participants:
                if participant != message.get("source_agent"):
                    await self._route_message_to_agent(participant, message)
            
            await self.logfire_logger.info(
                "Conversation message handled",
                conversation_id=conversation_id,
                participants=len(context.participants)
            )
            
            return {"success": True, "conversation_id": conversation_id}
            
        except Exception as e:
            await self.logfire_logger.error(
                "Conversation message handling failed",
                error=str(e),
                message=message
            )
            return {"success": False, "error": str(e)}
    
    async def _route_message_to_agent(
        self,
        target_agent: str,
        message: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Route message to target agent's queue."""
        try:
            # Get agent queue
            queue = self.agent_queues.get(target_agent)
            if not queue:
                return {
                    "success": False,
                    "error": f"Agent queue not found: {target_agent}"
                }
            
            # Add message to queue
            queue_result = await queue.enqueue(message)
            
            if not queue_result["success"]:
                return queue_result
            
            await self.logfire_logger.debug(
                "Message routed to agent",
                target_agent=target_agent,
                queue_size=queue.current_size()
            )
            
            return {"success": True, "queued_at": datetime.now(timezone.utc).isoformat()}
            
        except Exception as e:
            await self.logfire_logger.error(
                "Message routing failed",
                target_agent=target_agent,
                error=str(e)
            )
            return {"success": False, "error": str(e)}
    
    async def get_agent_queue_status(self, agent_name: str) -> Dict[str, Any]:
        """Get status of agent's message queue."""
        queue = self.agent_queues.get(agent_name)
        if not queue:
            return {"error": f"Agent queue not found: {agent_name}"}
        
        return {
            "agent_name": agent_name,
            "current_size": queue.current_size(),
            "max_size": queue.max_queue_size,
            "priority_processing": queue.priority_processing,
            "last_activity": queue.last_activity.isoformat() if queue.last_activity else None
        }
    
    async def get_all_queue_status(self) -> Dict[str, Any]:
        """Get status of all agent queues."""
        status = {}
        for agent_name in self.agent_queues.keys():
            status[agent_name] = await self.get_agent_queue_status(agent_name)
        return status
    
    async def get_conversation_status(self, conversation_id: str) -> Dict[str, Any]:
        """Get status of a conversation."""
        context = self.active_conversations.get(conversation_id)
        if not context:
            return {"error": f"Conversation not found: {conversation_id}"}
        
        return {
            "conversation_id": conversation_id,
            "participants": context.participants,
            "message_count": len(context.messages),
            "started_at": context.started_at.isoformat(),
            "last_activity": context.last_activity.isoformat() if context.last_activity else None,
            "governance_context": context.governance_context
        }
    
    async def close(self) -> None:
        """Close the broker and cleanup resources."""
        await self.logfire_logger.info("A2A Broker shutting down")
        
        # Clear active conversations
        self.active_conversations.clear()
        
        # Clear agent queues
        for queue in self.agent_queues.values():
            await queue.clear()
        
        self.agent_queues.clear()
        
        await self.logfire_logger.info("A2A Broker shutdown complete")