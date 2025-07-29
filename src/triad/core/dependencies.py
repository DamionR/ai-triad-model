"""
Dependency Injection System for Westminster Parliamentary AI System

Implements comprehensive dependency injection with constitutional oversight,
parliamentary procedures, and Crown authority management.
"""

from dataclasses import dataclass
from typing import Protocol, Optional, Dict, Any, List
import asyncio
import logfire
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

from .constitutional import ConstitutionalFramework, ConstitutionalDecision, ConstitutionalAuthority


class MCPClient(Protocol):
    """Protocol for Model Context Protocol client."""
    async def call_tool(self, tool_name: str, operation: str, parameters: dict) -> dict: ...
    async def register_adapter(self, adapter_name: str, adapter: Any) -> None: ...
    async def close(self) -> None: ...


class A2ABroker(Protocol):
    """Protocol for Agent-to-Agent communication broker."""
    async def broadcast_event(self, event: dict) -> None: ...
    async def broadcast_status_update(self, status: dict) -> None: ...
    async def broadcast_emergency(self, emergency: dict) -> None: ...
    async def register_cache_coordination(self, config: dict) -> None: ...
    async def close(self) -> None: ...


class ParliamentaryProcedure(Protocol):
    """Protocol for parliamentary procedures and democratic processes."""
    async def formal_response(self, question: str, responding_agent: str, 
                             questioning_agent: str, constitutional_requirement: bool) -> dict: ...
    async def ministerial_defense(self, decision: str, minister: str, challenger: str) -> dict: ...
    async def initiate_question_period(self, questions: List[dict]) -> dict: ...
    async def vote_of_no_confidence(self, target_agent: str, reasons: List[str]) -> dict: ...


class ConstitutionalCrisisManager(Protocol):
    """Protocol for constitutional crisis management."""
    async def handle_collective_responsibility_crisis(self, proposal: dict, agent_positions: dict) -> dict: ...
    async def resolve_constitutional_deadlock(self) -> dict: ...
    async def handle_loss_of_confidence(self) -> dict: ...
    async def restore_constitutional_order(self) -> dict: ...


class CrownPrerogative(Protocol):
    """Protocol for Crown reserve powers and constitutional authority."""
    async def exercise_reserve_power(self, power_type: str, justification: str, 
                                   affected_agents: List[str]) -> dict: ...
    async def grant_royal_assent(self, decision: ConstitutionalDecision) -> dict: ...
    async def dismiss_agents(self, agents: List[str]) -> dict: ...
    async def dissolve_government(self) -> dict: ...
    async def activate_emergency_governance(self) -> dict: ...


@dataclass
class TriadDeps:
    """
    Core dependencies container for all agents with complete Westminster framework.
    
    This contains all the dependencies needed for constitutional AI governance
    following Westminster parliamentary principles.
    """
    db_session: AsyncSession
    mcp_client: MCPClient
    a2a_broker: A2ABroker
    logfire_logger: logfire.Logger
    parliamentary_procedure: ParliamentaryProcedure
    constitutional_crisis_manager: ConstitutionalCrisisManager
    crown_prerogative: CrownPrerogative
    constitutional_framework: ConstitutionalFramework
    config: 'TriadConfig'
    http_client: Optional[AsyncClient] = None
    
    async def log_event(self, event_type: str, data: dict):
        """Centralized event logging with constitutional oversight."""
        await self.logfire_logger.info(
            f"Event: {event_type}",
            event_type=event_type,
            constitutional_oversight=True,
            **data
        )
        
        # Westminster parliamentary procedure: Log for constitutional record
        await self.log_constitutional_record(event_type, data)
        
        # Notify other agents via A2A protocol
        await self.a2a_broker.broadcast_event({
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
            "constitutional_branch": data.get("agent", "unknown")
        })
    
    async def log_constitutional_record(self, event_type: str, data: dict):
        """Log events for constitutional parliamentary record (Hansard equivalent)."""
        constitutional_record = {
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
            "constitutional_authority": data.get("agent", "system"),
            "parliamentary_session": await self.get_current_parliamentary_session(),
            "recorded_by": "constitutional_clerk"
        }
        
        # Store in constitutional record database
        from ..database.models import ConstitutionalRecordTable
        from sqlalchemy import insert
        
        await self.db_session.execute(
            insert(ConstitutionalRecordTable).values(**constitutional_record)
        )
        await self.db_session.commit()
    
    async def get_current_parliamentary_session(self) -> Optional[str]:
        """Get current parliamentary session ID."""
        if self.constitutional_framework.current_session:
            return self.constitutional_framework.current_session.session_id
        return None
    
    async def exercise_crown_prerogative(
        self, 
        prerogative_type: str, 
        justification: str,
        affected_agents: List[str]
    ) -> Dict[str, Any]:
        """Exercise Crown prerogative powers (Governor General equivalent)."""
        
        # Westminster Crown powers: dismissal, dissolution, appointment, assent
        if prerogative_type not in ["dismiss", "dissolve", "appoint", "refuse_assent", "emergency_powers"]:
            raise ValueError(f"Invalid Crown prerogative: {prerogative_type}")
        
        crown_action = {
            "prerogative_type": prerogative_type,
            "justification": justification,
            "affected_agents": affected_agents,
            "exercised_by": "overwatch_agent",
            "timestamp": datetime.utcnow().isoformat(),
            "constitutional_authority": "crown"
        }
        
        # Log constitutional intervention
        await self.logfire_logger.warning(
            "Crown prerogative exercised",
            **crown_action,
            constitutional_intervention=True
        )
        
        # Execute prerogative power through Crown protocol
        result = await self.crown_prerogative.exercise_reserve_power(
            prerogative_type, justification, affected_agents
        )
        
        return {**crown_action, "result": result}
    
    async def validate_constitutional_decision(
        self,
        decision: ConstitutionalDecision
    ) -> Dict[str, Any]:
        """Validate decision through constitutional framework."""
        return await self.constitutional_framework.validate_constitutional_decision(decision)
    
    async def integrate_external_system(
        self, 
        system_type: str, 
        operation: str, 
        parameters: dict
    ) -> dict:
        """Universal integration with existing systems via MCP."""
        with logfire.span("external_system_integration") as span:
            span.set_attribute("system_type", system_type)
            span.set_attribute("operation", operation)
            span.set_attribute("constitutional_oversight", True)
            
            result = await self.mcp_client.call_tool(
                f"{system_type}_adapter",
                operation,
                {**parameters, "constitutional_validation": True}
            )
            
            return result
    
    async def initiate_question_period(
        self,
        questioning_agent: str,
        target_agent: str,
        questions: List[str]
    ) -> Dict[str, Any]:
        """Initiate Westminster-style Question Period between agents."""
        question_period_data = {
            "questioning_agent": questioning_agent,
            "target_agent": target_agent,
            "questions": questions,
            "timestamp": datetime.utcnow().isoformat(),
            "parliamentary_session": await self.get_current_parliamentary_session()
        }
        
        # Execute through parliamentary procedure
        result = await self.parliamentary_procedure.initiate_question_period([
            {
                "question": q,
                "questioning_agent": questioning_agent,
                "target_agent": target_agent
            }
            for q in questions
        ])
        
        await self.log_event("question_period_initiated", question_period_data)
        
        return result
    
    async def collective_cabinet_decision(
        self,
        proposal: Dict[str, Any],
        required_agents: List[str]
    ) -> Dict[str, Any]:
        """Handle collective cabinet responsibility decisions."""
        
        # Create constitutional decision
        decision = ConstitutionalDecision(
            constitutional_authority=ConstitutionalAuthority.EXECUTIVE,
            decision_type="collective_cabinet",
            description=f"Collective cabinet decision: {proposal.get('title', 'Unknown')}",
            requires_collective_approval=True,
            agent_responsible="cabinet_collective"
        )
        
        # Validate constitutionally
        validation = await self.validate_constitutional_decision(decision)
        
        if not validation["constitutional_compliance"]:
            return {
                "approved": False,
                "reason": "Constitutional compliance failure",
                "violations": validation["violations"]
            }
        
        # Get positions from all required agents
        agent_positions = {}
        for agent in required_agents:
            # This would typically call the agent's decision method
            # For now, we'll simulate the process
            agent_positions[agent] = {
                "stance": "SUPPORT",  # This would be determined by the agent
                "reasoning": "Constitutional compliance verified",
                "prepared_to_resign": False
            }
        
        # Check for collective agreement
        all_support = all(pos["stance"] == "SUPPORT" for pos in agent_positions.values())
        
        if not all_support:
            # Trigger collective responsibility crisis
            return await self.constitutional_crisis_manager.handle_collective_responsibility_crisis(
                proposal, agent_positions
            )
        
        await self.log_event("collective_cabinet_decision", {
            "proposal": proposal,
            "agent_positions": agent_positions,
            "decision_approved": all_support
        })
        
        return {
            "collective_agreement": True,
            "agent_positions": agent_positions,
            "decision_approved": True,
            "constitutional_compliance": True
        }
    
    async def close(self):
        """Cleanup resources with constitutional logging."""
        await self.log_event("system_shutdown", {
            "reason": "Graceful shutdown initiated",
            "constitutional_authority": "crown"
        })
        
        if self.http_client:
            await self.http_client.aclose()
        await self.db_session.close()
        await self.a2a_broker.close()
        await self.mcp_client.close()


class TriadConfig:
    """Configuration settings for the Triad constitutional system."""
    
    def __init__(self):
        self.DATABASE_URL: str = "postgresql+asyncpg://localhost/triad_constitutional"
        self.LOGFIRE_TOKEN: str = ""
        self.A2A_BROKER_URL: str = "redis://localhost:6379"
        self.MCP_SERVER_URLS: Dict[str, str] = {}
        self.MODEL_CONFIGS: Dict[str, Any] = {
            "planner": {"model": "openai:gpt-4o", "temperature": 0.1},
            "executor": {"model": "openai:gpt-4o", "temperature": 0.0},
            "evaluator": {"model": "anthropic:claude-3-5-sonnet-latest", "temperature": 0.0},
            "overwatch": {"model": "openai:gpt-4o", "temperature": 0.1}
        }
        self.PERFORMANCE_THRESHOLDS: Dict[str, float] = {
            "task_timeout_seconds": 300,
            "max_memory_mb": 1024,
            "max_cpu_percent": 80.0,
            "accuracy_threshold": 0.95,
            "error_rate_threshold": 0.01,
            "constitutional_compliance_threshold": 0.95
        }
        self.INTEGRATION_ADAPTERS: Dict[str, str] = {}
        
        # Westminster Constitutional Settings
        self.PARLIAMENTARY_SESSION_DURATION_HOURS: int = 24 * 30  # 30 days
        self.QUESTION_PERIOD_MAX_DURATION_MINUTES: int = 60
        self.COLLECTIVE_RESPONSIBILITY_TIMEOUT_MINUTES: int = 30
        self.CROWN_INTERVENTION_THRESHOLD: float = 0.80  # Compliance below 80% triggers Crown review
        
        # Security and Authentication
        self.JWT_SECRET_KEY: str = ""
        self.JWT_ALGORITHM: str = "HS256"
        self.JWT_EXPIRATION_HOURS: int = 8
        
        # External System Integration
        self.MCP_TIMEOUT_SECONDS: int = 30
        self.A2A_MESSAGE_TIMEOUT_SECONDS: int = 10
        self.EXTERNAL_SYSTEM_RETRY_COUNT: int = 3
    
    @classmethod
    def from_environment(cls) -> 'TriadConfig':
        """Load configuration from environment variables."""
        import os
        
        config = cls()
        
        # Override with environment variables
        config.DATABASE_URL = os.getenv("DATABASE_URL", config.DATABASE_URL)
        config.LOGFIRE_TOKEN = os.getenv("LOGFIRE_TOKEN", config.LOGFIRE_TOKEN)
        config.A2A_BROKER_URL = os.getenv("A2A_BROKER_URL", config.A2A_BROKER_URL)
        config.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", config.JWT_SECRET_KEY)
        
        # MCP Server URLs from environment
        mcp_urls = os.getenv("MCP_SERVER_URLS", "")
        if mcp_urls:
            config.MCP_SERVER_URLS = dict(
                pair.split("=") for pair in mcp_urls.split(",") if "=" in pair
            )
        
        return config