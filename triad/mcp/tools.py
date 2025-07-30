"""
MCP Tools Integration

Core MCP tools for Pydantic AI agents with proper separation from
parliamentary toolsets. Focuses on MCP client operations only.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic_ai import RunContext
import logfire

from triad.core.dependencies import TriadDeps
from .client import MCPClient


class MCPTools:
    """
    Core MCP tools for Pydantic AI agents.
    
    Handles only MCP client operations - server connections,
    tool calling, and basic MCP functionality.
    Parliamentary oversight is handled by parliamentary_toolsets.py
    """
    
    def __init__(self, mcp_client: MCPClient):
        self.mcp_client = mcp_client
    
    async def call_mcp_tool(
        self,
        ctx: RunContext[TriadDeps],
        server_name: str,
        tool_name: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Call a tool on an MCP server.
        
        Basic MCP tool calling without parliamentary oversight.
        Constitutional oversight should be handled by parliamentary toolsets.
        """
        with logfire.span("mcp_tool_call") as span:
            span.set_attribute("server_name", server_name)
            span.set_attribute("tool_name", tool_name)
            span.set_attribute("requesting_agent", ctx.deps.config.get("agent_name", "unknown"))
            
            # Execute tool call through MCP client
            result = await self.mcp_client.call_tool(
                tool_name=f"{server_name}:{tool_name}",
                operation="execute",
                parameters=parameters or {},
                requesting_agent=ctx.deps.config.get("agent_name", "unknown")
            )
            
            return result
    
    async def connect_to_server(
        self,
        ctx: RunContext[TriadDeps],
        server_name: str,
        connection_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Connect to an MCP server.
        
        Basic MCP server connection without constitutional validation.
        Parliamentary validation should be handled by parliamentary toolsets.
        """
        with logfire.span("mcp_server_connect") as span:
            span.set_attribute("server_name", server_name)
            span.set_attribute("requesting_agent", ctx.deps.config.get("agent_name", "unknown"))
            
            # Connect through MCP client
            success = await self.mcp_client.connect_server(
                server_name=server_name,
                connection_params=connection_params
            )
            
            return {
                "success": success,
                "server_name": server_name,
                "connected_at": datetime.now().isoformat()
            }
    
    async def get_server_info(
        self,
        ctx: RunContext[TriadDeps],
        server_name: str
    ) -> Dict[str, Any]:
        """
        Get information about an MCP server.
        
        Returns server capabilities, tools, and connection status.
        """
        with logfire.span("mcp_server_info") as span:
            span.set_attribute("server_name", server_name)
            
            # Get server info through MCP client
            info = await self.mcp_client.get_server_info(server_name)
            
            return info
    
    async def disconnect_from_server(
        self,
        ctx: RunContext[TriadDeps],
        server_name: str
    ) -> Dict[str, Any]:
        """
        Disconnect from an MCP server.
        
        Clean disconnection from MCP server.
        """
        with logfire.span("mcp_server_disconnect") as span:
            span.set_attribute("server_name", server_name)
            
            # Disconnect through MCP client
            success = await self.mcp_client.disconnect_server(server_name)
            
            return {
                "success": success,
                "server_name": server_name,
                "disconnected_at": datetime.now().isoformat()
            }
    
    async def list_available_tools(
        self,
        ctx: RunContext[TriadDeps],
        server_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List available tools on MCP servers.
        
        Args:
            server_name: Specific server to list tools for, or None for all servers
        
        Returns:
            Dictionary of available tools by server
        """
        with logfire.span("mcp_list_tools") as span:
            span.set_attribute("server_name", server_name or "all")
            
            if server_name:
                # Get tools for specific server
                tools = await self.mcp_client.list_tools(server_name)
                return {server_name: tools}
            else:
                # Get tools for all connected servers
                all_tools = await self.mcp_client.list_all_tools()
                return all_tools
    
    async def get_connection_status(
        self,
        ctx: RunContext[TriadDeps]
    ) -> Dict[str, Any]:
        """
        Get connection status for all MCP servers.
        
        Returns:
            Dictionary with connection status for each server
        """
        with logfire.span("mcp_connection_status"):
            status = await self.mcp_client.get_connection_status()
            return status


# Helper functions for agent tool registration
def register_mcp_tools(agent, mcp_tools: MCPTools):
    """
    Register basic MCP tools with a Pydantic AI agent.
    
    These are low-level MCP operations. For parliamentary oversight,
    use parliamentary_toolsets.py instead.
    """
    
    @agent.tool
    async def call_mcp_tool(
        ctx: RunContext[TriadDeps],
        server_name: str,
        tool_name: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Call a tool on an MCP server."""
        return await mcp_tools.call_mcp_tool(ctx, server_name, tool_name, parameters)
    
    @agent.tool
    async def connect_to_mcp_server(
        ctx: RunContext[TriadDeps],
        server_name: str,
        connection_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Connect to an MCP server."""
        return await mcp_tools.connect_to_server(ctx, server_name, connection_params)
    
    @agent.tool
    async def get_mcp_server_info(
        ctx: RunContext[TriadDeps],
        server_name: str
    ) -> Dict[str, Any]:
        """Get information about an MCP server."""
        return await mcp_tools.get_server_info(ctx, server_name)
    
    @agent.tool
    async def disconnect_from_mcp_server(
        ctx: RunContext[TriadDeps],
        server_name: str
    ) -> Dict[str, Any]:
        """Disconnect from an MCP server."""
        return await mcp_tools.disconnect_from_server(ctx, server_name)
    
    @agent.tool
    async def list_mcp_tools(
        ctx: RunContext[TriadDeps],
        server_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """List available tools on MCP servers."""
        return await mcp_tools.list_available_tools(ctx, server_name)
    
    @agent.tool
    async def get_mcp_status(
        ctx: RunContext[TriadDeps]
    ) -> Dict[str, Any]:
        """Get connection status for all MCP servers."""
        return await mcp_tools.get_connection_status(ctx)