"""
Organization Configuration for Triad Model

Allows customization of the Westminster governance model for any organization type:
- Government (Parliament, Congress, etc.)
- Corporation (Board, Executive, Departments)
- Non-profit (Board, Directors, Committees)
- Personal (Individual decision-making framework)
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field
from dataclasses import dataclass


class OrganizationType(Enum):
    """Types of organizations that can use the Triad Model."""
    GOVERNMENT = "government"
    CORPORATION = "corporation"
    NON_PROFIT = "non_profit"
    EDUCATIONAL = "educational"
    PERSONAL = "personal"
    CUSTOM = "custom"


class AuthorityRole(Enum):
    """Generic authority roles based on Westminster model."""
    LEGISLATIVE = "legislative"      # Rule-making authority
    EXECUTIVE = "executive"          # Implementation authority
    JUDICIAL = "judicial"           # Evaluation/compliance authority
    OVERSIGHT = "oversight"         # Final oversight authority
    ADMINISTRATIVE = "administrative"  # Day-to-day operations
    ADVISORY = "advisory"           # Advisory role only


class AccessLevel(Enum):
    """Generic access levels for any organization."""
    PUBLIC = "public"               # Publicly accessible
    MEMBER = "member"               # Organization members
    MANAGER = "manager"             # Management level
    DIRECTOR = "director"           # Director/board level
    RESTRICTED = "restricted"       # Highly restricted
    TOP_SECRET = "top_secret"       # Highest level


@dataclass
class OrganizationContext:
    """Context for organization-specific operations."""
    agent_id: str
    authority_role: AuthorityRole
    organization_id: Optional[str] = None
    session_id: Optional[str] = None
    access_level: AccessLevel = AccessLevel.MEMBER
    compliance_required: bool = True
    audit_trail: bool = True


class RoleMapping(BaseModel):
    """Maps organization-specific roles to generic authority roles."""
    organization_role: str
    authority_role: AuthorityRole
    display_name: str
    description: str
    access_level: AccessLevel = AccessLevel.MEMBER


class OrganizationConfig(BaseModel):
    """Configuration for organization-specific terminology and structure."""
    
    # Basic organization info
    organization_type: OrganizationType
    organization_name: str
    organization_id: str
    
    # Terminology mappings
    terminology: Dict[str, str] = Field(default_factory=dict)
    
    # Role mappings
    role_mappings: List[RoleMapping] = Field(default_factory=list)
    
    # Custom settings
    enable_compliance_checks: bool = True
    enable_audit_trail: bool = True
    enable_crisis_management: bool = True
    custom_settings: Dict[str, Any] = Field(default_factory=dict)


# Pre-configured organization templates
ORGANIZATION_TEMPLATES = {
    OrganizationType.GOVERNMENT: OrganizationConfig(
        organization_type=OrganizationType.GOVERNMENT,
        organization_name="Parliamentary Democracy",
        organization_id="parliament",
        terminology={
            "legislative": "Parliament",
            "executive": "Cabinet",
            "judicial": "Courts",
            "oversight": "Crown/Head of State",
            "member": "Parliamentarian",
            "session": "Parliamentary Session",
            "proposal": "Bill",
            "rule": "Act",
            "meeting": "Sitting"
        },
        role_mappings=[
            RoleMapping(
                organization_role="Prime Minister",
                authority_role=AuthorityRole.EXECUTIVE,
                display_name="Prime Minister",
                description="Head of Government",
                access_level=AccessLevel.TOP_SECRET
            ),
            RoleMapping(
                organization_role="Speaker",
                authority_role=AuthorityRole.LEGISLATIVE,
                display_name="Speaker",
                description="Presiding officer of legislative body",
                access_level=AccessLevel.DIRECTOR
            ),
            RoleMapping(
                organization_role="Chief Justice",
                authority_role=AuthorityRole.JUDICIAL,
                display_name="Chief Justice",
                description="Head of judicial system",
                access_level=AccessLevel.TOP_SECRET
            )
        ]
    ),
    
    OrganizationType.CORPORATION: OrganizationConfig(
        organization_type=OrganizationType.CORPORATION,
        organization_name="Corporate Governance",
        organization_id="corporation",
        terminology={
            "legislative": "Board of Directors",
            "executive": "Executive Team",
            "judicial": "Compliance/Legal",
            "oversight": "Board Chair/Shareholders",
            "member": "Employee",
            "session": "Board Meeting",
            "proposal": "Motion/Proposal",
            "rule": "Policy",
            "meeting": "Meeting"
        },
        role_mappings=[
            RoleMapping(
                organization_role="CEO",
                authority_role=AuthorityRole.EXECUTIVE,
                display_name="Chief Executive Officer",
                description="Head of company operations",
                access_level=AccessLevel.TOP_SECRET
            ),
            RoleMapping(
                organization_role="Board Chair",
                authority_role=AuthorityRole.OVERSIGHT,
                display_name="Board Chairperson",
                description="Head of Board of Directors",
                access_level=AccessLevel.TOP_SECRET
            ),
            RoleMapping(
                organization_role="General Counsel",
                authority_role=AuthorityRole.JUDICIAL,
                display_name="General Counsel",
                description="Chief legal officer",
                access_level=AccessLevel.RESTRICTED
            )
        ]
    ),
    
    OrganizationType.NON_PROFIT: OrganizationConfig(
        organization_type=OrganizationType.NON_PROFIT,
        organization_name="Non-Profit Organization",
        organization_id="nonprofit",
        terminology={
            "legislative": "Board of Trustees",
            "executive": "Executive Director",
            "judicial": "Ethics Committee",
            "oversight": "Board/Donors",
            "member": "Volunteer/Staff",
            "session": "Board Meeting",
            "proposal": "Initiative",
            "rule": "Bylaw",
            "meeting": "Meeting"
        },
        role_mappings=[
            RoleMapping(
                organization_role="Executive Director",
                authority_role=AuthorityRole.EXECUTIVE,
                display_name="Executive Director",
                description="Head of operations",
                access_level=AccessLevel.DIRECTOR
            ),
            RoleMapping(
                organization_role="Board President",
                authority_role=AuthorityRole.LEGISLATIVE,
                display_name="Board President",
                description="Head of Board",
                access_level=AccessLevel.DIRECTOR
            )
        ]
    ),
    
    OrganizationType.PERSONAL: OrganizationConfig(
        organization_type=OrganizationType.PERSONAL,
        organization_name="Personal Decision Framework",
        organization_id="personal",
        terminology={
            "legislative": "Goal Setting",
            "executive": "Action Taking",
            "judicial": "Self-Evaluation",
            "oversight": "Values/Principles",
            "member": "Self",
            "session": "Planning Session",
            "proposal": "Idea",
            "rule": "Personal Rule",
            "meeting": "Reflection"
        },
        role_mappings=[
            RoleMapping(
                organization_role="Planner",
                authority_role=AuthorityRole.LEGISLATIVE,
                display_name="Personal Planner",
                description="Goal and rule setting",
                access_level=AccessLevel.TOP_SECRET
            ),
            RoleMapping(
                organization_role="Doer",
                authority_role=AuthorityRole.EXECUTIVE,
                display_name="Action Taker",
                description="Implementation",
                access_level=AccessLevel.TOP_SECRET
            ),
            RoleMapping(
                organization_role="Evaluator",
                authority_role=AuthorityRole.JUDICIAL,
                display_name="Self-Evaluator",
                description="Progress evaluation",
                access_level=AccessLevel.TOP_SECRET
            )
        ]
    )
}


class OrganizationManager:
    """Manages organization-specific configurations and terminology."""
    
    def __init__(self, config: Optional[OrganizationConfig] = None):
        """Initialize with organization config or default to generic."""
        self.config = config or self._create_generic_config()
        self._terminology_cache = {}
        
    def _create_generic_config(self) -> OrganizationConfig:
        """Create a generic organization config."""
        return OrganizationConfig(
            organization_type=OrganizationType.CUSTOM,
            organization_name="Generic Organization",
            organization_id="generic",
            terminology={
                "legislative": "Policy Making",
                "executive": "Implementation",
                "judicial": "Compliance",
                "oversight": "Oversight",
                "member": "Member",
                "session": "Session",
                "proposal": "Proposal",
                "rule": "Rule",
                "meeting": "Meeting"
            }
        )
    
    def get_term(self, generic_term: str) -> str:
        """Get organization-specific term for a generic concept."""
        return self.config.terminology.get(generic_term, generic_term)
    
    def get_role_display_name(self, authority_role: AuthorityRole) -> str:
        """Get display name for an authority role in this organization."""
        for mapping in self.config.role_mappings:
            if mapping.authority_role == authority_role:
                return mapping.display_name
        
        # Fallback to generic term
        return self.get_term(authority_role.value)
    
    def get_authority_for_org_role(self, org_role: str) -> Optional[AuthorityRole]:
        """Get authority role for an organization-specific role."""
        for mapping in self.config.role_mappings:
            if mapping.organization_role == org_role:
                return mapping.authority_role
        return None
    
    def create_context(
        self,
        agent_id: str,
        authority_role: AuthorityRole,
        session_id: Optional[str] = None
    ) -> OrganizationContext:
        """Create organization context for an agent."""
        # Find appropriate access level
        access_level = AccessLevel.MEMBER
        for mapping in self.config.role_mappings:
            if mapping.authority_role == authority_role:
                access_level = mapping.access_level
                break
        
        return OrganizationContext(
            agent_id=agent_id,
            authority_role=authority_role,
            organization_id=self.config.organization_id,
            session_id=session_id,
            access_level=access_level,
            compliance_required=self.config.enable_compliance_checks,
            audit_trail=self.config.enable_audit_trail
        )
    
    def format_message(self, template: str, **kwargs) -> str:
        """Format a message with organization-specific terminology."""
        # Replace generic terms with organization-specific ones
        formatted = template
        for generic, specific in self.config.terminology.items():
            formatted = formatted.replace(f"{{{generic}}}", specific)
        
        # Format with any additional kwargs
        return formatted.format(**kwargs)


# Global organization manager
_organization_manager: Optional[OrganizationManager] = None


def set_organization_config(config: OrganizationConfig):
    """Set the global organization configuration."""
    global _organization_manager
    _organization_manager = OrganizationManager(config)


def get_organization_manager() -> OrganizationManager:
    """Get the global organization manager."""
    global _organization_manager
    if _organization_manager is None:
        _organization_manager = OrganizationManager()
    return _organization_manager


def create_organization_from_template(
    template_type: OrganizationType,
    organization_name: Optional[str] = None,
    custom_terminology: Optional[Dict[str, str]] = None
) -> OrganizationConfig:
    """Create organization config from a template with customizations."""
    if template_type not in ORGANIZATION_TEMPLATES:
        raise ValueError(f"Unknown template type: {template_type}")
    
    # Start with template
    config = ORGANIZATION_TEMPLATES[template_type].copy()
    
    # Apply customizations
    if organization_name:
        config.organization_name = organization_name
    
    if custom_terminology:
        config.terminology.update(custom_terminology)
    
    return config