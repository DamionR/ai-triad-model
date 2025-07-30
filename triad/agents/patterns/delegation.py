"""
Agent Delegation Patterns

Implements Pydantic AI delegation patterns with proper authority levels,
message passing, and governance oversight for organizational workflows.
"""

import asyncio
from typing import Dict, List, Optional, Any, Union, Type
from datetime import datetime, timezone
from enum import Enum
import logfire
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models import ModelSettings
from pydantic_ai.messages import ModelMessage, UserPromptPart, SystemPromptPart

from triad.models.model_config import (
    get_model_config, 
    GovernanceRole,
    TriadModelConfig
)
from triad.tools.governance.base import (
    GovernanceContext,
    AuthorityLevel,
    SecurityLevel
)
from triad.agents.core.enhanced_agents import EnhancedGovernanceDeps
from triad.core.logging import get_logfire_config


class DelegationAuthority(Enum):
    """Authority levels for agent delegation."""
    WITHIN_DEPARTMENT = "within_department"      # Delegate within same department
    CROSS_DEPARTMENT = "cross_department"        # Delegate to different department
    SPECIALIZED_TEAM = "specialized_team"        # Delegate to specialized sub-team
    EXTERNAL_CONSULTANT = "external_consultant"  # Delegate to external consultant
    ESCALATION = "escalation"                    # Emergency escalation delegation


class MessageContext(BaseModel):
    """Context passed between agents during delegation."""
    originating_agent: str
    authority_level: AuthorityLevel
    delegation_chain: List[str] = Field(default_factory=list)
    session_id: Optional[str] = None
    context_metadata: Dict[str, Any] = Field(default_factory=dict)


class DelegationResult(BaseModel):
    """Result of an agent delegation operation."""
    delegated_to: str
    delegation_type: DelegationAuthority
    task_description: str
    result: Any
    usage_data: Dict[str, Any] = Field(default_factory=dict)
    governance_compliance: bool = True
    recommendations: List[str] = Field(default_factory=list)
    follow_up_required: bool = False
    delegation_successful: bool = True
    execution_time_seconds: float = 0.0


class GovernanceDelegationAgent:
    """
    Enhanced governance agent with proper Pydantic AI delegation patterns.
    
    Implements agent delegation, message passing, usage tracking, and
    multi-agent coordination following Pydantic AI best practices.
    """
    
    def __init__(
        self,
        role: GovernanceRole,
        agent_id: Optional[str] = None,
        model_config: Optional[TriadModelConfig] = None
    ):
        self.role = role
        self.agent_id = agent_id or f"{role.value}_delegation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.logger = get_logfire_config()
        self.model_config = model_config or get_model_config()
        
        # Create base agent
        self.agent = self.model_config.create_governance_agent(role)
        
        # Sub-agents for delegation
        self.sub_agents: Dict[str, Agent] = {}
        
        # Governance context
        self.governance_context = GovernanceContext(
            agent_id=self.agent_id,
            authority_level=self._role_to_authority(role),
            security_level=self._get_security_level(role)
        )
        
        # Enhanced dependencies with delegation support
        self.deps = EnhancedGovernanceDeps(
            agent_id=self.agent_id,
            authority_level=self._role_to_authority(role),
            governance_role=role,
            security_level=self._get_security_level(role)
        )
        
        # Register delegation tools
        self._register_delegation_tools()
    
    def _role_to_authority(self, role: GovernanceRole) -> AuthorityLevel:
        """Convert governance role to authority level."""
        authority_map = {
            GovernanceRole.PLANNER: AuthorityLevel.POLICY_MAKER,
            GovernanceRole.EXECUTOR: AuthorityLevel.EXECUTOR,
            GovernanceRole.EVALUATOR: AuthorityLevel.REVIEWER,
            GovernanceRole.OVERWATCH: AuthorityLevel.OVERSEER
        }
        return authority_map[role]
    
    def _get_security_level(self, role: GovernanceRole) -> SecurityLevel:
        """Get security level for role."""
        security_map = {
            GovernanceRole.PLANNER: SecurityLevel.MANAGEMENT,
            GovernanceRole.EXECUTOR: SecurityLevel.INTERNAL,
            GovernanceRole.EVALUATOR: SecurityLevel.MANAGEMENT,
            GovernanceRole.OVERWATCH: SecurityLevel.EXECUTIVE
        }
        return security_map[role]
    
    def _register_delegation_tools(self):
        """Register delegation tools with the agent following Pydantic AI patterns."""
        
        @self.agent.tool
        async def delegate_to_specialized_team(
            ctx: RunContext[EnhancedGovernanceDeps],
            team_type: str,
            task_description: str,
            urgency: str = "normal"
        ) -> str:
            """
            Delegate task to specialized organizational team.
            
            This follows Pydantic AI delegation pattern with proper usage tracking.
            """
            return await self._execute_delegation(
                ctx=ctx,
                delegation_type=DelegationAuthority.SPECIALIZED_TEAM,
                target_identifier=team_type,
                task_description=task_description,
                additional_params={"urgency": urgency}
            )
        
        @self.agent.tool
        async def coordinate_with_department(
            ctx: RunContext[EnhancedGovernanceDeps],
            target_department: str,
            coordination_request: str,
            policy_basis: str
        ) -> str:
            """
            Coordinate with other organizational departments (cross-department delegation).
            
            Implements proper cross-department communication with governance oversight.
            """
            return await self._execute_delegation(
                ctx=ctx,
                delegation_type=DelegationAuthority.CROSS_DEPARTMENT,
                target_identifier=target_department,
                task_description=coordination_request,
                additional_params={"policy_basis": policy_basis}
            )
        
        @self.agent.tool
        async def escalate_governance_issue(
            ctx: RunContext[EnhancedGovernanceDeps],
            issue_description: str,
            severity_level: str,
            immediate_actions_needed: List[str]
        ) -> str:
            """
            Escalate governance issue to higher authority.
            
            Emergency delegation pattern for governance issue management.
            """
            return await self._execute_delegation(
                ctx=ctx,
                delegation_type=DelegationAuthority.ESCALATION,
                target_identifier="oversight_authority",
                task_description=issue_description,
                additional_params={
                    "severity_level": severity_level,
                    "immediate_actions": immediate_actions_needed
                }
            )
        
        @self.agent.tool
        async def delegate_within_department(
            ctx: RunContext[EnhancedGovernanceDeps],
            team: str,
            task_description: str,
            deadline: Optional[str] = None
        ) -> str:
            """
            Delegate task within the same organizational department.
            
            Implements within-department delegation for specialized tasks.
            """
            return await self._execute_delegation(
                ctx=ctx,
                delegation_type=DelegationAuthority.WITHIN_DEPARTMENT,
                target_identifier=team,
                task_description=task_description,
                additional_params={"deadline": deadline}
            )
        
        @self.agent.tool
        async def consult_external_expert(
            ctx: RunContext[EnhancedGovernanceDeps],
            expertise_area: str,
            consultation_request: str,
            expert_credentials_required: str = "professional"
        ) -> str:
            """
            Consult external expert system or advisory body.
            
            Implements external expert delegation pattern.
            """
            return await self._execute_delegation(
                ctx=ctx,
                delegation_type=DelegationAuthority.EXTERNAL_CONSULTANT,
                target_identifier=expertise_area,
                task_description=consultation_request,
                additional_params={"credentials_required": expert_credentials_required}
            )
    
    async def _execute_delegation(
        self,
        ctx: RunContext[EnhancedGovernanceDeps],
        delegation_type: DelegationAuthority,
        target_identifier: str,
        task_description: str,
        additional_params: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Execute delegation following Pydantic AI patterns.
        
        This implements proper usage tracking, message context passing,
        and governance oversight for all delegations.
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            # Create message context for delegation
            message_context = MessageContext(
                originating_agent=self.agent_id,
                authority_level=self.governance_context.authority_level,
                delegation_chain=[self.agent_id],
                session_id=ctx.deps.session_id,
                context_metadata=additional_params or {}
            )
            
            # Get or create sub-agent for delegation target
            sub_agent = await self._get_or_create_sub_agent(
                target_identifier, delegation_type
            )
            
            # Prepare delegation prompt with governance context
            delegation_prompt = self._prepare_delegation_prompt(
                task_description, delegation_type, message_context, additional_params
            )
            
            # Execute delegation with proper usage tracking
            # This follows Pydantic AI pattern: pass ctx.usage to track total usage
            delegation_result = await sub_agent.run(
                delegation_prompt,
                deps=ctx.deps,  # Pass the same deps
                message_history=ctx.message_history if hasattr(ctx, 'message_history') else None,
                usage=ctx.usage  # Critical: pass usage for tracking
            )
            
            # Calculate execution time
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            # Create delegation result
            result = DelegationResult(
                delegated_to=target_identifier,
                delegation_type=delegation_type,
                task_description=task_description,
                result=delegation_result.data,
                usage_data=ctx.usage.__dict__ if ctx.usage else {},
                governance_compliance=True,  # Would validate this
                recommendations=[],
                follow_up_required=False,
                delegation_successful=True,
                execution_time_seconds=execution_time
            )
            
            # Log delegation
            self.logger.log_governance_event(
                event_type="delegation_executed",
                data={
                    "delegation_type": delegation_type.value,
                    "target": target_identifier,
                    "task_summary": task_description[:100],
                    "execution_time": execution_time,
                    "authority": self.governance_context.authority_level.value,
                    "agent_id": self.agent_id
                },
                authority=self.governance_context.authority_level.value
            )
            
            return f"Delegation to {target_identifier} completed successfully. Result: {delegation_result.data}"
            
        except Exception as e:
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            self.logger.log_governance_event(
                event_type="delegation_error",
                data={
                    "error": str(e),
                    "delegation_type": delegation_type.value,
                    "target": target_identifier,
                    "execution_time": execution_time,
                    "agent_id": self.agent_id
                },
                authority=self.governance_context.authority_level.value
            )
            
            return f"Delegation to {target_identifier} failed: {e}"
    
    async def _get_or_create_sub_agent(
        self, 
        target_identifier: str, 
        delegation_type: DelegationAuthority
    ) -> Agent:
        """Get or create sub-agent for delegation target."""
        
        if target_identifier not in self.sub_agents:
            # Create specialized sub-agent based on delegation type
            if delegation_type == DelegationAuthority.SPECIALIZED_TEAM:
                # Create team-specific agent
                sub_agent = self.model_config.create_governance_agent(
                    self.role,  # Same role but specialized
                    custom_settings=ModelSettings(
                        temperature=0.2,  # More focused for specialized work
                        max_tokens=2048
                    )
                )
                
                system_prompt = f"""You are a specialized organizational team for {target_identifier}.
                Your role is to provide detailed analysis and recommendations within your area of expertise.
                You report to the {self.role.value} agent and must maintain governance accountability."""
                
            elif delegation_type == DelegationAuthority.CROSS_DEPARTMENT:
                # Create cross-department coordination agent
                sub_agent = self.model_config.create_governance_agent(
                    GovernanceRole.EXECUTOR,  # Use executor role for coordination
                    custom_settings=ModelSettings(
                        temperature=0.3,
                        max_tokens=3072
                    )
                )
                
                system_prompt = f"""You are a cross-department coordination agent for {target_identifier}.
                Your role is to facilitate communication and coordination between organizational departments.
                Maintain governance standards and ensure proper authority levels are respected."""
                
            elif delegation_type == DelegationAuthority.EXTERNAL_CONSULTANT:
                # Create external expert consultation agent
                sub_agent = self.model_config.create_governance_agent(
                    GovernanceRole.EVALUATOR,  # Use evaluator role for expert analysis
                    custom_settings=ModelSettings(
                        temperature=0.1,  # Very focused for expert consultation
                        max_tokens=4096
                    )
                )
                
                system_prompt = f"""You are an external expert consultant in {target_identifier}.
                Provide professional analysis and recommendations based on your expertise.
                Maintain objectivity and provide evidence-based insights."""
                
            elif delegation_type == DelegationAuthority.ESCALATION:
                # Create escalation handling agent
                sub_agent = self.model_config.create_governance_agent(
                    GovernanceRole.OVERWATCH,  # Use overwatch role for escalations
                    custom_settings=ModelSettings(
                        temperature=0.1,  # Very focused for crisis handling
                        max_tokens=2048
                    )
                )
                
                system_prompt = f"""You are an escalation handling agent for governance issues.
                Your role is to assess escalated issues and provide appropriate oversight responses.
                Ensure governance compliance and recommend appropriate actions."""
                
            else:  # WITHIN_DEPARTMENT
                # Create within-department agent
                sub_agent = self.model_config.create_governance_agent(
                    self.role,
                    custom_settings=ModelSettings(
                        temperature=0.3,
                        max_tokens=2048
                    )
                )
                
                system_prompt = f"""You are a departmental agent for {target_identifier}.
                Your role is to handle specialized tasks within the department.
                Follow department procedures and report to your department lead."""
            
            # Store the sub-agent
            self.sub_agents[target_identifier] = sub_agent
        
        return self.sub_agents[target_identifier]
    
    def _prepare_delegation_prompt(
        self,
        task_description: str,
        delegation_type: DelegationAuthority,
        message_context: MessageContext,
        additional_params: Optional[Dict[str, Any]]
    ) -> str:
        """Prepare delegation prompt with proper context."""
        
        prompt = f"""
DELEGATION CONTEXT:
- Originating Agent: {message_context.originating_agent}
- Authority Level: {message_context.authority_level.value}
- Delegation Type: {delegation_type.value}
- Session ID: {message_context.session_id}

TASK DESCRIPTION:
{task_description}

ADDITIONAL PARAMETERS:
{additional_params or 'None'}

Please complete this delegated task according to organizational governance standards.
Provide a clear, actionable response with recommendations if appropriate.
        """
        
        return prompt.strip()