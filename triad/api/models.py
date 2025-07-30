"""
API Models for Triad Parliamentary System

Pydantic models for request/response validation with
constitutional compliance and Westminster accountability.
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


class AgentType(str, Enum):
    """Agent types in the Triad Model."""
    PLANNER = "planner_agent"
    EXECUTOR = "executor_agent"
    EVALUATOR = "evaluator_agent"
    OVERWATCH = "overwatch_agent"


class TaskPriority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Base Request/Response Models
class BaseRequest(BaseModel):
    """Base request model with constitutional requirements."""
    requesting_agent: Optional[str] = Field(None, description="Agent making the request for accountability")
    constitutional_oversight: bool = Field(True, description="Enable constitutional oversight")
    parliamentary_accountability: bool = Field(True, description="Enable parliamentary accountability")
    session_id: Optional[str] = Field(None, description="Parliamentary session identifier")


class BaseResponse(BaseModel):
    """Base response model with constitutional validation."""
    success: bool = Field(..., description="Operation success status")
    constitutional_validated: bool = Field(True, description="Constitutional validation performed")
    parliamentary_accountable: bool = Field(True, description="Parliamentary accountability maintained")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    session_id: Optional[str] = Field(None, description="Parliamentary session identifier")


# Task Models
class TaskRequest(BaseRequest):
    """Request to create or execute a task."""
    task_type: str = Field(..., description="Type of task to execute")
    task_description: str = Field(..., description="Detailed task description")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Task parameters")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="Task priority level")
    requires_approval: bool = Field(False, description="Whether task requires ministerial approval")
    target_agent: Optional[AgentType] = Field(None, description="Specific agent to handle task")


class TaskResponse(BaseResponse):
    """Response from task creation or execution."""
    task_id: str = Field(..., description="Unique task identifier")
    assigned_agent: AgentType = Field(..., description="Agent assigned to handle task")
    status: TaskStatus = Field(..., description="Current task status")
    constitutional_compliance: bool = Field(..., description="Constitutional compliance status")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    result: Optional[Dict[str, Any]] = Field(None, description="Task execution result")


# Agent-Specific Models
class PlannerRequest(BaseRequest):
    """Request for Planner Agent (Legislative Branch)."""
    planning_objective: str = Field(..., description="Planning objective or goal")
    requirements: List[str] = Field(default_factory=list, description="Planning requirements")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Planning constraints")
    stakeholders: List[str] = Field(default_factory=list, description="Stakeholders to consider")
    policy_compliance: bool = Field(True, description="Ensure policy compliance")


class PlannerResponse(BaseResponse):
    """Response from Planner Agent."""
    plan_id: str = Field(..., description="Unique plan identifier")
    workflow_plan: Dict[str, Any] = Field(..., description="Generated workflow plan")
    policy_analysis: Dict[str, Any] = Field(..., description="Policy compliance analysis")
    resource_requirements: List[Dict[str, Any]] = Field(default_factory=list, description="Required resources")
    risk_assessment: Dict[str, Any] = Field(..., description="Risk analysis")
    legislative_approval: bool = Field(..., description="Legislative approval status")


class ExecutorRequest(BaseRequest):
    """Request for Executor Agent (Executive Branch)."""
    plan_id: Optional[str] = Field(None, description="Plan to execute")
    execution_steps: List[Dict[str, Any]] = Field(default_factory=list, description="Steps to execute")
    resource_allocation: Dict[str, Any] = Field(default_factory=dict, description="Resource allocation")
    monitoring_requirements: List[str] = Field(default_factory=list, description="Monitoring needs")
    rollback_plan: Optional[Dict[str, Any]] = Field(None, description="Rollback procedure")


class ExecutorResponse(BaseResponse):
    """Response from Executor Agent."""
    execution_id: str = Field(..., description="Unique execution identifier")
    execution_status: Dict[str, Any] = Field(..., description="Execution progress status")
    completed_steps: List[Dict[str, Any]] = Field(default_factory=list, description="Completed steps")
    resource_usage: Dict[str, Any] = Field(..., description="Resource usage statistics")
    performance_metrics: Dict[str, Any] = Field(..., description="Performance measurements")
    executive_accountability: bool = Field(..., description="Executive accountability maintained")


class EvaluatorRequest(BaseRequest):
    """Request for Evaluator Agent (Judicial Branch)."""
    evaluation_target: str = Field(..., description="Target for evaluation")
    evaluation_criteria: List[str] = Field(..., description="Evaluation criteria")
    compliance_standards: List[str] = Field(default_factory=list, description="Compliance standards")
    precedent_analysis: bool = Field(True, description="Include precedent analysis")
    constitutional_review: bool = Field(True, description="Perform constitutional review")


class EvaluatorResponse(BaseResponse):
    """Response from Evaluator Agent."""
    evaluation_id: str = Field(..., description="Unique evaluation identifier")
    compliance_score: float = Field(..., ge=0.0, le=1.0, description="Compliance score (0-1)")
    constitutional_analysis: Dict[str, Any] = Field(..., description="Constitutional compliance analysis")
    violations: List[Dict[str, Any]] = Field(default_factory=list, description="Identified violations")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for improvement")
    judicial_decision: Dict[str, Any] = Field(..., description="Judicial decision and reasoning")


class OverwatchRequest(BaseRequest):
    """Request for Overwatch Agent (Crown/Monitoring)."""
    monitoring_scope: str = Field(..., description="Scope of monitoring")
    monitoring_duration: Optional[int] = Field(None, description="Monitoring duration in minutes")
    alert_thresholds: Dict[str, float] = Field(default_factory=dict, description="Alert thresholds")
    constitutional_monitoring: bool = Field(True, description="Monitor constitutional compliance")
    performance_monitoring: bool = Field(True, description="Monitor system performance")


class OverwatchResponse(BaseResponse):
    """Response from Overwatch Agent."""
    monitoring_id: str = Field(..., description="Unique monitoring identifier")
    system_health: Dict[str, Any] = Field(..., description="System health assessment")
    constitutional_status: Dict[str, Any] = Field(..., description="Constitutional compliance status")
    performance_metrics: Dict[str, Any] = Field(..., description="Performance monitoring data")
    alerts: List[Dict[str, Any]] = Field(default_factory=list, description="Active alerts")
    crown_oversight: Dict[str, Any] = Field(..., description="Crown oversight assessment")


# Parliamentary Models
class ParliamentarySession(BaseModel):
    """Parliamentary session information."""
    session_id: str = Field(..., description="Session identifier")
    session_type: str = Field(..., description="Type of parliamentary session")
    start_time: datetime = Field(..., description="Session start time")
    participants: List[AgentType] = Field(..., description="Participating agents")
    agenda: List[str] = Field(default_factory=list, description="Session agenda")
    constitutional_authority: ConstitutionalAuthority = Field(..., description="Governing authority")


class QuestionPeriod(BaseModel):
    """Parliamentary Question Period."""
    question: str = Field(..., description="Question being asked")
    questioning_agent: AgentType = Field(..., description="Agent asking question")
    responding_agent: AgentType = Field(..., description="Agent expected to respond")
    question_type: str = Field(..., description="Type of question")
    parliamentary_privilege: bool = Field(True, description="Parliamentary privilege applies")


class MotionRequest(BaseRequest):
    """Parliamentary motion request."""
    motion_type: str = Field(..., description="Type of motion")
    motion_text: str = Field(..., description="Motion text")
    proposing_agent: AgentType = Field(..., description="Agent proposing motion")
    requires_vote: bool = Field(True, description="Motion requires vote")
    constitutional_implication: bool = Field(False, description="Has constitutional implications")


class VoteResult(BaseModel):
    """Parliamentary vote result."""
    vote_id: str = Field(..., description="Vote identifier")
    motion_id: str = Field(..., description="Related motion identifier")
    votes_for: int = Field(..., description="Votes in favor")
    votes_against: int = Field(..., description="Votes against")
    abstentions: int = Field(..., description="Abstentions")
    result: str = Field(..., description="Vote result (passed/failed)")
    constitutional_validity: bool = Field(..., description="Constitutional validity")


# System Status Models
class SystemHealthRequest(BaseRequest):
    """System health check request."""
    include_agents: bool = Field(True, description="Include agent health")
    include_performance: bool = Field(True, description="Include performance metrics")
    include_constitutional: bool = Field(True, description="Include constitutional compliance")
    deep_check: bool = Field(False, description="Perform deep health check")


class SystemHealthResponse(BaseResponse):
    """System health check response."""
    overall_health: str = Field(..., description="Overall system health status")
    agent_health: Dict[str, Dict[str, Any]] = Field(..., description="Individual agent health")
    performance_metrics: Dict[str, Any] = Field(..., description="System performance metrics")
    constitutional_compliance: Dict[str, Any] = Field(..., description="Constitutional compliance status")
    active_sessions: int = Field(..., description="Number of active parliamentary sessions")
    system_uptime: float = Field(..., description="System uptime in seconds")


# Error Models
class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = Field(False, description="Always false for errors")
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Human-readable error message")
    constitutional_violation: bool = Field(False, description="Error involves constitutional violation")
    parliamentary_accountability: bool = Field(True, description="Parliamentary accountability maintained")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class ValidationError(BaseModel):
    """Validation error details."""
    field: str = Field(..., description="Field that failed validation")
    message: str = Field(..., description="Validation error message")
    constitutional_requirement: bool = Field(False, description="Is a constitutional requirement")


# Statistics and Reporting Models
class SystemStatistics(BaseModel):
    """System statistics for parliamentary oversight."""
    total_tasks_processed: int = Field(..., description="Total tasks processed")
    successful_tasks: int = Field(..., description="Successfully completed tasks")
    failed_tasks: int = Field(..., description="Failed tasks")
    constitutional_violations: int = Field(..., description="Constitutional violations detected")
    average_response_time: float = Field(..., description="Average response time in seconds")
    agent_utilization: Dict[str, float] = Field(..., description="Agent utilization rates")
    parliamentary_sessions: int = Field(..., description="Number of parliamentary sessions")
    democratic_accountability_score: float = Field(..., ge=0.0, le=1.0, description="Democratic accountability score")


class ConstitutionalReport(BaseModel):
    """Constitutional compliance report."""
    report_id: str = Field(..., description="Report identifier")
    reporting_period: Dict[str, datetime] = Field(..., description="Reporting period")
    overall_compliance_score: float = Field(..., ge=0.0, le=1.0, description="Overall compliance score")
    agent_compliance: Dict[str, float] = Field(..., description="Individual agent compliance scores")
    violations_summary: List[Dict[str, Any]] = Field(..., description="Summary of violations")
    recommendations: List[str] = Field(..., description="Recommendations for improvement")
    constitutional_authority: ConstitutionalAuthority = Field(..., description="Authority issuing report")
    parliamentary_approval: bool = Field(..., description="Parliamentary approval status")