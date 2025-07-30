"""
Constitutional Framework for Westminster Parliamentary AI System

Implements the core constitutional principles and governance mechanisms
based on the Canadian Westminster Parliamentary System.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime, timezone
import uuid


class ConstitutionalAuthority(str, Enum):
    """Westminster constitutional authority levels."""
    LEGISLATIVE = "legislative"  # Planner Agent - Parliament
    EXECUTIVE = "executive"      # Executor Agent - Prime Minister/Cabinet
    JUDICIAL = "judicial"        # Evaluator Agent - Supreme Court
    CROWN = "crown"             # Overwatch Agent - Governor General


class ConstitutionalPrinciple(str, Enum):
    """Fundamental constitutional principles of Westminster system."""
    PARLIAMENTARY_SOVEREIGNTY = "parliamentary_sovereignty"
    RESPONSIBLE_GOVERNMENT = "responsible_government"
    RULE_OF_LAW = "rule_of_law"
    SEPARATION_OF_POWERS = "separation_of_powers"
    CONSTITUTIONAL_MONARCHY = "constitutional_monarchy"
    DEMOCRATIC_ACCOUNTABILITY = "democratic_accountability"
    COLLECTIVE_RESPONSIBILITY = "collective_responsibility"
    MINISTERIAL_RESPONSIBILITY = "ministerial_responsibility"


class ConstitutionalDecision(BaseModel):
    """Model for constitutional decisions requiring validation."""
    decision_id: str
    constitutional_authority: ConstitutionalAuthority
    decision_type: str
    description: str
    requires_royal_assent: bool = False
    requires_collective_approval: bool = False
    constitutional_principles: List[ConstitutionalPrinciple] = []
    timestamp: datetime
    agent_responsible: str
    
    def __init__(self, **data):
        if "decision_id" not in data:
            data["decision_id"] = f"const_dec_{uuid.uuid4().hex[:8]}"
        if "timestamp" not in data:
            data["timestamp"] = datetime.now(timezone.utc)
        super().__init__(**data)


class ParliamentarySession(BaseModel):
    """Model for parliamentary sessions."""
    session_id: str
    session_number: int
    start_date: datetime
    end_date: Optional[datetime] = None
    status: str = "active"  # active, prorogued, dissolved
    government_agents: List[str] = []
    opposition_agents: List[str] = []
    constitutional_records: List[Dict[str, Any]] = []
    
    def __init__(self, **data):
        if "session_id" not in data:
            data["session_id"] = f"parl_session_{uuid.uuid4().hex[:8]}"
        if "start_date" not in data:
            data["start_date"] = datetime.now(timezone.utc)
        super().__init__(**data)


class ConstitutionalViolation(BaseModel):
    """Model for constitutional violations and breaches."""
    violation_id: str
    violation_type: str
    constitutional_principle_breached: ConstitutionalPrinciple
    offending_agent: str
    description: str
    severity: str  # minor, major, critical
    timestamp: datetime
    resolution_required: bool = True
    crown_intervention_required: bool = False
    
    def __init__(self, **data):
        if "violation_id" not in data:
            data["violation_id"] = f"const_viol_{uuid.uuid4().hex[:8]}"
        if "timestamp" not in data:
            data["timestamp"] = datetime.now(timezone.utc)
        super().__init__(**data)


class ConstitutionalFramework:
    """
    Core constitutional framework implementing Westminster parliamentary principles.
    
    This class ensures all AI agents operate within proper constitutional constraints
    and democratic accountability mechanisms.
    """
    
    def __init__(self):
        self.current_session: Optional[ParliamentarySession] = None
        self.constitutional_principles = {
            principle: {
                "description": self._get_principle_description(principle),
                "violations": [],
                "compliance_score": 1.0
            }
            for principle in ConstitutionalPrinciple
        }
        self.active_decisions: Dict[str, ConstitutionalDecision] = {}
        self.constitutional_record: List[Dict[str, Any]] = []
    
    def _get_principle_description(self, principle: ConstitutionalPrinciple) -> str:
        """Get description of constitutional principle."""
        descriptions = {
            ConstitutionalPrinciple.PARLIAMENTARY_SOVEREIGNTY: 
                "Parliament (collective agents) has supreme legal authority",
            ConstitutionalPrinciple.RESPONSIBLE_GOVERNMENT: 
                "Government (agents) must maintain confidence of parliament",
            ConstitutionalPrinciple.RULE_OF_LAW: 
                "All agents are subject to and accountable under constitutional law",
            ConstitutionalPrinciple.SEPARATION_OF_POWERS: 
                "Legislative, executive, and judicial functions are separated",
            ConstitutionalPrinciple.CONSTITUTIONAL_MONARCHY: 
                "Crown (Overwatch) provides constitutional oversight and reserve powers",
            ConstitutionalPrinciple.DEMOCRATIC_ACCOUNTABILITY: 
                "All agents must be transparent and accountable for their actions",
            ConstitutionalPrinciple.COLLECTIVE_RESPONSIBILITY: 
                "All agents collectively responsible for major system decisions",
            ConstitutionalPrinciple.MINISTERIAL_RESPONSIBILITY: 
                "Individual agents responsible for decisions in their domain"
        }
        return descriptions.get(principle, "Constitutional principle")
    
    async def validate_constitutional_decision(
        self, 
        decision: ConstitutionalDecision
    ) -> Dict[str, Any]:
        """
        Validate a decision against constitutional principles.
        
        This is the core constitutional validation mechanism that ensures
        all agent decisions comply with Westminster parliamentary principles.
        """
        validation_result = {
            "decision_id": decision.decision_id,
            "constitutional_compliance": True,
            "violations": [],
            "required_approvals": [],
            "constitutional_authority_valid": True,
            "recommendations": []
        }
        
        # Validate constitutional authority
        if not await self._validate_authority(decision):
            validation_result["constitutional_compliance"] = False
            validation_result["constitutional_authority_valid"] = False
            validation_result["violations"].append(
                "Invalid constitutional authority for decision type"
            )
        
        # Check separation of powers
        if not await self._validate_separation_of_powers(decision):
            validation_result["constitutional_compliance"] = False
            validation_result["violations"].append(
                "Decision violates separation of powers principle"
            )
        
        # Check if collective approval required
        if decision.requires_collective_approval:
            validation_result["required_approvals"].append("collective_cabinet_approval")
        
        # Check if royal assent required
        if decision.requires_royal_assent:
            validation_result["required_approvals"].append("crown_royal_assent")
        
        # Validate against constitutional principles
        for principle in decision.constitutional_principles:
            principle_validation = await self._validate_principle(decision, principle)
            if not principle_validation["compliant"]:
                validation_result["constitutional_compliance"] = False
                validation_result["violations"].extend(principle_validation["violations"])
        
        # Record decision in constitutional record
        await self._record_constitutional_decision(decision, validation_result)
        
        return validation_result
    
    async def _validate_authority(self, decision: ConstitutionalDecision) -> bool:
        """Validate that the agent has authority for this type of decision."""
        authority_mappings = {
            "planning": [ConstitutionalAuthority.LEGISLATIVE],
            "execution": [ConstitutionalAuthority.EXECUTIVE],
            "validation": [ConstitutionalAuthority.JUDICIAL],
            "oversight": [ConstitutionalAuthority.CROWN],
            "constitutional_crisis": [ConstitutionalAuthority.CROWN],
            "emergency": [ConstitutionalAuthority.CROWN]
        }
        
        allowed_authorities = authority_mappings.get(decision.decision_type, [])
        return decision.constitutional_authority in allowed_authorities
    
    async def _validate_separation_of_powers(self, decision: ConstitutionalDecision) -> bool:
        """Ensure decision respects separation of powers."""
        # Legislative agents cannot execute or validate
        if (decision.constitutional_authority == ConstitutionalAuthority.LEGISLATIVE and 
            decision.decision_type in ["execution", "validation"]):
            return False
        
        # Executive agents cannot create legislation or provide final validation
        if (decision.constitutional_authority == ConstitutionalAuthority.EXECUTIVE and 
            decision.decision_type in ["legislation", "final_validation"]):
            return False
        
        # Judicial agents cannot execute or create policy
        if (decision.constitutional_authority == ConstitutionalAuthority.JUDICIAL and 
            decision.decision_type in ["execution", "policy_creation"]):
            return False
        
        return True
    
    async def _validate_principle(
        self, 
        decision: ConstitutionalDecision, 
        principle: ConstitutionalPrinciple
    ) -> Dict[str, Any]:
        """Validate decision against specific constitutional principle."""
        validation = {"compliant": True, "violations": []}
        
        if principle == ConstitutionalPrinciple.COLLECTIVE_RESPONSIBILITY:
            # Major decisions must have collective approval
            if (decision.decision_type in ["major_policy", "system_change"] and 
                not decision.requires_collective_approval):
                validation["compliant"] = False
                validation["violations"].append(
                    "Major decisions require collective cabinet responsibility"
                )
        
        elif principle == ConstitutionalPrinciple.DEMOCRATIC_ACCOUNTABILITY:
            # All decisions must be transparent and recorded
            if not decision.description:
                validation["compliant"] = False
                validation["violations"].append(
                    "Decision lacks sufficient transparency and description"
                )
        
        elif principle == ConstitutionalPrinciple.CONSTITUTIONAL_MONARCHY:
            # Critical decisions require royal assent
            if (decision.decision_type in ["constitutional_change", "emergency_powers"] and 
                not decision.requires_royal_assent):
                validation["compliant"] = False
                validation["violations"].append(
                    "Constitutional changes require Crown royal assent"
                )
        
        return validation
    
    async def _record_constitutional_decision(
        self, 
        decision: ConstitutionalDecision, 
        validation_result: Dict[str, Any]
    ):
        """Record decision in constitutional record (Hansard equivalent)."""
        record_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "decision_id": decision.decision_id,
            "constitutional_authority": decision.constitutional_authority.value,
            "agent_responsible": decision.agent_responsible,
            "decision_type": decision.decision_type,
            "description": decision.description,
            "constitutional_compliance": validation_result["constitutional_compliance"],
            "violations": validation_result["violations"],
            "parliamentary_session": self.current_session.session_id if self.current_session else None,
            "recorded_by": "constitutional_clerk"
        }
        
        self.constitutional_record.append(record_entry)
        
        # Add to current parliamentary session
        if self.current_session:
            self.current_session.constitutional_records.append(record_entry)
    
    async def start_parliamentary_session(
        self, 
        government_agents: List[str],
        opposition_agents: Optional[List[str]] = None
    ) -> ParliamentarySession:
        """Start a new parliamentary session."""
        session_number = len([s for s in self.constitutional_record 
                             if s.get("event_type") == "session_start"]) + 1
        
        self.current_session = ParliamentarySession(
            session_number=session_number,
            government_agents=government_agents,
            opposition_agents=opposition_agents or []
        )
        
        # Record session start
        await self._record_constitutional_decision(
            ConstitutionalDecision(
                constitutional_authority=ConstitutionalAuthority.CROWN,
                decision_type="session_start",
                description=f"Parliamentary session {session_number} commenced",
                agent_responsible="crown"
            ),
            {"constitutional_compliance": True, "violations": []}
        )
        
        return self.current_session
    
    async def get_constitutional_compliance_score(self) -> Dict[str, Any]:
        """Get overall constitutional compliance score."""
        total_decisions = len(self.constitutional_record)
        if total_decisions == 0:
            return {"overall_score": 1.0, "principle_scores": {}, "recommendations": []}
        
        compliant_decisions = len([
            r for r in self.constitutional_record 
            if r.get("constitutional_compliance", True)
        ])
        
        overall_score = compliant_decisions / total_decisions
        
        # Calculate principle-specific scores
        principle_scores = {}
        for principle in ConstitutionalPrinciple:
            principle_data = self.constitutional_principles[principle]
            principle_scores[principle.value] = principle_data["compliance_score"]
        
        # Generate recommendations
        recommendations = []
        if overall_score < 0.95:
            recommendations.append("Review constitutional compliance procedures")
        if overall_score < 0.90:
            recommendations.append("Implement additional constitutional safeguards")
        if overall_score < 0.80:
            recommendations.append("Consider Crown intervention for constitutional crisis")
        
        return {
            "overall_score": overall_score,
            "total_decisions": total_decisions,
            "compliant_decisions": compliant_decisions,
            "principle_scores": principle_scores,
            "recommendations": recommendations,
            "parliamentary_session": self.current_session.session_id if self.current_session else None
        }