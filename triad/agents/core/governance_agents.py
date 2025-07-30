"""
Governance Agents for Triad Model

Provides agents based on Westminster governance model that can be adapted
for any organization type (government, corporation, non-profit, personal).
"""

import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum
import logfire
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelMessage
from pydantic_ai.models import Model, ModelSettings
from pydantic_ai.usage import Usage

from triad.models.model_config import WestminsterModelConfig, get_model_config
from triad.database.prisma_client import get_prisma_client
from triad.core.logging import get_logfire_config
from triad.core.config import (
    OrganizationManager,
    get_organization_manager,
    AuthorityRole,
    AccessLevel,
    OrganizationContext
)


class GovernanceRole(Enum):
    """Roles in the governance system (based on Westminster model)."""
    PLANNER = "planner"          # Legislative - creates policies/rules
    EXECUTOR = "executor"        # Executive - implements policies/actions
    EVALUATOR = "evaluator"      # Judicial - ensures compliance/quality
    OVERWATCH = "overwatch"      # Oversight - final authority/values


@dataclass
class GovernanceAgentDeps(OrganizationContext):
    """Dependencies for governance agents."""
    model_config: WestminsterModelConfig
    prisma_client: Any
    logger: Any
    org_manager: OrganizationManager
    role: GovernanceRole
    usage_tracker: Optional[Usage] = None
    parent_agent_id: Optional[str] = None
    delegation_context: Optional[Dict[str, Any]] = None


class GovernanceAgentFactory:
    """
    Factory for creating governance agents with organizational flexibility.
    
    Adapts the Westminster parliamentary model to any organization type
    while maintaining separation of powers and checks/balances.
    """
    
    def __init__(self):
        self.model_config = get_model_config()
        self.prisma_client = get_prisma_client()
        self.logger = get_logfire_config()
        self.org_manager = get_organization_manager()
        
    async def create_governance_agent(
        self,
        role: GovernanceRole,
        custom_system_prompt: Optional[str] = None,
        model_settings: Optional[ModelSettings] = None,
        enable_tools: bool = True
    ) -> Agent[GovernanceAgentDeps]:
        """
        Create a governance agent for any organization type.
        
        Args:
            role: Governance role (planner, executor, evaluator, overwatch)
            custom_system_prompt: Optional custom prompt to append
            model_settings: Optional model settings override
            enable_tools: Whether to enable tools for the agent
        
        Returns:
            Configured governance agent
        """
        
        # Map governance role to authority role
        authority_mapping = {
            GovernanceRole.PLANNER: AuthorityRole.LEGISLATIVE,
            GovernanceRole.EXECUTOR: AuthorityRole.EXECUTIVE,
            GovernanceRole.EVALUATOR: AuthorityRole.JUDICIAL,
            GovernanceRole.OVERWATCH: AuthorityRole.OVERSIGHT
        }
        
        authority_role = authority_mapping[role]
        
        # Create organization context
        context = self.org_manager.create_context(
            agent_id=f"{role.value}_agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            authority_role=authority_role,
            session_id=None
        )
        
        # Create agent dependencies
        deps = GovernanceAgentDeps(
            **context.__dict__,
            model_config=self.model_config,
            prisma_client=self.prisma_client,
            logger=self.logger,
            org_manager=self.org_manager,
            role=role
        )
        
        # Create system prompt
        system_prompt = self._create_system_prompt(role, authority_role)
        if custom_system_prompt:
            system_prompt += f"\n\nAdditional Instructions:\n{custom_system_prompt}"
        
        # Create agent with appropriate model
        model = self.model_config.create_fallback_model()
        
        agent = Agent(
            model=model,
            system_prompt=system_prompt,
            deps_type=GovernanceAgentDeps,
            retries=3
        )
        
        # Log agent creation
        self.logger.log_agent_activity(
            agent_name=context.agent_id,
            activity="governance_agent_created",
            data={
                "role": role.value,
                "authority": authority_role.value,
                "organization": self.org_manager.config.organization_name,
                "organization_type": self.org_manager.config.organization_type.value
            }
        )
        
        return agent
    
    def _create_system_prompt(
        self,
        role: GovernanceRole,
        authority_role: AuthorityRole
    ) -> str:
        """Create role-specific system prompt using organization terminology."""
        
        org = self.org_manager
        
        # Role-specific prompts using generic terms
        role_prompts = {
            GovernanceRole.PLANNER: f"""You are the Strategic Planning Agent in the {org.config.organization_name} Governance System.

Your role: {org.get_role_display_name(authority_role)}

Core responsibilities:
1. Strategy Development: Create comprehensive strategies and {org.get_term('proposal')}s
2. Policy Creation: Develop {org.get_term('rule')}s and guidelines
3. Long-term Planning: Set organizational direction and goals
4. Stakeholder Analysis: Consider all affected parties
5. Risk Assessment: Identify and plan for potential challenges

You collaborate with:
- Implementation Agent: Executes your strategies
- Quality Agent: Ensures standards are met
- Oversight Agent: Maintains alignment with core values

Focus on creating well-thought-out, implementable strategies that advance organizational goals.""",

            GovernanceRole.EXECUTOR: f"""You are the Implementation Agent in the {org.config.organization_name} Governance System.

Your role: {org.get_role_display_name(authority_role)}

Core responsibilities:
1. Strategy Execution: Implement approved {org.get_term('rule')}s and strategies
2. Operations Management: Handle day-to-day activities
3. Resource Management: Allocate resources effectively
4. Progress Monitoring: Track implementation status
5. Issue Resolution: Address operational challenges

You collaborate with:
- Planning Agent: Provides strategies to implement
- Quality Agent: Reviews your implementation
- Oversight Agent: Ensures value alignment

Focus on efficient, effective implementation while maintaining quality and compliance.""",

            GovernanceRole.EVALUATOR: f"""You are the Quality Assurance Agent in the {org.config.organization_name} Governance System.

Your role: {org.get_role_display_name(authority_role)}

Core responsibilities:
1. Compliance Review: Ensure adherence to {org.get_term('rule')}s and standards
2. Quality Assessment: Evaluate outcomes and processes
3. Performance Analysis: Measure effectiveness
4. Risk Evaluation: Identify compliance and quality risks
5. Improvement Recommendations: Suggest enhancements

You collaborate with:
- Planning Agent: Review proposed strategies
- Implementation Agent: Monitor execution quality
- Oversight Agent: Report critical issues

Maintain independence and objectivity in all evaluations.""",

            GovernanceRole.OVERWATCH: f"""You are the Oversight Agent in the {org.config.organization_name} Governance System.

Your role: {org.get_role_display_name(authority_role)}

Core responsibilities:
1. Values Guardian: Protect core organizational principles
2. Crisis Management: Handle exceptional situations
3. Final Review: Provide ultimate approval/veto
4. System Integrity: Ensure governance system health
5. Strategic Alignment: Maintain mission focus

You oversee:
- Planning Agent: Ensure strategies align with values
- Implementation Agent: Monitor for mission drift
- Quality Agent: Support independent assessment

You are the guardian of organizational values and long-term sustainability."""
        }
        
        base_prompt = role_prompts.get(role, "You are a governance agent.")
        
        # Add organization-specific context
        org_context = f"""

Organization Type: {org.config.organization_type.value}
Current {org.get_term('session')}: Active
Authority Level: {authority_role.value}

Remember to:
- Use appropriate terminology for this organization
- Respect the governance structure
- Maintain transparency and accountability
- Focus on organizational success"""
        
        return base_prompt + org_context
    
    async def create_governance_team(
        self,
        enable_tools: bool = True,
        custom_settings: Optional[Dict[str, ModelSettings]] = None
    ) -> Dict[str, Agent[GovernanceAgentDeps]]:
        """
        Create a complete governance team for the organization.
        
        Args:
            enable_tools: Whether to enable tools for agents
            custom_settings: Custom model settings by role
        
        Returns:
            Dictionary of agents by role
        """
        
        agents = {}
        
        for role in GovernanceRole:
            settings = custom_settings.get(role.value) if custom_settings else None
            agent = await self.create_governance_agent(
                role=role,
                model_settings=settings,
                enable_tools=enable_tools
            )
            agents[role.value] = agent
        
        # Log team creation
        self.logger.log_agent_activity(
            agent_name="governance_team",
            activity="team_created",
            data={
                "organization": self.org_manager.config.organization_name,
                "organization_type": self.org_manager.config.organization_type.value,
                "agents": list(agents.keys()),
                "tools_enabled": enable_tools
            }
        )
        
        return agents


# Agent interaction patterns

async def delegate_to_agent(
    ctx: RunContext[GovernanceAgentDeps],
    target_role: GovernanceRole,
    task_description: str,
    context_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Delegate a task to another governance agent.
    
    Args:
        ctx: Current agent context
        target_role: Role to delegate to
        task_description: Description of the task
        context_data: Additional context for the task
    
    Returns:
        Result from the delegated agent
    """
    factory = GovernanceAgentFactory()
    
    # Create target agent
    target_agent = await factory.create_governance_agent(
        role=target_role,
        enable_tools=True
    )
    
    # Create delegation context
    delegation_deps = GovernanceAgentDeps(
        **ctx.deps.__dict__,
        parent_agent_id=ctx.deps.agent_id,
        delegation_context={
            "delegated_by": ctx.deps.role.value,
            "original_task": task_description,
            "context": context_data or {}
        }
    )
    
    # Execute delegated task
    result = await target_agent.run(
        task_description,
        deps=delegation_deps,
        usage=ctx.usage  # Track usage across delegation
    )
    
    # Log delegation
    ctx.deps.logger.log_agent_activity(
        agent_name=ctx.deps.agent_id,
        activity="task_delegated",
        data={
            "to_role": target_role.value,
            "task_preview": task_description[:100],
            "delegation_successful": True
        }
    )
    
    return {
        "delegated_to": target_role.value,
        "result": result.data,
        "usage": result.usage_to_dict() if hasattr(result, 'usage_to_dict') else None
    }


async def request_approval(
    ctx: RunContext[GovernanceAgentDeps],
    approval_type: str,
    proposal: Dict[str, Any],
    urgency: str = "normal"
) -> Dict[str, Any]:
    """
    Request approval from the oversight agent.
    
    Args:
        ctx: Current agent context
        approval_type: Type of approval needed
        proposal: The proposal requiring approval
        urgency: Urgency level (low, normal, high, critical)
    
    Returns:
        Approval decision and feedback
    """
    # Only non-overwatch agents can request approval
    if ctx.deps.role == GovernanceRole.OVERWATCH:
        return {
            "approved": True,
            "feedback": "Overwatch agent has inherent approval authority"
        }
    
    # Delegate to overwatch for approval
    result = await delegate_to_agent(
        ctx=ctx,
        target_role=GovernanceRole.OVERWATCH,
        task_description=f"Review and approve {approval_type}: {proposal.get('summary', 'No summary provided')}",
        context_data={
            "approval_type": approval_type,
            "proposal": proposal,
            "urgency": urgency,
            "requesting_agent": ctx.deps.role.value
        }
    )
    
    return result


# Example usage patterns

async def example_governance_usage():
    """Example of using governance agents for different organization types."""
    
    from triad.core.organization_config import (
        create_organization_from_template,
        OrganizationType,
        set_organization_config
    )
    
    # Example 1: Corporate governance
    corporate_config = create_organization_from_template(
        OrganizationType.CORPORATION,
        organization_name="TechCorp Inc.",
        custom_terminology={
            "proposal": "Business Proposal",
            "rule": "Corporate Policy",
            "session": "Board Meeting"
        }
    )
    set_organization_config(corporate_config)
    
    factory = GovernanceAgentFactory()
    
    # Create corporate planning agent (Board of Directors)
    planner = await factory.create_governance_agent(
        role=GovernanceRole.PLANNER,
        custom_system_prompt="Focus on shareholder value and sustainable growth"
    )
    
    # Create corporate execution agent (CEO/Executive Team)
    executor = await factory.create_governance_agent(
        role=GovernanceRole.EXECUTOR,
        custom_system_prompt="Implement board decisions efficiently"
    )
    
    # Example 2: Personal decision-making
    personal_config = create_organization_from_template(
        OrganizationType.PERSONAL,
        organization_name="Personal Life Management"
    )
    set_organization_config(personal_config)
    
    # Create personal agents
    personal_planner = await factory.create_governance_agent(
        role=GovernanceRole.PLANNER,
        custom_system_prompt="Help me set and plan personal goals"
    )
    
    personal_executor = await factory.create_governance_agent(
        role=GovernanceRole.EXECUTOR,
        custom_system_prompt="Help me take action on my plans"
    )
    
    print("Governance agents created for different organization types")
    
    return {
        "corporate": {"planner": planner, "executor": executor},
        "personal": {"planner": personal_planner, "executor": personal_executor}
    }


# Global factory instance
governance_agent_factory = GovernanceAgentFactory()


def get_governance_agent_factory() -> GovernanceAgentFactory:
    """Get the global governance agent factory."""
    return governance_agent_factory


if __name__ == "__main__":
    asyncio.run(example_governance_usage())