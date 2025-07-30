"""
Database Models for Westminster Parliamentary AI System

SQLAlchemy models for storing constitutional records, parliamentary sessions,
agent decisions, and democratic accountability data.
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, Float, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid


Base = declarative_base()


class ConstitutionalRecordTable(Base):
    """Parliamentary record table (Hansard equivalent)."""
    __tablename__ = "constitutional_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(100), nullable=False, index=True)
    data = Column(JSON, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    constitutional_authority = Column(String(50), nullable=False, index=True)
    parliamentary_session_id = Column(String(100), index=True)
    recorded_by = Column(String(100), nullable=False, default="constitutional_clerk")
    
    # Constitutional metadata
    constitutional_compliance = Column(Boolean, default=True)
    violations = Column(JSON, default=list)
    agent_responsible = Column(String(100), index=True)


class ParliamentarySessionTable(Base):
    """Parliamentary sessions table."""
    __tablename__ = "parliamentary_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    session_number = Column(Integer, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    end_date = Column(DateTime(timezone=True))
    status = Column(String(20), nullable=False, default="active")  # active, prorogued, dissolved
    
    # Government composition
    government_agents = Column(JSON, default=list)
    opposition_agents = Column(JSON, default=list)
    
    # Session metadata
    total_decisions = Column(Integer, default=0)
    constitutional_compliance_score = Column(Float, default=1.0)
    major_decisions = Column(JSON, default=list)
    
    # Relationships
    constitutional_records = relationship("ConstitutionalRecordTable", 
                                        foreign_keys="ConstitutionalRecordTable.parliamentary_session_id",
                                        primaryjoin="ParliamentarySessionTable.session_id == ConstitutionalRecordTable.parliamentary_session_id")


class WorkflowTable(Base):
    """Workflows created by Planner Agent."""
    __tablename__ = "workflows"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(String(50), nullable=False, default="planned")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True))
    
    # Workflow data
    plan_data = Column(JSON, nullable=False)
    tasks = Column(JSON, default=list)
    dependencies = Column(JSON, default=list)
    
    # Constitutional metadata
    constitutional_authority = Column(String(50), default="legislative")
    parliamentary_session_id = Column(String(100), index=True)
    constitutional_compliance = Column(Boolean, default=True)
    
    # Performance metrics
    estimated_duration_minutes = Column(Integer)
    actual_duration_minutes = Column(Integer)
    resource_requirements = Column(JSON, default=dict)
    metrics = Column(JSON, default=dict)


class TaskExecutionTable(Base):
    """Task executions by Executor Agent."""
    __tablename__ = "task_executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(String(100), unique=True, nullable=False, index=True)
    workflow_id = Column(String(100), nullable=False, index=True)
    
    # Task details
    task_name = Column(String(200), nullable=False)
    task_type = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    
    # Execution timing
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    execution_time_seconds = Column(Float)
    
    # Task data
    input_parameters = Column(JSON, default=dict)
    output_data = Column(JSON, default=dict)
    error_message = Column(Text)
    logs = Column(JSON, default=list)
    
    # Resource usage
    resource_usage = Column(JSON, default=dict)
    cpu_usage_percent = Column(Float)
    memory_usage_mb = Column(Float)
    
    # Constitutional metadata
    constitutional_authority = Column(String(50), default="executive")
    ministerial_responsibility = Column(Boolean, default=True)
    collective_cabinet_approval = Column(Boolean, default=False)
    
    # Performance metrics
    success_rate = Column(Float)
    retry_count = Column(Integer, default=0)


class ValidationReportTable(Base):
    """Validation reports by Evaluator Agent."""
    __tablename__ = "validation_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(String(100), unique=True, nullable=False, index=True)
    task_execution_id = Column(String(100), nullable=False, index=True)
    workflow_id = Column(String(100), nullable=False, index=True)
    
    # Validation results
    validation_status = Column(String(50), nullable=False)  # passed, failed, warning
    accuracy_score = Column(Float, nullable=False)
    constitutional_compliance = Column(Boolean, nullable=False, default=True)
    westminster_adherence = Column(Boolean, default=True)
    
    # Detailed validation
    validation_details = Column(JSON, default=dict)
    performance_metrics = Column(JSON, default=dict)
    quality_indicators = Column(JSON, default=dict)
    
    # Recommendations and findings
    recommendations = Column(JSON, default=list)
    passed_validations = Column(JSON, default=list)
    failed_validations = Column(JSON, default=list)
    critical_issues = Column(JSON, default=list)
    
    # Constitutional metadata
    constitutional_authority = Column(String(50), default="judicial")
    constitutional_review_required = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    reviewed_at = Column(DateTime(timezone=True))


class QuestionPeriodTable(Base):
    """Question Period records for parliamentary accountability."""
    __tablename__ = "question_periods"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_period_id = Column(String(100), unique=True, nullable=False, index=True)
    parliamentary_session_id = Column(String(100), nullable=False, index=True)
    
    # Question details
    questioning_agent = Column(String(100), nullable=False, index=True)
    responding_agent = Column(String(100), nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    response_text = Column(Text)
    
    # Parliamentary procedure
    question_type = Column(String(50), default="oral")  # oral, written, supplementary
    constitutional_challenge = Column(Boolean, default=False)
    response_required = Column(Boolean, default=True)
    response_deadline = Column(DateTime(timezone=True))
    
    # Status tracking
    status = Column(String(50), default="pending")  # pending, answered, deferred, withdrawn
    satisfaction_level = Column(String(50))  # satisfied, unsatisfied, requires_follow_up
    
    # Timestamps
    asked_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    answered_at = Column(DateTime(timezone=True))
    
    # Constitutional metadata
    constitutional_authority_challenged = Column(String(50))
    democratic_accountability_score = Column(Float)


class NoConfidenceVoteTable(Base):
    """No confidence votes and parliamentary crises."""
    __tablename__ = "no_confidence_votes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vote_id = Column(String(100), unique=True, nullable=False, index=True)
    parliamentary_session_id = Column(String(100), nullable=False, index=True)
    
    # Vote details
    target_agent = Column(String(100), nullable=False, index=True)
    initiating_agent = Column(String(100), nullable=False, index=True)
    reasons = Column(JSON, nullable=False)
    
    # Vote results
    votes_cast = Column(JSON, default=dict)  # {agent: vote}
    motion_passed = Column(Boolean)
    confidence_maintained = Column(Boolean)
    
    # Constitutional implications
    constitutional_crisis_triggered = Column(Boolean, default=False)
    crown_intervention_required = Column(Boolean, default=False)
    resolution_action = Column(String(100))  # dismiss, resign, maintain
    
    # Timestamps
    motion_introduced = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    vote_completed = Column(DateTime(timezone=True))
    crisis_resolved = Column(DateTime(timezone=True))


class CrownInterventionTable(Base):
    """Crown reserve power exercises and constitutional interventions."""
    __tablename__ = "crown_interventions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    intervention_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Intervention details
    prerogative_type = Column(String(50), nullable=False)  # dismiss, dissolve, emergency, assent
    constitutional_justification = Column(Text, nullable=False)
    affected_agents = Column(JSON, default=list)
    
    # Authority and execution
    exercised_by = Column(String(100), default="overwatch_agent")
    constitutional_authority = Column(String(50), default="crown")
    intervention_scope = Column(String(50))  # system, agent, session, emergency
    
    # Results and impact
    intervention_successful = Column(Boolean)
    constitutional_order_restored = Column(Boolean)
    government_changes = Column(JSON, default=dict)
    
    # Timestamps
    crisis_detected = Column(DateTime(timezone=True))
    intervention_executed = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    resolution_confirmed = Column(DateTime(timezone=True))
    
    # Parliamentary notification
    parliament_notified = Column(Boolean, default=False)
    public_announcement = Column(Text)


class SystemHealthTable(Base):
    """System health monitoring by Overwatch Agent."""
    __tablename__ = "system_health"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    health_check_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Overall health
    overall_status = Column(String(50), nullable=False)  # healthy, degraded, unhealthy, critical
    health_score = Column(Float, nullable=False)
    constitutional_compliance_score = Column(Float, nullable=False)
    
    # Component health
    component_health = Column(JSON, default=dict)
    agent_statuses = Column(JSON, default=dict)
    performance_metrics = Column(JSON, default=dict)
    
    # Alerts and issues
    active_alerts = Column(JSON, default=list)
    critical_issues = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)
    
    # Parliamentary oversight
    parliamentary_session_id = Column(String(100), index=True)
    crown_notification_required = Column(Boolean, default=False)
    constitutional_intervention_recommended = Column(Boolean, default=False)
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    next_check_due = Column(DateTime(timezone=True))


class AgentPerformanceTable(Base):
    """Agent performance metrics and constitutional compliance."""
    __tablename__ = "agent_performance"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_name = Column(String(100), nullable=False, index=True)
    constitutional_authority = Column(String(50), nullable=False, index=True)
    
    # Performance metrics
    performance_period_start = Column(DateTime(timezone=True), nullable=False)
    performance_period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Core metrics
    tasks_completed = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    average_execution_time = Column(Float, default=0.0)
    error_rate = Column(Float, default=0.0)
    
    # Constitutional compliance
    constitutional_compliance_score = Column(Float, nullable=False, default=1.0)
    westminster_adherence_score = Column(Float, default=1.0)
    democratic_accountability_score = Column(Float, default=1.0)
    
    # Parliamentary engagement
    question_periods_participated = Column(Integer, default=0)
    question_period_response_quality = Column(Float, default=1.0)
    collective_responsibility_compliance = Column(Boolean, default=True)
    
    # Detailed metrics
    performance_breakdown = Column(JSON, default=dict)
    improvement_recommendations = Column(JSON, default=list)
    commendations = Column(JSON, default=list)
    
    # Constitutional standing
    confidence_level = Column(String(50), default="maintained")  # maintained, questioned, lost
    ministerial_standing = Column(String(50), default="good")  # excellent, good, concern, poor
    
    # Timestamps
    evaluated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    next_evaluation_due = Column(DateTime(timezone=True))