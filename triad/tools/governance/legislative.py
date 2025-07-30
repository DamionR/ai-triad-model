"""
Legislative Toolset

Tools for legislative analysis, bill tracking, and parliamentary procedures
with organizational governance integration.
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


class LegislativeToolset(FunctionToolset):
    """
    Toolset for legislative analysis and parliamentary procedures.
    
    Provides tools for bill analysis, amendment tracking, committee management,
    and legislative process automation.
    """
    
    def __init__(self):
        super().__init__()
        self.logger = get_logfire_config()
        self.name = "legislative"


@LegislativeToolset.tool
async def track_bill_progress(
    ctx: RunContext[GovernanceContext],
    bill_number: str,
    current_stage: str
) -> Dict[str, Any]:
    """
    Track the progress of a bill through governance stages.
    
    Args:
        bill_number: Official bill number
        current_stage: Current stage of the bill
    
    Returns:
        Bill progress tracking information
    """
    logger = get_logfire_config()
    
    try:
        # Governance stages for organizational processes
        governance_stages = [
            "draft",
            "review",
            "stakeholder_consultation",
            "revision",
            "approval",
            "implementation",
            "monitoring"
        ]
        
        try:
            current_index = governance_stages.index(current_stage)
        except ValueError:
            current_index = 0
        
        progress_info = {
            "bill_number": bill_number,
            "current_stage": current_stage,
            "current_stage_index": current_index,
            "total_stages": len(governance_stages),
            "progress_percentage": (current_index / len(governance_stages)) * 100,
            "completed_stages": governance_stages[:current_index],
            "remaining_stages": governance_stages[current_index + 1:],
            "next_stage": governance_stages[current_index + 1] if current_index < len(governance_stages) - 1 else None,
            "estimated_completion": None,  # Would calculate based on historical data
            "tracked_by": ctx.deps.agent_id,
            "tracking_timestamp": datetime.now(timezone.utc).isoformat(),
            "governance_oversight": True
        }
        
        # Add stage-specific information
        stage_info = {
            "draft": "Initial policy/procedure draft created",
            "review": "Internal review and validation",
            "stakeholder_consultation": "Consultation with affected parties",
            "revision": "Incorporate feedback and revisions",
            "approval": "Final approval by authority",
            "implementation": "Deploy and execute policy",
            "monitoring": "Monitor effectiveness and compliance"
        }
        
        progress_info["stage_description"] = stage_info.get(current_stage, "Unknown stage")
        
        # Log bill tracking
        logger.log_governance_event(
            event_type="bill_progress_tracking",
            data={
                "bill_number": bill_number,
                "current_stage": current_stage,
                "progress_percentage": progress_info["progress_percentage"],
                "authority": ctx.deps.authority_level.value
            },
            authority=ctx.deps.authority_level.value
        )
        
        return progress_info
        
    except Exception as e:
        logger.log_governance_event(
            event_type="bill_tracking_error",
            data={"error": str(e), "bill_number": bill_number, "agent_id": ctx.deps.agent_id},
            authority=ctx.deps.authority_level.value
        )
        raise


@LegislativeToolset.tool
async def schedule_committee_review(
    ctx: RunContext[GovernanceContext],
    bill_number: str,
    committee_name: str,
    priority: str = "normal"
) -> Dict[str, Any]:
    """
    Schedule a bill for committee review.
    
    Args:
        bill_number: Official bill number
        committee_name: Name of reviewing committee
        priority: Priority level (urgent, high, normal, low)
    
    Returns:
        Committee scheduling information
    """
    logger = get_logfire_config()
    
    try:
        # Validate authority for scheduling
        if ctx.deps.authority_level not in [
            AuthorityLevel.COORDINATOR,
            AuthorityLevel.OVERSEER,
            AuthorityLevel.POLICY_MAKER
        ]:
            return {
                "success": False,
                "error": "Insufficient authority for committee scheduling",
                "required_authority": "coordinator, overseer, or policy_maker"
            }
        
        # Generate scheduling information
        scheduling_info = {
            "bill_number": bill_number,
            "committee_name": committee_name,
            "priority": priority,
            "estimated_review_duration": "2-4 weeks",  # Based on priority
            "hearing_requirements": [],
            "expert_consultation_needed": True,
            "stakeholder_input_required": False,
            "scheduled_by": ctx.deps.agent_id,
            "scheduling_timestamp": datetime.now(timezone.utc).isoformat(),
            "success": True
        }
        
        # Adjust based on priority
        if priority == "urgent":
            scheduling_info["estimated_review_duration"] = "1-2 weeks"
            scheduling_info["hearing_requirements"] = ["expedited_review"]
        elif priority == "high":
            scheduling_info["estimated_review_duration"] = "2-3 weeks"
        elif priority == "low":
            scheduling_info["estimated_review_duration"] = "4-8 weeks"
        
        # Determine if stakeholder input is needed
        complex_bills = ["budget", "policy", "organizational", "process"]
        if any(term in bill_number.lower() for term in complex_bills):
            scheduling_info["stakeholder_input_required"] = True
            scheduling_info["estimated_review_duration"] = "6-12 weeks"
        
        logger.log_governance_event(
            event_type="committee_review_scheduled",
            data={
                "bill_number": bill_number,
                "committee": committee_name,
                "priority": priority,
                "authority": ctx.deps.authority_level.value
            },
            authority=ctx.deps.authority_level.value
        )
        
        return scheduling_info
        
    except Exception as e:
        logger.log_governance_event(
            event_type="committee_scheduling_error",
            data={"error": str(e), "bill_number": bill_number, "agent_id": ctx.deps.agent_id},
            authority=ctx.deps.authority_level.value
        )
        raise


@LegislativeToolset.tool
async def analyze_amendment_impact(
    ctx: RunContext[GovernanceContext],
    bill_number: str,
    amendment_text: str,
    amendment_type: str = "modification"
) -> Dict[str, Any]:
    """
    Analyze the impact of a proposed amendment.
    
    Args:
        bill_number: Bill being amended
        amendment_text: Text of the proposed amendment
        amendment_type: Type of amendment (addition, modification, deletion)
    
    Returns:
        Amendment impact analysis
    """
    logger = get_logfire_config()
    
    try:
        # Basic impact analysis
        impact_analysis = {
            "bill_number": bill_number,
            "amendment_type": amendment_type,
            "impact_level": "medium",  # low, medium, high, critical
            "affected_sections": [],
            "stakeholder_impact": {},
            "implementation_complexity": "moderate",
            "estimated_cost": "low",
            "timeline_impact": "minimal",
            "recommendations": [],
            "analyzed_by": ctx.deps.agent_id,
            "analysis_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Analyze amendment complexity
        word_count = len(amendment_text.split())
        if word_count > 500:
            impact_analysis["impact_level"] = "high"
            impact_analysis["implementation_complexity"] = "complex"
        elif word_count > 200:
            impact_analysis["impact_level"] = "medium"
        else:
            impact_analysis["impact_level"] = "low"
            impact_analysis["implementation_complexity"] = "simple"
        
        # Check for critical keywords
        critical_keywords = ["authority", "approval", "oversight", "compliance"]
        if any(keyword in amendment_text.lower() for keyword in critical_keywords):
            impact_analysis["impact_level"] = "critical"
            impact_analysis["recommendations"].append("Requires governance review")
        
        # Process impact analysis
        process_keywords = ["process", "procedure", "workflow"]
        if any(keyword in amendment_text.lower() for keyword in process_keywords):
            impact_analysis["timeline_impact"] = "significant"
            impact_analysis["recommendations"].append("Update process documentation")
        
        logger.log_governance_event(
            event_type="amendment_impact_analyzed",
            data={
                "bill_number": bill_number,
                "amendment_type": amendment_type,
                "impact_level": impact_analysis["impact_level"],
                "authority": ctx.deps.authority_level.value
            },
            authority=ctx.deps.authority_level.value
        )
        
        return impact_analysis
        
    except Exception as e:
        logger.log_governance_event(
            event_type="amendment_analysis_error",
            data={"error": str(e), "bill_number": bill_number, "agent_id": ctx.deps.agent_id},
            authority=ctx.deps.authority_level.value
        )
        raise


@LegislativeToolset.tool
async def generate_legislative_summary(
    ctx: RunContext[GovernanceContext],
    bill_number: str,
    bill_text: str,
    summary_type: str = "executive"
) -> Dict[str, Any]:
    """
    Generate a summary of a legislative bill.
    
    Args:
        bill_number: Official bill number
        bill_text: Full text of the bill
        summary_type: Type of summary (executive, technical, public)
    
    Returns:
        Generated bill summary
    """
    logger = get_logfire_config()
    
    try:
        # Generate basic summary metrics
        word_count = len(bill_text.split())
        sections = bill_text.count("Section") + bill_text.count("Article")
        
        summary = {
            "bill_number": bill_number,
            "summary_type": summary_type,
            "word_count": word_count,
            "section_count": sections,
            "complexity_level": "medium",
            "key_provisions": [],
            "stakeholder_impact": {},
            "implementation_timeline": "6 months",
            "executive_summary": "",
            "technical_details": {},
            "public_impact": "",
            "generated_by": ctx.deps.agent_id,
            "generation_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Determine complexity
        if word_count > 10000 or sections > 50:
            summary["complexity_level"] = "high"
            summary["implementation_timeline"] = "12 months"
        elif word_count < 2000 or sections < 10:
            summary["complexity_level"] = "low"
            summary["implementation_timeline"] = "3 months"
        
        # Generate summary based on type
        if summary_type == "executive":
            summary["executive_summary"] = f"This policy document contains {sections} sections addressing organizational governance."
        elif summary_type == "technical":
            summary["technical_details"] = {
                "requirements": "Standard governance procedures",
                "dependencies": "Existing organizational policies",
                "resources_needed": "Moderate"
            }
        elif summary_type == "public":
            summary["public_impact"] = "This policy affects organizational procedures and stakeholder interactions."
        
        # Extract key provisions (simplified)
        key_provisions = []
        if "shall" in bill_text.lower():
            key_provisions.append("Contains mandatory requirements")
        if "may" in bill_text.lower():
            key_provisions.append("Includes discretionary provisions")
        if "authority" in bill_text.lower():
            key_provisions.append("Defines authority levels")
        
        summary["key_provisions"] = key_provisions
        
        logger.log_governance_event(
            event_type="legislative_summary_generated",
            data={
                "bill_number": bill_number,
                "summary_type": summary_type,
                "complexity": summary["complexity_level"],
                "authority": ctx.deps.authority_level.value
            },
            authority=ctx.deps.authority_level.value
        )
        
        return summary
        
    except Exception as e:
        logger.log_governance_event(
            event_type="summary_generation_error",
            data={"error": str(e), "bill_number": bill_number, "agent_id": ctx.deps.agent_id},
            authority=ctx.deps.authority_level.value
        )
        raise


@LegislativeToolset.tool
async def validate_legislative_format(
    ctx: RunContext[GovernanceContext],
    bill_text: str,
    format_standards: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Validate a bill's format against organizational standards.
    
    Args:
        bill_text: Full text of the bill to validate
        format_standards: Optional custom format standards
    
    Returns:
        Format validation results
    """
    logger = get_logfire_config()
    
    try:
        validation_result = {
            "format_valid": True,
            "validation_issues": [],
            "compliance_score": 1.0,
            "required_fixes": [],
            "recommendations": [],
            "validated_by": ctx.deps.agent_id,
            "validation_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        issues = []
        
        # Check for basic structural elements
        if "Purpose:" not in bill_text and "Objective:" not in bill_text:
            issues.append("Missing purpose/objective statement")
        
        if "Section" not in bill_text and "Article" not in bill_text:
            issues.append("No clear section structure")
        
        if "Effective Date" not in bill_text and "Implementation" not in bill_text:
            issues.append("Missing implementation date")
        
        # Check for governance elements
        if "Authority" not in bill_text and "Responsibility" not in bill_text:
            issues.append("Authority/responsibility not clearly defined")
        
        # Calculate compliance score
        total_checks = 4
        compliance_score = max(0.0, (total_checks - len(issues)) / total_checks)
        
        validation_result["validation_issues"] = issues
        validation_result["compliance_score"] = compliance_score
        validation_result["format_valid"] = len(issues) == 0
        
        if issues:
            validation_result["required_fixes"] = [
                "Add missing structural elements",
                "Define authority and responsibility",
                "Include implementation timeline"
            ]
        
        logger.log_governance_event(
            event_type="legislative_format_validated",
            data={
                "format_valid": validation_result["format_valid"],
                "compliance_score": compliance_score,
                "issues_count": len(issues),
                "authority": ctx.deps.authority_level.value
            },
            authority=ctx.deps.authority_level.value
        )
        
        return validation_result
        
    except Exception as e:
        logger.log_governance_event(
            event_type="format_validation_error",
            data={"error": str(e), "agent_id": ctx.deps.agent_id},
            authority=ctx.deps.authority_level.value
        )
        raise