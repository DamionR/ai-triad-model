"""
Multi-Agent Patterns for Triad Governance System

Aggregates and provides access to all multi-agent coordination patterns
including delegation, coordination, and workflow examples.
"""

# Import all pattern components
from .delegation import (
    DelegationAuthority,
    MessageContext,
    DelegationResult,
    GovernanceDelegationAgent
)

from .coordination import (
    CoordinationPattern,
    CoordinationResult,
    MultiAgentCoordinator
)

from .workflows import (
    example_delegation_workflow,
    example_programmatic_handoff,
    example_collaborative_analysis,
    example_oversight_workflow,
    example_consensus_building,
    get_multi_agent_coordinator,
    run_all_examples
)

# Re-export for backward compatibility
__all__ = [
    # Delegation patterns
    "DelegationAuthority",
    "MessageContext", 
    "DelegationResult",
    "GovernanceDelegationAgent",
    
    # Coordination patterns
    "CoordinationPattern",
    "CoordinationResult", 
    "MultiAgentCoordinator",
    
    # Workflow examples
    "example_delegation_workflow",
    "example_programmatic_handoff",
    "example_collaborative_analysis",
    "example_oversight_workflow",
    "example_consensus_building",
    "get_multi_agent_coordinator",
    "run_all_examples"
]

# Convenience function to get a configured coordinator
def create_multi_agent_system():
    """Create a fully configured multi-agent coordination system."""
    return MultiAgentCoordinator()

# Convenience function to create a delegation agent
def create_delegation_agent(role, agent_id=None, model_config=None):
    """Create a governance delegation agent."""
    return GovernanceDelegationAgent(role, agent_id, model_config)