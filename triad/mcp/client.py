"""
MCP Client Implementation

Client for Model Context Protocol with constitutional oversight
and Westminster parliamentary accountability for external integrations.
"""

from typing import Dict, Any, List, Optional, Union
import asyncio
import json
from datetime import datetime, timezone
import uuid
import logfire
import httpx

from .adapters import SystemAdapter
from triad.core.constitutional import ConstitutionalAuthority, ConstitutionalDecision


class MCPClient:
    """
    Client for Model Context Protocol integration.
    
    Provides constitutional oversight for all external system integrations
    following Westminster parliamentary principles.
    """
    
    def __init__(
        self,
        logfire_logger: logfire,
        timeout_seconds: int = 30,
        constitutional_oversight: bool = True
    ):
        self.logfire_logger = logfire_logger
        self.timeout_seconds = timeout_seconds
        self.constitutional_oversight = constitutional_oversight
        
        # Registered adapters and servers
        self.adapters: Dict[str, SystemAdapter] = {}
        self.server_urls: Dict[str, str] = {}
        self.tool_registry: Dict[str, Dict[str, Any]] = {}
        
        # Integration tracking
        self.active_integrations: Dict[str, Dict[str, Any]] = {}
        self.integration_history: List[Dict[str, Any]] = []
        
        # HTTP client for MCP server communication
        self.http_client = httpx.AsyncClient(timeout=timeout_seconds)
        
        # Initialize constitutional compliance tracking
        self.constitutional_violations: List[Dict[str, Any]] = []
        
    async def register_adapter(
        self,
        adapter_name: str,
        adapter: SystemAdapter
    ) -> None:
        """
        Register system adapter with constitutional validation.
        """
        with logfire.span("register_mcp_adapter") as span:
            span.set_attribute("adapter_name", adapter_name)
            span.set_attribute("adapter_type", type(adapter).__name__)
            
            # Constitutional validation for adapter registration
            if self.constitutional_oversight:
                validation_result = await self._validate_adapter_registration(adapter_name, adapter)
                if not validation_result["constitutional_compliance"]:
                    raise ValueError(f"Adapter registration violates constitutional principles: {validation_result['violations']}")
            
            self.adapters[adapter_name] = adapter
            
            # Initialize adapter with constitutional constraints
            await adapter.initialize({
                "constitutional_oversight": self.constitutional_oversight,
                "parliamentary_accountability": True,
                "audit_trail": True
            })
            
            await self.logfire_logger.info(
                "MCP adapter registered",
                adapter_name=adapter_name,
                adapter_type=type(adapter).__name__,
                constitutional_oversight=self.constitutional_oversight
            )
    
    async def register_server(
        self,
        server_name: str,
        server_url: str,
        capabilities: Optional[List[str]] = None
    ) -> None:
        """
        Register MCP server with capabilities.
        """
        with logfire.span("register_mcp_server") as span:
            span.set_attribute("server_name", server_name)
            span.set_attribute("server_url", server_url)
            
            self.server_urls[server_name] = server_url
            
            # Discover tools from server
            if capabilities:
                await self._discover_server_tools(server_name, server_url, capabilities)
            
            await self.logfire_logger.info(
                "MCP server registered",
                server_name=server_name,
                server_url=server_url,
                capabilities=capabilities or []
            )
    
    async def call_tool(
        self,
        tool_name: str,
        operation: str,
        parameters: Dict[str, Any],
        requesting_agent: Optional[str] = None,
        constitutional_validation: bool = True
    ) -> Dict[str, Any]:
        """
        Call external tool through MCP with constitutional oversight.
        """
        with logfire.span("mcp_tool_call") as span:
            integration_id = f"mcp_{uuid.uuid4().hex[:8]}"
            span.set_attribute("integration_id", integration_id)
            span.set_attribute("tool_name", tool_name)
            span.set_attribute("operation", operation)
            span.set_attribute("requesting_agent", requesting_agent or "system")
            
            start_time = datetime.now(timezone.utc)
            
            # Constitutional validation if required
            if constitutional_validation and self.constitutional_oversight:
                validation_result = await self._validate_tool_call(
                    tool_name, operation, parameters, requesting_agent
                )
                if not validation_result["constitutional_compliance"]:
                    await self.logfire_logger.warning(
                        "MCP tool call blocked by constitutional validation",
                        integration_id=integration_id,
                        violations=validation_result["violations"]
                    )
                    return {
                        "success": False,
                        "error": "Constitutional compliance failure",
                        "violations": validation_result["violations"],
                        "integration_id": integration_id
                    }
            
            # Track active integration
            integration_record = {
                "integration_id": integration_id,
                "tool_name": tool_name,
                "operation": operation,
                "requesting_agent": requesting_agent,
                "start_time": start_time,
                "constitutional_validation": constitutional_validation,
                "status": "in_progress"
            }
            self.active_integrations[integration_id] = integration_record
            
            try:
                # Execute tool call
                if tool_name in self.adapters:
                    # Use registered adapter
                    result = await self._call_adapter_tool(
                        tool_name, operation, parameters, integration_id
                    )
                elif tool_name in self.server_urls:
                    # Use MCP server
                    result = await self._call_server_tool(
                        tool_name, operation, parameters, integration_id
                    )
                else:
                    # Attempt dynamic tool resolution
                    result = await self._resolve_and_call_tool(
                        tool_name, operation, parameters, integration_id
                    )
                
                # Update integration record
                integration_record.update({
                    "status": "completed",
                    "success": result.get("success", True),
                    "end_time": datetime.now(timezone.utc),
                    "execution_time_seconds": (datetime.now(timezone.utc) - start_time).total_seconds(),
                    "result_size": len(str(result))
                })
                
                # Log successful integration
                await self.logfire_logger.info(
                    "MCP tool call completed",
                    integration_id=integration_id,
                    success=result.get("success", True),
                    execution_time=integration_record["execution_time_seconds"]
                )
                
                # Add integration metadata
                result["integration_id"] = integration_id
                result["constitutional_validated"] = constitutional_validation
                result["parliamentary_accountable"] = True
                
                return result
                
            except Exception as e:
                # Update integration record with error
                integration_record.update({
                    "status": "failed",
                    "success": False,
                    "error": str(e),
                    "end_time": datetime.now(timezone.utc),
                    "execution_time_seconds": (datetime.now(timezone.utc) - start_time).total_seconds()
                })
                
                await self.logfire_logger.error(
                    "MCP tool call failed",
                    integration_id=integration_id,
                    tool_name=tool_name,
                    error=str(e)
                )
                
                return {
                    "success": False,
                    "error": str(e),
                    "integration_id": integration_id,
                    "constitutional_validated": constitutional_validation
                }
                
            finally:
                # Move to history and clean up
                self.integration_history.append(integration_record)
                if integration_id in self.active_integrations:
                    del self.active_integrations[integration_id]
                
                # Limit history size
                if len(self.integration_history) > 1000:
                    self.integration_history = self.integration_history[-500:]
    
    async def query_external_system(
        self,
        system_type: str,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        requesting_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query external system with constitutional safeguards.
        """
        return await self.call_tool(
            tool_name=f"{system_type}_adapter",
            operation="query",
            parameters={
                "query": query,
                "parameters": parameters or {},
                "read_only": True,  # Constitutional protection
                "audit_trail": True
            },
            requesting_agent=requesting_agent,
            constitutional_validation=True
        )
    
    async def update_external_system(
        self,
        system_type: str,
        operation: str,
        data: Dict[str, Any],
        requesting_agent: str,
        ministerial_approval: bool = True
    ) -> Dict[str, Any]:
        """
        Update external system with ministerial responsibility.
        """
        if not ministerial_approval:
            return {
                "success": False,
                "error": "Ministerial approval required for external system updates",
                "constitutional_requirement": "ministerial_responsibility"
            }
        
        return await self.call_tool(
            tool_name=f"{system_type}_adapter",
            operation=operation,
            parameters={
                "data": data,
                "requesting_agent": requesting_agent,
                "ministerial_approval": ministerial_approval,
                "backup_original": True,  # Constitutional safeguard
                "audit_trail": True
            },
            requesting_agent=requesting_agent,
            constitutional_validation=True
        )
    
    async def validate_external_integration(
        self,
        integration_id: str,
        validation_criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate external integration for constitutional compliance.
        """
        with logfire.span("validate_external_integration") as span:
            span.set_attribute("integration_id", integration_id)
            
            # Find integration record
            integration_record = None
            for record in self.integration_history:
                if record["integration_id"] == integration_id:
                    integration_record = record
                    break
            
            if not integration_record:
                return {
                    "validation_success": False,
                    "error": "Integration record not found"
                }
            
            validation_result = {
                "integration_id": integration_id,
                "validation_timestamp": datetime.now(timezone.utc).isoformat(),
                "constitutional_compliance": True,
                "parliamentary_accountability": True,
                "violations": [],
                "recommendations": []
            }
            
            # Check constitutional compliance
            if not integration_record.get("constitutional_validation", False):
                validation_result["violations"].append("Integration bypassed constitutional validation")
                validation_result["constitutional_compliance"] = False
            
            # Check success rate
            if not integration_record.get("success", False):
                validation_result["violations"].append("Integration failed to complete successfully")
            
            # Check execution time
            execution_time = integration_record.get("execution_time_seconds", 0)
            if execution_time > self.timeout_seconds:
                validation_result["violations"].append(f"Integration exceeded timeout: {execution_time}s")
            
            # Apply custom validation criteria
            if validation_criteria:
                for criterion, threshold in validation_criteria.items():
                    if criterion in integration_record:
                        if integration_record[criterion] < threshold:
                            validation_result["violations"].append(
                                f"Integration failed {criterion} threshold: {integration_record[criterion]} < {threshold}"
                            )
            
            # Generate recommendations
            if validation_result["violations"]:
                validation_result["recommendations"].extend([
                    "Review integration procedures for constitutional compliance",
                    "Implement additional safeguards for external system access",
                    "Consider ministerial review of integration policies"
                ])
                validation_result["constitutional_compliance"] = False
            
            await self.logfire_logger.info(
                "External integration validated",
                integration_id=integration_id,
                constitutional_compliance=validation_result["constitutional_compliance"],
                violations_count=len(validation_result["violations"])
            )
            
            return validation_result
    
    async def _validate_adapter_registration(
        self,
        adapter_name: str,
        adapter: SystemAdapter
    ) -> Dict[str, Any]:
        """Validate adapter registration against constitutional principles."""
        violations = []
        
        # Check adapter has required constitutional methods
        required_methods = ["initialize", "validate_operation", "audit_trail"]
        for method in required_methods:
            if not hasattr(adapter, method):
                violations.append(f"Adapter missing required constitutional method: {method}")
        
        # Check adapter supports audit trail
        if not getattr(adapter, "supports_audit_trail", False):
            violations.append("Adapter does not support audit trail requirement")
        
        return {
            "constitutional_compliance": len(violations) == 0,
            "violations": violations,
            "adapter_name": adapter_name
        }
    
    async def _validate_tool_call(
        self,
        tool_name: str,
        operation: str,
        parameters: Dict[str, Any],
        requesting_agent: Optional[str]
    ) -> Dict[str, Any]:
        """Validate tool call for constitutional compliance."""
        violations = []
        
        # Check requesting agent authority
        if not requesting_agent:
            violations.append("Tool call must identify requesting agent for accountability")
        
        # Check for dangerous operations
        dangerous_operations = ["delete", "drop", "truncate", "destroy", "remove_all"]
        if operation.lower() in dangerous_operations:
            if not parameters.get("ministerial_approval", False):
                violations.append(f"Dangerous operation '{operation}' requires ministerial approval")
        
        # Check for constitutional safeguards
        if operation in ["update", "modify", "change"] and not parameters.get("backup_original", False):
            violations.append("Modification operations should include backup safeguard")
        
        # Check audit trail requirement
        if not parameters.get("audit_trail", False):
            violations.append("Operations must include audit trail for accountability")
        
        return {
            "constitutional_compliance": len(violations) == 0,
            "violations": violations,
            "tool_name": tool_name,
            "operation": operation
        }
    
    async def _call_adapter_tool(
        self,
        tool_name: str,
        operation: str,
        parameters: Dict[str, Any],
        integration_id: str
    ) -> Dict[str, Any]:
        """Call tool through registered adapter."""
        adapter = self.adapters[tool_name]
        
        # Add constitutional metadata
        constitutional_parameters = {
            **parameters,
            "integration_id": integration_id,
            "constitutional_oversight": self.constitutional_oversight,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            result = await adapter.execute_operation(operation, constitutional_parameters)
            
            # Ensure constitutional compliance in result
            if not isinstance(result, dict):
                result = {"data": result}
            
            result.update({
                "success": True,
                "adapter_used": tool_name,
                "constitutional_validated": True
            })
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "adapter_used": tool_name,
                "constitutional_validated": True
            }
    
    async def _call_server_tool(
        self,
        server_name: str,
        operation: str,
        parameters: Dict[str, Any],
        integration_id: str
    ) -> Dict[str, Any]:
        """Call tool through MCP server."""
        server_url = self.server_urls[server_name]
        
        # Prepare MCP request
        mcp_request = {
            "jsonrpc": "2.0",
            "id": integration_id,
            "method": "tools/call",
            "params": {
                "name": operation,
                "arguments": {
                    **parameters,
                    "integration_id": integration_id,
                    "constitutional_oversight": self.constitutional_oversight
                }
            }
        }
        
        try:
            response = await self.http_client.post(
                f"{server_url}/mcp",
                json=mcp_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if "error" in result:
                    return {
                        "success": False,
                        "error": result["error"],
                        "server_used": server_name
                    }
                
                return {
                    "success": True,
                    "data": result.get("result", {}),
                    "server_used": server_name,
                    "constitutional_validated": True
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "server_used": server_name
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "server_used": server_name
            }
    
    async def _resolve_and_call_tool(
        self,
        tool_name: str,
        operation: str,
        parameters: Dict[str, Any],
        integration_id: str
    ) -> Dict[str, Any]:
        """Attempt to resolve and call unknown tool."""
        
        # Check tool registry
        if tool_name in self.tool_registry:
            tool_info = self.tool_registry[tool_name]
            server_name = tool_info["server"]
            return await self._call_server_tool(server_name, operation, parameters, integration_id)
        
        # Try common adapter patterns
        adapter_patterns = [
            f"{tool_name}_adapter",
            f"{tool_name}_mcp_server",
            f"generic_{tool_name}",
            "generic_adapter_server"
        ]
        
        for pattern in adapter_patterns:
            if pattern in self.adapters:
                return await self._call_adapter_tool(pattern, operation, parameters, integration_id)
            elif pattern in self.server_urls:
                return await self._call_server_tool(pattern, operation, parameters, integration_id)
        
        return {
            "success": False,
            "error": f"Tool '{tool_name}' not found in registered adapters or servers",
            "available_tools": list(self.adapters.keys()) + list(self.server_urls.keys())
        }
    
    async def _discover_server_tools(
        self,
        server_name: str,
        server_url: str,
        capabilities: List[str]
    ) -> None:
        """Discover tools available from MCP server."""
        try:
            # Request tool list from server
            discovery_request = {
                "jsonrpc": "2.0",
                "id": f"discover_{uuid.uuid4().hex[:8]}",
                "method": "tools/list",
                "params": {}
            }
            
            response = await self.http_client.post(
                f"{server_url}/mcp",
                json=discovery_request
            )
            
            if response.status_code == 200:
                result = response.json()
                tools = result.get("result", {}).get("tools", [])
                
                for tool in tools:
                    tool_name = tool.get("name")
                    if tool_name:
                        self.tool_registry[tool_name] = {
                            "server": server_name,
                            "capabilities": capabilities,
                            "description": tool.get("description", ""),
                            "schema": tool.get("inputSchema", {})
                        }
                
                await self.logfire_logger.info(
                    "Discovered MCP server tools",
                    server_name=server_name,
                    tools_count=len(tools)
                )
                
        except Exception as e:
            await self.logfire_logger.warning(
                "Failed to discover MCP server tools",
                server_name=server_name,
                error=str(e)
            )
    
    async def get_integration_statistics(self) -> Dict[str, Any]:
        """Get integration statistics for parliamentary oversight."""
        total_integrations = len(self.integration_history)
        successful_integrations = len([r for r in self.integration_history if r.get("success", False)])
        
        constitutional_validated = len([
            r for r in self.integration_history if r.get("constitutional_validation", False)
        ])
        
        # Calculate average execution time
        execution_times = [
            r.get("execution_time_seconds", 0) 
            for r in self.integration_history 
            if r.get("execution_time_seconds")
        ]
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        return {
            "total_integrations": total_integrations,
            "successful_integrations": successful_integrations,
            "success_rate": successful_integrations / max(total_integrations, 1),
            "constitutional_validation_rate": constitutional_validated / max(total_integrations, 1),
            "average_execution_time_seconds": avg_execution_time,
            "active_integrations": len(self.active_integrations),
            "registered_adapters": len(self.adapters),
            "registered_servers": len(self.server_urls),
            "constitutional_violations": len(self.constitutional_violations),
            "parliamentary_accountability": True
        }
    
    async def close(self) -> None:
        """Clean shutdown of MCP client."""
        # Close all adapters
        for adapter in self.adapters.values():
            try:
                if hasattr(adapter, "close"):
                    await adapter.close()
            except Exception as e:
                await self.logfire_logger.warning(
                    "Error closing MCP adapter",
                    error=str(e)
                )
        
        # Close HTTP client
        await self.http_client.aclose()
        
        # Clear state
        self.adapters.clear()
        self.server_urls.clear()
        self.tool_registry.clear()
        self.active_integrations.clear()
        
        await self.logfire_logger.info("MCP client shutdown completed")