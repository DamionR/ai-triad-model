"""
Parliamentary Procedures Implementation

Westminster parliamentary procedures including Question Period,
collective responsibility, and democratic accountability mechanisms.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import uuid
import logfire

from triad.core.constitutional import ConstitutionalAuthority, ConstitutionalPrinciple


class ParliamentaryProcedure:
    """
    Implementation of Westminster parliamentary procedures.
    
    Provides formal mechanisms for:
    - Question Period
    - Ministerial responsibility
    - Collective cabinet responsibility
    - Parliamentary scrutiny
    """
    
    def __init__(self, logfire_logger: logfire):
        self.logfire_logger = logfire_logger
        self.active_question_periods: Dict[str, Any] = {}
        self.parliamentary_record: List[Dict[str, Any]] = []
        
    async def formal_response(
        self,
        question: str, 
        responding_agent: str,
        questioning_agent: str,
        constitutional_requirement: bool = False
    ) -> Dict[str, Any]:
        """
        Handle formal parliamentary response during Question Period.
        
        Following Westminster tradition where ministers must respond
        to questions about their departments and decisions.
        """
        with logfire.span("formal_parliamentary_response") as span:
            span.set_attribute("responding_agent", responding_agent)
            span.set_attribute("questioning_agent", questioning_agent)
            span.set_attribute("constitutional_requirement", constitutional_requirement)
            
            response_id = f"qp_response_{uuid.uuid4().hex[:8]}"
            
            # Generate formal parliamentary response
            response = await self._generate_parliamentary_response(
                question, responding_agent, questioning_agent, constitutional_requirement
            )
            
            # Record in parliamentary record (Hansard equivalent)
            record_entry = {
                "response_id": response_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "question": question,
                "response": response,
                "responding_agent": responding_agent,
                "questioning_agent": questioning_agent,
                "constitutional_requirement": constitutional_requirement,
                "parliamentary_procedure": "question_period",
                "response_satisfactory": True  # Would be evaluated
            }
            
            self.parliamentary_record.append(record_entry)
            
            await self.logfire_logger.info(
                "Parliamentary response recorded",
                response_id=response_id,
                responding_agent=responding_agent,
                question_type="constitutional" if constitutional_requirement else "standard"
            )
            
            return {
                "response_id": response_id,
                "response_text": response,
                "parliamentary_record": record_entry,
                "follow_up_required": constitutional_requirement,
                "satisfaction_level": "satisfactory"
            }
    
    async def ministerial_defense(
        self,
        decision: str,
        minister: str,
        challenger: str
    ) -> Dict[str, Any]:
        """
        Handle ministerial defense of decisions.
        
        Ministers must defend their decisions when challenged,
        maintaining the principle of ministerial responsibility.
        """
        with logfire.span("ministerial_defense") as span:
            span.set_attribute("minister", minister)
            span.set_attribute("challenger", challenger)
            
            defense_id = f"defense_{uuid.uuid4().hex[:8]}"
            
            # Formulate ministerial defense
            defense = await self._formulate_ministerial_defense(decision, minister, challenger)
            
            # Record defense in parliamentary record
            defense_record = {
                "defense_id": defense_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "decision_challenged": decision,
                "minister": minister,
                "challenger": challenger,
                "defense_statement": defense["statement"],
                "constitutional_grounds": defense["constitutional_grounds"],
                "parliamentary_procedure": "ministerial_defense",
                "successful": defense["successful"]
            }
            
            self.parliamentary_record.append(defense_record)
            
            await self.logfire_logger.info(
                "Ministerial defense recorded",
                defense_id=defense_id,
                minister=minister,
                successful=defense["successful"]
            )
            
            return {
                "defense_id": defense_id,
                "defense_statement": defense["statement"],
                "successful": defense["successful"],
                "constitutional_compliance": defense["constitutional_grounds"],
                "parliamentary_confidence": "maintained" if defense["successful"] else "questioned"
            }
    
    async def initiate_question_period(
        self,
        questions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Initiate formal Question Period session.
        
        Westminster tradition of regular questioning of ministers
        by other members for accountability.
        """
        with logfire.span("question_period_initiation") as span:
            question_period_id = f"qp_{uuid.uuid4().hex[:8]}"
            span.set_attribute("question_period_id", question_period_id)
            span.set_attribute("question_count", len(questions))
            
            question_period = {
                "session_id": question_period_id,
                "start_time": datetime.now(timezone.utc),
                "questions": questions,
                "responses": [],
                "status": "active",
                "parliamentary_procedure": "question_period"
            }
            
            self.active_question_periods[question_period_id] = question_period
            
            # Process each question
            for question_data in questions:
                response = await self.formal_response(
                    question=question_data["question"],
                    responding_agent=question_data["target_agent"],
                    questioning_agent=question_data["questioning_agent"],
                    constitutional_requirement=question_data.get("constitutional_challenge", False)
                )
                question_period["responses"].append(response)
            
            question_period["end_time"] = datetime.now(timezone.utc)
            question_period["status"] = "completed"
            question_period["duration_minutes"] = (
                question_period["end_time"] - question_period["start_time"]
            ).total_seconds() / 60
            
            await self.logfire_logger.info(
                "Question Period completed",
                session_id=question_period_id,
                questions_addressed=len(questions),
                duration_minutes=question_period["duration_minutes"]
            )
            
            return {
                "question_period_id": question_period_id,
                "questions_addressed": len(questions),
                "all_responses_satisfactory": all(
                    r["satisfaction_level"] == "satisfactory" for r in question_period["responses"]
                ),
                "constitutional_challenges": len([
                    q for q in questions if q.get("constitutional_challenge", False)
                ]),
                "parliamentary_confidence": "maintained"
            }
    
    async def vote_of_no_confidence(
        self,
        target_agent: str,
        reasons: List[str]
    ) -> Dict[str, Any]:
        """
        Handle vote of no confidence procedure.
        
        Westminster mechanism for removing ministers who have
        lost the confidence of the House.
        """
        with logfire.span("no_confidence_vote") as span:
            vote_id = f"noconf_{uuid.uuid4().hex[:8]}"
            span.set_attribute("vote_id", vote_id)
            span.set_attribute("target_agent", target_agent)
            
            # Formal no confidence procedure
            vote_record = {
                "vote_id": vote_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "target_agent": target_agent,
                "reasons": reasons,
                "parliamentary_procedure": "no_confidence_vote",
                "motion_text": f"That this House has no confidence in {target_agent}",
                "constitutional_grounds": await self._assess_constitutional_grounds(reasons),
                "vote_result": "pending"
            }
            
            # In a real system, this would involve actual voting
            # For now, we'll assess based on reasons provided
            vote_passes = await self._assess_no_confidence_validity(target_agent, reasons)
            
            vote_record["vote_result"] = "passed" if vote_passes else "failed"
            vote_record["confidence_lost"] = vote_passes
            
            self.parliamentary_record.append(vote_record)
            
            await self.logfire_logger.info(
                "No confidence vote recorded",
                vote_id=vote_id,
                target_agent=target_agent,
                vote_passed=vote_passes
            )
            
            result = {
                "vote_id": vote_id,
                "motion_passed": vote_passes,
                "confidence_lost": vote_passes,
                "constitutional_crisis": vote_passes,
                "required_action": "resignation" if vote_passes else "continue_in_office"
            }
            
            if vote_passes:
                result["crown_intervention_required"] = True
                result["constitutional_implications"] = [
                    "Minister must resign or be dismissed",
                    "Constitutional crisis initiated",
                    "Crown reserve powers may be exercised"
                ]
            
            return result
    
    async def collective_responsibility_check(
        self,
        proposal: Dict[str, Any],
        agent_positions: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Check collective cabinet responsibility compliance.
        
        All cabinet members must publicly support decisions
        or resign - core Westminster principle.
        """
        with logfire.span("collective_responsibility_check") as span:
            check_id = f"colresp_{uuid.uuid4().hex[:8]}"
            span.set_attribute("check_id", check_id)
            
            # Analyze agent positions
            supporters = [agent for agent, position in agent_positions.items() if position == "SUPPORT"]
            opponents = [agent for agent, position in agent_positions.items() if position == "OPPOSE"]
            abstainers = [agent for agent, position in agent_positions.items() if position == "ABSTAIN"]
            
            # Collective responsibility requires unanimous public support
            collective_responsibility_maintained = len(opponents) == 0 and len(abstainers) == 0
            
            responsibility_record = {
                "check_id": check_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "proposal": proposal,
                "agent_positions": agent_positions,
                "supporters": supporters,
                "opponents": opponents,
                "abstainers": abstainers,
                "collective_responsibility_maintained": collective_responsibility_maintained,
                "parliamentary_procedure": "collective_responsibility"
            }
            
            self.parliamentary_record.append(responsibility_record)
            
            result = {
                "collective_agreement": collective_responsibility_maintained,
                "supporters": supporters,
                "dissenting_agents": opponents + abstainers,
                "constitutional_compliance": collective_responsibility_maintained
            }
            
            if not collective_responsibility_maintained:
                result["constitutional_crisis"] = True
                result["required_actions"] = [
                    "Dissenting agents must resign or be dismissed",
                    "Cabinet reshuffling may be required",
                    "Crown intervention may be necessary"
                ]
                result["crisis_type"] = "collective_responsibility_breakdown"
            
            await self.logfire_logger.info(
                "Collective responsibility checked",
                check_id=check_id,
                maintained=collective_responsibility_maintained,
                dissenting_count=len(opponents) + len(abstainers)
            )
            
            return result
    
    async def parliamentary_scrutiny(
        self,
        agent: str,
        scrutiny_type: str,
        evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Conduct parliamentary scrutiny of agent performance.
        
        Ongoing oversight mechanism to ensure accountability.
        """
        with logfire.span("parliamentary_scrutiny") as span:
            scrutiny_id = f"scrutiny_{uuid.uuid4().hex[:8]}"
            span.set_attribute("scrutiny_id", scrutiny_id)
            span.set_attribute("agent", agent)
            span.set_attribute("scrutiny_type", scrutiny_type)
            
            # Conduct scrutiny assessment
            assessment = await self._conduct_scrutiny_assessment(agent, scrutiny_type, evidence)
            
            scrutiny_record = {
                "scrutiny_id": scrutiny_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "agent": agent,
                "scrutiny_type": scrutiny_type,
                "evidence": evidence,
                "assessment": assessment,
                "parliamentary_procedure": "scrutiny",
                "findings": assessment["findings"],
                "recommendations": assessment["recommendations"]
            }
            
            self.parliamentary_record.append(scrutiny_record)
            
            await self.logfire_logger.info(
                "Parliamentary scrutiny completed",
                scrutiny_id=scrutiny_id,
                agent=agent,
                overall_rating=assessment["overall_rating"]
            )
            
            return {
                "scrutiny_id": scrutiny_id,
                "overall_rating": assessment["overall_rating"],
                "findings": assessment["findings"],
                "recommendations": assessment["recommendations"],
                "confidence_maintained": assessment["overall_rating"] >= "satisfactory",
                "follow_up_required": assessment["overall_rating"] == "unsatisfactory"
            }
    
    async def _generate_parliamentary_response(
        self,
        question: str,
        responding_agent: str,
        questioning_agent: str,
        constitutional_requirement: bool
    ) -> str:
        """Generate formal parliamentary response."""
        
        # Authority mapping for responses
        authority_context = {
            "planner_agent": "as the minister responsible for planning and policy",
            "executor_agent": "as the minister responsible for implementation and execution", 
            "evaluator_agent": "as the minister responsible for validation and compliance",
            "overwatch_agent": "speaking for the Crown"
        }
        
        context = authority_context.get(responding_agent, "as a minister of the Crown")
        
        if constitutional_requirement:
            response = f"Thank you for the question from the honourable {questioning_agent}. {context}, I take constitutional matters very seriously. The question regarding '{question}' touches on fundamental Westminster principles that this government upholds. I can assure this House that all actions taken have been in full compliance with our constitutional framework and democratic accountability requirements."
        else:
            response = f"Thank you for the question from the honourable {questioning_agent}. {context}, I am pleased to respond. Regarding '{question}', the government has acted responsibly and in accordance with established procedures. I am confident that our approach maintains both effectiveness and accountability to this House."
        
        return response
    
    async def _formulate_ministerial_defense(
        self,
        decision: str,
        minister: str,
        challenger: str
    ) -> Dict[str, Any]:
        """Formulate ministerial defense of challenged decision."""
        
        # Assess strength of defense based on decision
        constitutional_grounds = [
            "Decision made within constitutional authority",
            "Proper consultation and procedure followed",
            "Maintains separation of powers",
            "Subject to parliamentary oversight"
        ]
        
        defense_statement = f"The honourable {challenger} has challenged the decision regarding '{decision}'. I stand by this decision as it was made within my constitutional authority, following proper procedures, and in the best interests of the system. I am fully accountable to this House for this decision and am prepared to defend it on both procedural and substantive grounds."
        
        # Simple success assessment - in reality would be more complex
        successful = len(decision) > 10  # Arbitrary metric for demonstration
        
        return {
            "statement": defense_statement,
            "constitutional_grounds": constitutional_grounds,
            "successful": successful
        }
    
    async def _assess_constitutional_grounds(
        self,
        reasons: List[str]
    ) -> List[str]:
        """Assess constitutional grounds for no confidence vote."""
        
        constitutional_reasons = []
        
        for reason in reasons:
            if any(term in reason.lower() for term in ["constitutional", "illegal", "improper", "abuse"]):
                constitutional_reasons.append(reason)
        
        return constitutional_reasons
    
    async def _assess_no_confidence_validity(
        self,
        target_agent: str,
        reasons: List[str]
    ) -> bool:
        """Assess whether no confidence vote should pass."""
        
        # Assess based on severity and number of reasons
        constitutional_violations = await self._assess_constitutional_grounds(reasons)
        
        # Vote passes if there are constitutional violations or multiple serious reasons
        return len(constitutional_violations) > 0 or len(reasons) >= 3
    
    async def _conduct_scrutiny_assessment(
        self,
        agent: str,
        scrutiny_type: str,
        evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Conduct assessment during parliamentary scrutiny."""
        
        findings = []
        recommendations = []
        
        # Analyze evidence
        if evidence.get("performance_issues"):
            findings.append("Performance concerns identified")
            recommendations.append("Implement performance improvement plan")
        
        if evidence.get("constitutional_violations"):
            findings.append("Constitutional compliance issues found")
            recommendations.append("Review constitutional procedures")
        
        # Determine overall rating
        if len(findings) == 0:
            overall_rating = "excellent"
        elif len(findings) <= 2:
            overall_rating = "satisfactory"
        else:
            overall_rating = "unsatisfactory"
        
        return {
            "findings": findings,
            "recommendations": recommendations,
            "overall_rating": overall_rating,
            "evidence_assessment": "thorough" if len(evidence) > 3 else "adequate"
        }
    
    def get_parliamentary_record(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        procedure_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get parliamentary record (Hansard) entries."""
        
        filtered_records = self.parliamentary_record
        
        if start_date:
            filtered_records = [
                r for r in filtered_records 
                if datetime.fromisoformat(r["timestamp"]) >= start_date
            ]
        
        if end_date:
            filtered_records = [
                r for r in filtered_records
                if datetime.fromisoformat(r["timestamp"]) <= end_date
            ]
        
        if procedure_type:
            filtered_records = [
                r for r in filtered_records
                if r.get("parliamentary_procedure") == procedure_type
            ]
        
        return filtered_records
    
    def get_question_period_statistics(self) -> Dict[str, Any]:
        """Get statistics on Question Period activity."""
        
        qp_records = [r for r in self.parliamentary_record if r.get("parliamentary_procedure") == "question_period"]
        
        if not qp_records:
            return {
                "total_questions": 0,
                "satisfactory_responses": 0,
                "constitutional_challenges": 0,
                "response_rate": 0.0
            }
        
        constitutional_challenges = len([
            r for r in qp_records if r.get("constitutional_requirement", False)
        ])
        
        satisfactory_responses = len([
            r for r in qp_records if r.get("response_satisfactory", True)
        ])
        
        return {
            "total_questions": len(qp_records),
            "satisfactory_responses": satisfactory_responses,
            "constitutional_challenges": constitutional_challenges,
            "response_rate": satisfactory_responses / len(qp_records) if qp_records else 0.0,
            "average_constitutional_challenges_per_period": constitutional_challenges / len(self.active_question_periods) if self.active_question_periods else 0
        }