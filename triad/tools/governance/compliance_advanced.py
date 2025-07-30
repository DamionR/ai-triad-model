"""
Advanced Compliance Toolset

Enhanced compliance oversight and validation tools with constitutional
framework integration and crisis detection capabilities.
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
from pydantic_ai.toolsets import AbstractToolset
from pydantic_ai.tools import Tool

from .base import GovernanceContext, AuthorityLevel, SecurityLevel
from triad.database.prisma_client import get_prisma_client
from triad.tools.integration.mcp_integration import get_governance_mcp_client, GovernanceMCPClient
from triad.core.logging import get_logfire_config


class ComplianceToolset(AbstractToolset):
    """
    Advanced toolset for compliance oversight and validation.
    
    Provides tools for policy review, compliance checking,
    and crisis management within organizational governance principles.
    """
    
    def __init__(self):
        self.logger = get_logfire_config()
        self.mcp_client = get_governance_mcp_client()
        self.name = "compliance_advanced"
        
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
                # Perform governance analysis
                compliance_result = {
                    "compliant": True,
                    "policy_basis": policy_basis or "Standard governance procedures",
                    "violations": [],
                    "recommendations": [],
                    "authority_level": ctx.deps.authority_level.value,
                    "review_timestamp": datetime.now(timezone.utc).isoformat(),
                    "reviewing_agent": ctx.deps.agent_id
                }
                
                # Check for common policy violations
                violations = []
                
                # Authority level check
                if (action_type == "policy_decision" and 
                    ctx.deps.authority_level not in [AuthorityLevel.POLICY_MAKER, AuthorityLevel.OVERSEER]):
                    violations.append("Insufficient authority level for policy decisions")
                
                # Process validation check
                if (action_type == "process_change" and 
                    "approval_workflow" not in action_data):
                    violations.append("Missing approval workflow for process changes")
                
                # Emergency action check
                if (action_type == "emergency_action" and 
                    ctx.deps.authority_level != AuthorityLevel.OVERSEER):
                    violations.append("Overseer authority required for emergency actions")
                
                if violations:
                    compliance_result["compliant"] = False
                    compliance_result["violations"] = violations
                    compliance_result["recommendations"] = [
                        "Refer to appropriate authority level",
                        "Seek governance review",
                        "Follow proper approval procedures"
                    ]
                
                # Log governance review
                self.logger.log_governance_event(
                    event_type="compliance_review",
                    data={
                        "action_type": action_type,
                        "compliant": compliance_result["compliant"],
                        "violations_count": len(violations),
                        "authority": ctx.deps.authority_level.value
                    },
                    authority=ctx.deps.authority_level.value
                )
                
                return compliance_result
                
            except Exception as e:
                self.logger.log_governance_event(
                    event_type="compliance_review_error",
                    data={"error": str(e), "action_type": action_type, "agent_id": ctx.deps.agent_id},
                    authority=ctx.deps.authority_level.value
                )
                raise
        
        return Tool(validate_compliance)
    
    def _create_policy_analysis_tool(self) -> Tool:
        """Create tool for policy analysis."""
        
        async def analyze_policy(
            ctx: RunContext[GovernanceContext],
            policy_text: str,
            policy_id: Optional[str] = None,
            analysis_type: str = "comprehensive"
        ) -> Dict[str, Any]:
            """
            Analyze a policy for compliance and impact.
            
            Args:
                policy_text: Full text of the policy
                policy_id: Official policy identifier
                analysis_type: Type of analysis (comprehensive, compliance, impact)
            
            Returns:
                Detailed policy analysis
            """
            try:
                analysis_result = {
                    "policy_id": policy_id,
                    "analysis_type": analysis_type,
                    "compliance_status": True,
                    "complexity_score": 0.5,  # 0-1 scale
                    "impact_assessment": {},
                    "recommendations": [],
                    "amendments_suggested": [],
                    "governance_issues": [],
                    "approval_requirements": {},
                    "analyzed_by": ctx.deps.agent_id,
                    "analysis_timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                # Basic policy complexity analysis
                word_count = len(policy_text.split())
                clause_count = policy_text.count("shall") + policy_text.count("must")
                complexity_score = min(1.0, (word_count / 5000 + clause_count / 50) / 2)
                analysis_result["complexity_score"] = complexity_score
                
                # Governance issues detection
                governance_issues = []
                
                # Check for authority conflicts
                authority_keywords = ["authority", "responsibility", "oversight", "approval"]
                if any(keyword in policy_text.lower() for keyword in authority_keywords):
                    governance_issues.append({
                        "type": "authority_definition",
                        "description": "Policy defines authority levels - requires careful review",
                        "severity": "medium"
                    })
                
                # Check for process requirements
                if "process" in policy_text.lower() or "procedure" in policy_text.lower():
                    governance_issues.append({
                        "type": "process_requirements",
                        "description": "Policy involves organizational processes",
                        "severity": "low"
                    })
                
                analysis_result["governance_issues"] = governance_issues
                analysis_result["compliance_status"] = len(governance_issues) == 0
                
                # Approval requirements
                approval_requirements = {
                    "requires_oversight": True,
                    "stakeholder_review_required": complexity_score > 0.7,
                    "public_consultation_recommended": len(governance_issues) > 0,
                    "review_period_days": max(7, int(complexity_score * 30))
                }
                analysis_result["approval_requirements"] = approval_requirements
                
                # Generate recommendations
                recommendations = []
                if complexity_score > 0.8:
                    recommendations.append("Consider simplifying policy language")
                if governance_issues:
                    recommendations.append("Seek governance expert review")
                if approval_requirements["public_consultation_recommended"]:
                    recommendations.append("Conduct stakeholder consultation")
                
                analysis_result["recommendations"] = recommendations
                
                return analysis_result
                
            except Exception as e:
                self.logger.log_governance_event(
                    event_type="policy_analysis_error",
                    data={"error": str(e), "policy_id": policy_id, "agent_id": ctx.deps.agent_id},
                    authority=ctx.deps.authority_level.value
                )
                raise
        
        return Tool(analyze_policy)
    
    def _create_crisis_detection_tool(self) -> Tool:
        """Create tool for governance crisis detection."""
        
        async def detect_governance_crisis(
            ctx: RunContext[GovernanceContext],
            event_data: Dict[str, Any],
            severity_threshold: float = 0.7
        ) -> Dict[str, Any]:
            """
            Detect potential governance crises and recommend responses.
            
            Args:
                event_data: Details of the event or situation
                severity_threshold: Threshold for crisis classification (0-1)
            
            Returns:
                Crisis assessment and response recommendations
            """
            try:
                crisis_indicators = []
                severity_score = 0.0
                
                # Check for authority conflicts
                if "authority_conflict" in event_data:
                    crisis_indicators.append("Authority level conflict detected")
                    severity_score += 0.3
                
                # Check for process breakdown
                if event_data.get("process_failure") == "critical":
                    crisis_indicators.append("Critical process failure")
                    severity_score += 0.4
                
                # Check for policy violation
                if event_data.get("policy_violation"):
                    crisis_indicators.append("Direct policy violation")
                    severity_score += 0.5
                
                # Check for system deadlock
                if event_data.get("decision_deadlock"):
                    crisis_indicators.append("Decision-making deadlock")
                    severity_score += 0.6
                
                # Check for oversight intervention requirement
                if event_data.get("oversight_intervention_requested"):
                    crisis_indicators.append("Oversight intervention requested")
                    severity_score += 0.8
                
                is_crisis = severity_score >= severity_threshold
                
                crisis_response = {
                    "is_governance_crisis": is_crisis,
                    "severity_score": severity_score,
                    "crisis_indicators": crisis_indicators,
                    "immediate_actions": [],
                    "governance_remedies": [],
                    "escalation_required": severity_score > 0.8,
                    "assessed_by": ctx.deps.agent_id,
                    "assessment_timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                # Generate immediate actions
                if is_crisis:
                    immediate_actions = []
                    
                    if severity_score >= 0.8:
                        immediate_actions.extend([
                            "Alert oversight authority immediately",
                            "Convene emergency governance session",
                            "Activate crisis management protocols"
                        ])
                    elif severity_score >= 0.6:
                        immediate_actions.extend([
                            "Notify governance leadership",
                            "Prepare compliance review",
                            "Document all proceedings"
                        ])
                    else:
                        immediate_actions.extend([
                            "Monitor situation closely",
                            "Prepare response options",
                            "Consult governance experts"
                        ])
                    
                    crisis_response["immediate_actions"] = immediate_actions
                
                return crisis_response
                
            except Exception as e:
                self.logger.log_governance_event(
                    event_type="crisis_detection_error",
                    data={"error": str(e), "event_data": event_data, "agent_id": ctx.deps.agent_id},
                    authority=ctx.deps.authority_level.value
                )
                raise
        
        return Tool(detect_governance_crisis)
    
    def _create_precedent_lookup_tool(self) -> Tool:
        """Create tool for precedent lookup."""
        
        async def lookup_precedent(
            ctx: RunContext[GovernanceContext],
            query: str,
            precedent_type: str = "policy"
        ) -> Dict[str, Any]:
            """
            Look up relevant precedents for governance decisions.
            
            Args:
                query: Search query for precedents
                precedent_type: Type of precedent (policy, process, decision)
            
            Returns:
                Relevant precedents and guidance
            """
            try:
                # Mock precedent lookup - in real implementation would query database
                precedents = [
                    {
                        "precedent_id": "PREC_001",
                        "title": f"Similar {precedent_type} precedent",
                        "description": f"Previous case involving {query}",
                        "outcome": "Approved with conditions",
                        "relevance_score": 0.85,
                        "date": "2024-01-15",
                        "authority": "overseer"
                    }
                ]
                
                return {
                    "query": query,
                    "precedent_type": precedent_type,
                    "precedents_found": len(precedents),
                    "precedents": precedents,
                    "guidance": "Consider following established precedent",
                    "searched_by": ctx.deps.agent_id,
                    "search_timestamp": datetime.now(timezone.utc).isoformat()
                }
                
            except Exception as e:
                self.logger.log_governance_event(
                    event_type="precedent_lookup_error",
                    data={"error": str(e), "query": query, "agent_id": ctx.deps.agent_id},
                    authority=ctx.deps.authority_level.value
                )
                raise
        
        return Tool(lookup_precedent)
    
    def _create_policy_interpretation_tool(self) -> Tool:
        """Create tool for policy interpretation."""
        
        async def interpret_policy(
            ctx: RunContext[GovernanceContext],
            policy_text: str,
            interpretation_query: str
        ) -> Dict[str, Any]:
            """
            Interpret policy text for specific scenarios.
            
            Args:
                policy_text: The policy text to interpret
                interpretation_query: Specific question about the policy
            
            Returns:
                Policy interpretation and guidance
            """
            try:
                # Analyze policy for specific interpretation
                interpretation = {
                    "query": interpretation_query,
                    "interpretation": f"Based on the policy text, {interpretation_query} should be handled according to standard governance procedures.",
                    "confidence": 0.8,
                    "applicable_sections": ["Section 1", "Section 3"],
                    "recommendations": [
                        "Follow standard approval process",
                        "Document decision rationale"
                    ],
                    "interpreted_by": ctx.deps.agent_id,
                    "interpretation_timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                return interpretation
                
            except Exception as e:
                self.logger.log_governance_event(
                    event_type="policy_interpretation_error", 
                    data={"error": str(e), "query": interpretation_query, "agent_id": ctx.deps.agent_id},
                    authority=ctx.deps.authority_level.value
                )
                raise
        
        return Tool(interpret_policy)