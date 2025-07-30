"""
A2A Client Implementation

Client interface for agents to communicate with the A2A broker
following Westminster constitutional principles.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx
import logfire

from .models import TaskRequest, TaskResponse, AgentMessage, ConstitutionalPriority, MessageType


class A2AClient:
    """
    Client for agent-to-agent communication.
    
    Provides interface for agents to send requests, responses,
    and messages through the A2A broker with constitutional oversight.
    """
    
    def __init__(
        self,
        agent_name: str,
        broker_url: str,
        constitutional_authority: str,
        logfire_logger: logfire,
        timeout_seconds: int = 30
    ):
        self.agent_name = agent_name
        self.broker_url = broker_url
        self.constitutional_authority = constitutional_authority
        self.logfire_logger = logfire_logger
        self.timeout_seconds = timeout_seconds
        self.http_client = httpx.AsyncClient(timeout=timeout_seconds)
        
        # Client state
        self.active_requests: Dict[str, TaskRequest] = {}
        self.conversation_contexts: Dict[str, str] = {}  # context_id -> conversation_type
        
        # Constitutional compliance settings
        self.parliamentary_oversight = True
        self.constitutional_review_threshold = ConstitutionalPriority.CONSTITUTIONAL
    
    async def send_task(
        self,
        target_agent: str,
        task_type: str,
        task_description: str,
        task_parameters: Optional[Dict[str, Any]] = None,
        priority: ConstitutionalPriority = ConstitutionalPriority.ROUTINE,
        constitutional_authority_required: bool = False,
        deadline: Optional[datetime] = None,
        context_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send task request to another agent.
        """
        with logfire.span("a2a_send_task") as span:
            span.set_attribute("target_agent", target_agent)
            span.set_attribute("task_type", task_type)
            span.set_attribute("priority", priority.value)
            
            # Create task request
            request = TaskRequest(
                requesting_agent=self.agent_name,
                target_agent=target_agent,
                task_type=task_type,
                task_description=task_description,
                task_parameters=task_parameters or {},
                context_id=context_id,
                priority=priority,
                constitutional_authority_required=constitutional_authority_required,
                parliamentary_oversight=self.parliamentary_oversight,
                crown_notification=priority in [ConstitutionalPriority.CROWN_URGENT, ConstitutionalPriority.EMERGENCY],
                deadline=deadline
            )
            
            # Store active request
            self.active_requests[request.request_id] = request
            
            try:
                # Send to broker
                response = await self.http_client.post(
                    f"{self.broker_url}/task-request",
                    json=request.model_dump(),
                    headers={"X-Agent-Name": self.agent_name}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    await self.logfire_logger.info(
                        "Task request sent successfully",
                        request_id=request.request_id,
                        target_agent=target_agent,
                        constitutional_validated=result.get("constitutional_validated", False)
                    )
                    
                    return {
                        "success": True,
                        "request_id": request.request_id,
                        "broker_response": result
                    }
                else:
                    error_data = response.json() if response.content else {"error": "Unknown error"}
                    
                    await self.logfire_logger.error(
                        "Task request failed",
                        request_id=request.request_id,
                        status_code=response.status_code,
                        error=error_data
                    )
                    
                    return {
                        "success": False,
                        "error": error_data,
                        "status_code": response.status_code
                    }
                    
            except Exception as e:
                await self.logfire_logger.error(
                    "Task request exception",
                    request_id=request.request_id,
                    error=str(e)
                )
                
                return {
                    "success": False,
                    "error": str(e)
                }
    
    async def send_response(
        self,
        request_id: str,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        execution_time_seconds: Optional[float] = None,
        resources_used: Optional[Dict[str, float]] = None,
        constitutional_compliance: bool = True,
        validation_required: bool = False,
        accuracy_score: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Send response to a task request.
        """
        with logfire.span("a2a_send_response") as span:
            span.set_attribute("request_id", request_id)
            span.set_attribute("status", status)
            
            response = TaskResponse(
                request_id=request_id,
                responding_agent=self.agent_name,
                status=status,
                result=result,
                error_message=error_message,
                execution_time_seconds=execution_time_seconds,
                resources_used=resources_used or {},
                constitutional_compliance=constitutional_compliance,
                validation_required=validation_required,
                ministerial_responsibility_accepted=True,  # Agent accepts responsibility
                accuracy_score=accuracy_score
            )
            
            try:
                # Send response to broker
                http_response = await self.http_client.post(
                    f"{self.broker_url}/task-response",
                    json=response.model_dump(),
                    headers={"X-Agent-Name": self.agent_name}
                )
                
                if http_response.status_code == 200:
                    result_data = http_response.json()
                    
                    await self.logfire_logger.info(
                        "Task response sent successfully",
                        response_id=response.response_id,
                        request_id=request_id,
                        status=status
                    )
                    
                    return {
                        "success": True,
                        "response_id": response.response_id,
                        "broker_response": result_data
                    }
                else:
                    error_data = http_response.json() if http_response.content else {"error": "Unknown error"}
                    
                    await self.logfire_logger.error(
                        "Task response failed",
                        response_id=response.response_id,
                        status_code=http_response.status_code,
                        error=error_data
                    )
                    
                    return {
                        "success": False,
                        "error": error_data
                    }
                    
            except Exception as e:
                await self.logfire_logger.error(
                    "Task response exception",
                    response_id=response.response_id,
                    error=str(e)
                )
                
                return {
                    "success": False,
                    "error": str(e)
                }
    
    async def send_message(
        self,
        recipient_agent: Optional[str],
        subject: str,
        content: str,
        message_type: MessageType = MessageType.STATUS_UPDATE,
        structured_data: Optional[Dict[str, Any]] = None,
        priority: ConstitutionalPriority = ConstitutionalPriority.ROUTINE,
        requires_response: bool = False,
        response_deadline: Optional[datetime] = None,
        broadcast: bool = False,
        context_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send message to another agent or broadcast.
        """
        with logfire.span("a2a_send_message") as span:
            span.set_attribute("recipient_agent", recipient_agent or "broadcast")
            span.set_attribute("message_type", message_type.value)
            span.set_attribute("priority", priority.value)
            
            message = AgentMessage(
                message_type=message_type,
                sender_agent=self.agent_name,
                recipient_agent=recipient_agent,
                subject=subject,
                content=content,
                structured_data=structured_data or {},
                constitutional_authority=self.constitutional_authority,
                requires_response=requires_response,
                response_deadline=response_deadline,
                priority=priority,
                broadcast=broadcast,
                crown_copy=priority in [ConstitutionalPriority.CROWN_URGENT, ConstitutionalPriority.EMERGENCY]
            )
            
            try:
                endpoint = "/broadcast" if broadcast else "/message"
                http_response = await self.http_client.post(
                    f"{self.broker_url}{endpoint}",
                    json=message.model_dump(),
                    headers={"X-Agent-Name": self.agent_name}
                )
                
                if http_response.status_code == 200:
                    result = http_response.json()
                    
                    await self.logfire_logger.info(
                        "Message sent successfully",
                        message_id=message.message_id,
                        recipient=recipient_agent or "broadcast",
                        message_type=message_type.value
                    )
                    
                    return {
                        "success": True,
                        "message_id": message.message_id,
                        "broker_response": result
                    }
                else:
                    error_data = http_response.json() if http_response.content else {"error": "Unknown error"}
                    
                    return {
                        "success": False,
                        "error": error_data
                    }
                    
            except Exception as e:
                await self.logfire_logger.error(
                    "Message send exception",
                    message_id=message.message_id,
                    error=str(e)
                )
                
                return {
                    "success": False,
                    "error": str(e)
                }
    
    async def start_conversation(
        self,
        conversation_type: str,
        participants: List[str],
        topic: str
    ) -> Dict[str, Any]:
        """
        Start multi-agent conversation.
        """
        with logfire.span("a2a_start_conversation") as span:
            span.set_attribute("conversation_type", conversation_type)
            span.set_attribute("participants_count", len(participants))
            
            conversation_data = {
                "conversation_type": conversation_type,
                "participants": participants,
                "initiated_by": self.agent_name,
                "topic": topic
            }
            
            try:
                response = await self.http_client.post(
                    f"{self.broker_url}/conversation/start",
                    json=conversation_data,
                    headers={"X-Agent-Name": self.agent_name}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    context_id = result.get("context_id")
                    
                    if context_id:
                        self.conversation_contexts[context_id] = conversation_type
                    
                    await self.logfire_logger.info(
                        "Conversation started",
                        context_id=context_id,
                        conversation_type=conversation_type
                    )
                    
                    return {
                        "success": True,
                        "context_id": context_id,
                        "broker_response": result
                    }
                else:
                    error_data = response.json() if response.content else {"error": "Unknown error"}
                    
                    return {
                        "success": False,
                        "error": error_data
                    }
                    
            except Exception as e:
                await self.logfire_logger.error(
                    "Conversation start exception",
                    error=str(e)
                )
                
                return {
                    "success": False,
                    "error": str(e)
                }
    
    async def send_in_conversation(
        self,
        context_id: str,
        message_content: str,
        message_type: MessageType = MessageType.STATUS_UPDATE,
        structured_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send message within existing conversation.
        """
        return await self.send_message(
            recipient_agent=None,  # Will be routed to conversation participants
            subject=f"Conversation: {self.conversation_contexts.get(context_id, 'Unknown')}",
            content=message_content,
            message_type=message_type,
            structured_data=structured_data,
            context_id=context_id
        )
    
    async def request_question_period(
        self,
        target_agent: str,
        questions: List[str],
        constitutional_challenge: bool = False
    ) -> Dict[str, Any]:
        """
        Request formal Question Period with another agent.
        """
        return await self.send_task(
            target_agent=target_agent,
            task_type="question_period",
            task_description="Formal Question Period requested",
            task_parameters={
                "questions": questions,
                "constitutional_challenge": constitutional_challenge,
                "parliamentary_procedure": "question_period"
            },
            priority=ConstitutionalPriority.PARLIAMENTARY,
            constitutional_authority_required=constitutional_challenge
        )
    
    async def respond_to_question_period(
        self,
        request_id: str,
        responses: List[str],
        constitutional_compliance: bool = True
    ) -> Dict[str, Any]:
        """
        Respond to Question Period request.
        """
        return await self.send_response(
            request_id=request_id,
            status="completed",
            result={
                "responses": responses,
                "parliamentary_procedure": "question_period_response",
                "ministerial_accountability": True
            },
            constitutional_compliance=constitutional_compliance
        )
    
    async def request_collective_decision(
        self,
        proposal: Dict[str, Any],
        required_participants: List[str]
    ) -> Dict[str, Any]:
        """
        Request collective cabinet decision.
        """
        context_id = await self.start_conversation(
            conversation_type="collective_decision",
            participants=required_participants,
            topic=f"Collective Decision: {proposal.get('title', 'Proposal')}"
        )
        
        if context_id.get("success"):
            return await self.send_in_conversation(
                context_id=context_id["context_id"],
                message_content=f"Collective decision required: {proposal}",
                message_type=MessageType.COLLECTIVE_DECISION,
                structured_data={"proposal": proposal}
            )
        
        return context_id
    
    async def notify_constitutional_violation(
        self,
        violation_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Notify system of constitutional violation.
        """
        return await self.send_message(
            recipient_agent="overwatch_agent",
            subject="Constitutional Violation Detected",
            content=f"Constitutional violation: {violation_details.get('description', 'Unknown violation')}",
            message_type=MessageType.CONSTITUTIONAL_ALERT,
            structured_data=violation_details,
            priority=ConstitutionalPriority.CONSTITUTIONAL,
            requires_response=True
        )
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """
        Get status of this agent's message queue.
        """
        try:
            response = await self.http_client.get(
                f"{self.broker_url}/queue/{self.agent_name}",
                headers={"X-Agent-Name": self.agent_name}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def acknowledge_message(
        self,
        message_id: str
    ) -> Dict[str, Any]:
        """
        Acknowledge receipt of message.
        """
        try:
            response = await self.http_client.post(
                f"{self.broker_url}/acknowledge/{message_id}",
                headers={"X-Agent-Name": self.agent_name}
            )
            
            return {
                "success": response.status_code == 200,
                "message_id": message_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def close(self) -> None:
        """Clean shutdown of A2A client."""
        # Clear active state
        self.active_requests.clear()
        self.conversation_contexts.clear()
        
        # Close HTTP client
        await self.http_client.aclose()
        
        await self.logfire_logger.info(
            "A2A client shutdown completed",
            agent=self.agent_name
        )