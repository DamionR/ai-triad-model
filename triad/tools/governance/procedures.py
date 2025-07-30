"""
Organizational Procedures Toolset

Tools for organizational procedures, decision-making processes, and
governance session management with compliance oversight.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass
import logfire
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.toolsets import FunctionToolset
from pydantic_ai.tools import Tool

from .base import GovernanceContext, AuthorityLevel, SecurityLevel
from triad.database.prisma_client import get_prisma_client
from triad.tools.integration.mcp_integration import get_governance_mcp_client
from triad.core.logging import get_logfire_config


class OrganizationalProcedureToolset(FunctionToolset):
    """
    Toolset for organizational procedures, decision-making, and session management.
    
    Provides tools for managing governance sessions, decision processes,
    voting procedures, and maintaining organizational order.
    """
    
    def __init__(self):
        super().__init__()
        self.logger = get_logfire_config()
        self.name = "organizational_procedure"


@OrganizationalProcedureToolset.tool
async def validate_organizational_procedure(
    ctx: RunContext[GovernanceContext],
    procedure_type: str,
    procedure_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Validate organizational procedures according to governance standards.
    
    Args:
        procedure_type: Type of organizational procedure
        procedure_data: Details of the procedure
    
    Returns:
        Procedure validation results
    """
    logger = get_logfire_config()
    
    try:
        validation_result = {
            "procedure_type": procedure_type,
            "is_valid": True,
            "violations": [],
            "warnings": [],
            "recommendations": [],
            "governance_compliance": True,
            "validated_by": ctx.deps.agent_id,
            "validation_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        violations = []
        warnings = []
        recommendations = []
        
        # Validate based on procedure type
        if procedure_type == "decision_process":
            # Check decision process rules
            if "decision_topic" not in procedure_data:
                violations.append("Decision topic is required")
            
            if "stakeholders" not in procedure_data:
                violations.append("Stakeholder list is required")
            
            if procedure_data.get("decision_complexity", "low") == "high" and not procedure_data.get("expert_consultation"):
                warnings.append("High complexity decisions should include expert consultation")
            
            if not procedure_data.get("documentation_plan"):
                recommendations.append("Consider creating decision documentation plan")
        
        elif procedure_type == "stakeholder_consultation":
            # Check consultation rules
            if "consultation_topic" not in procedure_data:
                violations.append("Consultation topic is required")
            
            if "consultation_duration" not in procedure_data:
                warnings.append("No consultation duration specified")
            
            if procedure_data.get("stakeholder_groups") and len(procedure_data["stakeholder_groups"]) == 0:
                warnings.append("No stakeholder groups identified")
        
        elif procedure_type == "approval_process":
            # Check approval procedures
            if "approval_request" not in procedure_data:
                violations.append("Approval request details required")
            
            if "approval_authority" not in procedure_data:
                violations.append("Approval authority must be specified")
            
            valid_authorities = [auth.value for auth in AuthorityLevel]
            if procedure_data.get("approval_authority") not in valid_authorities:
                violations.append(f"Invalid approval authority. Must be one of: {valid_authorities}")
        
        elif procedure_type == "oversight_review":
            # Check oversight requirements
            if "review_scope" not in procedure_data:
                violations.append("Review scope required for oversight")
            
            if not procedure_data.get("compliance_check", False):
                violations.append("Compliance check required for oversight review")
            
            if ctx.deps.authority_level != AuthorityLevel.OVERSEER:
                violations.append("Only overseer authority can conduct oversight review")
        
        # Update validation result
        validation_result["violations"] = violations
        validation_result["warnings"] = warnings
        validation_result["recommendations"] = recommendations
        validation_result["is_valid"] = len(violations) == 0
        validation_result["governance_compliance"] = len(violations) == 0
        
        logger.log_governance_event(
            event_type="procedure_validation",
            data={
                "procedure_type": procedure_type,
                "is_valid": validation_result["is_valid"],
                "violations_count": len(violations),
                "warnings_count": len(warnings),
                "authority": ctx.deps.authority_level.value
            },
            authority=ctx.deps.authority_level.value
        )
        
        return validation_result
        
    except Exception as e:
        logger.log_governance_event(
            event_type="procedure_validation_error",
            data={"error": str(e), "procedure_type": procedure_type, "agent_id": ctx.deps.agent_id},
            authority=ctx.deps.authority_level.value
        )
        raise


@OrganizationalProcedureToolset.tool
async def manage_decision_process(
    ctx: RunContext[GovernanceContext],
    action: str,
    decision_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Manage organizational decision-making processes.
    
    Args:
        action: Action to take (initiate, evaluate, decide, document)
        decision_data: Decision details if initiating or evaluating
    
    Returns:
        Decision process management results
    """
    logger = get_logfire_config()
    
    try:
        management_result = {
            "action": action,
            "status": "success",
            "current_decision": None,
            "pending_decisions": 0,
            "next_steps": [],
            "managed_by": ctx.deps.agent_id,
            "management_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if action == "initiate":
            if not decision_data:
                management_result["status"] = "failed"
                management_result["error"] = "Decision data required for initiation"
                return management_result
            
            # Validate authority for decision initiation
            if ctx.deps.authority_level not in [
                AuthorityLevel.POLICY_MAKER,
                AuthorityLevel.COORDINATOR,
                AuthorityLevel.OVERSEER
            ]:
                management_result["status"] = "failed"
                management_result["error"] = "Insufficient authority for decision initiation"
                return management_result
            
            decision_id = f"DEC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            management_result["current_decision"] = {
                "decision_id": decision_id,
                "topic": decision_data.get("topic", "Organizational decision"),
                "priority": decision_data.get("priority", "normal"),
                "stakeholders": decision_data.get("stakeholders", []),
                "status": "initiated",
                "created_by": ctx.deps.agent_id
            }
            management_result["next_steps"] = [
                "Gather stakeholder input",
                "Evaluate options",
                "Make decision"
            ]
        
        elif action == "evaluate":
            # Evaluate decision options
            management_result["evaluation"] = {
                "options_analyzed": 3,
                "recommendation": "Option 2 - Balanced approach",
                "evaluation_criteria": ["cost", "impact", "feasibility"],
                "risk_assessment": "medium"
            }
            management_result["next_steps"] = ["Present to decision maker", "Prepare implementation plan"]
        
        elif action == "decide":
            # Validate authority for final decision
            if ctx.deps.authority_level not in [
                AuthorityLevel.POLICY_MAKER,
                AuthorityLevel.OVERSEER
            ]:
                management_result["status"] = "failed"
                management_result["error"] = "Insufficient authority for final decision"
                return management_result
            
            management_result["decision"] = {
                "outcome": "approved",
                "rationale": "Meets organizational objectives",
                "implementation_date": "2024-02-01",
                "decided_by": ctx.deps.agent_id
            }
            management_result["next_steps"] = ["Document decision", "Begin implementation"]
        
        elif action == "document":
            management_result["documentation"] = {
                "decision_record_created": True,
                "stakeholders_notified": True,
                "implementation_plan": "attached",
                "review_date": "quarterly"
            }
            management_result["next_steps"] = ["Monitor implementation", "Schedule review"]
        
        logger.log_governance_event(
            event_type="decision_process_managed",
            data={
                "action": action,
                "status": management_result["status"],
                "authority": ctx.deps.authority_level.value
            },
            authority=ctx.deps.authority_level.value
        )
        
        return management_result
        
    except Exception as e:
        logger.log_governance_event(
            event_type="decision_management_error",
            data={"error": str(e), "action": action, "agent_id": ctx.deps.agent_id},
            authority=ctx.deps.authority_level.value
        )
        raise


@OrganizationalProcedureToolset.tool
async def conduct_voting_procedure(
    ctx: RunContext[GovernanceContext],
    motion_text: str,
    voting_method: str = "consensus",
    eligible_voters: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Conduct a voting procedure for organizational decisions.
    
    Args:
        motion_text: Text of the motion being voted on
        voting_method: Method of voting (consensus, majority, unanimous)
        eligible_voters: List of eligible voter IDs
    
    Returns:
        Voting procedure results
    """
    logger = get_logfire_config()
    
    try:
        # Validate authority for conducting votes
        if ctx.deps.authority_level not in [
            AuthorityLevel.COORDINATOR,
            AuthorityLevel.OVERSEER
        ]:
            return {
                "success": False,
                "error": "Insufficient authority for conducting votes",
                "required_authority": "coordinator or overseer"
            }
        
        # Mock voting results - in real implementation would handle actual voting
        voting_result = {
            "motion_text": motion_text,
            "voting_method": voting_method,
            "eligible_voters_count": len(eligible_voters) if eligible_voters else 5,
            "votes_cast": 5,
            "results": {
                "in_favor": 4,
                "against": 1,
                "abstentions": 0
            },
            "outcome": "passed",  # passed, failed, requires_revote
            "vote_percentage": 80.0,
            "quorum_met": True,
            "conducted_by": ctx.deps.agent_id,
            "voting_timestamp": datetime.now(timezone.utc).isoformat(),
            "success": True
        }
        
        # Determine outcome based on voting method
        if voting_method == "unanimous" and voting_result["results"]["against"] > 0:
            voting_result["outcome"] = "failed"
            voting_result["reason"] = "Unanimous consent required"
        elif voting_method == "consensus" and voting_result["vote_percentage"] < 75:
            voting_result["outcome"] = "requires_revote"
            voting_result["reason"] = "Consensus threshold not met"
        elif voting_method == "majority" and voting_result["vote_percentage"] < 50:
            voting_result["outcome"] = "failed"
            voting_result["reason"] = "Majority not achieved"
        
        logger.log_governance_event(
            event_type="voting_conducted",
            data={
                "voting_method": voting_method,
                "outcome": voting_result["outcome"],
                "vote_percentage": voting_result["vote_percentage"],
                "authority": ctx.deps.authority_level.value
            },
            authority=ctx.deps.authority_level.value
        )
        
        return voting_result
        
    except Exception as e:
        logger.log_governance_event(
            event_type="voting_error",
            data={"error": str(e), "motion_text": motion_text[:100], "agent_id": ctx.deps.agent_id},
            authority=ctx.deps.authority_level.value
        )
        raise


@OrganizationalProcedureToolset.tool
async def schedule_governance_session(
    ctx: RunContext[GovernanceContext],
    session_type: str,
    session_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Schedule a governance session or meeting.
    
    Args:
        session_type: Type of session (planning, review, decision, emergency)
        session_data: Session details and requirements
    
    Returns:
        Session scheduling results
    """
    logger = get_logfire_config()
    
    try:
        # Validate authority for scheduling sessions
        if ctx.deps.authority_level not in [
            AuthorityLevel.COORDINATOR,
            AuthorityLevel.OVERSEER,
            AuthorityLevel.ADMINISTRATOR
        ]:
            return {
                "success": False,
                "error": "Insufficient authority for session scheduling",
                "required_authority": "coordinator, overseer, or administrator"  
            }
        
        session_id = f"SES_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        scheduling_result = {
            "session_id": session_id,
            "session_type": session_type,
            "title": session_data.get("title", f"{session_type.title()} Session"),
            "scheduled_date": session_data.get("date", "2024-02-01T10:00:00Z"),
            "duration": session_data.get("duration", "2 hours"),
            "location": session_data.get("location", "Conference Room A"),
            "attendees": session_data.get("attendees", []),
            "agenda_items": session_data.get("agenda", []),
            "required_preparations": [],
            "materials_needed": [],
            "scheduled_by": ctx.deps.agent_id,
            "scheduling_timestamp": datetime.now(timezone.utc).isoformat(),
            "success": True
        }
        
        # Add session-specific requirements
        if session_type == "emergency":
            scheduling_result["priority"] = "urgent"
            scheduling_result["required_preparations"] = ["Emergency protocols review"]
            scheduling_result["duration"] = "1 hour"
        elif session_type == "decision":
            scheduling_result["required_preparations"] = [
                "Review decision materials",
                "Prepare voting procedures"
            ]
            scheduling_result["materials_needed"] = ["Decision documents", "Voting system"]
        elif session_type == "review":
            scheduling_result["required_preparations"] = [
                "Compile review materials",
                "Prepare assessment reports"
            ]
        
        # Send notifications (mock)
        scheduling_result["notifications_sent"] = len(scheduling_result["attendees"])
        
        logger.log_governance_event(
            event_type="session_scheduled",
            data={
                "session_id": session_id,
                "session_type": session_type,
                "attendees_count": len(scheduling_result["attendees"]),
                "authority": ctx.deps.authority_level.value
            },
            authority=ctx.deps.authority_level.value
        )
        
        return scheduling_result
        
    except Exception as e:
        logger.log_governance_event(
            event_type="session_scheduling_error",
            data={"error": str(e), "session_type": session_type, "agent_id": ctx.deps.agent_id},
            authority=ctx.deps.authority_level.value
        )
        raise


@OrganizationalProcedureToolset.tool
async def generate_meeting_minutes(
    ctx: RunContext[GovernanceContext],
    session_id: str,
    meeting_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate meeting minutes for a governance session.
    
    Args:
        session_id: ID of the session
        meeting_data: Meeting details and outcomes
    
    Returns:
        Generated meeting minutes
    """
    logger = get_logfire_config()
    
    try:
        minutes = {
            "session_id": session_id,
            "meeting_title": meeting_data.get("title", "Governance Session"),
            "date": meeting_data.get("date", datetime.now().strftime("%Y-%m-%d")),
            "start_time": meeting_data.get("start_time", "10:00 AM"),
            "end_time": meeting_data.get("end_time", "12:00 PM"),
            "chairperson": meeting_data.get("chairperson", ctx.deps.agent_id),
            "attendees": meeting_data.get("attendees", []),
            "absentees": meeting_data.get("absentees", []),
            "agenda_items": [],
            "decisions_made": [],
            "action_items": [],
            "next_meeting": meeting_data.get("next_meeting", "TBD"),
            "prepared_by": ctx.deps.agent_id,
            "preparation_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Generate agenda items with outcomes
        for i, item in enumerate(meeting_data.get("agenda", []), 1):
            agenda_item = {
                "item_number": i,
                "topic": item.get("topic", f"Agenda Item {i}"),
                "presenter": item.get("presenter", "Chair"),
                "discussion_summary": item.get("summary", "Item discussed and reviewed"),
                "outcome": item.get("outcome", "Information received")
            }
            minutes["agenda_items"].append(agenda_item)
        
        # Generate decisions made
        decisions = meeting_data.get("decisions", [])
        for decision in decisions:
            decision_record = {
                "decision_topic": decision.get("topic", "Decision item"),
                "decision_outcome": decision.get("outcome", "Approved"),
                "vote_result": decision.get("vote", "Consensus"),
                "implementation_date": decision.get("implementation", "TBD")
            }
            minutes["decisions_made"].append(decision_record)
        
        # Generate action items
        actions = meeting_data.get("actions", [])
        for action in actions:
            action_item = {
                "action_description": action.get("description", "Follow up action"),
                "assigned_to": action.get("assignee", "TBD"),
                "due_date": action.get("due_date", "Next meeting"),
                "priority": action.get("priority", "normal")
            }
            minutes["action_items"].append(action_item)
        
        logger.log_governance_event(
            event_type="meeting_minutes_generated",
            data={
                "session_id": session_id,
                "agenda_items": len(minutes["agenda_items"]),
                "decisions": len(minutes["decisions_made"]),
                "actions": len(minutes["action_items"]),
                "authority": ctx.deps.authority_level.value
            },
            authority=ctx.deps.authority_level.value
        )
        
        return minutes
        
    except Exception as e:
        logger.log_governance_event(
            event_type="minutes_generation_error",
            data={"error": str(e), "session_id": session_id, "agent_id": ctx.deps.agent_id},
            authority=ctx.deps.authority_level.value
        )
        raise