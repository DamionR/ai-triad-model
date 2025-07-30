"""
Pydantic Models for Triad Model Database

Pydantic models that mirror the Prisma schema for type safety
and validation in the Westminster Parliamentary AI System.
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class ConstitutionalAuthority(str, Enum):
    """Constitutional authorities in Westminster system."""
    LEGISLATIVE = "legislative"
    EXECUTIVE = "executive"
    JUDICIAL = "judicial"
    CROWN = "crown"


class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class WorkflowStatus(str, Enum):
    """Workflow status."""
    DRAFT = "draft"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


class ParliamentarySessionStatus(str, Enum):
    """Parliamentary session status."""
    ACTIVE = "active"
    ADJOURNED = "adjourned"
    CLOSED = "closed"


class MessageType(str, Enum):
    """Message types for agent communication."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class VoteChoice(str, Enum):
    """Voting choices."""
    FOR = "for"
    AGAINST = "against"
    ABSTAIN = "abstain"


class CrisisSeverity(str, Enum):
    """Crisis severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Pydantic Models (matching Prisma schema)

class AgentModel(BaseModel):
    """Agent model for constitutional agents."""
    id: str
    name: str
    constitutional_authority: ConstitutionalAuthority
    model: str = "claude-3-5-sonnet-20241022"
    active: bool = True
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TaskModel(BaseModel):
    """Task model for agent tasks."""
    id: str
    type: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    
    requesting_agent_id: str
    assigned_agent_id: str
    
    constitutional_compliance: bool = True
    parliamentary_approval: bool = True
    
    parameters: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    workflow_id: Optional[str] = None
    
    class Config:
        from_attributes = True


class WorkflowModel(BaseModel):
    """Workflow model for multi-step processes."""
    id: str
    name: str
    description: str
    status: WorkflowStatus = WorkflowStatus.DRAFT
    
    objective: str
    requirements: List[str] = Field(default_factory=list)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    stakeholders: List[str] = Field(default_factory=list)
    
    policy_compliance: bool = True
    legislative_approval: bool = False
    
    created_at: datetime
    updated_at: datetime
    approved_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MessageSessionModel(BaseModel):
    """Message session for agent conversations."""
    id: str
    session_id: str
    agent_id: str
    
    constitutional_authority: ConstitutionalAuthority
    parliamentary_session_id: Optional[str] = None
    
    started_at: datetime
    last_activity: datetime
    active: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True


class AgentMessageModel(BaseModel):
    """Agent message in conversation."""
    id: str
    session_id: str
    agent_id: str
    
    message_type: MessageType
    content: Optional[str] = None
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    
    constitutional_validated: bool = True
    parliamentary_context: Optional[Dict[str, Any]] = None
    
    timestamp: datetime
    
    class Config:
        from_attributes = True


class ParliamentarySessionModel(BaseModel):
    """Parliamentary session model."""
    id: str
    session_type: str
    status: ParliamentarySessionStatus = ParliamentarySessionStatus.ACTIVE
    
    start_time: datetime
    end_time: Optional[datetime] = None
    
    agenda: List[str] = Field(default_factory=list)
    participants: List[str] = Field(default_factory=list)
    
    constitutional_authority: ConstitutionalAuthority
    
    class Config:
        from_attributes = True


class ParliamentaryActionModel(BaseModel):
    """Parliamentary action model."""
    id: str
    session_id: str
    agent_id: str
    
    action_type: str
    content: str
    
    constitutional_basis: Optional[str] = None
    parliamentary_privilege: bool = True
    
    timestamp: datetime
    
    class Config:
        from_attributes = True


class QuestionPeriodModel(BaseModel):
    """Question Period model."""
    id: str
    session_id: str
    
    question: str
    questioning_agent: str
    responding_agent: str
    
    answer: Optional[str] = None
    answered_at: Optional[datetime] = None
    
    question_type: str
    parliamentary_privilege: bool = True
    
    created_at: datetime
    
    class Config:
        from_attributes = True


class MotionModel(BaseModel):
    """Parliamentary motion model."""
    id: str
    session_id: str
    
    motion_type: str
    motion_text: str
    proposing_agent: str
    
    requires_vote: bool = True
    constitutional_implication: bool = False
    
    status: str = "proposed"
    
    created_at: datetime
    voted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class VoteModel(BaseModel):
    """Voting record model."""
    id: str
    motion_id: str
    
    voting_agent: str
    vote: VoteChoice
    
    constitutional_validity: bool = True
    
    timestamp: datetime
    
    class Config:
        from_attributes = True


class ConstitutionalReviewModel(BaseModel):
    """Constitutional review model."""
    id: str
    
    review_type: str
    target_id: str
    target_type: str
    
    constitutional_compliant: bool
    violations: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    
    reviewing_agent: str
    constitutional_authority: ConstitutionalAuthority
    
    created_at: datetime
    
    class Config:
        from_attributes = True


class ValidationReportModel(BaseModel):
    """Validation report model."""
    id: str
    
    validation_type: str
    target_id: str
    target_type: str
    
    valid: bool
    score: Optional[float] = None
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    
    validated_by: str
    
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuditLogModel(BaseModel):
    """Audit log model."""
    id: str
    
    event_type: str
    event_data: Dict[str, Any]
    
    agent_id: Optional[str] = None
    task_id: Optional[str] = None
    workflow_id: Optional[str] = None
    
    constitutional_oversight: bool = True
    parliamentary_accountability: bool = True
    
    timestamp: datetime
    
    class Config:
        from_attributes = True


class SystemMetricModel(BaseModel):
    """System metric model."""
    id: str
    
    metric_type: str
    metric_name: str
    value: float
    unit: str
    
    agent_name: Optional[str] = None
    component_name: Optional[str] = None
    
    timestamp: datetime
    
    class Config:
        from_attributes = True


class CrisisEventModel(BaseModel):
    """Crisis event model."""
    id: str
    
    crisis_type: str
    severity: CrisisSeverity
    status: str = "active"
    
    description: str
    affected_components: List[str] = Field(default_factory=list)
    
    crown_intervention: bool = False
    emergency_powers: bool = False
    
    detected_at: datetime
    contained_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    resolution_actions: List[Dict[str, Any]] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


# Request/Response Models for API

class CreateAgentRequest(BaseModel):
    """Request to create a new agent."""
    name: str
    constitutional_authority: ConstitutionalAuthority
    model: str = "claude-3-5-sonnet-20241022"


class CreateTaskRequest(BaseModel):
    """Request to create a new task."""
    type: str
    description: str
    requesting_agent_id: str
    assigned_agent_id: str
    priority: TaskPriority = TaskPriority.MEDIUM
    parameters: Optional[Dict[str, Any]] = None


class UpdateTaskStatusRequest(BaseModel):
    """Request to update task status."""
    status: TaskStatus
    result: Optional[Dict[str, Any]] = None


class CreateMessageSessionRequest(BaseModel):
    """Request to create a message session."""
    session_id: str
    agent_id: str
    constitutional_authority: ConstitutionalAuthority
    parliamentary_session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AddMessageRequest(BaseModel):
    """Request to add a message to session."""
    session_id: str
    agent_id: str
    message_type: MessageType
    content: Optional[str] = None
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    parliamentary_context: Optional[Dict[str, Any]] = None


class CreateParliamentarySessionRequest(BaseModel):
    """Request to create parliamentary session."""
    session_type: str
    constitutional_authority: ConstitutionalAuthority
    agenda: Optional[List[str]] = None
    participants: Optional[List[str]] = None


class RecordParliamentaryActionRequest(BaseModel):
    """Request to record parliamentary action."""
    session_id: str
    agent_id: str
    action_type: str
    content: str
    constitutional_basis: Optional[str] = None


class CreateConstitutionalReviewRequest(BaseModel):
    """Request to create constitutional review."""
    review_type: str
    target_id: str
    target_type: str
    constitutional_compliant: bool
    violations: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    reviewing_agent: str
    constitutional_authority: ConstitutionalAuthority


class LogAuditEventRequest(BaseModel):
    """Request to log audit event."""
    event_type: str
    event_data: Dict[str, Any]
    agent_id: Optional[str] = None
    task_id: Optional[str] = None
    workflow_id: Optional[str] = None


class RecordSystemMetricRequest(BaseModel):
    """Request to record system metric."""
    metric_type: str
    metric_name: str
    value: float
    unit: str
    agent_name: Optional[str] = None
    component_name: Optional[str] = None