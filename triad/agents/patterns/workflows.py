"""
Multi-Agent Workflow Examples

Example workflows and utility functions demonstrating multi-agent
coordination patterns for governance applications.
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import logfire

from triad.models.model_config import GovernanceRole
from .delegation import GovernanceDelegationAgent, DelegationAuthority
from .coordination import MultiAgentCoordinator, CoordinationPattern
from triad.core.logging import get_logfire_config


async def example_delegation_workflow():
    """
    Example workflow demonstrating proper agent delegation patterns.
    
    Shows how to use delegation for specialized organizational tasks.
    """
    logger = get_logfire_config()
    
    # Create a planner agent with delegation capabilities
    planner_agent = GovernanceDelegationAgent(GovernanceRole.PLANNER)
    
    # Example task that requires delegation
    complex_task = """
    Analyze the proposed organizational restructuring plan and provide recommendations.
    This requires input from multiple departments and specialized teams.
    """
    
    try:
        logger.log_governance_event(
            event_type="example_delegation_started",
            data={"task": complex_task[:100]},
            authority="system"
        )
        
        # Run the agent with delegation capability
        result = await planner_agent.agent.run(
            f"""
            Please analyze this organizational task: {complex_task}
            
            You should delegate specialized aspects to appropriate teams and synthesize results.
            Use your delegation tools when you need specialized expertise.
            """,
            deps=planner_agent.deps
        )
        
        workflow_result = {
            "agent_id": planner_agent.agent_id,
            "task": complex_task,
            "result": result.data,
            "delegations_used": len(planner_agent.sub_agents),
            "success": True
        }
        
        logger.log_governance_event(
            event_type="example_delegation_completed",
            data={
                "delegations_count": workflow_result["delegations_used"],
                "success": workflow_result["success"]
            },
            authority="system"
        )
        
        return workflow_result
        
    except Exception as e:
        logger.log_governance_event(
            event_type="example_delegation_error",
            data={"error": str(e)},
            authority="system"
        )
        raise


async def example_programmatic_handoff():
    """
    Example workflow demonstrating programmatic agent hand-off.
    
    Shows sequential coordination between multiple governance agents.
    """
    logger = get_logfire_config()
    
    # Create multi-agent coordinator
    coordinator = MultiAgentCoordinator()
    
    # Define a complex governance task
    governance_task = """
    Evaluate the proposed new data privacy policy for compliance, implementation feasibility,
    and organizational impact. Provide comprehensive recommendations.
    """
    
    # Define agent sequence for comprehensive analysis
    agent_sequence = [
        GovernanceRole.PLANNER,    # Initial analysis and planning
        GovernanceRole.EVALUATOR,  # Compliance and risk evaluation
        GovernanceRole.EXECUTOR,   # Implementation feasibility
        GovernanceRole.OVERWATCH   # Final oversight and synthesis
    ]
    
    try:
        logger.log_governance_event(
            event_type="example_handoff_started",
            data={
                "task": governance_task[:100],
                "agent_sequence": [role.value for role in agent_sequence]
            },
            authority="system"
        )
        
        # Execute programmatic handoff
        handoff_result = await coordinator.execute_programmatic_handoff(
            task=governance_task,
            agent_sequence=agent_sequence,
            coordination_type=CoordinationPattern.SEQUENTIAL
        )
        
        workflow_result = {
            "coordination_id": handoff_result.coordination_id,
            "task": governance_task,
            "coordination_pattern": handoff_result.coordination_pattern.value,
            "participating_agents": handoff_result.participating_agents,
            "agent_results": handoff_result.agent_results,
            "final_synthesis": handoff_result.final_synthesis,
            "execution_time": handoff_result.total_execution_time,
            "success": True
        }
        
        logger.log_governance_event(
            event_type="example_handoff_completed",
            data={
                "coordination_id": handoff_result.coordination_id,
                "execution_time": handoff_result.total_execution_time,
                "agents_count": len(handoff_result.participating_agents)
            },
            authority="system"
        )
        
        return workflow_result
        
    except Exception as e:
        logger.log_governance_event(
            event_type="example_handoff_error",
            data={"error": str(e)},
            authority="system"
        )
        raise


async def example_collaborative_analysis():
    """
    Example workflow demonstrating collaborative agent analysis.
    
    Shows how multiple agents can work simultaneously on the same task.
    """
    logger = get_logfire_config()
    
    coordinator = MultiAgentCoordinator()
    
    # Define a task that benefits from multiple perspectives
    analysis_task = """
    Assess the impact of implementing remote work policies across the organization.
    Consider operational, legal, financial, and strategic implications.
    """
    
    # All agents work collaboratively
    collaborative_agents = [
        GovernanceRole.PLANNER,    # Strategic planning perspective
        GovernanceRole.EVALUATOR,  # Risk and compliance perspective
        GovernanceRole.EXECUTOR,   # Operational implementation perspective
    ]
    
    try:
        logger.log_governance_event(
            event_type="example_collaboration_started",
            data={
                "task": analysis_task[:100],
                "agents": [role.value for role in collaborative_agents]
            },
            authority="system"
        )
        
        # Execute collaborative analysis
        collaboration_result = await coordinator.execute_programmatic_handoff(
            task=analysis_task,
            agent_sequence=collaborative_agents,
            coordination_type=CoordinationPattern.COLLABORATIVE
        )
        
        workflow_result = {
            "coordination_id": collaboration_result.coordination_id,
            "task": analysis_task,
            "collaboration_results": collaboration_result.agent_results,
            "synthesis": collaboration_result.final_synthesis,
            "execution_time": collaboration_result.total_execution_time,
            "success": True
        }
        
        logger.log_governance_event(
            event_type="example_collaboration_completed",
            data={
                "coordination_id": collaboration_result.coordination_id,
                "execution_time": collaboration_result.total_execution_time
            },
            authority="system"
        )
        
        return workflow_result
        
    except Exception as e:
        logger.log_governance_event(
            event_type="example_collaboration_error",
            data={"error": str(e)},
            authority="system"
        )
        raise


async def example_oversight_workflow():
    """
    Example workflow demonstrating oversight coordination pattern.
    
    Shows how primary agents work with oversight review.
    """
    logger = get_logfire_config()
    
    coordinator = MultiAgentCoordinator()
    
    # Define a high-stakes decision requiring oversight
    oversight_task = """
    Approve the proposed budget reallocation that will affect multiple departments.
    This requires thorough analysis and oversight approval.
    """
    
    # Primary agents + oversight
    oversight_sequence = [
        GovernanceRole.PLANNER,    # Budget planning analysis
        GovernanceRole.EXECUTOR,   # Implementation impact assessment
        GovernanceRole.OVERWATCH   # Final oversight and approval
    ]
    
    try:
        logger.log_governance_event(
            event_type="example_oversight_started",
            data={
                "task": oversight_task[:100],
                "oversight_agents": [role.value for role in oversight_sequence]
            },
            authority="system"
        )
        
        # Execute oversight workflow
        oversight_result = await coordinator.execute_programmatic_handoff(
            task=oversight_task,
            agent_sequence=oversight_sequence,
            coordination_type=CoordinationPattern.OVERSIGHT
        )
        
        workflow_result = {
            "coordination_id": oversight_result.coordination_id,
            "task": oversight_task,
            "primary_analysis": {
                k: v for k, v in oversight_result.agent_results.items()
                if v.get("phase") == "primary"
            },
            "oversight_review": {
                k: v for k, v in oversight_result.agent_results.items()
                if v.get("phase") == "oversight"
            },
            "final_decision": oversight_result.final_synthesis,
            "execution_time": oversight_result.total_execution_time,
            "success": True
        }
        
        logger.log_governance_event(
            event_type="example_oversight_completed",
            data={
                "coordination_id": oversight_result.coordination_id,
                "oversight_provided": len(workflow_result["oversight_review"]) > 0
            },
            authority="system"
        )
        
        return workflow_result
        
    except Exception as e:
        logger.log_governance_event(
            event_type="example_oversight_error",
            data={"error": str(e)},
            authority="system"
        )
        raise


async def example_consensus_building():
    """
    Example workflow demonstrating consensus building among agents.
    
    Shows how agents can work through disagreements to reach consensus.
    """
    logger = get_logfire_config()
    
    coordinator = MultiAgentCoordinator()
    
    # Define a task that may have different perspectives
    consensus_task = """
    Decide on the technology stack for the new customer portal project.
    Consider technical requirements, costs, team expertise, and long-term maintainability.
    """
    
    # All governance roles participate in consensus
    consensus_agents = [
        GovernanceRole.PLANNER,    # Strategic technology planning
        GovernanceRole.EXECUTOR,   # Technical implementation
        GovernanceRole.EVALUATOR,  # Risk and compliance assessment
        GovernanceRole.OVERWATCH   # Final governance perspective
    ]
    
    try:
        logger.log_governance_event(
            event_type="example_consensus_started",
            data={
                "task": consensus_task[:100],
                "consensus_agents": [role.value for role in consensus_agents]
            },
            authority="system"
        )
        
        # Execute consensus building
        consensus_result = await coordinator.execute_programmatic_handoff(
            task=consensus_task,
            agent_sequence=consensus_agents,
            coordination_type=CoordinationPattern.CONSENSUS
        )
        
        workflow_result = {
            "coordination_id": consensus_result.coordination_id,
            "task": consensus_task,
            "initial_positions": {
                k: v for k, v in consensus_result.agent_results.items()
                if k.endswith("_initial")
            },
            "consensus_positions": {
                k: v for k, v in consensus_result.agent_results.items()
                if k.endswith("_consensus")
            },
            "final_consensus": consensus_result.final_synthesis,
            "execution_time": consensus_result.total_execution_time,
            "success": True
        }
        
        logger.log_governance_event(
            event_type="example_consensus_completed",
            data={
                "coordination_id": consensus_result.coordination_id,
                "consensus_achieved": True
            },
            authority="system"
        )
        
        return workflow_result
        
    except Exception as e:
        logger.log_governance_event(
            event_type="example_consensus_error",
            data={"error": str(e)},
            authority="system"
        )
        raise


def get_multi_agent_coordinator() -> MultiAgentCoordinator:
    """Get a configured multi-agent coordinator instance."""
    return MultiAgentCoordinator()


async def run_all_examples():
    """
    Run all example workflows to demonstrate multi-agent patterns.
    
    This is useful for testing and demonstration purposes.
    """
    logger = get_logfire_config()
    
    examples = [
        ("Delegation Workflow", example_delegation_workflow),
        ("Programmatic Handoff", example_programmatic_handoff),
        ("Collaborative Analysis", example_collaborative_analysis),
        ("Oversight Workflow", example_oversight_workflow),
        ("Consensus Building", example_consensus_building)
    ]
    
    results = {}
    
    for example_name, example_func in examples:
        try:
            logger.log_governance_event(
                event_type="example_workflow_starting",
                data={"example": example_name},
                authority="system"
            )
            
            start_time = datetime.now(timezone.utc)
            result = await example_func()
            end_time = datetime.now(timezone.utc)
            
            results[example_name] = {
                "result": result,
                "execution_time": (end_time - start_time).total_seconds(),
                "success": True
            }
            
            logger.log_governance_event(
                event_type="example_workflow_completed",
                data={
                    "example": example_name,
                    "execution_time": results[example_name]["execution_time"]
                },
                authority="system"
            )
            
        except Exception as e:
            results[example_name] = {
                "result": None,
                "error": str(e),
                "success": False
            }
            
            logger.log_governance_event(
                event_type="example_workflow_failed",
                data={
                    "example": example_name,
                    "error": str(e)
                },
                authority="system"
            )
    
    return results