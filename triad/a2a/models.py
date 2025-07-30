"""
A2A Communication Models

Data models for agent-to-agent communication with constitutional oversight.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from enum import Enum
import uuid


class MessageType(str, Enum):
    """Types of A2A messages."""
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    STATUS_UPDATE = "status_update"
    CONSTITUTIONAL_ALERT = "constitutional_alert"
    QUESTION_PERIOD = "question_period"
    COLLECTIVE_DECISION = "collective_decision"
    EMERGENCY_BROADCAST = "emergency_broadcast"


class MessageStatus(str, Enum):
    """Status of A2A messages."""
    PENDING = "pending"
    DELIVERED = "delivered"
    ACKNOWLEDGED = "acknowledged"
    PROCESSED = "processed"
    FAILED = "failed"
    EXPIRED = "expired"


class ConstitutionalPriority(str, Enum):
    """Constitutional priority levels for messages."""
    ROUTINE = "routine"
    PARLIAMENTARY = "parliamentary"
    CONSTITUTIONAL = "constitutional"
    CROWN_URGENT = "crown_urgent"
    EMERGENCY = "emergency"


class TaskRequest(BaseModel):
    """Request for another agent to perform a task."""
    request_id: str = Field(default_factory=lambda: f"req_{uuid.uuid4().hex[:8]}")
    requesting_agent: str = Field(..., description="Agent making the request")
    target_agent: str = Field(..., description="Agent receiving the request")
    
    # Task details
    task_type: str = Field(..., description="Type of task requested")
    task_description: str = Field(..., description="Detailed task description")
    task_parameters: Dict[str, Any] = Field(default_factory=dict, description="Task parameters")
    
    # Context and conversation
    context_id: Optional[str] = Field(None, description="Conversation context ID")
    parent_request_id: Optional[str] = Field(None, description="Parent request if this is a follow-up")
    
    # Constitutional oversight
    constitutional_authority_required: bool = Field(default=False, description="Requires constitutional validation")
    parliamentary_oversight: bool = Field(default=True, description="Subject to parliamentary oversight")
    crown_notification: bool = Field(default=False, description="Requires Crown notification")
    
    # Priority and timing
    priority: ConstitutionalPriority = Field(default=ConstitutionalPriority.ROUTINE)
    deadline: Optional[datetime] = Field(None, description="Task deadline")
    max_execution_time_minutes: int = Field(default=60, description="Maximum execution time")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    parliamentary_session_id: Optional[str] = Field(None, description="Current parliamentary session")
    
    def requires_urgent_handling(self) -> bool:
        """Check if request requires urgent handling."""
        return self.priority in [ConstitutionalPriority.CROWN_URGENT, ConstitutionalPriority.EMERGENCY]
    
    def requires_constitutional_review(self) -> bool:
        """Check if request requires constitutional review."""
        return self.constitutional_authority_required or self.crown_notification


class TaskResponse(BaseModel):
    """Response to a task request."""
    response_id: str = Field(default_factory=lambda: f"resp_{uuid.uuid4().hex[:8]}")
    request_id: str = Field(..., description="Original request ID")
    responding_agent: str = Field(..., description="Agent providing response")
    
    # Response details
    status: str = Field(..., description="Response status: completed, failed, partial")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result data")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    # Execution metadata
    execution_time_seconds: Optional[float] = Field(None, description="Time taken to execute")
    resources_used: Dict[str, float] = Field(default_factory=dict, description="Resources consumed")
    
    # Constitutional compliance
    constitutional_compliance: bool = Field(default=True, description="Constitutional compliance status")
    validation_required: bool = Field(default=False, description="Requires evaluator validation")
    ministerial_responsibility_accepted: bool = Field(default=True, description="Minister accepts responsibility")
    
    # Quality metrics
    accuracy_score: Optional[float] = Field(None, description="Accuracy score if available")
    confidence_level: float = Field(default=0.9, description="Confidence in result")
    
    # Timestamps
    completed_at: datetime = Field(default_factory=datetime.utcnow)
    
    def is_successful(self) -> bool:
        """Check if response indicates successful completion."""
        return self.status == "completed" and not self.error_message


class AgentMessage(BaseModel):
    """General message between agents."""
    message_id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:8]}")
    message_type: MessageType = Field(..., description="Type of message")
    
    # Sender and recipient
    sender_agent: str = Field(..., description="Sending agent")
    recipient_agent: Optional[str] = Field(None, description="Specific recipient (None for broadcast)")
    
    # Message content
    subject: str = Field(..., description="Message subject")
    content: str = Field(..., description="Message content")
    structured_data: Dict[str, Any] = Field(default_factory=dict, description="Structured message data")
    
    # Constitutional context
    constitutional_authority: str = Field(..., description="Constitutional authority of sender")
    parliamentary_procedure: Optional[str] = Field(None, description="Related parliamentary procedure")
    requires_response: bool = Field(default=False, description="Requires response")
    response_deadline: Optional[datetime] = Field(None, description="Response deadline")
    
    # Message routing
    priority: ConstitutionalPriority = Field(default=ConstitutionalPriority.ROUTINE)
    broadcast: bool = Field(default=False, description="Broadcast to all agents")
    crown_copy: bool = Field(default=False, description="Copy Crown on message")
    
    # Status tracking
    status: MessageStatus = Field(default=MessageStatus.PENDING)
    delivered_at: Optional[datetime] = Field(None, description="Delivery timestamp")
    acknowledged_at: Optional[datetime] = Field(None, description="Acknowledgment timestamp")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="Message expiration")
    
    def is_expired(self) -> bool:
        """Check if message has expired."""
        if not self.expires_at:
            return False
        return datetime.now(timezone.utc) > self.expires_at
    
    def requires_immediate_attention(self) -> bool:
        """Check if message requires immediate attention."""
        return (
            self.priority in [ConstitutionalPriority.CROWN_URGENT, ConstitutionalPriority.EMERGENCY] or
            self.message_type in [MessageType.CONSTITUTIONAL_ALERT, MessageType.EMERGENCY_BROADCAST]
        )


class ConversationContext(BaseModel):
    """Context for ongoing agent conversations."""
    context_id: str = Field(default_factory=lambda: f"ctx_{uuid.uuid4().hex[:8]}")
    conversation_type: str = Field(..., description="Type of conversation")
    
    # Participants
    participants: List[str] = Field(..., description="Participating agents")
    initiated_by: str = Field(..., description="Agent who initiated conversation")
    
    # Conversation state
    status: str = Field(default="active", description="Conversation status")
    current_topic: Optional[str] = Field(None, description="Current discussion topic")
    
    # Constitutional oversight
    constitutional_oversight: bool = Field(default=True, description="Under constitutional oversight")
    parliamentary_record: bool = Field(default=True, description="Record in parliamentary Hansard")
    crown_monitoring: bool = Field(default=False, description="Crown monitoring required")
    
    # Message history
    message_count: int = Field(default=0, description="Number of messages in conversation")
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    parliamentary_session_id: Optional[str] = Field(None, description="Parliamentary session")
    
    def is_active(self) -> bool:
        """Check if conversation is active."""
        return self.status == "active"
    
    def add_participant(self, agent: str) -> None:
        """Add participant to conversation."""
        if agent not in self.participants:
            self.participants.append(agent)
    
    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.now(timezone.utc)
        self.message_count += 1


class BroadcastMessage(BaseModel):
    """System-wide broadcast message."""
    broadcast_id: str = Field(default_factory=lambda: f"broadcast_{uuid.uuid4().hex[:8]}")
    message_type: MessageType = Field(..., description="Type of broadcast")
    
    # Broadcast details
    sender_agent: str = Field(..., description="Broadcasting agent")
    subject: str = Field(..., description="Broadcast subject")
    content: str = Field(..., description="Broadcast content")
    
    # Targeting
    target_agents: Optional[List[str]] = Field(None, description="Specific target agents (None for all)")
    constitutional_authorities: Optional[List[str]] = Field(None, description="Target by authority")
    
    # Priority and handling
    priority: ConstitutionalPriority = Field(..., description="Broadcast priority")
    immediate_action_required: bool = Field(default=False, description="Requires immediate action")
    parliamentary_notification: bool = Field(default=True, description="Notify parliament")
    
    # Response requirements
    acknowledgment_required: bool = Field(default=True, description="Requires acknowledgment")
    response_required: bool = Field(default=False, description="Requires response")
    response_deadline: Optional[datetime] = Field(None, description="Response deadline")
    
    # Delivery tracking
    delivered_to: List[str] = Field(default_factory=list, description="Agents message was delivered to")
    acknowledged_by: List[str] = Field(default_factory=list, description="Agents who acknowledged")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="Broadcast expiration")
    
    def get_delivery_rate(self) -> float:
        """Calculate delivery rate."""
        if not self.target_agents:
            return 0.0
        return len(self.delivered_to) / len(self.target_agents)
    
    def get_acknowledgment_rate(self) -> float:
        """Calculate acknowledgment rate."""
        if not self.delivered_to:
            return 0.0
        return len(self.acknowledged_by) / len(self.delivered_to)


class MessageQueue(BaseModel):
    """Message queue for agent communication."""
    queue_id: str = Field(default_factory=lambda: f"queue_{uuid.uuid4().hex[:8]}")
    agent_name: str = Field(..., description="Queue owner agent")
    
    # Queue contents
    pending_messages: List[str] = Field(default_factory=list, description="Pending message IDs")
    processing_message: Optional[str] = Field(None, description="Currently processing message ID")
    
    # Queue metrics
    messages_processed: int = Field(default=0, description="Total messages processed")
    messages_failed: int = Field(default=0, description="Failed message processing")
    average_processing_time: float = Field(default=0.0, description="Average processing time")
    
    # Queue status
    status: str = Field(default="active", description="Queue status")
    last_processed: Optional[datetime] = Field(None, description="Last message processed time")
    
    # Configuration
    max_queue_size: int = Field(default=100, description="Maximum queue size")
    priority_processing: bool = Field(default=True, description="Process by priority")
    
    def is_full(self) -> bool:
        """Check if queue is full."""
        return len(self.pending_messages) >= self.max_queue_size
    
    def get_queue_health(self) -> Dict[str, Any]:
        """Get queue health metrics."""
        success_rate = 0.0
        if self.messages_processed > 0:
            success_rate = (self.messages_processed - self.messages_failed) / self.messages_processed
        
        return {
            "queue_size": len(self.pending_messages),
            "capacity_used": len(self.pending_messages) / self.max_queue_size,
            "success_rate": success_rate,
            "average_processing_time": self.average_processing_time,
            "status": self.status
        }