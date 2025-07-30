"""
Base MCP Server Implementation

Base MCP server with governance compliance and organizational
accountability for all MCP server implementations.
"""

from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime, timezone
import uuid
import json
from abc import ABC, abstractmethod
import logfire


class MCPServer(ABC):
    """
    Base MCP server with governance compliance.
    
    Provides common functionality for all MCP servers including
    governance oversight and organizational accountability.
    """
    
    def __init__(self, server_name: str, logfire_logger: logfire):
        self.server_name = server_name
        self.logfire_logger = logfire_logger
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.resources: Dict[str, Dict[str, Any]] = {}
        
        # Governance settings
        self.governance_oversight = True
        self.organizational_accountability = True
        
        # Server state
        self.initialized = False
        self.tool_call_count = 0
        self.error_count = 0
        
        # Register server tools
        self._register_tools()
    
    @abstractmethod
    def _register_tools(self) -> None:
        """Register server tools. Implemented by subclasses."""
        pass
    
    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize MCP server with governance configuration."""
        self.governance_oversight = config.get("governance_oversight", True)
        self.organizational_accountability = config.get("organizational_accountability", True)
        
        await self._server_initialize(config)
        self.initialized = True
        
        await self.logfire_logger.info(
            "MCP server initialized",
            server_name=self.server_name,
            tools_count=len(self.tools),
            governance_oversight=self.governance_oversight
        )
    
    @abstractmethod
    async def _server_initialize(self, config: Dict[str, Any]) -> None:
        """Server-specific initialization."""
        pass
    
    async def handle_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        call_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Handle tool call with governance oversight."""
        if not self.initialized:
            return {
                "success": False,
                "error": "MCP server not initialized"
            }
        
        call_id = call_id or f"call_{uuid.uuid4().hex[:8]}"
        
        with logfire.span("mcp_tool_call") as span:
            span.set_attribute("server_name", self.server_name)
            span.set_attribute("tool_name", tool_name)
            span.set_attribute("call_id", call_id)
            
            try:
                # Validate tool exists
                if tool_name not in self.tools:
                    return {
                        "success": False,
                        "error": f"Tool '{tool_name}' not found",
                        "available_tools": list(self.tools.keys())
                    }
                
                # Governance validation
                if self.governance_oversight:
                    validation_result = await self._validate_tool_call(tool_name, arguments)
                    if not validation_result["compliant"]:
                        return {
                            "success": False,
                            "error": "Governance compliance failure",
                            "violations": validation_result["violations"],
                            "call_id": call_id
                        }
                
                # Execute tool
                result = await self._execute_tool(tool_name, arguments, call_id)
                
                self.tool_call_count += 1
                
                await self.logfire_logger.info(
                    "MCP tool call completed",
                    server_name=self.server_name,
                    tool_name=tool_name,
                    call_id=call_id,
                    success=result.get("success", True)
                )
                
                return result
                
            except Exception as e:
                self.error_count += 1
                
                await self.logfire_logger.error(
                    "MCP tool call failed",
                    server_name=self.server_name,
                    tool_name=tool_name,
                    call_id=call_id,
                    error=str(e)
                )
                
                return {
                    "success": False,
                    "error": str(e),
                    "call_id": call_id
                }
    
    @abstractmethod
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any], call_id: str) -> Dict[str, Any]:
        """Execute specific tool. Implemented by subclasses."""
        pass
    
    async def _validate_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Validate tool call for governance compliance."""
        violations = []
        
        # Check for required arguments
        tool_spec = self.tools.get(tool_name, {})
        required_args = tool_spec.get("required_arguments", [])
        
        for arg in required_args:
            if arg not in arguments:
                violations.append(f"Missing required argument: {arg}")
        
        # Check for governance requirements
        if not arguments.get("governance_validation", True):
            violations.append("Tool call must include governance validation")
        
        # Check for organizational context
        if self.organizational_accountability and not arguments.get("organizational_context"):
            violations.append("Tool call must include organizational context")
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations
        }
    
    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        required_arguments: Optional[List[str]] = None
    ) -> None:
        """Register a tool with the server."""
        self.tools[name] = {
            "name": name,
            "description": description,
            "inputSchema": input_schema,
            "required_arguments": required_arguments or [],
            "governance_oversight": True
        }
    
    def register_resource(
        self,
        name: str,
        uri: str,
        description: str,
        mime_type: str = "text/plain"
    ) -> None:
        """Register a resource with the server."""
        self.resources[name] = {
            "uri": uri,
            "name": name,
            "description": description,
            "mimeType": mime_type
        }
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available tools."""
        return {
            "tools": list(self.tools.values()),
            "server_name": self.server_name,
            "governance_oversight": self.governance_oversight
        }
    
    async def list_resources(self) -> Dict[str, Any]:
        """List available resources."""
        return {
            "resources": list(self.resources.values()),
            "server_name": self.server_name
        }
    
    async def get_server_statistics(self) -> Dict[str, Any]:
        """Get server statistics."""
        success_rate = 0.0
        if self.tool_call_count > 0:
            success_count = self.tool_call_count - self.error_count
            success_rate = success_count / self.tool_call_count
        
        return {
            "server_name": self.server_name,
            "initialized": self.initialized,
            "tool_call_count": self.tool_call_count,
            "error_count": self.error_count,
            "success_rate": success_rate,
            "tools_count": len(self.tools),
            "resources_count": len(self.resources),
            "governance_oversight": self.governance_oversight,
            "organizational_accountability": self.organizational_accountability
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform server health check."""
        health_status = "healthy"
        
        if not self.initialized:
            health_status = "not_initialized"
        elif self.error_count > self.tool_call_count * 0.5:  # More than 50% errors
            health_status = "degraded"
        
        return {
            "server_name": self.server_name,
            "status": health_status,
            "initialized": self.initialized,
            "uptime": datetime.now(timezone.utc).isoformat(),
            "error_rate": self.error_count / max(self.tool_call_count, 1)
        }
    
    async def shutdown(self) -> None:
        """Shutdown the MCP server gracefully."""
        await self.logfire_logger.info(
            "MCP server shutting down",
            server_name=self.server_name,
            tool_calls_processed=self.tool_call_count
        )
        
        # Perform server-specific cleanup
        await self._server_shutdown()
        
        self.initialized = False
    
    async def _server_shutdown(self) -> None:
        """Server-specific shutdown logic. Override in subclasses."""
        pass