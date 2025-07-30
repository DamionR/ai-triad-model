"""
Configuration Management

Core configuration classes and organization-specific settings
for the Triad governance model.
"""

from .config import (
    Environment,
    ConstitutionalAuthority,
    AppConfig,
    ServerConfig,
    DatabaseConfig,
    SecurityConfig,
    TriadConfig,
    load_config,
    get_config
)

from .organization_config import (
    OrganizationType,
    AuthorityRole,
    AccessLevel,
    OrganizationContext,
    RoleMapping,
    OrganizationConfig,
    OrganizationManager,
    set_organization_config,
    get_organization_manager,
    create_organization_from_template
)

__all__ = [
    # Core configuration
    "Environment",
    "ConstitutionalAuthority", 
    "AppConfig",
    "ServerConfig",
    "DatabaseConfig",
    "SecurityConfig",
    "TriadConfig",
    "load_config",
    "get_config",
    
    # Organization configuration
    "OrganizationType",
    "AuthorityRole",
    "AccessLevel",
    "OrganizationContext",
    "RoleMapping",
    "OrganizationConfig",
    "OrganizationManager",
    "set_organization_config",
    "get_organization_manager",
    "create_organization_from_template"
]