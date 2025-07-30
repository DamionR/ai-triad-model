"""
Base Agent Class for Westminster Parliamentary AI System

Provides common functionality for all agents including constitutional
compliance, parliamentary procedures, and democratic accountability.
"""

from typing import Optional, Dict, Any, List
from pydantic_ai import Agent, RunContext
from dataclasses import dataclass
import logfire

from triad.core.dependencies import TriadDeps
from triad.core.constitutional import ConstitutionalAuthority, ConstitutionalDecision


class BaseAgent:
    """
    Base class for all Westminster Parliamentary agents.
    
    Provides common functionality including:
    - Constitutional compliance validation
    - Parliamentary procedure adherence
    - Democratic accountability mechanisms
    - Crown oversight integration
    """
    
    def __init__(
        self,
        name: str,
        constitutional_authority: ConstitutionalAuthority,
        model: str,
        system_prompt: str,
        deps_type: type[TriadDeps] = TriadDeps
    ):
        self.name = name
        self.constitutional_authority = constitutional_authority
        self.model = model
        
        # Create the Pydantic AI agent
        self.agent = Agent(
            model,
            deps_type=deps_type,
            system_prompt=system_prompt
        )
        
        # Register common tools
        self._register_common_tools()
        
        # Convert to A2A application for inter-agent communication
        self.a2a_app = None
    
    def _register_common_tools(self):
        """Register tools common to all agents."""
        
        @self.agent.tool
        async def validate_constitutional_decision(
            ctx: RunContext[TriadDeps],
            decision_type: str,
            description: str,
            requires_collective_approval: bool = False,
            requires_royal_assent: bool = False
        ) -> Dict[str, Any]:
            """Validate a decision against constitutional principles."""
            decision = ConstitutionalDecision(
                constitutional_authority=self.constitutional_authority,
                decision_type=decision_type,
                description=description,
                requires_collective_approval=requires_collective_approval,
                requires_royal_assent=requires_royal_assent,
                agent_responsible=self.name
            )
            
            validation_result = await ctx.deps.validate_constitutional_decision(decision)
            
            await ctx.deps.log_event(
                "constitutional_decision_validated",
                {
                    "agent": self.name,
                    "decision_id": decision.decision_id,
                    "compliant": validation_result["constitutional_compliance"],
                    "violations": validation_result["violations"]
                }
            )
            
            return validation_result
        
        @self.agent.tool
        async def participate_in_question_period(
            ctx: RunContext[TriadDeps],
            question: str,
            questioner: str,
            constitutional_challenge: bool = False
        ) -> str:
            """Participate in Westminster-style Question Period."""
            response = await ctx.deps.parliamentary_procedure.formal_response(
                question=question,
                responding_agent=self.name,
                questioning_agent=questioner,
                constitutional_requirement=constitutional_challenge
            )
            
            await ctx.deps.log_event(
                "question_period_participation",
                {
                    "agent": self.name,
                    "questioner": questioner,
                    "question": question,
                    "constitutional_challenge": constitutional_challenge,
                    "response": response
                }
            )
            
            return response["response_text"]
        
        @self.agent.tool
        async def request_crown_intervention(
            ctx: RunContext[TriadDeps],
            intervention_type: str,
            justification: str,
            urgency: str = "normal"
        ) -> Dict[str, Any]:
            """Request Crown (Overwatch) intervention for constitutional matters."""
            if urgency == "emergency":
                # Emergency powers can be invoked immediately
                result = await ctx.deps.exercise_crown_prerogative(
                    intervention_type,
                    justification,
                    [self.name]
                )
            else:
                # Normal process requires formal request
                await ctx.deps.log_event(
                    "crown_intervention_requested",
                    {
                        "requesting_agent": self.name,
                        "intervention_type": intervention_type,
                        "justification": justification,
                        "urgency": urgency
                    }
                )
                result = {"status": "pending_crown_review", "request_logged": True}
            
            return result
        
        @self.agent.tool
        async def log_parliamentary_record(
            ctx: RunContext[TriadDeps],
            event_type: str,
            details: Dict[str, Any]
        ) -> None:
            """Log events to parliamentary record (Hansard)."""
            await ctx.deps.log_constitutional_record(
                event_type,
                {
                    **details,
                    "agent": self.name,
                    "constitutional_authority": self.constitutional_authority.value
                }
            )
    
    def to_a2a(self):
        """Convert agent to A2A application for inter-agent communication."""
        if not self.a2a_app:
            self.a2a_app = self.agent.to_a2a()
        return self.a2a_app
    
    async def check_confidence(self, deps: TriadDeps) -> Dict[str, Any]:
        """Check if agent maintains confidence of the system."""
        with logfire.span("confidence_check", agent=self.name):
            # Check performance metrics
            performance_query = """
            SELECT 
                constitutional_compliance_score,
                confidence_level,
                ministerial_standing
            FROM agent_performance
            WHERE agent_name = $1
            ORDER BY evaluated_at DESC
            LIMIT 1
            """
            
            result = await deps.db_session.execute(
                performance_query,
                [self.name]
            )
            row = result.fetchone()
            
            if not row:
                return {
                    "confidence_maintained": True,
                    "compliance_score": 1.0,
                    "standing": "new_agent"
                }
            
            return {
                "confidence_maintained": row["confidence_level"] == "maintained",
                "compliance_score": row["constitutional_compliance_score"],
                "standing": row["ministerial_standing"],
                "action_required": row["confidence_level"] == "lost"
            }
    
    async def handle_no_confidence(self, deps: TriadDeps, reasons: List[str]) -> Dict[str, Any]:
        """Handle a no-confidence motion against this agent."""
        with logfire.span("no_confidence_handling", agent=self.name):
            await deps.log_event(
                "no_confidence_motion",
                {
                    "target_agent": self.name,
                    "reasons": reasons,
                    "constitutional_authority": self.constitutional_authority.value
                }
            )
            
            # Agent must defend or resign
            defense_options = {
                "defend": "Present defense in Question Period",
                "resign": "Accept responsibility and resign",
                "appeal": "Appeal to Crown for intervention"
            }
            
            return {
                "motion_received": True,
                "defense_options": defense_options,
                "constitutional_process": "Westminster no-confidence procedure initiated"
            }