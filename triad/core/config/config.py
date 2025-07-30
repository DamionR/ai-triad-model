"""
Configuration Management for Triad Model

Handles configuration loading and validation with constitutional
compliance and Westminster parliamentary requirements.
"""

from typing import Dict, Any, Optional, List, Union
import os
from pathlib import Path
import yaml
from pydantic import BaseModel, Field, validator
from enum import Enum
import logfire


class Environment(str, Enum):
    """Application environment types."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class ConstitutionalAuthority(str, Enum):
    """Constitutional authorities in Westminster system."""
    LEGISLATIVE = "legislative"
    EXECUTIVE = "executive"
    JUDICIAL = "judicial"
    CROWN = "crown"


class AppConfig(BaseModel):
    """Application configuration."""
    name: str = "Triad Model"
    version: str = "1.0.0"
    description: str = "Westminster Parliamentary AI System with Constitutional Oversight"
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = True


class ServerConfig(BaseModel):
    """Server configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    workers: int = 1
    timeout: int = 300


class ConstitutionalConfig(BaseModel):
    """Constitutional framework configuration."""
    framework_version: str = "Westminster_Parliamentary_v1.0"
    oversight_enabled: bool = True
    parliamentary_accountability: bool = True
    separation_of_powers: bool = True
    rule_of_law: bool = True
    democratic_principles: bool = True
    strict_compliance: bool = False
    audit_requirements: str = "standard"
    
    authorities: Dict[str, Dict[str, Any]] = Field(default_factory=lambda: {
        "legislative": {
            "name": "Legislative Branch",
            "agent": "planner_agent",
            "powers": ["policy_creation", "planning", "legislative_review"]
        },
        "executive": {
            "name": "Executive Branch",
            "agent": "executor_agent", 
            "powers": ["implementation", "execution", "administrative_action"]
        },
        "judicial": {
            "name": "Judicial Branch",
            "agent": "evaluator_agent",
            "powers": ["constitutional_review", "compliance_evaluation", "judicial_decision"]
        },
        "crown": {
            "name": "Crown",
            "agent": "overwatch_agent",
            "powers": ["constitutional_oversight", "crisis_management", "royal_prerogative"]
        }
    })


class AgentConfig(BaseModel):
    """Individual agent configuration."""
    name: str
    constitutional_authority: ConstitutionalAuthority
    model: str = "claude-3-5-sonnet-20241022"
    max_retries: int = 3
    timeout_seconds: int = 120


class AgentsConfig(BaseModel):
    """All agents configuration."""
    planner_agent: AgentConfig = Field(default_factory=lambda: AgentConfig(
        name="Planner Agent",
        constitutional_authority=ConstitutionalAuthority.LEGISLATIVE,
        timeout_seconds=120
    ))
    executor_agent: AgentConfig = Field(default_factory=lambda: AgentConfig(
        name="Executor Agent", 
        constitutional_authority=ConstitutionalAuthority.EXECUTIVE,
        timeout_seconds=180
    ))
    evaluator_agent: AgentConfig = Field(default_factory=lambda: AgentConfig(
        name="Evaluator Agent",
        constitutional_authority=ConstitutionalAuthority.JUDICIAL,
        timeout_seconds=90
    ))
    overwatch_agent: AgentConfig = Field(default_factory=lambda: AgentConfig(
        name="Overwatch Agent",
        constitutional_authority=ConstitutionalAuthority.CROWN,
        timeout_seconds=60
    ))


class ParliamentaryConfig(BaseModel):
    """Parliamentary procedures configuration."""
    question_period: Dict[str, Any] = Field(default_factory=lambda: {
        "enabled": True,
        "default_duration_minutes": 30,
        "parliamentary_privilege": True
    })
    motions: Dict[str, Any] = Field(default_factory=lambda: {
        "enabled": True,
        "require_vote": True,
        "constitutional_review": True
    })
    voting: Dict[str, Any] = Field(default_factory=lambda: {
        "enabled": True,
        "quorum_required": 3,
        "majority_threshold": 0.5
    })
    sessions: Dict[str, Any] = Field(default_factory=lambda: {
        "max_duration_hours": 8,
        "agenda_required": True,
        "transparency": True
    })


class A2AConfig(BaseModel):
    """Agent-to-Agent communication configuration."""
    broker: Dict[str, Any] = Field(default_factory=lambda: {
        "enabled": True,
        "constitutional_oversight": True,
        "audit_trail": True
    })
    message_queue: Dict[str, Any] = Field(default_factory=lambda: {
        "max_size": 1000,
        "timeout_seconds": 30,
        "retry_attempts": 3
    })
    routing: Dict[str, Any] = Field(default_factory=lambda: {
        "load_balancing": "round_robin",
        "failover_enabled": True,
        "circuit_breaker": True
    })


class MCPConfig(BaseModel):
    """Model Context Protocol configuration."""
    client: Dict[str, Any] = Field(default_factory=lambda: {
        "enabled": True,
        "timeout_seconds": 30,
        "constitutional_oversight": True
    })
    servers: Dict[str, Dict[str, Any]] = Field(default_factory=lambda: {
        "validation_server": {
            "enabled": True,
            "url": "http://localhost:8001",
            "constitutional_validation": True
        },
        "monitoring_server": {
            "enabled": True,
            "url": "http://localhost:8002", 
            "health_checks": True
        },
        "integration_server": {
            "enabled": True,
            "url": "http://localhost:8003",
            "external_systems": True
        }
    })
    adapters: Dict[str, Dict[str, Any]] = Field(default_factory=lambda: {
        "legacy_database": {
            "enabled": False,
            "read_only": True,
            "backup_enabled": True
        },
        "external_api": {
            "enabled": False,
            "rate_limit": 100,
            "timeout_seconds": 30
        },
        "file_system": {
            "enabled": False,
            "base_path": "/tmp/triad",
            "read_only": True
        }
    })


class DatabaseConfig(BaseModel):
    """Database configuration."""
    postgresql: Dict[str, Any] = Field(default_factory=lambda: {
        "enabled": False,
        "host": "localhost",
        "port": 5432,
        "database": "triad_model",
        "username": "triad_user",
        "password": None,
        "max_connections": 20
    })
    sqlite: Dict[str, Any] = Field(default_factory=lambda: {
        "enabled": True,
        "path": "data/triad_model.db",
        "constitutional_audit": True
    })


class LoggingConfig(BaseModel):
    """Logging and observability configuration."""
    level: str = "INFO"
    format: str = "json"
    
    logfire: Dict[str, Any] = Field(default_factory=lambda: {
        "enabled": True,
        "service_name": "triad-model",
        "service_version": "1.0.0",
        "constitutional_logging": True,
        "parliamentary_audit": True
    })
    
    audit_trail: Dict[str, Any] = Field(default_factory=lambda: {
        "enabled": True,
        "retention_days": 90,
        "constitutional_compliance": True
    })


class SecurityConfig(BaseModel):
    """Security configuration."""
    api: Dict[str, Any] = Field(default_factory=lambda: {
        "cors_enabled": True,
        "trusted_hosts": ["*"],
        "rate_limiting": False
    })
    
    constitutional: Dict[str, Any] = Field(default_factory=lambda: {
        "separation_enforcement": True,
        "authority_validation": True,
        "audit_trail_protection": True
    })
    
    authentication: Dict[str, Any] = Field(default_factory=lambda: {
        "enabled": False,
        "provider": "oauth2",
        "constitutional_roles": True
    })


class MonitoringConfig(BaseModel):
    """Monitoring and health checks configuration."""
    health_checks: Dict[str, Any] = Field(default_factory=lambda: {
        "enabled": True,
        "interval_seconds": 30,
        "constitutional_compliance": True
    })
    
    metrics: Dict[str, Any] = Field(default_factory=lambda: {
        "enabled": True,
        "export_interval_seconds": 60,
        "parliamentary_metrics": True
    })
    
    alerts: Dict[str, Any] = Field(default_factory=lambda: {
        "enabled": True,
        "constitutional_violations": True,
        "performance_thresholds": {
            "response_time_ms": 1000,
            "error_rate_percent": 5.0,
            "cpu_usage_percent": 80.0
        }
    })


class TriadConfig(BaseModel):
    """Main Triad Model configuration."""
    app: AppConfig = Field(default_factory=AppConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    constitutional: ConstitutionalConfig = Field(default_factory=ConstitutionalConfig)
    agents: AgentsConfig = Field(default_factory=AgentsConfig)
    parliamentary: ParliamentaryConfig = Field(default_factory=ParliamentaryConfig)
    a2a: A2AConfig = Field(default_factory=A2AConfig)
    mcp: MCPConfig = Field(default_factory=MCPConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    
    # Development and production overrides
    development: Dict[str, Any] = Field(default_factory=lambda: {
        "debug_mode": True,
        "auto_reload": True,
        "mock_external_services": True,
        "constitutional_testing": True
    })
    
    production: Dict[str, Any] = Field(default_factory=lambda: {
        "debug_mode": False,
        "auto_reload": False,
        "mock_external_services": False,
        "security_hardened": True
    })
    
    @validator('constitutional')
    def validate_constitutional_framework(cls, v):
        """Validate constitutional framework requirements."""
        if not v.oversight_enabled:
            raise ValueError("Constitutional oversight cannot be disabled")
        if not v.parliamentary_accountability:
            raise ValueError("Parliamentary accountability is required")
        if not v.separation_of_powers:
            raise ValueError("Separation of powers must be maintained")
        return v
    
    @validator('agents')
    def validate_agent_authorities(cls, v):
        """Validate agent constitutional authorities are unique."""
        authorities = [agent.constitutional_authority for agent in [
            v.planner_agent, v.executor_agent, v.evaluator_agent, v.overwatch_agent
        ]]
        if len(set(authorities)) != len(authorities):
            raise ValueError("Each agent must have unique constitutional authority")
        return v


class ConfigManager:
    """
    Configuration manager for Triad Model.
    
    Handles loading, validation, and management of configuration
    with constitutional compliance requirements.
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir) if config_dir else Path("config")
        self.config: Optional[TriadConfig] = None
        self._environment_overrides: Dict[str, Any] = {}
        
    def load_config(self, environment: Optional[str] = None) -> TriadConfig:
        """
        Load configuration for specified environment.
        
        Loads base configuration and applies environment-specific
        overrides with constitutional validation.
        """
        try:
            # Determine environment
            env = environment or os.getenv("TRIAD_ENV", "development")
            
            # Load base configuration
            base_config = self._load_yaml_config("default.yaml")
            
            # Load environment-specific overrides
            env_config = self._load_yaml_config(f"{env}.yaml")
            
            # Merge configurations
            merged_config = self._merge_configs(base_config, env_config)
            
            # Apply environment variable overrides
            merged_config = self._apply_env_overrides(merged_config)
            
            # Validate and create config object
            self.config = TriadConfig(**merged_config)
            
            logfire.info(
                "Configuration loaded successfully",
                environment=env,
                constitutional_framework=self.config.constitutional.framework_version
            )
            
            return self.config
            
        except Exception as e:
            logfire.error("Failed to load configuration", error=str(e))
            raise ConfigurationError(f"Configuration loading failed: {str(e)}")
    
    def _load_yaml_config(self, filename: str) -> Dict[str, Any]:
        """Load YAML configuration file."""
        config_path = self.config_dir / filename
        
        if not config_path.exists():
            if filename == "default.yaml":
                raise FileNotFoundError(f"Base configuration file not found: {config_path}")
            return {}  # Environment-specific configs are optional
        
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in {filename}: {str(e)}")
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge configuration dictionaries."""
        merged = base.copy()
        
        for key, value in override.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides."""
        # Environment variable patterns:
        # TRIAD_APP_DEBUG=true -> app.debug = true
        # TRIAD_DATABASE_POSTGRESQL_PASSWORD=secret -> database.postgresql.password = secret
        
        for env_var, value in os.environ.items():
            if env_var.startswith("TRIAD_"):
                # Parse environment variable path
                path_parts = env_var[6:].lower().split("_")  # Remove TRIAD_ prefix
                
                # Navigate to config location
                current = config
                for part in path_parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                
                # Set value with type conversion
                key = path_parts[-1]
                current[key] = self._convert_env_value(value)
        
        return config
    
    def _convert_env_value(self, value: str) -> Union[str, int, float, bool, None]:
        """Convert environment variable string to appropriate type."""
        # Boolean conversion
        if value.lower() in ("true", "yes", "1", "on"):
            return True
        elif value.lower() in ("false", "no", "0", "off"):
            return False
        
        # None conversion
        if value.lower() in ("null", "none", ""):
            return None
        
        # Numeric conversion
        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            pass
        
        # String (default)
        return value
    
    def get_agent_config(self, agent_name: str) -> AgentConfig:
        """Get configuration for specific agent."""
        if not self.config:
            raise ConfigurationError("Configuration not loaded")
        
        agent_configs = {
            "planner_agent": self.config.agents.planner_agent,
            "executor_agent": self.config.agents.executor_agent,
            "evaluator_agent": self.config.agents.evaluator_agent,
            "overwatch_agent": self.config.agents.overwatch_agent
        }
        
        if agent_name not in agent_configs:
            raise ConfigurationError(f"Unknown agent: {agent_name}")
        
        return agent_configs[agent_name]
    
    def get_constitutional_authority(self, agent_name: str) -> str:
        """Get constitutional authority for agent."""
        agent_config = self.get_agent_config(agent_name)
        return agent_config.constitutional_authority.value
    
    def validate_constitutional_compliance(self) -> Dict[str, Any]:
        """Validate configuration meets constitutional requirements."""
        if not self.config:
            raise ConfigurationError("Configuration not loaded")
        
        compliance = {
            "constitutional_oversight": self.config.constitutional.oversight_enabled,
            "parliamentary_accountability": self.config.constitutional.parliamentary_accountability,
            "separation_of_powers": self.config.constitutional.separation_of_powers,
            "rule_of_law": self.config.constitutional.rule_of_law,
            "democratic_principles": self.config.constitutional.democratic_principles,
            "audit_trail": self.config.logging.audit_trail["enabled"],
            "agent_authorities_unique": True,  # Validated by Pydantic
            "constitutional_compliant": True
        }
        
        # Check for any compliance failures
        compliance["constitutional_compliant"] = all([
            compliance["constitutional_oversight"],
            compliance["parliamentary_accountability"], 
            compliance["separation_of_powers"],
            compliance["rule_of_law"],
            compliance["democratic_principles"],
            compliance["audit_trail"]
        ])
        
        return compliance


class ConfigurationError(Exception):
    """Configuration-related errors."""
    pass


# Global configuration manager instance
config_manager = ConfigManager()


def get_config() -> TriadConfig:
    """Get current configuration."""
    if not config_manager.config:
        config_manager.load_config()
    return config_manager.config


def load_config(environment: Optional[str] = None) -> TriadConfig:
    """Load configuration for environment."""
    return config_manager.load_config(environment)