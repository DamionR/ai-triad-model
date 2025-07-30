"""
Crown Prerogative Implementation

Implements Westminster Crown reserve powers and constitutional authority
as exercised through the Governor General role.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid
import logfire

from triad.core.constitutional import ConstitutionalAuthority, ConstitutionalPrinciple, ConstitutionalDecision


class CrownPrerogative:
    """
    Implementation of Crown reserve powers.
    
    Provides constitutional authority mechanisms including:
    - Agent dismissal and appointment powers
    - Parliamentary dissolution
    - Royal assent and refusal
    - Emergency powers activation
    - Constitutional crisis intervention
    """
    
    def __init__(self, logfire_logger: logfire):
        self.logfire_logger = logfire_logger
        self.reserve_power_exercises: List[Dict[str, Any]] = []
        self.emergency_powers_active = False
        self.interim_appointments: Dict[str, str] = {}
        
    async def exercise_reserve_power(
        self,
        power_type: str,
        justification: str,
        affected_agents: List[str]
    ) -> Dict[str, Any]:
        """
        Exercise Crown reserve powers in constitutional matters.
        
        Reserve powers should be used sparingly and only when
        constitutional order is threatened or democratic governance fails.
        """
        with logfire.span("exercise_reserve_power") as span:
            span.set_attribute("power_type", power_type)
            span.set_attribute("affected_agents_count", len(affected_agents))
            
            exercise_id = f"crown_power_{uuid.uuid4().hex[:8]}"
            
            # Validate power type
            valid_powers = ["dismiss", "dissolve", "refuse_assent", "emergency_powers", "appoint"]
            if power_type not in valid_powers:
                raise ValueError(f"Invalid reserve power: {power_type}. Valid powers: {valid_powers}")
            
            # Create exercise record
            exercise_record = {
                "exercise_id": exercise_id,
                "power_type": power_type,
                "justification": justification,
                "affected_agents": affected_agents,
                "exercised_at": datetime.now(timezone.utc),
                "constitutional_authority": ConstitutionalAuthority.CROWN.value,
                "successful": False,
                "constitutional_impact": await self._assess_constitutional_impact(power_type, affected_agents)
            }
            
            try:
                # Execute specific power
                if power_type == "dismiss":
                    result = await self._exercise_dismissal_power(affected_agents, justification)
                elif power_type == "dissolve":
                    result = await self._exercise_dissolution_power(justification)
                elif power_type == "refuse_assent":
                    result = await self._exercise_refusal_power(affected_agents[0], justification)
                elif power_type == "emergency_powers":
                    result = await self._activate_emergency_powers(justification)
                elif power_type == "appoint":
                    result = await self._exercise_appointment_power(affected_agents, justification)
                
                exercise_record.update(result)
                exercise_record["successful"] = result.get("success", False)
                
                await self.logfire_logger.warning(
                    "Crown reserve power exercised",
                    exercise_id=exercise_id,
                    power_type=power_type,
                    successful=exercise_record["successful"],
                    constitutional_impact=exercise_record["constitutional_impact"]
                )
                
            except Exception as e:
                exercise_record["error"] = str(e)
                exercise_record["successful"] = False
                
                await self.logfire_logger.error(
                    "Crown reserve power exercise failed",
                    exercise_id=exercise_id,
                    power_type=power_type,
                    error=str(e)
                )
            
            self.reserve_power_exercises.append(exercise_record)
            
            return {
                "exercise_id": exercise_id,
                "power_exercised": power_type,
                "successful": exercise_record["successful"],
                "constitutional_impact": exercise_record["constitutional_impact"],
                "result": exercise_record.get("result", {}),
                "parliamentary_notification_required": True,
                "public_announcement_required": power_type in ["dismiss", "dissolve", "emergency_powers"]
            }
    
    async def grant_royal_assent(
        self,
        decision: ConstitutionalDecision
    ) -> Dict[str, Any]:
        """
        Grant royal assent to constitutional decisions.
        
        Final approval mechanism for major system decisions,
        ensuring constitutional compliance.
        """
        with logfire.span("grant_royal_assent") as span:
            span.set_attribute("decision_id", decision.decision_id)
            span.set_attribute("decision_type", decision.decision_type)
            
            assent_id = f"assent_{uuid.uuid4().hex[:8]}"
            
            # Review decision for constitutional compliance
            constitutional_review = await self._conduct_constitutional_review(decision)
            
            assent_record = {
                "assent_id": assent_id,
                "decision_id": decision.decision_id,
                "decision_type": decision.decision_type,
                "constitutional_review": constitutional_review,
                "assent_granted": constitutional_review["compliant"],
                "granted_at": datetime.now(timezone.utc) if constitutional_review["compliant"] else None,
                "refused_at": None if constitutional_review["compliant"] else datetime.now(timezone.utc)
            }
            
            if constitutional_review["compliant"]:
                # Grant assent
                assent_record["assent_text"] = f"We, by and with the advice and consent of the Parliamentary System, do enact that the decision '{decision.description}' shall have the force of constitutional law."
                
                await self.logfire_logger.info(
                    "Royal assent granted",
                    assent_id=assent_id,
                    decision_id=decision.decision_id
                )
            else:
                # Refuse assent
                assent_record["refusal_reasons"] = constitutional_review["violations"]
                assent_record["refusal_text"] = f"We cannot, in good conscience and constitutional duty, grant our assent to the decision '{decision.description}' due to constitutional violations."
                
                await self.logfire_logger.warning(
                    "Royal assent refused",
                    assent_id=assent_id,
                    decision_id=decision.decision_id,
                    violations=constitutional_review["violations"]
                )
            
            return assent_record
    
    async def dismiss_agents(
        self,
        agents: List[str]
    ) -> Dict[str, Any]:
        """
        Dismiss agents using Crown authority.
        
        Nuclear option for removing agents who have lost confidence
        or violated constitutional principles.
        """
        justification = "Agents dismissed for loss of confidence and constitutional violations"
        return await self.exercise_reserve_power("dismiss", justification, agents)
    
    async def dissolve_government(self) -> Dict[str, Any]:
        """
        Dissolve the parliamentary system.
        
        Most extreme constitutional power, used when the system
        has become ungovernable or faces irreconcilable deadlock.
        """
        justification = "Parliamentary system dissolved due to constitutional crisis and inability to maintain effective governance"
        return await self.exercise_reserve_power("dissolve", justification, [])
    
    async def activate_emergency_governance(self) -> Dict[str, Any]:
        """
        Activate emergency governance protocols.
        
        Suspends normal parliamentary operations and assumes
        direct Crown control during critical emergencies.
        """
        justification = "Emergency governance activated due to critical system failure threatening constitutional order"
        return await self.exercise_reserve_power("emergency_powers", justification, [])
    
    async def _exercise_dismissal_power(
        self,
        agents: List[str],
        justification: str
    ) -> Dict[str, Any]:
        """Exercise power to dismiss agents."""
        
        dismissed_agents = []
        dismissal_results = {}
        
        for agent in agents:
            # Record dismissal
            dismissal_results[agent] = {
                "dismissed": True,
                "dismissal_reason": justification,
                "dismissed_at": datetime.now(timezone.utc),
                "replacement_required": True
            }
            dismissed_agents.append(agent)
            
            # Add to interim appointments needed
            self.interim_appointments[agent] = "vacant"
        
        return {
            "success": True,
            "dismissed_agents": dismissed_agents,
            "dismissal_results": dismissal_results,
            "interim_appointments_required": len(dismissed_agents),
            "constitutional_consequence": "agents_dismissed"
        }
    
    async def _exercise_dissolution_power(
        self,
        justification: str
    ) -> Dict[str, Any]:
        """Exercise power to dissolve parliament."""
        
        dissolution_record = {
            "parliament_dissolved": True,
            "dissolution_reason": justification,
            "dissolved_at": datetime.now(timezone.utc),
            "new_session_required": True,
            "emergency_governance_period": True
        }
        
        # Activate emergency powers temporarily
        self.emergency_powers_active = True
        
        return {
            "success": True,
            "dissolution_record": dissolution_record,
            "constitutional_consequence": "parliament_dissolved",
            "emergency_powers_activated": True
        }
    
    async def _activate_emergency_powers(
        self,
        justification: str
    ) -> Dict[str, Any]:
        """Activate emergency powers."""
        
        self.emergency_powers_active = True
        
        emergency_record = {
            "emergency_powers_activated": True,
            "activation_reason": justification,
            "activated_at": datetime.now(timezone.utc),
            "normal_operations_suspended": True,
            "crown_direct_control": True
        }
        
        return {
            "success": True,
            "emergency_record": emergency_record,
            "constitutional_consequence": "emergency_governance"
        }
    
    async def _assess_constitutional_impact(
        self,
        power_type: str,
        affected_agents: List[str]
    ) -> str:
        """Assess the constitutional impact of exercising reserve power."""
        
        impact_assessments = {
            "dismiss": "high" if len(affected_agents) > 1 else "moderate",
            "dissolve": "critical",
            "refuse_assent": "moderate",
            "emergency_powers": "critical",
            "appoint": "low"
        }
        
        return impact_assessments.get(power_type, "moderate")
    
    async def _conduct_constitutional_review(
        self,
        decision: ConstitutionalDecision
    ) -> Dict[str, Any]:
        """Conduct constitutional review of a decision."""
        
        violations = []
        
        # Check constitutional principles
        if ConstitutionalPrinciple.SEPARATION_OF_POWERS in decision.constitutional_principles:
            # Verify separation of powers is maintained
            if decision.constitutional_authority == ConstitutionalAuthority.LEGISLATIVE and decision.decision_type == "execution":
                violations.append("Legislative branch cannot execute decisions")
        
        if ConstitutionalPrinciple.COLLECTIVE_RESPONSIBILITY in decision.constitutional_principles:
            # Verify collective approval was obtained if required
            if decision.requires_collective_approval and not decision.description.find("collective approval obtained"):
                violations.append("Collective responsibility not fulfilled")
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "constitutional_principles_reviewed": [p.value for p in decision.constitutional_principles]
        }
    
    async def _exercise_refusal_power(
        self,
        decision_id: str,
        justification: str
    ) -> Dict[str, Any]:
        """Exercise power to refuse royal assent."""
        
        refusal_record = {
            "assent_refused": True,
            "decision_id": decision_id,
            "refusal_reason": justification,
            "refused_at": datetime.now(timezone.utc),
            "decision_blocked": True
        }
        
        return {
            "success": True,
            "refusal_record": refusal_record,
            "constitutional_consequence": "decision_blocked"
        }
    
    async def _exercise_appointment_power(
        self,
        positions: List[str],
        justification: str
    ) -> Dict[str, Any]:
        """Exercise power to make appointments."""
        
        appointments = {}
        
        for position in positions:
            # Create interim appointment ID
            interim_id = f"interim_{position}_{uuid.uuid4().hex[:8]}"
            appointments[position] = {
                "interim_id": interim_id,
                "appointed_at": datetime.now(timezone.utc),
                "appointment_reason": justification,
                "status": "interim",
                "constitutional_authority": "crown_prerogative"
            }
            
            self.interim_appointments[position] = interim_id
        
        return {
            "success": True,
            "appointments": appointments,
            "constitutional_consequence": "interim_appointments_made"
        }