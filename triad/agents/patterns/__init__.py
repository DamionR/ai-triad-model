"""
Agent Patterns

Multi-agent coordination patterns and communication strategies.
"""

from .multi_agent_patterns import (
    DelegationAuthority,
    MessageContext,
    DelegationResult,
    GovernanceDelegationAgent,
    CoordinationPattern,
    CoordinationResult,
    MultiAgentCoordinator,
    example_delegation_workflow,
    example_programmatic_handoff,
    example_collaborative_analysis,
    example_oversight_workflow,
    example_consensus_building,
    get_multi_agent_coordinator,
    run_all_examples,
    create_multi_agent_system,
    create_delegation_agent
)

from .delegation import DelegationAuthority, MessageContext, DelegationResult, GovernanceDelegationAgent
from .coordination import CoordinationPattern, CoordinationResult, MultiAgentCoordinator  
from .workflows import (
    example_delegation_workflow,
    example_programmatic_handoff,
    example_collaborative_analysis,
    example_oversight_workflow,
    example_consensus_building,
    get_multi_agent_coordinator,
    run_all_examples
)

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
    "run_all_examples",
    
    # Convenience functions
    "create_multi_agent_system",
    "create_delegation_agent"
]