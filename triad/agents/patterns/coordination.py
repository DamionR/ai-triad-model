"""
Multi-Agent Coordination Patterns

Implements Pydantic AI multi-agent coordination patterns including
programmatic hand-off, message passing, and usage tracking across
multiple governance agents.
"""

import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
from enum import Enum
import logfire
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelMessage, UserPromptPart, SystemPromptPart

from triad.models.model_config import GovernanceRole
from .delegation import GovernanceDelegationAgent, MessageContext, DelegationResult
from triad.tools.governance.base import GovernanceContext, AuthorityLevel
from triad.core.logging import get_logfire_config


class CoordinationPattern(Enum):
    """Patterns for multi-agent coordination."""
    DELEGATION = "delegation"                # One agent delegates to another
    SEQUENTIAL = "sequential"               # Agents work in sequence
    COLLABORATIVE = "collaborative"         # Agents work simultaneously
    HIERARCHICAL = "hierarchical"          # Strict authority hierarchy
    CONSENSUS = "consensus"                 # Agents must reach consensus
    OVERSIGHT = "oversight"                 # Primary agents + oversight review


class CoordinationResult(BaseModel):
    """Result of multi-agent coordination."""
    coordination_id: str
    coordination_pattern: CoordinationPattern
    participating_agents: List[str]
    task_description: str
    agent_results: Dict[str, Any] = Field(default_factory=dict)
    final_synthesis: str = ""
    governance_compliance: bool = True
    execution_summary: Dict[str, Any] = Field(default_factory=dict)
    total_execution_time: float = 0.0


class MultiAgentCoordinator:
    """
    Coordinator for multi-agent workflows using Pydantic AI patterns.
    
    Implements programmatic hand-off, message passing, and usage tracking
    across multiple governance agents.
    """
    
    def __init__(self):
        self.logger = get_logfire_config()
        self.agents: Dict[str, GovernanceDelegationAgent] = {}
        self.coordination_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def create_delegation_agents(self) -> Dict[GovernanceRole, GovernanceDelegationAgent]:
        """Create all governance agents with delegation support."""
        agents = {}
        
        for role in [GovernanceRole.PLANNER, GovernanceRole.EXECUTOR,
                    GovernanceRole.EVALUATOR, GovernanceRole.OVERWATCH]:
            
            agent = GovernanceDelegationAgent(role)
            agents[role] = agent
            self.agents[agent.agent_id] = agent
        
        self.logger.log_governance_event(
            event_type="delegation_agents_created",
            data={
                "agent_count": len(agents),
                "roles": [role.value for role in agents.keys()]
            },
            authority="system"
        )
        
        return agents
    
    async def execute_programmatic_handoff(
        self,
        task: str,
        agent_sequence: List[GovernanceRole],
        coordination_type: CoordinationPattern = CoordinationPattern.SEQUENTIAL
    ) -> CoordinationResult:
        """
        Execute programmatic agent hand-off following Pydantic AI patterns.
        
        This implements proper message passing and context accumulation
        between agents in the sequence.
        """
        coordination_id = f"handoff_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now(timezone.utc)
        
        try:
            # Initialize coordination session
            self.coordination_sessions[coordination_id] = {
                "task": task,
                "agent_sequence": [role.value for role in agent_sequence],
                "coordination_type": coordination_type.value,
                "started_at": start_time,
                "results": {},
                "message_history": []
            }
            
            # Accumulated message history for proper context passing
            accumulated_messages: List[ModelMessage] = [
                SystemPromptPart(content=f"Multi-agent coordination task: {task}"),
                UserPromptPart(content=task)
            ]
            
            coordination_result = CoordinationResult(
                coordination_id=coordination_id,
                coordination_pattern=coordination_type,
                participating_agents=[f"{role.value}_agent" for role in agent_sequence],
                task_description=task
            )
            
            # Execute based on coordination pattern
            if coordination_type == CoordinationPattern.SEQUENTIAL:
                await self._execute_sequential_coordination(
                    agent_sequence, task, accumulated_messages, coordination_result
                )
            elif coordination_type == CoordinationPattern.COLLABORATIVE:
                await self._execute_collaborative_coordination(
                    agent_sequence, task, accumulated_messages, coordination_result
                )
            elif coordination_type == CoordinationPattern.OVERSIGHT:
                await self._execute_oversight_coordination(
                    agent_sequence, task, accumulated_messages, coordination_result
                )
            elif coordination_type == CoordinationPattern.CONSENSUS:
                await self._execute_consensus_coordination(
                    agent_sequence, task, accumulated_messages, coordination_result
                )
            
            # Calculate total execution time
            end_time = datetime.now(timezone.utc)
            coordination_result.total_execution_time = (end_time - start_time).total_seconds()
            
            # Generate final synthesis
            coordination_result.final_synthesis = self._generate_synthesis(coordination_result)
            
            # Log coordination completion
            self.logger.log_governance_event(
                event_type="coordination_completed",
                data={
                    "coordination_id": coordination_id,
                    "pattern": coordination_type.value,
                    "agents_count": len(agent_sequence),
                    "execution_time": coordination_result.total_execution_time
                },
                authority="system"
            )
            
            return coordination_result
            
        except Exception as e:
            self.logger.log_governance_event(
                event_type="coordination_error",
                data={
                    "coordination_id": coordination_id,
                    "error": str(e),
                    "pattern": coordination_type.value
                },
                authority="system"
            )
            raise
    
    async def _execute_sequential_coordination(
        self,
        agent_sequence: List[GovernanceRole],
        task: str,
        accumulated_messages: List[ModelMessage],
        coordination_result: CoordinationResult
    ):
        """Execute sequential coordination pattern."""
        
        for i, role in enumerate(agent_sequence):
            agent = await self._get_agent_by_role(role)
            
            # Create context-aware prompt for this agent
            context_prompt = self._create_contextual_prompt(
                task, role, i, len(agent_sequence), accumulated_messages
            )
            
            # Execute with accumulated message history
            result = await agent.agent.run(
                context_prompt,
                deps=agent.deps
            )
            
            # Add result to message history for next agent
            accumulated_messages.append(
                SystemPromptPart(
                    content=f"Agent {role.value} response: {result.data}"
                )
            )
            
            coordination_result.agent_results[role.value] = {
                "result": result.data,
                "execution_order": i + 1,
                "authority_level": agent.governance_context.authority_level.value
            }
    
    async def _execute_collaborative_coordination(
        self,
        agent_sequence: List[GovernanceRole],
        task: str,
        accumulated_messages: List[ModelMessage],
        coordination_result: CoordinationResult
    ):
        """Execute collaborative coordination pattern."""
        
        collaboration_tasks = []
        
        for role in agent_sequence:
            agent = await self._get_agent_by_role(role)
            
            collaborative_prompt = f"""
            COLLABORATIVE GOVERNANCE TASK
            
            Primary Task: {task}
            Your Role: {role.value} ({agent.governance_context.authority_level.value} authority)
            Collaboration Partners: {[r.value for r in agent_sequence if r != role]}
            
            Provide your authority level's perspective on this task.
            Consider how your analysis complements other organizational levels.
            """
            
            # Execute collaboratively (simultaneously)
            collaboration_tasks.append(
                agent.agent.run(
                    collaborative_prompt,
                    deps=agent.deps
                )
            )
        
        # Wait for all collaborative results
        collaborative_results = await asyncio.gather(*collaboration_tasks, return_exceptions=True)
        
        # Process collaborative results
        for i, (role, result) in enumerate(zip(agent_sequence, collaborative_results)):
            if isinstance(result, Exception):
                coordination_result.agent_results[role.value] = {
                    "result": f"Error: {result}",
                    "execution_order": i + 1,
                    "error": True
                }
            else:
                coordination_result.agent_results[role.value] = {
                    "result": result.data,
                    "execution_order": i + 1,
                    "authority_level": role.value
                }
    
    async def _execute_oversight_coordination(
        self,
        agent_sequence: List[GovernanceRole],
        task: str,
        accumulated_messages: List[ModelMessage],
        coordination_result: CoordinationResult
    ):
        """Execute oversight coordination pattern."""
        
        # Primary agents work, then oversight review
        primary_agents = [role for role in agent_sequence 
                         if role != GovernanceRole.OVERWATCH]
        oversight_agents = [role for role in agent_sequence 
                          if role == GovernanceRole.OVERWATCH]
        
        # Primary agent execution
        primary_tasks = []
        for role in primary_agents:
            agent = await self._get_agent_by_role(role)
            
            primary_prompt = f"""
            PRIMARY ANALYSIS TASK (Subject to Governance Oversight)
            
            Task: {task}
            Your Authority: {agent.governance_context.authority_level.value}
            
            Provide thorough analysis knowing this will be subject to governance review.
            Include your reasoning and governance considerations.
            """
            
            primary_tasks.append(
                agent.agent.run(
                    primary_prompt,
                    deps=agent.deps
                )
            )
        
        # Execute primary tasks
        primary_results = await asyncio.gather(*primary_tasks, return_exceptions=True)
        
        # Record primary results
        for i, (role, result) in enumerate(zip(primary_agents, primary_results)):
            if not isinstance(result, Exception):
                coordination_result.agent_results[role.value] = {
                    "result": result.data,
                    "execution_order": i + 1,
                    "phase": "primary"
                }
        
        # Oversight review phase
        if oversight_agents:
            oversight_agent = await self._get_agent_by_role(oversight_agents[0])
            
            # Prepare oversight summary
            primary_summary = "\n".join([
                f"{role.value}: {coordination_result.agent_results[role.value]['result']}"
                for role in primary_agents
                if role.value in coordination_result.agent_results
            ])
            
            oversight_prompt = f"""
            GOVERNANCE OVERSIGHT REVIEW
            
            Original Task: {task}
            
            Primary Agent Results:
            {primary_summary}
            
            As the oversight authority, review these results for:
            1. Governance compliance
            2. Policy consistency
            3. Risk assessment
            4. Final recommendations
            
            Provide oversight findings and any required corrections.
            """
            
            oversight_result = await oversight_agent.agent.run(
                oversight_prompt,
                deps=oversight_agent.deps
            )
            
            coordination_result.agent_results[GovernanceRole.OVERWATCH.value] = {
                "result": oversight_result.data,
                "execution_order": len(primary_agents) + 1,
                "phase": "oversight"
            }
    
    async def _execute_consensus_coordination(
        self,
        agent_sequence: List[GovernanceRole],
        task: str,
        accumulated_messages: List[ModelMessage],
        coordination_result: CoordinationResult
    ):
        """Execute consensus coordination pattern."""
        
        # First round: Initial responses
        initial_tasks = []
        for role in agent_sequence:
            agent = await self._get_agent_by_role(role)
            
            initial_prompt = f"""
            CONSENSUS BUILDING TASK - INITIAL RESPONSE
            
            Task: {task}
            Your Role: {role.value}
            
            Provide your initial perspective on this task.
            This is the first round of a consensus-building process.
            """
            
            initial_tasks.append(
                agent.agent.run(
                    initial_prompt,
                    deps=agent.deps
                )
            )
        
        # Get initial responses
        initial_results = await asyncio.gather(*initial_tasks, return_exceptions=True)
        
        # Process initial responses
        initial_summary = []
        for role, result in zip(agent_sequence, initial_results):
            if not isinstance(result, Exception):
                initial_summary.append(f"{role.value}: {result.data}")
                coordination_result.agent_results[f"{role.value}_initial"] = {
                    "result": result.data,
                    "phase": "initial"
                }
        
        # Second round: Consensus building
        consensus_tasks = []
        summary_text = "\n".join(initial_summary)
        
        for role in agent_sequence:
            agent = await self._get_agent_by_role(role)
            
            consensus_prompt = f"""
            CONSENSUS BUILDING TASK - CONSENSUS ROUND
            
            Original Task: {task}
            Your Role: {role.value}
            
            Initial Responses from All Agents:
            {summary_text}
            
            Review all perspectives and provide a consensus-oriented response.
            Focus on areas of agreement and propose solutions for disagreements.
            """
            
            consensus_tasks.append(
                agent.agent.run(
                    consensus_prompt,
                    deps=agent.deps
                )
            )
        
        # Get consensus responses
        consensus_results = await asyncio.gather(*consensus_tasks, return_exceptions=True)
        
        # Process consensus results
        for role, result in zip(agent_sequence, consensus_results):
            if not isinstance(result, Exception):
                coordination_result.agent_results[f"{role.value}_consensus"] = {
                    "result": result.data,
                    "phase": "consensus"
                }
    
    async def _get_agent_by_role(self, role: GovernanceRole) -> GovernanceDelegationAgent:
        """Get agent by governance role."""
        for agent in self.agents.values():
            if agent.role == role:
                return agent
        
        # Create agent if it doesn't exist
        agent = GovernanceDelegationAgent(role)
        self.agents[agent.agent_id] = agent
        return agent
    
    def _create_contextual_prompt(
        self,
        task: str,
        role: GovernanceRole,
        position: int,
        total_agents: int,
        message_history: List[ModelMessage]
    ) -> str:
        """Create context-aware prompt for sequential execution."""
        
        context = f"""
        SEQUENTIAL COORDINATION TASK
        
        Primary Task: {task}
        Your Role: {role.value} (Position {position + 1} of {total_agents})
        
        Previous Agent Results:
        """
        
        # Add previous results from message history
        for i, msg in enumerate(message_history[2:]):  # Skip system and user messages
            if hasattr(msg, 'content'):
                context += f"\n{i + 1}. {msg.content[:200]}..."
        
        context += f"""
        
        Instructions:
        - Build upon previous agent work where appropriate
        - Provide your unique {role.value} perspective
        - Consider governance implications
        - If you're the final agent, provide synthesis and recommendations
        """
        
        return context.strip()
    
    def _generate_synthesis(self, coordination_result: CoordinationResult) -> str:
        """Generate final synthesis of coordination results."""
        
        agent_count = len([k for k in coordination_result.agent_results.keys() 
                          if not k.endswith('_initial')])
        
        synthesis = f"""
        MULTI-AGENT COORDINATION SYNTHESIS
        
        Task: {coordination_result.task_description}
        Pattern: {coordination_result.coordination_pattern.value}
        Participating Agents: {agent_count}
        
        Key Findings:
        """
        
        # Extract key points from each agent
        for agent_name, result in coordination_result.agent_results.items():
            if not agent_name.endswith('_initial') and not result.get('error'):
                result_text = result['result'][:150] + "..." if len(result['result']) > 150 else result['result']
                synthesis += f"\n- {agent_name}: {result_text}"
        
        synthesis += f"""
        
        Governance Compliance: {'✓' if coordination_result.governance_compliance else '✗'}
        Total Execution Time: {coordination_result.total_execution_time:.2f} seconds
        """
        
        return synthesis.strip()