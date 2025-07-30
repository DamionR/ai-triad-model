"""
Compliance Toolset

Tools for compliance oversight, validation, and policy analysis.
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import logfire
from pydantic_ai import RunContext
from pydantic_ai.toolsets import AbstractToolset
from pydantic_ai.tools import Tool

from .base import GovernanceContext, AuthorityLevel
from triad.core.logging import get_logfire_config


class ComplianceToolset(AbstractToolset):
    """
    Toolset for compliance oversight and validation.
    
    Provides tools for policy review, compliance checking,
    and crisis management within organizational governance principles.
    """
    
    def __init__(self):
        self.logger = get_logfire_config()
        self.name = "compliance"
        
    async def get_tools(self) -> List[Tool]:
        """Get all compliance oversight tools."""
        return [
            self._create_compliance_validation_tool(),
            self._create_policy_analysis_tool(),
            self._create_crisis_detection_tool(),
            self._create_precedent_lookup_tool(),
            self._create_policy_interpretation_tool()
        ]
    
    def _create_compliance_validation_tool(self) -> Tool:
        """Create tool for compliance validation."""
        
        async def validate_compliance(
            ctx: RunContext[GovernanceContext],
            action_type: str,
            action_data: Dict[str, Any],
            policy_basis: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Validate an action's compliance with organizational policies.
            
            Args:
                action_type: Type of action being validated
                action_data: Details of the action
                policy_basis: Policy authority or precedent
            
            Returns:
                Compliance assessment
            """
            try:
                with self.logger.governance_session_span(
                    "compliance-validation",
                    [ctx.deps.agent_id]
                ) as span:
                    
                    # Validate authority level
                    if ctx.deps.authority_level not in [
                        AuthorityLevel.REVIEWER, 
                        AuthorityLevel.OVERSEER
                    ]:
                        return {
                            "compliant": False,
                            "error": "Insufficient authority for compliance validation",
                            "required_authority": "reviewer or overseer"
                        }
                    
                    # Perform compliance analysis
                    analysis_result = {
                        "compliant": True,
                        "action_type": action_type,
                        "policy_basis": policy_basis,
                        "violations": [],
                        "recommendations": [],
                        "reviewed_by": ctx.deps.agent_id,
                        "review_timestamp": datetime.now(timezone.utc).isoformat()
                    }
                    
                    # Basic compliance checks
                    if not action_data:
                        analysis_result["compliant"] = False
                        analysis_result["violations"].append("No action data provided")
                    
                    # Log compliance check
                    self.logger.log_governance_event(
                        event_type="compliance_validation_completed",
                        data={
                            "action_type": action_type,
                            "compliant": analysis_result["compliant"],
                            "authority": ctx.deps.authority_level.value
                        },
                        authority=ctx.deps.authority_level.value
                    )
                    
                    span.set_attribute("compliance.result", analysis_result["compliant"])
                    span.set_attribute("compliance.action_type", action_type)
                    
                    return analysis_result
                    
            except Exception as e:
                self.logger.log_governance_event(
                    event_type="compliance_validation_error",
                    data={
                        "error": str(e),
                        "action_type": action_type,
                        "agent_id": ctx.deps.agent_id
                    },
                    authority=ctx.deps.authority_level.value
                )
                raise
        
        return Tool(validate_compliance)
    
    def _create_policy_analysis_tool(self) -> Tool:
        """Create tool for policy analysis."""
        
        async def analyze_policy(
            ctx: RunContext[GovernanceContext],
            policy_text: str,
            analysis_type: str = "comprehensive"
        ) -> Dict[str, Any]:
            """
            Analyze policy for compliance and effectiveness.
            
            Args:
                policy_text: The policy text to analyze
                analysis_type: Type of analysis (comprehensive, basic, impact)
            
            Returns:
                Policy analysis results
            """
            try:
                with self.logger.governance_session_span(
                    "policy-analysis", 
                    [ctx.deps.agent_id]
                ) as span:
                    
                    analysis_result = {
                        "analysis_type": analysis_type,
                        "policy_summary": policy_text[:200] + "..." if len(policy_text) > 200 else policy_text,
                        "compliance_score": 0.85,  # Mock score
                        "issues": [],
                        "recommendations": [
                            "Consider stakeholder impact assessment",
                            "Review implementation timeline"
                        ],
                        "analyzed_by": ctx.deps.agent_id,
                        "analysis_timestamp": datetime.now(timezone.utc).isoformat()
                    }
                    
                    # Log analysis
                    self.logger.log_governance_event(
                        event_type="policy_analysis_completed",
                        data={
                            "analysis_type": analysis_type,
                            "compliance_score": analysis_result["compliance_score"],
                            "authority": ctx.deps.authority_level.value
                        },
                        authority=ctx.deps.authority_level.value
                    )
                    
                    return analysis_result
                    
            except Exception as e:
                self.logger.log_governance_event(
                    event_type="policy_analysis_error",
                    data={"error": str(e), "agent_id": ctx.deps.agent_id},
                    authority=ctx.deps.authority_level.value
                )
                raise
        
        return Tool(analyze_policy)
    
    def _create_crisis_detection_tool(self) -> Tool:
        """Create tool for crisis detection."""
        
        async def detect_crisis(
            ctx: RunContext[GovernanceContext],
            indicators: List[str],
            severity_threshold: str = "medium"
        ) -> Dict[str, Any]:
            """
            Detect potential organizational crises.
            
            Args:
                indicators: List of crisis indicators
                severity_threshold: Minimum severity to report
            
            Returns:
                Crisis detection results
            """
            try:
                crisis_detected = len(indicators) > 2  # Simple logic
                severity = "high" if len(indicators) > 4 else "medium" if len(indicators) > 2 else "low"
                
                result = {
                    "crisis_detected": crisis_detected,
                    "severity": severity,
                    "indicators": indicators,
                    "recommended_actions": [
                        "Notify oversight authority",
                        "Activate crisis response protocol"
                    ] if crisis_detected else [],
                    "detected_by": ctx.deps.agent_id,
                    "detection_timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                if crisis_detected:
                    self.logger.log_governance_event(
                        event_type="crisis_detected",
                        data={
                            "severity": severity,
                            "indicators_count": len(indicators),
                            "authority": ctx.deps.authority_level.value
                        },
                        authority=ctx.deps.authority_level.value
                    )
                
                return result
                
            except Exception as e:
                self.logger.log_governance_event(
                    event_type="crisis_detection_error",
                    data={"error": str(e), "agent_id": ctx.deps.agent_id},
                    authority=ctx.deps.authority_level.value
                )
                raise
        
        return Tool(detect_crisis)
    
    def _create_precedent_lookup_tool(self) -> Tool:
        """Create tool for precedent lookup."""
        
        async def lookup_precedent(
            ctx: RunContext[GovernanceContext],
            case_type: str,
            keywords: List[str]
        ) -> Dict[str, Any]:
            """
            Look up organizational precedents.
            
            Args:
                case_type: Type of case to look up
                keywords: Keywords for search
            
            Returns:
                Precedent lookup results
            """
            try:
                # Mock precedent data
                precedents = [
                    {
                        "case_id": "PREC001",
                        "case_type": case_type,
                        "summary": f"Similar case involving {', '.join(keywords[:2])}",
                        "decision": "Approved with conditions",
                        "date": "2024-01-15"
                    }
                ]
                
                result = {
                    "case_type": case_type,
                    "keywords": keywords,
                    "precedents": precedents,
                    "total_found": len(precedents),
                    "looked_up_by": ctx.deps.agent_id,
                    "lookup_timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                return result
                
            except Exception as e:
                self.logger.log_governance_event(
                    event_type="precedent_lookup_error",
                    data={"error": str(e), "agent_id": ctx.deps.agent_id},
                    authority=ctx.deps.authority_level.value
                )
                raise
        
        return Tool(lookup_precedent)
    
    def _create_policy_interpretation_tool(self) -> Tool:
        """Create tool for policy interpretation."""
        
        async def interpret_policy(
            ctx: RunContext[GovernanceContext],
            policy_reference: str,
            specific_question: str
        ) -> Dict[str, Any]:
            """
            Interpret policy for specific situations.
            
            Args:
                policy_reference: Reference to the policy
                specific_question: Specific question about the policy
            
            Returns:
                Policy interpretation results
            """
            try:
                result = {
                    "policy_reference": policy_reference,
                    "question": specific_question,
                    "interpretation": f"Based on {policy_reference}, the recommended approach is to follow standard procedures with appropriate oversight.",
                    "confidence": 0.8,
                    "applicable_sections": ["Section 2.1", "Section 3.4"],
                    "interpreted_by": ctx.deps.agent_id,
                    "interpretation_timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                return result
                
            except Exception as e:
                self.logger.log_governance_event(
                    event_type="policy_interpretation_error",
                    data={"error": str(e), "agent_id": ctx.deps.agent_id},
                    authority=ctx.deps.authority_level.value
                )
                raise
        
        return Tool(interpret_policy)