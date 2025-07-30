"""
Enhanced Westminster Parliamentary Agents with Tools and MCP Integration

Provides constitutional agents with comprehensive toolsets, MCP server access,
and parliamentary-specific capabilities for democratic governance.
"""

import asyncio
from typing import Dict, List, Optional, Any, Type
from datetime import datetime, timezone
from enum import Enum
import logfire
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models import ModelSettings

from triad.models.model_config import (
    get_model_config, 
    ParliamentaryRole, 
    create_constitutional_agents as create_base_agents
)
from triad.tools.parliamentary_toolsets import (
    ParliamentaryContext,
    ParliamentaryAuthority,
    ToolSecurityLevel,
    get_toolset,
    register_toolsets_with_agent
)
from triad.tools.mcp_integration import (
    get_parliamentary_mcp_client,
    setup_constitutional_agent_mcp_tools,
    CONSTITUTIONAL_AGENT_MCP_TOOLS
)
from triad.core.logging import get_logfire_config
from triad.database.prisma_client import get_prisma_client


class AgentCapability(Enum):
    """Capabilities that can be enabled for parliamentary agents."""
    CONSTITUTIONAL_REVIEW = "constitutional_review"
    LEGISLATIVE_ANALYSIS = "legislative_analysis"
    PARLIAMENTARY_PROCEDURE = "parliamentary_procedure"
    POLICY_RESEARCH = "policy_research"
    CITIZEN_ENGAGEMENT = "citizen_engagement"
    CRISIS_MANAGEMENT = "crisis_management"
    AUDIT_AND_OVERSIGHT = "audit_and_oversight"
    INTERNATIONAL_RELATIONS = "international_relations"


class EnhancedParliamentaryDeps(BaseModel):
    """Enhanced dependencies for parliamentary agents with tools and MCP."""
    
    # Basic parliamentary context
    agent_id: str
    constitutional_authority: ParliamentaryAuthority
    parliamentary_role: ParliamentaryRole
    
    # Session context
    session_id: Optional[str] = None
    parliamentary_session_id: Optional[str] = None
    
    # Security and permissions
    security_clearance: ToolSecurityLevel = ToolSecurityLevel.PARLIAMENTARY
    constitutional_oversight: bool = True
    
    # Capabilities
    enabled_capabilities: List[AgentCapability] = Field(default_factory=list)
    
    # Tool configuration
    available_toolsets: List[str] = Field(default_factory=list)
    mcp_servers: Dict[str, List[str]] = Field(default_factory=dict)
    
    # Agent metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: Optional[datetime] = None
    
    # Performance tracking
    tasks_completed: int = 0
    constitutional_reviews_conducted: int = 0
    parliamentary_procedures_managed: int = 0


class EnhancedConstitutionalAgent:
    """
    Enhanced constitutional agent with integrated tools and MCP capabilities.
    
    Provides comprehensive parliamentary functionality including constitutional
    oversight, legislative analysis, and democratic process management.
    """
    
    def __init__(
        self,
        role: ParliamentaryRole,
        agent_id: Optional[str] = None,
        custom_capabilities: Optional[List[AgentCapability]] = None,
        custom_model_settings: Optional[ModelSettings] = None
    ):
        self.role = role
        self.agent_id = agent_id or f"{role.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.logger = get_logfire_config()
        self.model_config = get_model_config()
        self.mcp_client = get_parliamentary_mcp_client()
        
        # Initialize capabilities based on role
        self.capabilities = self._get_default_capabilities(role)
        if custom_capabilities:
            self.capabilities.extend(custom_capabilities)
        
        # Create parliamentary context
        self.parliamentary_context = ParliamentaryContext(
            agent_id=self.agent_id,
            constitutional_authority=self._role_to_authority(role),
            security_clearance=self._get_security_clearance(role),
            constitutional_oversight=True
        )
        
        # Create enhanced dependencies
        self.deps = EnhancedParliamentaryDeps(
            agent_id=self.agent_id,
            constitutional_authority=self._role_to_authority(role),
            parliamentary_role=role,
            security_clearance=self._get_security_clearance(role),
            enabled_capabilities=self.capabilities,
            available_toolsets=self._get_default_toolsets(role),
            mcp_servers=CONSTITUTIONAL_AGENT_MCP_TOOLS.get(role.value, {})
        )
        
        # Create base agent
        self.agent = self._create_base_agent(custom_model_settings)
        
        # Enhanced agent will be initialized async
        self._initialized = False
    
    def _get_default_capabilities(self, role: ParliamentaryRole) -> List[AgentCapability]:
        """Get default capabilities for a parliamentary role."""
        capability_map = {
            ParliamentaryRole.PLANNER: [
                AgentCapability.LEGISLATIVE_ANALYSIS,
                AgentCapability.POLICY_RESEARCH,
                AgentCapability.CITIZEN_ENGAGEMENT,
                AgentCapability.CONSTITUTIONAL_REVIEW
            ],
            ParliamentaryRole.EXECUTOR: [
                AgentCapability.POLICY_RESEARCH,
                AgentCapability.PARLIAMENTARY_PROCEDURE,
                AgentCapability.AUDIT_AND_OVERSIGHT,
                AgentCapability.INTERNATIONAL_RELATIONS
            ],
            ParliamentaryRole.EVALUATOR: [
                AgentCapability.CONSTITUTIONAL_REVIEW,
                AgentCapability.LEGISLATIVE_ANALYSIS,
                AgentCapability.AUDIT_AND_OVERSIGHT,
                AgentCapability.CRISIS_MANAGEMENT
            ],
            ParliamentaryRole.OVERWATCH: [
                AgentCapability.CONSTITUTIONAL_REVIEW,
                AgentCapability.CRISIS_MANAGEMENT,
                AgentCapability.AUDIT_AND_OVERSIGHT,
                AgentCapability.PARLIAMENTARY_PROCEDURE
            ]
        }
        
        return capability_map.get(role, [])
    
    def _role_to_authority(self, role: ParliamentaryRole) -> ParliamentaryAuthority:
        """Convert parliamentary role to constitutional authority."""
        authority_map = {
            ParliamentaryRole.PLANNER: ParliamentaryAuthority.LEGISLATIVE,
            ParliamentaryRole.EXECUTOR: ParliamentaryAuthority.EXECUTIVE,
            ParliamentaryRole.EVALUATOR: ParliamentaryAuthority.JUDICIAL,
            ParliamentaryRole.OVERWATCH: ParliamentaryAuthority.CROWN,
            ParliamentaryRole.SPEAKER: ParliamentaryAuthority.SPEAKER,
            ParliamentaryRole.CLERK: ParliamentaryAuthority.CLERK
        }
        
        return authority_map[role]
    
    def _get_security_clearance(self, role: ParliamentaryRole) -> ToolSecurityLevel:
        """Get security clearance level for role."""
        clearance_map = {
            ParliamentaryRole.PLANNER: ToolSecurityLevel.PARLIAMENTARY,
            ParliamentaryRole.EXECUTOR: ToolSecurityLevel.MINISTERIAL,
            ParliamentaryRole.EVALUATOR: ToolSecurityLevel.CONSTITUTIONAL,
            ParliamentaryRole.OVERWATCH: ToolSecurityLevel.CROWN,
            ParliamentaryRole.SPEAKER: ToolSecurityLevel.PARLIAMENTARY,
            ParliamentaryRole.CLERK: ToolSecurityLevel.PARLIAMENTARY
        }
        
        return clearance_map[role]
    
    def _get_default_toolsets(self, role: ParliamentaryRole) -> List[str]:
        """Get default toolsets for a parliamentary role."""
        toolset_map = {
            ParliamentaryRole.PLANNER: [
                "constitutional",
                "legislative", 
                "parliamentary_procedure"
            ],
            ParliamentaryRole.EXECUTOR: [
                "legislative",
                "parliamentary_procedure"
            ],
            ParliamentaryRole.EVALUATOR: [
                "constitutional",
                "legislative"
            ],
            ParliamentaryRole.OVERWATCH: [
                "constitutional",
                "parliamentary_procedure"
            ]
        }
        
        return toolset_map.get(role, ["constitutional"])
    
    def _create_base_agent(self, custom_settings: Optional[ModelSettings] = None) -> Agent:
        """Create the base Pydantic AI agent."""
        return self.model_config.create_parliamentary_agent(
            role=self.role,
            custom_settings=custom_settings
        )
    
    async def initialize(self) -> None:
        """Initialize the enhanced agent with tools and MCP capabilities."""
        if self._initialized:
            return
        
        try:
            with self.logger.parliamentary_session_span(
                f"agent-initialization-{self.role.value}",
                [self.agent_id]
            ) as span:
                
                # Register parliamentary toolsets
                await register_toolsets_with_agent(
                    agent=self.agent,
                    toolsets=self.deps.available_toolsets,
                    parliamentary_context=self.parliamentary_context
                )
                
                # Setup MCP tools based on role
                await setup_constitutional_agent_mcp_tools(
                    agent=self.agent,
                    agent_role=self.role.value,
                    parliamentary_context=self.parliamentary_context
                )
                
                # Log successful initialization
                self.logger.log_agent_activity(
                    agent_name=self.agent_id,
                    activity="agent_initialized",
                    data={
                        "role": self.role.value,
                        "constitutional_authority": self.parliamentary_context.constitutional_authority.value,
                        "capabilities": [cap.value for cap in self.capabilities],
                        "toolsets": self.deps.available_toolsets,
                        "mcp_servers": list(self.deps.mcp_servers.keys()),
                        "security_clearance": self.deps.security_clearance.value
                    }
                )
                
                span.set_attribute("agent.role", self.role.value)
                span.set_attribute("agent.capabilities_count", len(self.capabilities))
                span.set_attribute("agent.toolsets_count", len(self.deps.available_toolsets))
                
                self._initialized = True
                
        except Exception as e:
            self.logger.log_agent_activity(
                agent_name=self.agent_id,
                activity="agent_initialization_error",
                data={
                    "error": str(e),
                    "role": self.role.value
                }
            )
            raise
    
    async def run_with_context(
        self,
        prompt: str,
        session_id: Optional[str] = None,
        parliamentary_session_id: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None,
        message_history: Optional[List] = None,
        usage=None
    ) -> Any:
        """
        Run the agent with parliamentary context and constitutional oversight.
        
        Now implements proper Pydantic AI patterns for message passing and usage tracking.
        
        Args:
            prompt: The prompt to execute
            session_id: Optional session ID for tracking
            parliamentary_session_id: Optional parliamentary session ID
            additional_context: Additional context data
            message_history: ModelMessage history for context (Pydantic AI pattern)
            usage: Usage tracking object (Pydantic AI pattern)
        
        Returns:
            Agent response with constitutional metadata
        """
        if not self._initialized:
            await self.initialize()
        
        # Update context
        self.deps.session_id = session_id
        self.deps.parliamentary_session_id = parliamentary_session_id
        self.deps.last_activity = datetime.now(timezone.utc)
        
        try:
            async with self.logger.agent_task_span(
                self.agent_id,
                "parliamentary_task_execution",
                {
                    "prompt_length": len(prompt),
                    "session_id": session_id,
                    "parliamentary_session_id": parliamentary_session_id,
                    "additional_context": bool(additional_context),
                    "message_history_length": len(message_history) if message_history else 0
                }
            ) as span:
                
                # Execute with proper Pydantic AI patterns
                response = await self.agent.run(
                    prompt,
                    deps=self.deps,
                    message_history=message_history or [],  # Proper message history passing
                    usage=usage  # Proper usage tracking
                )
                
                # Update performance metrics
                self.deps.tasks_completed += 1
                
                # Add constitutional metadata to response
                constitutional_metadata = {
                    "executed_by": self.agent_id,
                    "constitutional_authority": self.parliamentary_context.constitutional_authority.value,
                    "parliamentary_role": self.role.value,
                    "execution_timestamp": datetime.now(timezone.utc).isoformat(),
                    "session_id": session_id,
                    "parliamentary_session_id": parliamentary_session_id,
                    "constitutional_oversight": True,
                    "security_clearance": self.deps.security_clearance.value,
                    "tasks_completed": self.deps.tasks_completed,
                    "usage_data": usage.__dict__ if usage else None
                }
                
                # Log task completion
                self.logger.log_agent_activity(
                    agent_name=self.agent_id,
                    activity="task_completed",
                    data={
                        "prompt_summary": prompt[:100] + "..." if len(prompt) > 100 else prompt,
                        "response_length": len(str(response)),
                        "session_context": bool(session_id),
                        "parliamentary_context": bool(parliamentary_session_id),
                        "message_history_length": len(message_history) if message_history else 0
                    }
                )
                
                span.set_attribute("task.completed", True)
                span.set_attribute("response.length", len(str(response)))
                span.set_attribute("message_history.length", len(message_history) if message_history else 0)
                
                return {
                    "response": response,
                    "constitutional_metadata": constitutional_metadata,
                    "message_history": message_history,
                    "usage": usage
                }
                
        except Exception as e:
            self.logger.log_agent_activity(
                agent_name=self.agent_id,
                activity="task_execution_error",
                data={
                    "error": str(e),
                    "prompt_summary": prompt[:100] + "..." if len(prompt) > 100 else prompt
                }
            )
            raise
    
    async def conduct_constitutional_review(
        self,
        subject: str,
        review_data: Dict[str, Any],
        review_type: str = "compliance"
    ) -> Dict[str, Any]:
        """
        Conduct a constitutional review with enhanced capabilities.
        
        Args:
            subject: Subject of the review
            review_data: Data to review
            review_type: Type of review (compliance, crisis, interpretation)
        
        Returns:
            Constitutional review results
        """
        if AgentCapability.CONSTITUTIONAL_REVIEW not in self.capabilities:
            raise PermissionError(f"Agent {self.agent_id} lacks constitutional review capability")
        
        if not self._initialized:
            await self.initialize()
        
        try:
            # Use constitutional toolset for review
            constitutional_toolset = get_toolset("constitutional")
            
            # Create context for review
            review_context = RunContext(deps=self.deps)
            
            # Perform appropriate type of review
            if review_type == "compliance":
                result = await constitutional_toolset.call_tool(
                    "validate_constitutional_compliance",
                    {
                        "action_type": subject,
                        "action_data": review_data,
                        "constitutional_basis": review_data.get("constitutional_basis")
                    },
                    review_context
                )
            elif review_type == "crisis":
                result = await constitutional_toolset.call_tool(
                    "detect_constitutional_crisis",
                    {
                        "event_data": review_data,
                        "severity_threshold": 0.7
                    },
                    review_context
                )
            else:
                raise ValueError(f"Unknown review type: {review_type}")
            
            # Update performance metrics
            self.deps.constitutional_reviews_conducted += 1
            
            # Log constitutional review
            self.logger.log_constitutional_event(
                event=f"constitutional_review_{review_type}",
                authority=self.parliamentary_context.constitutional_authority.value,
                details={
                    "subject": subject,
                    "review_type": review_type,
                    "conducted_by": self.agent_id,
                    "reviews_conducted": self.deps.constitutional_reviews_conducted
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.log_constitutional_event(
                event="constitutional_review_error",
                authority=self.parliamentary_context.constitutional_authority.value,
                details={
                    "error": str(e),
                    "subject": subject,
                    "review_type": review_type,
                    "agent_id": self.agent_id
                }
            )
            raise
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the enhanced agent."""
        return {
            "agent_id": self.agent_id,
            "role": self.role.value,
            "constitutional_authority": self.parliamentary_context.constitutional_authority.value,
            "security_clearance": self.deps.security_clearance.value,
            "initialized": self._initialized,
            "capabilities": [cap.value for cap in self.capabilities],
            "toolsets": self.deps.available_toolsets,
            "mcp_servers": self.deps.mcp_servers,
            "performance": {
                "tasks_completed": self.deps.tasks_completed,
                "constitutional_reviews_conducted": self.deps.constitutional_reviews_conducted,
                "parliamentary_procedures_managed": self.deps.parliamentary_procedures_managed
            },
            "session_context": {
                "current_session_id": self.deps.session_id,
                "parliamentary_session_id": self.deps.parliamentary_session_id,
                "last_activity": self.deps.last_activity.isoformat() if self.deps.last_activity else None
            },
            "created_at": self.deps.created_at.isoformat(),
            "constitutional_oversight": self.deps.constitutional_oversight
        }


class ParliamentaryAgentManager:
    """
    Manager for enhanced constitutional agents with comprehensive oversight.
    
    Provides centralized management, coordination, and monitoring of all
    parliamentary agents in the Westminster system.
    """
    
    def __init__(self):
        self.logger = get_logfire_config()
        self.agents: Dict[str, EnhancedConstitutionalAgent] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
    async def create_constitutional_agents(
        self,
        custom_capabilities: Optional[Dict[ParliamentaryRole, List[AgentCapability]]] = None
    ) -> Dict[ParliamentaryRole, EnhancedConstitutionalAgent]:
        """
        Create all four constitutional agents with enhanced capabilities.
        
        Args:
            custom_capabilities: Optional custom capabilities per role
        
        Returns:
            Dictionary of enhanced constitutional agents
        """
        try:
            agents = {}
            
            for role in [ParliamentaryRole.PLANNER, ParliamentaryRole.EXECUTOR,
                        ParliamentaryRole.EVALUATOR, ParliamentaryRole.OVERWATCH]:
                
                # Get custom capabilities for this role
                role_capabilities = None
                if custom_capabilities and role in custom_capabilities:
                    role_capabilities = custom_capabilities[role]
                
                # Create enhanced agent
                agent = EnhancedConstitutionalAgent(
                    role=role,
                    custom_capabilities=role_capabilities
                )
                
                # Initialize agent
                await agent.initialize()
                
                # Store agent
                agents[role] = agent
                self.agents[agent.agent_id] = agent
            
            self.logger.log_parliamentary_event(
                event_type="constitutional_agents_created",
                data={
                    "agent_count": len(agents),
                    "roles": [role.value for role in agents.keys()],
                    "total_capabilities": sum(len(agent.capabilities) for agent in agents.values())
                },
                authority="system"
            )
            
            return agents
            
        except Exception as e:
            self.logger.log_parliamentary_event(
                event_type="agent_creation_error",
                data={"error": str(e)},
                authority="system"
            )
            raise
    
    async def start_parliamentary_session(
        self,
        session_type: str,
        participating_agents: List[str],
        agenda: Optional[List[str]] = None
    ) -> str:
        """
        Start a parliamentary session with multiple agents.
        
        Args:
            session_type: Type of parliamentary session
            participating_agents: List of agent IDs to participate
            agenda: Optional session agenda
        
        Returns:
            Parliamentary session ID
        """
        session_id = f"parliament_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Validate participating agents
            for agent_id in participating_agents:
                if agent_id not in self.agents:
                    raise ValueError(f"Unknown agent: {agent_id}")
            
            # Create session record
            session_record = {
                "session_id": session_id,
                "session_type": session_type,
                "participating_agents": participating_agents,
                "agenda": agenda or [],
                "started_at": datetime.now(timezone.utc),
                "status": "active",
                "proceedings": []
            }
            
            self.active_sessions[session_id] = session_record
            
            # Notify participating agents
            for agent_id in participating_agents:
                agent = self.agents[agent_id]
                agent.deps.parliamentary_session_id = session_id
            
            self.logger.log_parliamentary_event(
                event_type="parliamentary_session_started",
                data={
                    "session_id": session_id,
                    "session_type": session_type,
                    "participant_count": len(participating_agents),
                    "agenda_items": len(agenda) if agenda else 0
                },
                authority="speaker"
            )
            
            return session_id
            
        except Exception as e:
            self.logger.log_parliamentary_event(
                event_type="parliamentary_session_start_error",
                data={
                    "error": str(e),
                    "session_type": session_type
                },
                authority="speaker"
            )
            raise
    
    async def coordinate_agents(
        self,
        task: str,
        participating_roles: List[ParliamentaryRole],
        coordination_type: str = "collaborative"
    ) -> Dict[str, Any]:
        """
        Coordinate multiple agents for a complex parliamentary task.
        
        Args:
            task: Task description
            participating_roles: Roles that should participate
            coordination_type: Type of coordination (collaborative, sequential, oversight)
        
        Returns:
            Coordination results from all participating agents
        """
        try:
            coordination_id = f"coord_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Find agents for participating roles
            participating_agents = []
            for role in participating_roles:
                for agent in self.agents.values():
                    if agent.role == role:
                        participating_agents.append(agent)
                        break
            
            if len(participating_agents) != len(participating_roles):
                raise ValueError("Could not find agents for all required roles")
            
            coordination_results = {
                "coordination_id": coordination_id,
                "task": task,
                "coordination_type": coordination_type,
                "participating_agents": [agent.agent_id for agent in participating_agents],
                "results": {},
                "constitutional_oversight": True,
                "coordinated_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Execute coordination based on type
            if coordination_type == "collaborative":
                # All agents work on the task simultaneously
                tasks = []
                for agent in participating_agents:
                    task_prompt = f"As part of coordination {coordination_id}, please address: {task}"
                    tasks.append(agent.run_with_context(task_prompt))
                
                # Wait for all agents to complete
                agent_responses = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Collect results
                for i, response in enumerate(agent_responses):
                    agent = participating_agents[i]
                    if isinstance(response, Exception):
                        coordination_results["results"][agent.agent_id] = {
                            "status": "error",
                            "error": str(response)
                        }
                    else:
                        coordination_results["results"][agent.agent_id] = response
            
            elif coordination_type == "sequential":
                # Agents work in sequence based on constitutional authority
                authority_order = [
                    ParliamentaryAuthority.LEGISLATIVE,
                    ParliamentaryAuthority.EXECUTIVE,
                    ParliamentaryAuthority.JUDICIAL,
                    ParliamentaryAuthority.CROWN
                ]
                
                # Sort agents by constitutional authority
                sorted_agents = sorted(
                    participating_agents,
                    key=lambda a: authority_order.index(a.parliamentary_context.constitutional_authority)
                    if a.parliamentary_context.constitutional_authority in authority_order else 999
                )
                
                accumulated_context = {"initial_task": task}
                
                for agent in sorted_agents:
                    task_prompt = f"Building on previous work in coordination {coordination_id}: {task}\n"
                    task_prompt += f"Previous context: {accumulated_context}"
                    
                    response = await agent.run_with_context(task_prompt)
                    coordination_results["results"][agent.agent_id] = response
                    
                    # Add to accumulated context
                    accumulated_context[agent.agent_id] = response.get("response", "")
            
            elif coordination_type == "oversight":
                # Primary agents work, oversight agent reviews
                primary_agents = [a for a in participating_agents 
                                if a.parliamentary_context.constitutional_authority != ParliamentaryAuthority.CROWN]
                oversight_agents = [a for a in participating_agents 
                                  if a.parliamentary_context.constitutional_authority == ParliamentaryAuthority.CROWN]
                
                # Primary agents work first
                primary_tasks = []
                for agent in primary_agents:
                    task_prompt = f"As part of oversight coordination {coordination_id}, please address: {task}"
                    primary_tasks.append(agent.run_with_context(task_prompt))
                
                primary_responses = await asyncio.gather(*primary_tasks, return_exceptions=True)
                
                # Collect primary results
                for i, response in enumerate(primary_responses):
                    agent = primary_agents[i]
                    coordination_results["results"][agent.agent_id] = response
                
                # Oversight review
                for oversight_agent in oversight_agents:
                    oversight_prompt = f"Constitutional oversight review for coordination {coordination_id}.\n"
                    oversight_prompt += f"Original task: {task}\n"
                    oversight_prompt += f"Primary agent responses: {primary_responses}"
                    
                    oversight_response = await oversight_agent.conduct_constitutional_review(
                        subject="agent_coordination",
                        review_data={
                            "coordination_id": coordination_id,
                            "task": task,
                            "primary_responses": primary_responses
                        },
                        review_type="compliance"
                    )
                    
                    coordination_results["results"][oversight_agent.agent_id] = {
                        "response": oversight_response,
                        "constitutional_metadata": {
                            "review_type": "coordination_oversight",
                            "constitutional_compliance": oversight_response.get("compliant", True)
                        }
                    }
            
            # Log coordination completion
            self.logger.log_parliamentary_event(
                event_type="agent_coordination_completed",
                data={
                    "coordination_id": coordination_id,
                    "coordination_type": coordination_type,
                    "participating_agents": len(participating_agents),
                    "results_count": len(coordination_results["results"]),
                    "successful_results": sum(1 for r in coordination_results["results"].values() 
                                            if r.get("status") != "error")
                },
                authority="system"
            )
            
            return coordination_results
            
        except Exception as e:
            self.logger.log_parliamentary_event(
                event_type="agent_coordination_error",
                data={
                    "error": str(e),
                    "task": task,
                    "coordination_type": coordination_type
                },
                authority="system"
            )
            raise
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the parliamentary agent system."""
        agent_statuses = {}
        for agent_id, agent in self.agents.items():
            agent_statuses[agent_id] = await agent.get_agent_status()
        
        mcp_status = await get_parliamentary_mcp_client().get_server_status()
        
        return {
            "agent_count": len(self.agents),
            "active_sessions": len(self.active_sessions),
            "agents": agent_statuses,
            "mcp_servers": mcp_status,
            "system_health": "operational",
            "constitutional_oversight": True,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }


# Global agent manager
parliamentary_agent_manager = ParliamentaryAgentManager()


def get_parliamentary_agent_manager() -> ParliamentaryAgentManager:
    """Get the global parliamentary agent manager."""
    return parliamentary_agent_manager


async def create_enhanced_constitutional_agents(
    custom_capabilities: Optional[Dict[ParliamentaryRole, List[AgentCapability]]] = None
) -> Dict[ParliamentaryRole, EnhancedConstitutionalAgent]:
    """
    Create enhanced constitutional agents with comprehensive capabilities.
    
    Args:
        custom_capabilities: Optional custom capabilities per role
    
    Returns:
        Dictionary of enhanced constitutional agents
    """
    manager = get_parliamentary_agent_manager()
    return await manager.create_constitutional_agents(custom_capabilities)