"""
Model Context Protocol (MCP) Integration

Core MCP functionality for connecting to external systems.
Parliamentary oversight and constitutional compliance handled
by the tools module.
"""

from .client import MCPClient
from .adapters import SystemAdapter, LegacyDatabaseAdapter, APIAdapter
from .servers import ValidationServer, MonitoringServer, IntegrationServer
from .tools import MCPTools, register_mcp_tools

__all__ = [
    # Core MCP functionality
    "MCPClient",
    "MCPTools",
    "register_mcp_tools",
    
    # MCP adapters
    "SystemAdapter",
    "LegacyDatabaseAdapter", 
    "APIAdapter",
    
    # MCP servers
    "ValidationServer",
    "MonitoringServer",
    "IntegrationServer",
]