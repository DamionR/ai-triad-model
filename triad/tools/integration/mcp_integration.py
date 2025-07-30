"""
Governance MCP Integration for Triad Model System

Provides Model Context Protocol integration with compliance oversight,
security validation, and organizational accountability for AI agents.
This handles the governance-specific MCP functionality.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass
import logfire
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.tools import Tool

from triad.mcp.client import MCPClient
from triad.tools.parliamentary_toolsets import ParliamentaryContext, ParliamentaryAuthority, ToolSecurityLevel
from triad.core.logging import get_logfire_config


class MCPServerType(Enum):
    """Types of MCP servers for parliamentary operations."""
    LEGISLATIVE_DATABASE = "legislative_database"
    CONSTITUTIONAL_LAW = "constitutional_law"
    HANSARD_ARCHIVE = "hansard_archive"
    CITIZEN_ENGAGEMENT = "citizen_engagement"
    POLICY_ANALYSIS = "policy_analysis"
    PARLIAMENTARY_PROCEDURE = "parliamentary_procedure"
    EXTERNAL_API = "external_api"
    GOVERNMENT_DATA = "government_data"


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server."""
    name: str
    server_type: MCPServerType
    connection_params: Dict[str, Any]
    security_level: ToolSecurityLevel
    constitutional_authority_required: Optional[ParliamentaryAuthority] = None
    enabled: bool = True
    description: str = ""
    available_tools: List[str] = None


class ParliamentaryMCPClient:
    """
    MCP client specialized for Westminster Parliamentary AI operations.
    
    Provides constitutional oversight, security validation, and democratic
    accountability for all MCP server interactions.
    """
    
    def __init__(self):
        self.logger = get_logfire_config()
        self.mcp_client = MCPClient()
        self.servers: Dict[str, MCPServerConfig] = {}
        self.active_connections: Dict[str, Any] = {}
        
        # Initialize default parliamentary MCP servers
        self._init_parliamentary_servers()
    
    def _init_parliamentary_servers(self):
        """Initialize default parliamentary MCP servers."""
        
        # Legislative Database Server
        self.servers["legislative_db"] = MCPServerConfig(
            name="legislative_db",
            server_type=MCPServerType.LEGISLATIVE_DATABASE,
            connection_params={
                "command": "python",
                "args": ["triad/mcp/servers/legislative_database_server.py"],
                "env": {"PARLIAMENTARY_OVERSIGHT": "true"}
            },
            security_level=ToolSecurityLevel.PARLIAMENTARY,
            constitutional_authority_required=ParliamentaryAuthority.LEGISLATIVE,
            description="Access to bills, acts, regulations, and legislative history",
            available_tools=[
                "search_bills",
                "get_bill_text",
                "track_amendments",
                "analyze_legislative_impact"
            ]
        )
        
        # Constitutional Law Server
        self.servers["constitutional_law"] = MCPServerConfig(
            name="constitutional_law",
            server_type=MCPServerType.CONSTITUTIONAL_LAW,
            connection_params={
                "command": "python",
                "args": ["triad/mcp/servers/constitutional_law_server.py"],
                "env": {"CONSTITUTIONAL_AUTHORITY": "required"}
            },
            security_level=ToolSecurityLevel.CONSTITUTIONAL,
            constitutional_authority_required=ParliamentaryAuthority.JUDICIAL,
            description="Constitutional interpretation, Charter rights, and legal precedents",
            available_tools=[
                "search_constitutional_cases",
                "interpret_charter_rights",
                "analyze_constitutional_compliance",
                "lookup_legal_precedents"
            ]
        )
        
        # Hansard Archive Server
        self.servers["hansard_archive"] = MCPServerConfig(
            name="hansard_archive",
            server_type=MCPServerType.HANSARD_ARCHIVE,
            connection_params={
                "command": "python",
                "args": ["triad/mcp/servers/hansard_server.py"],
                "env": {"PARLIAMENTARY_RECORDS": "true"}
            },
            security_level=ToolSecurityLevel.PUBLIC,
            description="Parliamentary debate records and proceedings archive",
            available_tools=[
                "search_debates",
                "get_session_transcript",
                "analyze_speaking_patterns",
                "track_member_positions"
            ]
        )
        
        # Citizen Engagement Server
        self.servers["citizen_engagement"] = MCPServerConfig(
            name="citizen_engagement",
            server_type=MCPServerType.CITIZEN_ENGAGEMENT,
            connection_params={
                "command": "python",
                "args": ["triad/mcp/servers/citizen_engagement_server.py"],
                "env": {"DEMOCRATIC_PARTICIPATION": "true"}
            },
            security_level=ToolSecurityLevel.PUBLIC,
            description="Public consultation, petitions, and citizen feedback systems",
            available_tools=[
                "process_petition",
                "analyze_public_consultation",
                "track_citizen_feedback",
                "generate_engagement_report"
            ]
        )
        
        # Policy Analysis Server
        self.servers["policy_analysis"] = MCPServerConfig(
            name="policy_analysis",
            server_type=MCPServerType.POLICY_ANALYSIS,
            connection_params={
                "command": "python",
                "args": ["triad/mcp/servers/policy_analysis_server.py"],
                "env": {"POLICY_RESEARCH": "true"}
            },
            security_level=ToolSecurityLevel.MINISTERIAL,
            constitutional_authority_required=ParliamentaryAuthority.EXECUTIVE,
            description="Policy research, impact analysis, and evidence synthesis",
            available_tools=[
                "analyze_policy_options",
                "assess_economic_impact",
                "evaluate_social_outcomes",
                "compare_international_practices"
            ]
        )
    
    async def connect_to_server(
        self,
        server_name: str,
        parliamentary_context: ParliamentaryContext
    ) -> bool:
        """
        Connect to an MCP server with constitutional validation.
        
        Args:
            server_name: Name of the server to connect to
            parliamentary_context: Parliamentary context for the connection
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if server_name not in self.servers:
                raise ValueError(f"Unknown MCP server: {server_name}")
            
            server_config = self.servers[server_name]
            
            # Validate constitutional authority
            if (server_config.constitutional_authority_required and 
                parliamentary_context.constitutional_authority != server_config.constitutional_authority_required):
                raise PermissionError(
                    f"Server {server_name} requires {server_config.constitutional_authority_required.value} authority, "
                    f"but agent has {parliamentary_context.constitutional_authority.value}"
                )
            
            # Validate security clearance
            security_levels = [ToolSecurityLevel.PUBLIC, ToolSecurityLevel.PARLIAMENTARY, 
                             ToolSecurityLevel.MINISTERIAL, ToolSecurityLevel.CONSTITUTIONAL, 
                             ToolSecurityLevel.CROWN]
            
            if (security_levels.index(parliamentary_context.security_clearance) < 
                security_levels.index(server_config.security_level)):
                raise PermissionError(
                    f"Insufficient security clearance for server {server_name}. "
                    f"Required: {server_config.security_level.value}, "
                    f"Available: {parliamentary_context.security_clearance.value}"
                )
            
            # Establish connection
            connection_success = await self.mcp_client.connect_server(
                server_name=server_name,
                connection_params=server_config.connection_params
            )
            
            if connection_success:
                self.active_connections[server_name] = {
                    "connected_at": datetime.now(timezone.utc),
                    "agent_id": parliamentary_context.agent_id,
                    "constitutional_authority": parliamentary_context.constitutional_authority.value,
                    "server_config": server_config
                }
                
                self.logger.log_parliamentary_event(
                    event_type="mcp_server_connected",
                    data={
                        "server_name": server_name,
                        "server_type": server_config.server_type.value,
                        "security_level": server_config.security_level.value,
                        "connecting_agent": parliamentary_context.agent_id
                    },
                    authority=parliamentary_context.constitutional_authority.value
                )
            
            return connection_success
            
        except Exception as e:
            self.logger.log_parliamentary_event(
                event_type="mcp_connection_error",
                data={
                    "server_name": server_name,
                    "error": str(e),
                    "agent_id": parliamentary_context.agent_id
                },
                authority=parliamentary_context.constitutional_authority.value
            )
            return False
    
    async def call_server_tool(
        self,
        server_name: str,
        tool_name: str,
        parameters: Dict[str, Any],
        parliamentary_context: ParliamentaryContext
    ) -> Dict[str, Any]:
        """
        Call a tool on an MCP server with constitutional oversight.
        
        Args:
            server_name: Name of the MCP server
            tool_name: Name of the tool to call
            parameters: Tool parameters
            parliamentary_context: Parliamentary context
        
        Returns:
            Tool execution results
        """
        try:
            # Ensure server connection
            if server_name not in self.active_connections:
                connection_success = await self.connect_to_server(server_name, parliamentary_context)
                if not connection_success:
                    raise ConnectionError(f"Could not connect to MCP server: {server_name}")
            
            server_config = self.servers[server_name]
            
            # Validate tool availability
            if (server_config.available_tools and 
                tool_name not in server_config.available_tools):
                raise ValueError(
                    f"Tool {tool_name} not available on server {server_name}. "
                    f"Available tools: {server_config.available_tools}"
                )
            
            # Add constitutional context to parameters
            enhanced_parameters = {
                **parameters,
                "constitutional_context": {
                    "agent_id": parliamentary_context.agent_id,
                    "constitutional_authority": parliamentary_context.constitutional_authority.value,
                    "session_id": parliamentary_context.session_id,
                    "parliamentary_session_id": parliamentary_context.parliamentary_session_id,
                    "security_clearance": parliamentary_context.security_clearance.value,
                    "constitutional_oversight": parliamentary_context.constitutional_oversight
                }
            }
            
            # Execute tool with MCP client
            with self.logger.parliamentary_session_span(
                f"mcp-tool-{server_name}-{tool_name}",
                [parliamentary_context.agent_id]
            ) as span:
                span.set_attribute("mcp.server", server_name)
                span.set_attribute("mcp.tool", tool_name)
                span.set_attribute("mcp.security_level", server_config.security_level.value)
                
                result = await self.mcp_client.call_tool(
                    tool_name=f"{server_name}:{tool_name}",
                    operation="execute",
                    parameters=enhanced_parameters,
                    requesting_agent=parliamentary_context.agent_id,
                    constitutional_validation=parliamentary_context.constitutional_oversight
                )
                
                # Add parliamentary accountability metadata
                result["parliamentary_metadata"] = {
                    "called_by": parliamentary_context.agent_id,
                    "constitutional_authority": parliamentary_context.constitutional_authority.value,
                    "server_name": server_name,
                    "tool_name": tool_name,
                    "call_timestamp": datetime.now(timezone.utc).isoformat(),
                    "constitutional_oversight": parliamentary_context.constitutional_oversight,
                    "security_level": server_config.security_level.value
                }
                
                span.set_attribute("mcp.result_status", result.get("status", "unknown"))
            
            return result
            
        except Exception as e:
            self.logger.log_parliamentary_event(
                event_type="mcp_tool_call_error",
                data={
                    "server_name": server_name,
                    "tool_name": tool_name,
                    "error": str(e),
                    "agent_id": parliamentary_context.agent_id
                },
                authority=parliamentary_context.constitutional_authority.value
            )
            raise
    
    def create_mcp_tool_for_agent(
        self,
        server_name: str,
        tool_name: str,
        tool_description: str
    ) -> Callable:
        """
        Create a Pydantic AI tool that calls an MCP server tool.
        
        Args:
            server_name: Name of the MCP server
            tool_name: Name of the tool on the server
            tool_description: Description for the AI agent
        
        Returns:
            Callable tool function for Pydantic AI agent
        """
        
        async def mcp_tool_wrapper(
            ctx: RunContext[ParliamentaryContext],
            **parameters
        ) -> Dict[str, Any]:
            """Wrapper function for MCP tool calls."""
            return await self.call_server_tool(
                server_name=server_name,
                tool_name=tool_name,
                parameters=parameters,
                parliamentary_context=ctx.deps
            )
        
        # Set function metadata for Pydantic AI
        mcp_tool_wrapper.__name__ = f"{server_name}_{tool_name}"
        mcp_tool_wrapper.__doc__ = tool_description
        
        return mcp_tool_wrapper
    
    async def get_server_status(self) -> Dict[str, Any]:
        """Get status of all MCP servers."""
        status = {
            "total_servers": len(self.servers),
            "active_connections": len(self.active_connections),
            "servers": {},
            "checked_at": datetime.now(timezone.utc).isoformat()
        }
        
        for server_name, server_config in self.servers.items():
            server_status = {
                "enabled": server_config.enabled,
                "server_type": server_config.server_type.value,
                "security_level": server_config.security_level.value,
                "constitutional_authority_required": (
                    server_config.constitutional_authority_required.value 
                    if server_config.constitutional_authority_required else None
                ),
                "connected": server_name in self.active_connections,
                "available_tools": server_config.available_tools or [],
                "description": server_config.description
            }
            
            if server_name in self.active_connections:
                connection_info = self.active_connections[server_name]
                server_status.update({
                    "connected_at": connection_info["connected_at"].isoformat(),
                    "connected_by": connection_info["agent_id"],
                    "connection_authority": connection_info["constitutional_authority"]
                })
            
            status["servers"][server_name] = server_status
        
        return status
    
    async def disconnect_all_servers(self):
        """Disconnect from all MCP servers."""
        try:
            for server_name in list(self.active_connections.keys()):
                await self.mcp_client.disconnect_server(server_name)
                del self.active_connections[server_name]
            
            self.logger.log_parliamentary_event(
                event_type="all_mcp_servers_disconnected",
                data={"disconnected_count": len(self.active_connections)},
                authority="system"
            )
            
        except Exception as e:
            self.logger.log_parliamentary_event(
                event_type="mcp_disconnect_error",
                data={"error": str(e)},
                authority="system"
            )


# Global parliamentary MCP client
parliamentary_mcp_client = ParliamentaryMCPClient()


def get_parliamentary_mcp_client() -> ParliamentaryMCPClient:
    """Get the global parliamentary MCP client."""
    return parliamentary_mcp_client


async def register_mcp_tools_with_agent(
    agent: Agent,
    server_tools: Dict[str, List[str]],
    parliamentary_context: ParliamentaryContext
) -> Agent:
    """
    Register MCP server tools with a Pydantic AI agent.
    
    Args:
        agent: Pydantic AI agent
        server_tools: Dictionary mapping server names to lists of tool names
        parliamentary_context: Parliamentary context
    
    Returns:
        Agent with registered MCP tools
    """
    mcp_client = get_parliamentary_mcp_client()
    
    try:
        for server_name, tool_names in server_tools.items():
            if server_name not in mcp_client.servers:
                raise ValueError(f"Unknown MCP server: {server_name}")
            
            server_config = mcp_client.servers[server_name]
            
            for tool_name in tool_names:
                # Create tool description
                tool_description = (
                    f"Access {tool_name} on {server_name} MCP server. "
                    f"Server type: {server_config.server_type.value}. "
                    f"Security level: {server_config.security_level.value}. "
                    f"{server_config.description}"
                )
                
                # Create and register MCP tool
                mcp_tool = mcp_client.create_mcp_tool_for_agent(
                    server_name=server_name,
                    tool_name=tool_name,
                    tool_description=tool_description
                )
                
                # Register with agent
                agent.tool(mcp_tool)
        
        mcp_client.logger.log_agent_activity(
            agent_name=parliamentary_context.agent_id,
            activity="mcp_tools_registered",
            data={
                "servers": list(server_tools.keys()),
                "total_tools": sum(len(tools) for tools in server_tools.values()),
                "constitutional_authority": parliamentary_context.constitutional_authority.value
            }
        )
        
        return agent
        
    except Exception as e:
        mcp_client.logger.log_agent_activity(
            agent_name=parliamentary_context.agent_id,
            activity="mcp_tool_registration_error",
            data={"error": str(e), "server_tools": server_tools}
        )
        raise


# Predefined MCP tool configurations for constitutional agents
CONSTITUTIONAL_AGENT_MCP_TOOLS = {
    "planner": {
        "legislative_db": ["search_bills", "get_bill_text", "track_amendments"],
        "policy_analysis": ["analyze_policy_options", "assess_economic_impact"],
        "citizen_engagement": ["analyze_public_consultation", "track_citizen_feedback"]
    },
    
    "executor": {
        "legislative_db": ["get_bill_text", "analyze_legislative_impact"],
        "policy_analysis": ["analyze_policy_options", "evaluate_social_outcomes"],
        "government_data": ["access_department_data", "track_implementation_metrics"]
    },
    
    "evaluator": {
        "constitutional_law": ["search_constitutional_cases", "interpret_charter_rights", "analyze_constitutional_compliance"],
        "legislative_db": ["search_bills", "get_bill_text"],
        "hansard_archive": ["search_debates", "get_session_transcript"]
    },
    
    "overwatch": {
        "constitutional_law": ["analyze_constitutional_compliance", "lookup_legal_precedents"],
        "hansard_archive": ["search_debates", "analyze_speaking_patterns"],
        "policy_analysis": ["compare_international_practices"],
        "citizen_engagement": ["generate_engagement_report"]
    }
}


async def setup_constitutional_agent_mcp_tools(
    agent: Agent,
    agent_role: str,
    parliamentary_context: ParliamentaryContext
) -> Agent:
    """
    Set up MCP tools for a constitutional agent based on their role.
    
    Args:
        agent: Pydantic AI agent
        agent_role: Role of the agent (planner, executor, evaluator, overwatch)
        parliamentary_context: Parliamentary context
    
    Returns:
        Agent with role-appropriate MCP tools
    """
    if agent_role.lower() not in CONSTITUTIONAL_AGENT_MCP_TOOLS:
        raise ValueError(f"Unknown agent role: {agent_role}")
    
    role_tools = CONSTITUTIONAL_AGENT_MCP_TOOLS[agent_role.lower()]
    
    return await register_mcp_tools_with_agent(
        agent=agent,
        server_tools=role_tools,
        parliamentary_context=parliamentary_context
    )