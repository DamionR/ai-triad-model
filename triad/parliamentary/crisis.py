"""
Constitutional Crisis Management

Implements Westminster constitutional crisis management procedures
including deadlock resolution and emergency protocols.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import uuid
import logfire

from triad.core.constitutional import ConstitutionalAuthority, ConstitutionalPrinciple


class ConstitutionalCrisisManager:
    """
    Manages constitutional crises following Westminster conventions.
    
    Handles:
    - Collective responsibility breakdowns
    - Constitutional deadlocks
    - Loss of confidence situations
    - Emergency interventions
    """
    
    def __init__(self, logfire_logger: logfire):
        self.logfire_logger = logfire_logger
        self.active_crises: Dict[str, Any] = {}
        self.crisis_resolution_protocols: Dict[str, List[str]] = {
            "collective_responsibility": [
                "Assess dissenting positions",
                "Attempt compromise negotiation", 
                "Require resignations or dismissals",
                "Cabinet reshuffling if necessary",
                "Crown intervention if unresolved"
            ],
            "constitutional_deadlock": [
                "Identify constitutional issues",
                "Invoke parliamentary procedure",
                "Seek Crown guidance",
                "Exercise reserve powers if necessary"
            ],
            "loss_of_confidence": [
                "Formal vote of no confidence",
                "Resignation or dismissal",
                "Appointment of replacement",
                "Restoration of parliamentary confidence"
            ]
        }
    
    async def handle_collective_responsibility_crisis(
        self,
        proposal: Dict[str, Any],
        agent_positions: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Handle crisis arising from collective responsibility breakdown.
        
        When cabinet members cannot maintain unified public support,
        constitutional crisis mechanisms are triggered.
        """
        with logfire.span("collective_responsibility_crisis") as span:
            crisis_id = f"colresp_crisis_{uuid.uuid4().hex[:8]}"
            span.set_attribute("crisis_id", crisis_id)
            
            # Analyze the breakdown
            supporters = [agent for agent, pos in agent_positions.items() if pos == "SUPPORT"]
            dissenting = [agent for agent, pos in agent_positions.items() if pos in ["OPPOSE", "ABSTAIN"]]
            
            crisis_record = {
                "crisis_id": crisis_id,
                "crisis_type": "collective_responsibility_breakdown",
                "triggered_at": datetime.now(timezone.utc),
                "proposal": proposal,
                "agent_positions": agent_positions,
                "supporters": supporters,
                "dissenting_agents": dissenting,
                "severity": "high" if len(dissenting) > 1 else "moderate"
            }
            
            self.active_crises[crisis_id] = crisis_record
            
            # Apply resolution protocol
            resolution_steps = self.crisis_resolution_protocols["collective_responsibility"]
            
            # Step 1: Assess dissenting positions
            dissent_analysis = await self._analyze_dissenting_positions(dissenting, proposal)
            
            # Step 2: Attempt compromise negotiation
            compromise_result = await self._attempt_compromise_negotiation(
                proposal, agent_positions, dissent_analysis
            )
            
            crisis_resolution = {
                "crisis_id": crisis_id,
                "resolution_attempted": True,
                "compromise_successful": compromise_result["successful"],
                "actions_taken": [],
                "constitutional_order_restored": compromise_result["successful"]
            }
            
            if compromise_result["successful"]:
                crisis_resolution["actions_taken"].extend([
                    "Compromise negotiated successfully",
                    "Modified proposal accepted by all parties",
                    "Collective responsibility restored"
                ])
                crisis_record["status"] = "resolved"
                crisis_record["resolved_at"] = datetime.now(timezone.utc)
            else:
                # Step 3: Require resignations or dismissals
                crisis_resolution["actions_taken"].extend([
                    "Compromise negotiations failed",
                    "Dissenting agents must resign or face dismissal",
                    "Crown intervention may be required"
                ])
                crisis_resolution["required_resignations"] = dissenting
                crisis_resolution["crown_intervention_recommended"] = True
                crisis_record["status"] = "escalated"
            
            await self.logfire_logger.warning(
                "Collective responsibility crisis handled",
                crisis_id=crisis_id,
                dissenting_agents=len(dissenting),
                compromise_successful=compromise_result["successful"]
            )
            
            return crisis_resolution
    
    async def resolve_constitutional_deadlock(self) -> Dict[str, Any]:
        """
        Resolve constitutional deadlocks using Westminster procedures.
        
        When the system cannot function due to constitutional disputes,
        formal resolution mechanisms are applied.
        """
        with logfire.span("resolve_constitutional_deadlock") as span:
            deadlock_id = f"deadlock_{uuid.uuid4().hex[:8]}"
            span.set_attribute("deadlock_id", deadlock_id)
            
            # Identify current deadlocks
            deadlock_issues = await self._identify_deadlock_issues()
            
            deadlock_record = {
                "deadlock_id": deadlock_id,
                "identified_at": datetime.now(timezone.utc),
                "deadlock_issues": deadlock_issues,
                "resolution_protocol": self.crisis_resolution_protocols["constitutional_deadlock"],
                "severity": "critical" if len(deadlock_issues) > 2 else "high"
            }
            
            self.active_crises[deadlock_id] = deadlock_record
            
            # Apply resolution protocol
            resolution_actions = []
            
            # Step 1: Identify constitutional issues
            constitutional_analysis = await self._analyze_constitutional_issues(deadlock_issues)
            resolution_actions.append(f"Constitutional analysis completed: {len(deadlock_issues)} issues identified")
            
            # Step 2: Invoke parliamentary procedure
            parliamentary_intervention = await self._invoke_parliamentary_procedure(deadlock_issues)
            resolution_actions.extend(parliamentary_intervention["actions"])
            
            # Step 3: Assess if Crown guidance needed
            crown_guidance_needed = len(deadlock_issues) > 1 or any(
                issue.get("severity") == "critical" for issue in deadlock_issues
            )
            
            resolution_result = {
                "deadlock_id": deadlock_id,
                "constitutional_issues_identified": len(deadlock_issues),
                "parliamentary_intervention": parliamentary_intervention["successful"],
                "crown_guidance_required": crown_guidance_needed,
                "resolution_actions": resolution_actions,
                "constitutional_order_restored": parliamentary_intervention["successful"] and not crown_guidance_needed
            }
            
            if crown_guidance_needed:
                resolution_result["recommended_crown_actions"] = [
                    "Exercise constitutional interpretation authority",
                    "Provide formal guidance to resolve deadlock",
                    "Exercise reserve powers if necessary"
                ]
                deadlock_record["status"] = "awaiting_crown_intervention"
            else:
                deadlock_record["status"] = "resolved"
                deadlock_record["resolved_at"] = datetime.now(timezone.utc)
            
            await self.logfire_logger.error(
                "Constitutional deadlock resolution attempted",
                deadlock_id=deadlock_id,
                issues_count=len(deadlock_issues),
                crown_intervention_required=crown_guidance_needed
            )
            
            return resolution_result
    
    async def handle_loss_of_confidence(self) -> Dict[str, Any]:
        """
        Handle system-wide loss of confidence situation.
        
        When the parliamentary system loses confidence in the government,
        formal procedures for restoration are triggered.
        """
        with logfire.span("handle_loss_of_confidence") as span:
            confidence_crisis_id = f"confidence_{uuid.uuid4().hex[:8]}"
            span.set_attribute("crisis_id", confidence_crisis_id)
            
            # Assess current confidence levels
            confidence_assessment = await self._assess_system_confidence()
            
            crisis_record = {
                "crisis_id": confidence_crisis_id,
                "crisis_type": "loss_of_confidence",
                "triggered_at": datetime.now(timezone.utc),
                "confidence_assessment": confidence_assessment,
                "severity": "critical",
                "affected_agents": confidence_assessment["agents_with_lost_confidence"]
            }
            
            self.active_crises[confidence_crisis_id] = crisis_record
            
            # Apply confidence restoration protocol
            restoration_protocol = self.crisis_resolution_protocols["loss_of_confidence"]
            restoration_actions = []
            
            # Determine required actions based on scope
            if len(confidence_assessment["agents_with_lost_confidence"]) > 1:
                # Multiple agents - systemic crisis
                restoration_actions.extend([
                    "Systemic loss of confidence identified",
                    "Cabinet dissolution recommended",
                    "Crown intervention required for system restoration"
                ])
                restoration_type = "systemic"
            else:
                # Individual agent crisis
                affected_agent = confidence_assessment["agents_with_lost_confidence"][0]
                restoration_actions.extend([
                    f"Individual loss of confidence: {affected_agent}",
                    "Agent resignation or dismissal required",
                    "Replacement appointment needed"
                ])
                restoration_type = "individual"
            
            restoration_result = {
                "confidence_crisis_id": confidence_crisis_id,
                "restoration_type": restoration_type,
                "affected_agents": confidence_assessment["agents_with_lost_confidence"],
                "restoration_actions": restoration_actions,
                "crown_intervention_required": restoration_type == "systemic",
                "parliamentary_dissolution_recommended": restoration_type == "systemic"
            }
            
            if restoration_type == "systemic":
                restoration_result["emergency_protocols"] = [
                    "Suspend normal parliamentary operations",
                    "Invoke Crown emergency powers",
                    "Establish interim governance",
                    "Plan system reconstitution"
                ]
                crisis_record["status"] = "systemic_crisis"
            else:
                crisis_record["status"] = "individual_crisis"
            
            await self.logfire_logger.critical(
                "Loss of confidence crisis handled",
                crisis_id=confidence_crisis_id,
                crisis_type=restoration_type,
                affected_agents=len(confidence_assessment["agents_with_lost_confidence"])
            )
            
            return restoration_result
    
    async def restore_constitutional_order(self) -> Dict[str, Any]:
        """
        Restore constitutional order after crisis resolution.
        
        Implements post-crisis procedures to ensure stable governance.
        """
        with logfire.span("restore_constitutional_order") as span:
            restoration_id = f"restore_{uuid.uuid4().hex[:8]}"
            span.set_attribute("restoration_id", restoration_id)
            
            # Assess current system state
            system_state = await self._assess_post_crisis_state()
            
            restoration_plan = {
                "restoration_id": restoration_id,
                "initiated_at": datetime.now(timezone.utc),
                "system_state_assessment": system_state,
                "restoration_steps": [],
                "constitutional_compliance_restored": False,
                "parliamentary_confidence_restored": False
            }
            
            # Step 1: Verify constitutional compliance
            if system_state["constitutional_violations"] > 0:
                restoration_plan["restoration_steps"].append(
                    "Address remaining constitutional violations"
                )
            else:
                restoration_plan["constitutional_compliance_restored"] = True
            
            # Step 2: Confirm agent appointments
            if system_state["vacant_positions"] > 0:
                restoration_plan["restoration_steps"].append(
                    f"Fill {system_state['vacant_positions']} vacant positions"
                )
            
            # Step 3: Restore parliamentary confidence
            confidence_restoration = await self._restore_parliamentary_confidence()
            restoration_plan["restoration_steps"].extend(confidence_restoration["actions"])
            restoration_plan["parliamentary_confidence_restored"] = confidence_restoration["successful"]
            
            # Step 4: Resume normal operations
            if (restoration_plan["constitutional_compliance_restored"] and 
                restoration_plan["parliamentary_confidence_restored"]):
                restoration_plan["restoration_steps"].append("Resume normal parliamentary operations")
                restoration_plan["constitutional_order_restored"] = True
                
                # Clear resolved crises
                for crisis_id, crisis in self.active_crises.items():
                    if crisis.get("status") in ["resolved", "restored"]:
                        crisis["completed_at"] = datetime.now(timezone.utc)
            
            await self.logfire_logger.info(
                "Constitutional order restoration attempted",
                restoration_id=restoration_id,
                order_restored=restoration_plan["constitutional_order_restored"]
            )
            
            return restoration_plan
    
    async def _analyze_dissenting_positions(
        self,
        dissenting_agents: List[str],
        proposal: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze why agents are dissenting from collective position."""
        
        analysis = {
            "dissenting_agents": dissenting_agents,
            "common_concerns": [],
            "constitutional_objections": [],
            "compromise_possible": False
        }
        
        # In a real system, this would query agents for their specific objections
        # For now, we'll simulate based on proposal characteristics
        if proposal.get("constitutional_impact"):
            analysis["constitutional_objections"].append("Concerns about constitutional compliance")
        
        if proposal.get("resource_intensive"):
            analysis["common_concerns"].append("Resource allocation concerns")
        
        # Assess if compromise is possible
        analysis["compromise_possible"] = len(analysis["constitutional_objections"]) == 0
        
        return analysis
    
    async def _attempt_compromise_negotiation(
        self,
        proposal: Dict[str, Any],
        agent_positions: Dict[str, str],
        dissent_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Attempt to negotiate a compromise solution."""
        
        if not dissent_analysis["compromise_possible"]:
            return {
                "successful": False,
                "reason": "Constitutional objections cannot be compromised"
            }
        
        # Simple compromise logic - in reality would be more sophisticated
        if len(dissent_analysis["common_concerns"]) <= 2:
            return {
                "successful": True,
                "compromise_proposal": {
                    **proposal,
                    "modified": True,
                    "concerns_addressed": dissent_analysis["common_concerns"]
                }
            }
        
        return {
            "successful": False,
            "reason": "Too many irreconcilable differences"
        }
    
    async def _identify_deadlock_issues(self) -> List[Dict[str, Any]]:
        """Identify current constitutional deadlock issues."""
        
        # Simulate deadlock detection
        issues = []
        
        # Check for ongoing crises
        for crisis_id, crisis in self.active_crises.items():
            if crisis.get("status") in ["unresolved", "escalated"]:
                issues.append({
                    "issue_type": "unresolved_crisis",
                    "crisis_id": crisis_id,
                    "severity": crisis.get("severity", "moderate"),
                    "duration_hours": (datetime.now(timezone.utc) - crisis["triggered_at"]).total_seconds() / 3600
                })
        
        return issues
    
    async def _analyze_constitutional_issues(
        self,
        issues: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze constitutional issues for resolution guidance."""
        
        return {
            "total_issues": len(issues),
            "critical_issues": len([i for i in issues if i.get("severity") == "critical"]),
            "constitutional_principles_affected": [
                ConstitutionalPrinciple.SEPARATION_OF_POWERS,
                ConstitutionalPrinciple.COLLECTIVE_RESPONSIBILITY
            ],
            "resolution_complexity": "high" if len(issues) > 2 else "moderate"
        }
    
    async def _invoke_parliamentary_procedure(
        self,
        issues: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Invoke parliamentary procedures to resolve issues."""
        
        actions_taken = []
        
        for issue in issues:
            if issue["issue_type"] == "unresolved_crisis":
                actions_taken.append(f"Escalated crisis {issue['crisis_id']} to parliamentary procedure")
        
        return {
            "successful": len(actions_taken) > 0,
            "actions": actions_taken
        }
    
    async def _assess_system_confidence(self) -> Dict[str, Any]:
        """Assess current system-wide confidence levels."""
        
        # Simulate confidence assessment
        agents = ["planner_agent", "executor_agent", "evaluator_agent"]
        agents_with_lost_confidence = []
        
        # Simple simulation - in reality would check actual confidence metrics
        for crisis in self.active_crises.values():
            if crisis.get("severity") == "critical":
                agents_with_lost_confidence.extend(crisis.get("affected_agents", []))
        
        return {
            "overall_confidence": "lost" if agents_with_lost_confidence else "maintained",
            "agents_with_lost_confidence": list(set(agents_with_lost_confidence)),
            "confidence_score": 0.3 if agents_with_lost_confidence else 0.9
        }
    
    async def _assess_post_crisis_state(self) -> Dict[str, Any]:
        """Assess system state after crisis events."""
        
        return {
            "constitutional_violations": len([
                c for c in self.active_crises.values() 
                if c.get("crisis_type") == "constitutional_violation"
            ]),
            "vacant_positions": len([
                c for c in self.active_crises.values()
                if c.get("status") == "resignation_required"
            ]),
            "active_crises": len([
                c for c in self.active_crises.values()
                if c.get("status") not in ["resolved", "completed"]
            ])
        }
    
    async def _restore_parliamentary_confidence(self) -> Dict[str, Any]:
        """Restore parliamentary confidence in the system."""
        
        actions = [
            "Verify all agent positions are filled",
            "Confirm constitutional compliance",
            "Resume normal parliamentary procedures"
        ]
        
        return {
            "successful": True,  # Simplified for demonstration
            "actions": actions
        }
    
    def get_active_crises(self) -> Dict[str, Any]:
        """Get all currently active constitutional crises."""
        return {
            crisis_id: crisis for crisis_id, crisis in self.active_crises.items()
            if crisis.get("status") not in ["resolved", "completed"]
        }
    
    def get_crisis_statistics(self) -> Dict[str, Any]:
        """Get statistics on constitutional crises."""
        
        total_crises = len(self.active_crises)
        resolved_crises = len([
            c for c in self.active_crises.values()
            if c.get("status") in ["resolved", "completed"]
        ])
        
        crisis_types = {}
        for crisis in self.active_crises.values():
            crisis_type = crisis.get("crisis_type", "unknown")
            crisis_types[crisis_type] = crisis_types.get(crisis_type, 0) + 1
        
        return {
            "total_crises": total_crises,
            "resolved_crises": resolved_crises,
            "active_crises": total_crises - resolved_crises,
            "resolution_rate": resolved_crises / total_crises if total_crises > 0 else 0,
            "crisis_types": crisis_types,
            "average_resolution_time_hours": 24.0  # Placeholder
        }