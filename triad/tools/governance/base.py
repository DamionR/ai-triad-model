"""
Base Governance Tools

Core classes and enums for governance toolsets.
"""

from typing import Optional
from enum import Enum
from dataclasses import dataclass


class AuthorityLevel(Enum):
    """Authority levels in the governance system."""
    POLICY_MAKER = "policy_maker"      # Creates rules and policies
    EXECUTOR = "executor"              # Implements decisions
    REVIEWER = "reviewer"              # Reviews and ensures compliance
    OVERSEER = "overseer"              # Final oversight authority
    COORDINATOR = "coordinator"        # Coordinates processes
    ADMINISTRATOR = "administrator"    # Administrative functions


class SecurityLevel(Enum):
    """Security access levels for governance tools."""
    PUBLIC = "public"           # Public access
    INTERNAL = "internal"       # Internal organization access
    MANAGEMENT = "management"   # Management level access
    EXECUTIVE = "executive"     # Executive level access
    TOP_LEVEL = "top_level"     # Highest level access


@dataclass
class GovernanceContext:
    """Context for governance tool operations."""
    agent_id: str
    authority_level: AuthorityLevel
    session_id: Optional[str] = None
    governance_session_id: Optional[str] = None
    security_clearance: SecurityLevel = SecurityLevel.INTERNAL
    compliance_oversight: bool = True