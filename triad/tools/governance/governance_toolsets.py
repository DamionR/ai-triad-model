"""
Governance Toolsets for Triad Model System

Aggregates and provides access to all governance toolsets with
MCP integration and organizational procedures.
"""

# Import all toolset components
from .base import AuthorityLevel, SecurityLevel, GovernanceContext
from .compliance import ComplianceToolset
from .policy import PolicyToolset
from .process import ProcessToolset
from .compliance_advanced import ComplianceToolset as AdvancedComplianceToolset
from .legislative import LegislativeToolset
from .procedures import OrganizationalProcedureToolset

# Re-export for backward compatibility
__all__ = [
    # Base classes
    "AuthorityLevel",
    "SecurityLevel", 
    "GovernanceContext",
    
    # Toolsets
    "ComplianceToolset",
    "PolicyToolset",
    "ProcessToolset", 
    "AdvancedComplianceToolset",
    "LegislativeToolset",
    "OrganizationalProcedureToolset"
]

# Convenience function to get all toolsets
def get_all_governance_toolsets():
    """Get all available governance toolsets."""
    return {
        "compliance": ComplianceToolset(),
        "policy": PolicyToolset(),
        "process": ProcessToolset(),
        "compliance_advanced": AdvancedComplianceToolset(),
        "legislative": LegislativeToolset(),
        "procedures": OrganizationalProcedureToolset()
    }

# Convenience function to get toolsets by authority level
def get_toolsets_by_authority(authority_level: AuthorityLevel):
    """Get toolsets appropriate for the given authority level."""
    toolsets = {}
    
    if authority_level in [AuthorityLevel.OVERSEER]:
        # Overseers get access to all toolsets
        toolsets = get_all_governance_toolsets()
    elif authority_level == AuthorityLevel.POLICY_MAKER:
        toolsets = {
            "policy": PolicyToolset(),
            "legislative": LegislativeToolset(),
            "compliance_advanced": AdvancedComplianceToolset()
        }
    elif authority_level == AuthorityLevel.EXECUTOR:
        toolsets = {
            "process": ProcessToolset(),
            "procedures": OrganizationalProcedureToolset(),
            "compliance": ComplianceToolset()
        }
    elif authority_level == AuthorityLevel.REVIEWER:
        toolsets = {
            "compliance": ComplianceToolset(),
            "compliance_advanced": AdvancedComplianceToolset(),
            "policy": PolicyToolset()
        }
    elif authority_level == AuthorityLevel.COORDINATOR:
        toolsets = {
            "procedures": OrganizationalProcedureToolset(),
            "process": ProcessToolset(),
            "legislative": LegislativeToolset()
        }
    elif authority_level == AuthorityLevel.ADMINISTRATOR:
        toolsets = {
            "procedures": OrganizationalProcedureToolset(),
            "compliance": ComplianceToolset()
        }
    
    return toolsets