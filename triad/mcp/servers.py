"""
MCP Servers Implementation

MCP servers for specialized functionality with Westminster constitutional
oversight and parliamentary accountability.
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
    Base MCP server with constitutional compliance.
    
    Provides common functionality for all MCP servers including
    constitutional oversight and parliamentary accountability.
    """
    
    def __init__(self, server_name: str, logfire_logger: logfire):
        self.server_name = server_name
        self.logfire_logger = logfire_logger
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.resources: Dict[str, Dict[str, Any]] = {}
        
        # Constitutional settings
        self.constitutional_oversight = True
        self.parliamentary_accountability = True
        
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
        """Initialize MCP server with constitutional configuration."""
        self.constitutional_oversight = config.get("constitutional_oversight", True)
        self.parliamentary_accountability = config.get("parliamentary_accountability", True)
        
        await self._server_initialize(config)
        self.initialized = True
        
        await self.logfire_logger.info(
            "MCP server initialized",
            server_name=self.server_name,
            tools_count=len(self.tools),
            constitutional_oversight=self.constitutional_oversight
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
        """Handle tool call with constitutional oversight."""
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
                
                # Constitutional validation
                if self.constitutional_oversight:
                    validation_result = await self._validate_tool_call(tool_name, arguments)
                    if not validation_result["compliant"]:
                        return {
                            "success": False,
                            "error": "Constitutional compliance failure",
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
        """Validate tool call for constitutional compliance."""
        violations = []
        
        # Check for required arguments
        tool_spec = self.tools.get(tool_name, {})
        required_args = tool_spec.get("required_arguments", [])
        
        for arg in required_args:
            if arg not in arguments:
                violations.append(f"Missing required argument: {arg}")
        
        # Check for constitutional requirements
        if not arguments.get("constitutional_validation", True):
            violations.append("Tool call must include constitutional validation")
        
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
            "constitutional_oversight": True
        }
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available tools."""
        return {
            "tools": list(self.tools.values()),
            "server_name": self.server_name,
            "constitutional_oversight": self.constitutional_oversight
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
            "constitutional_oversight": self.constitutional_oversight
        }


class ValidationServer(MCPServer):
    """
    MCP server for validation tools.
    
    Provides tools for validating data, configurations,
    and compliance with constitutional requirements.
    """
    
    def __init__(self, logfire_logger: logfire):
        super().__init__("validation_server", logfire_logger)
        self.validation_cache: Dict[str, Dict[str, Any]] = {}
    
    def _register_tools(self) -> None:
        """Register validation tools."""
        
        self.register_tool(
            name="validate_data",
            description="Validate data against schema with constitutional compliance",
            input_schema={
                "type": "object",
                "properties": {
                    "data": {"type": "object", "description": "Data to validate"},
                    "schema": {"type": "object", "description": "Validation schema"},
                    "constitutional_validation": {"type": "boolean", "default": True}
                },
                "required": ["data", "schema"]
            },
            required_arguments=["data", "schema"]
        )
        
        self.register_tool(
            name="validate_configuration",
            description="Validate system configuration for compliance",
            input_schema={
                "type": "object",
                "properties": {
                    "configuration": {"type": "object", "description": "Configuration to validate"},
                    "validation_rules": {"type": "object", "description": "Validation rules"},
                    "constitutional_validation": {"type": "boolean", "default": True}
                },
                "required": ["configuration"]
            },
            required_arguments=["configuration"]
        )
        
        self.register_tool(
            name="validate_constitutional_compliance",
            description="Validate action for constitutional compliance",
            input_schema={
                "type": "object",
                "properties": {
                    "action": {"type": "object", "description": "Action to validate"},
                    "agent": {"type": "string", "description": "Agent performing action"},
                    "constitutional_principles": {"type": "array", "description": "Applicable principles"}
                },
                "required": ["action", "agent"]
            },
            required_arguments=["action", "agent"]
        )
    
    async def _server_initialize(self, config: Dict[str, Any]) -> None:
        """Initialize validation server."""
        # Load validation schemas and rules
        self.validation_schemas = config.get("validation_schemas", {})
        self.constitutional_rules = config.get("constitutional_rules", {})
        
        await self.logfire_logger.info(
            "Validation server initialized",
            schemas_count=len(self.validation_schemas),
            constitutional_rules_count=len(self.constitutional_rules)
        )
    
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any], call_id: str) -> Dict[str, Any]:
        """Execute validation tool."""
        
        if tool_name == "validate_data":
            return await self._validate_data(arguments, call_id)
        elif tool_name == "validate_configuration":
            return await self._validate_configuration(arguments, call_id)
        elif tool_name == "validate_constitutional_compliance":
            return await self._validate_constitutional_compliance(arguments, call_id)
        else:
            return {
                "success": False,
                "error": f"Unknown validation tool: {tool_name}"
            }
    
    async def _validate_data(self, arguments: Dict[str, Any], call_id: str) -> Dict[str, Any]:
        """Validate data against schema."""
        data = arguments["data"]
        schema = arguments["schema"]
        
        # Simulate data validation
        await asyncio.sleep(0.1)
        
        validation_errors = []
        
        # Simple validation logic
        if "required" in schema:
            for field in schema["required"]:
                if field not in data:
                    validation_errors.append(f"Missing required field: {field}")
        
        if "properties" in schema:
            for field, field_schema in schema["properties"].items():
                if field in data:
                    field_type = field_schema.get("type")
                    if field_type == "string" and not isinstance(data[field], str):
                        validation_errors.append(f"Field {field} must be string")
                    elif field_type == "number" and not isinstance(data[field], (int, float)):
                        validation_errors.append(f"Field {field} must be number")
        
        # Cache validation result
        cache_key = f"data_validation_{call_id}"
        self.validation_cache[cache_key] = {
            "data": data,
            "schema": schema,
            "errors": validation_errors,
            "valid": len(validation_errors) == 0,
            "validated_at": datetime.now(timezone.utc).isoformat()
        }
        
        return {
            "success": True,
            "data": {
                "valid": len(validation_errors) == 0,
                "errors": validation_errors,
                "call_id": call_id,
                "validation_type": "data_schema"
            }
        }
    
    async def _validate_configuration(self, arguments: Dict[str, Any], call_id: str) -> Dict[str, Any]:
        """Validate system configuration."""
        configuration = arguments["configuration"]
        validation_rules = arguments.get("validation_rules", {})
        
        # Simulate configuration validation
        await asyncio.sleep(0.2)
        
        validation_errors = []
        warnings = []
        
        # Check for required configuration keys
        required_keys = validation_rules.get("required_keys", [])
        for key in required_keys:
            if key not in configuration:
                validation_errors.append(f"Missing required configuration key: {key}")
        
        # Check for dangerous configurations
        if configuration.get("debug_mode", False):
            warnings.append("Debug mode enabled in production")
        
        if not configuration.get("constitutional_oversight", True):
            validation_errors.append("Constitutional oversight cannot be disabled")
        
        return {
            "success": True,
            "data": {
                "valid": len(validation_errors) == 0,
                "errors": validation_errors,
                "warnings": warnings,
                "call_id": call_id,
                "validation_type": "configuration"
            }
        }
    
    async def _validate_constitutional_compliance(self, arguments: Dict[str, Any], call_id: str) -> Dict[str, Any]:
        """Validate constitutional compliance."""
        action = arguments["action"]
        agent = arguments["agent"]
        principles = arguments.get("constitutional_principles", [])
        
        # Simulate constitutional validation
        await asyncio.sleep(0.1)
        
        violations = []
        
        # Check agent authority
        authority_map = {
            "planner_agent": ["planning", "policy"],
            "executor_agent": ["execution", "implementation"],
            "evaluator_agent": ["validation", "compliance"],
            "overwatch_agent": ["monitoring", "oversight"]
        }
        
        allowed_actions = authority_map.get(agent, [])
        action_type = action.get("type", "unknown")
        
        if action_type not in allowed_actions and action_type not in ["query", "status"]:
            violations.append(f"Agent {agent} lacks authority for action type {action_type}")
        
        # Check separation of powers
        if agent == "planner_agent" and action_type == "execution":
            violations.append("Legislative branch cannot execute actions directly")
        
        return {
            "success": True,
            "data": {
                "constitutional_compliant": len(violations) == 0,
                "violations": violations,
                "principles_checked": principles,
                "call_id": call_id,
                "validation_type": "constitutional_compliance"
            }
        }


class MonitoringServer(MCPServer):
    """
    MCP server for monitoring and observability tools.
    
    Provides tools for system monitoring, health checks,
    and performance analysis with constitutional oversight.
    """
    
    def __init__(self, logfire_logger: logfire):
        super().__init__("monitoring_server", logfire_logger)
        self.metrics_storage: Dict[str, List[Dict[str, Any]]] = {}
        self.alert_thresholds: Dict[str, float] = {}
    
    def _register_tools(self) -> None:
        """Register monitoring tools."""
        
        self.register_tool(
            name="collect_metrics",
            description="Collect system metrics with constitutional oversight",
            input_schema={
                "type": "object",
                "properties": {
                    "metric_types": {"type": "array", "description": "Types of metrics to collect"},
                    "time_window": {"type": "string", "description": "Time window for metrics"},
                    "constitutional_validation": {"type": "boolean", "default": True}
                },
                "required": ["metric_types"]
            },
            required_arguments=["metric_types"]
        )
        
        self.register_tool(
            name="health_check",
            description="Perform comprehensive system health check",
            input_schema={
                "type": "object",
                "properties": {
                    "components": {"type": "array", "description": "Components to check"},
                    "deep_check": {"type": "boolean", "description": "Perform deep health check"},
                    "constitutional_validation": {"type": "boolean", "default": True}
                }
            }
        )
        
        self.register_tool(
            name="analyze_performance",
            description="Analyze system performance trends",
            input_schema={
                "type": "object",
                "properties": {
                    "analysis_type": {"type": "string", "description": "Type of analysis"},
                    "time_period": {"type": "string", "description": "Analysis time period"},
                    "constitutional_validation": {"type": "boolean", "default": True}
                },
                "required": ["analysis_type"]
            },
            required_arguments=["analysis_type"]
        )
    
    async def _server_initialize(self, config: Dict[str, Any]) -> None:
        """Initialize monitoring server."""
        self.alert_thresholds = config.get("alert_thresholds", {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "error_rate": 5.0,
            "response_time": 1000.0
        })
    
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any], call_id: str) -> Dict[str, Any]:
        """Execute monitoring tool."""
        
        if tool_name == "collect_metrics":
            return await self._collect_metrics(arguments, call_id)
        elif tool_name == "health_check":
            return await self._health_check(arguments, call_id)
        elif tool_name == "analyze_performance":
            return await self._analyze_performance(arguments, call_id)
        else:
            return {
                "success": False,
                "error": f"Unknown monitoring tool: {tool_name}"
            }
    
    async def _collect_metrics(self, arguments: Dict[str, Any], call_id: str) -> Dict[str, Any]:
        """Collect system metrics."""
        metric_types = arguments["metric_types"]
        time_window = arguments.get("time_window", "1h")
        
        # Simulate metrics collection
        await asyncio.sleep(0.3)
        
        collected_metrics = {}
        
        for metric_type in metric_types:
            if metric_type == "cpu_usage":
                collected_metrics["cpu_usage"] = {
                    "current": 45.2,
                    "average": 42.8,
                    "peak": 78.5,
                    "unit": "percent"
                }
            elif metric_type == "memory_usage":
                collected_metrics["memory_usage"] = {
                    "current": 512.3,
                    "average": 480.1,
                    "peak": 890.2,
                    "unit": "MB"
                }
            elif metric_type == "response_time":
                collected_metrics["response_time"] = {
                    "current": 245.6,
                    "average": 203.4,
                    "peak": 1205.8,
                    "unit": "ms"
                }
            elif metric_type == "error_rate":
                collected_metrics["error_rate"] = {
                    "current": 2.1,
                    "average": 1.8,
                    "peak": 8.3,
                    "unit": "percent"
                }
        
        # Store metrics
        storage_key = f"metrics_{call_id}"
        self.metrics_storage[storage_key] = {
            "metrics": collected_metrics,
            "time_window": time_window,
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "call_id": call_id
        }
        
        return {
            "success": True,
            "data": {
                "metrics": collected_metrics,
                "time_window": time_window,
                "collection_timestamp": datetime.now(timezone.utc).isoformat(),
                "call_id": call_id
            }
        }
    
    async def _health_check(self, arguments: Dict[str, Any], call_id: str) -> Dict[str, Any]:
        """Perform system health check."""
        components = arguments.get("components", ["database", "api", "agents", "constitutional_framework"])
        deep_check = arguments.get("deep_check", False)
        
        # Simulate health check
        await asyncio.sleep(0.5 if deep_check else 0.2)
        
        health_results = {}
        overall_health = "healthy"
        
        for component in components:
            if component == "database":
                health_results["database"] = {
                    "status": "healthy",
                    "response_time_ms": 15.2,
                    "connections": 8,
                    "max_connections": 100
                }
            elif component == "api":
                health_results["api"] = {
                    "status": "healthy",
                    "response_time_ms": 89.3,
                    "requests_per_second": 45.2,
                    "error_rate": 0.8
                }
            elif component == "agents":
                health_results["agents"] = {
                    "status": "healthy",
                    "active_agents": 4,
                    "queue_sizes": {
                        "planner_agent": 3,
                        "executor_agent": 7,
                        "evaluator_agent": 2,
                        "overwatch_agent": 1
                    }
                }
            elif component == "constitutional_framework":
                health_results["constitutional_framework"] = {
                    "status": "healthy",
                    "compliance_score": 0.98,
                    "active_violations": 0,
                    "parliamentary_session": "active"
                }
        
        # Check for any unhealthy components
        if any(result.get("status") != "healthy" for result in health_results.values()):
            overall_health = "degraded"
        
        return {
            "success": True,
            "data": {
                "overall_health": overall_health,
                "component_health": health_results,
                "check_type": "deep" if deep_check else "standard",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "call_id": call_id
            }
        }
    
    async def _analyze_performance(self, arguments: Dict[str, Any], call_id: str) -> Dict[str, Any]:
        """Analyze system performance trends."""
        analysis_type = arguments["analysis_type"]
        time_period = arguments.get("time_period", "24h")
        
        # Simulate performance analysis
        await asyncio.sleep(0.4)
        
        analysis_results = {}
        
        if analysis_type == "throughput":
            analysis_results = {
                "metric": "throughput",
                "current_rps": 125.3,
                "trend": "stable",
                "peak_rps": 234.7,
                "average_rps": 118.9,
                "recommendations": [
                    "Throughput is within normal parameters",
                    "Consider scaling if peak exceeds 300 RPS"
                ]
            }
        elif analysis_type == "latency":
            analysis_results = {
                "metric": "latency",
                "current_p95_ms": 245.6,
                "trend": "improving",
                "peak_p95_ms": 890.2,
                "average_p95_ms": 203.4,
                "recommendations": [
                    "Latency trends are improving",
                    "Monitor for any spikes above 500ms"
                ]
            }
        elif analysis_type == "constitutional_compliance":
            analysis_results = {
                "metric": "constitutional_compliance",
                "current_score": 0.97,
                "trend": "stable",
                "violations_per_hour": 0.2,
                "compliance_trend": "excellent",
                "recommendations": [
                    "Constitutional compliance excellent",
                    "Continue monitoring for any violations"
                ]
            }
        
        return {
            "success": True,
            "data": {
                "analysis": analysis_results,
                "time_period": time_period,
                "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
                "call_id": call_id
            }
        }


class IntegrationServer(MCPServer):
    """
    MCP server for system integration tools.
    
    Provides tools for managing external system integrations
    with constitutional oversight and parliamentary accountability.
    """
    
    def __init__(self, logfire_logger: logfire):
        super().__init__("integration_server", logfire_logger)
        self.integration_registry: Dict[str, Dict[str, Any]] = {}
        self.active_connections: Dict[str, Dict[str, Any]] = {}
    
    def _register_tools(self) -> None:
        """Register integration tools."""
        
        self.register_tool(
            name="register_integration",
            description="Register new external system integration",
            input_schema={
                "type": "object",
                "properties": {
                    "integration_name": {"type": "string", "description": "Name of integration"},
                    "system_type": {"type": "string", "description": "Type of external system"},
                    "connection_config": {"type": "object", "description": "Connection configuration"},
                    "constitutional_validation": {"type": "boolean", "default": True}
                },
                "required": ["integration_name", "system_type", "connection_config"]
            },
            required_arguments=["integration_name", "system_type", "connection_config"]
        )
        
        self.register_tool(
            name="test_integration",
            description="Test external system integration",
            input_schema={
                "type": "object",
                "properties": {
                    "integration_name": {"type": "string", "description": "Integration to test"},
                    "test_type": {"type": "string", "description": "Type of test to perform"},
                    "constitutional_validation": {"type": "boolean", "default": True}
                },
                "required": ["integration_name"]
            },
            required_arguments=["integration_name"]
        )
        
        self.register_tool(
            name="manage_connection",
            description="Manage external system connection",
            input_schema={
                "type": "object",
                "properties": {
                    "integration_name": {"type": "string", "description": "Integration name"},
                    "action": {"type": "string", "description": "Action: connect, disconnect, refresh"},
                    "constitutional_validation": {"type": "boolean", "default": True}
                },
                "required": ["integration_name", "action"]
            },
            required_arguments=["integration_name", "action"]
        )
    
    async def _server_initialize(self, config: Dict[str, Any]) -> None:
        """Initialize integration server."""
        # Load existing integrations
        self.integration_registry = config.get("existing_integrations", {})
        
        await self.logfire_logger.info(
            "Integration server initialized",
            existing_integrations=len(self.integration_registry)
        )
    
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any], call_id: str) -> Dict[str, Any]:
        """Execute integration tool."""
        
        if tool_name == "register_integration":
            return await self._register_integration(arguments, call_id)
        elif tool_name == "test_integration":
            return await self._test_integration(arguments, call_id)
        elif tool_name == "manage_connection":
            return await self._manage_connection(arguments, call_id)
        else:
            return {
                "success": False,
                "error": f"Unknown integration tool: {tool_name}"
            }
    
    async def _register_integration(self, arguments: Dict[str, Any], call_id: str) -> Dict[str, Any]:
        """Register new integration."""
        integration_name = arguments["integration_name"]
        system_type = arguments["system_type"]
        connection_config = arguments["connection_config"]
        
        # Simulate integration registration
        await asyncio.sleep(0.2)
        
        # Check if integration already exists
        if integration_name in self.integration_registry:
            return {
                "success": False,
                "error": f"Integration '{integration_name}' already exists",
                "call_id": call_id
            }
        
        # Register integration
        integration_record = {
            "integration_name": integration_name,
            "system_type": system_type,
            "connection_config": self._sanitize_config(connection_config),
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "status": "registered",
            "constitutional_oversight": True,
            "parliamentary_accountability": True
        }
        
        self.integration_registry[integration_name] = integration_record
        
        return {
            "success": True,
            "data": {
                "integration_name": integration_name,
                "system_type": system_type,
                "status": "registered",
                "constitutional_compliant": True,
                "call_id": call_id
            }
        }
    
    async def _test_integration(self, arguments: Dict[str, Any], call_id: str) -> Dict[str, Any]:
        """Test integration connectivity."""
        integration_name = arguments["integration_name"]
        test_type = arguments.get("test_type", "connectivity")
        
        # Check if integration exists
        if integration_name not in self.integration_registry:
            return {
                "success": False,
                "error": f"Integration '{integration_name}' not found",
                "call_id": call_id
            }
        
        # Simulate integration test
        await asyncio.sleep(0.3)
        
        test_results = {
            "integration_name": integration_name,
            "test_type": test_type,
            "status": "passed",
            "response_time_ms": 156.7,
            "constitutional_compliance": True,
            "test_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if test_type == "connectivity":
            test_results.update({
                "connection_status": "connected",
                "authentication": "successful",
                "permissions": "validated"
            })
        elif test_type == "performance":
            test_results.update({
                "throughput_rps": 89.2,
                "latency_p95_ms": 245.6,
                "error_rate": 0.5
            })
        
        return {
            "success": True,
            "data": test_results
        }
    
    async def _manage_connection(self, arguments: Dict[str, Any], call_id: str) -> Dict[str, Any]:
        """Manage integration connection."""
        integration_name = arguments["integration_name"]
        action = arguments["action"]
        
        # Check if integration exists
        if integration_name not in self.integration_registry:
            return {
                "success": False,
                "error": f"Integration '{integration_name}' not found",
                "call_id": call_id
            }
        
        # Simulate connection management
        await asyncio.sleep(0.2)
        
        if action == "connect":
            self.active_connections[integration_name] = {
                "connected_at": datetime.now(timezone.utc).isoformat(),
                "status": "active",
                "connection_id": f"conn_{uuid.uuid4().hex[:8]}"
            }
            
            return {
                "success": True,
                "data": {
                    "integration_name": integration_name,
                    "action": action,
                    "status": "connected",
                    "connection_id": self.active_connections[integration_name]["connection_id"],
                    "call_id": call_id
                }
            }
            
        elif action == "disconnect":
            if integration_name in self.active_connections:
                del self.active_connections[integration_name]
            
            return {
                "success": True,
                "data": {
                    "integration_name": integration_name,
                    "action": action,
                    "status": "disconnected",
                    "call_id": call_id
                }
            }
            
        elif action == "refresh":
            if integration_name in self.active_connections:
                self.active_connections[integration_name]["refreshed_at"] = datetime.now(timezone.utc).isoformat()
            
            return {
                "success": True,
                "data": {
                    "integration_name": integration_name,
                    "action": action,
                    "status": "refreshed",
                    "call_id": call_id
                }
            }
        
        else:
            return {
                "success": False,
                "error": f"Unknown action: {action}",
                "available_actions": ["connect", "disconnect", "refresh"],
                "call_id": call_id
            }
    
    def _sanitize_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from configuration."""
        sanitized = config.copy()
        
        # Remove sensitive fields
        sensitive_fields = ["password", "token", "key", "secret", "credential"]
        
        for field in sensitive_fields:
            for key in list(sanitized.keys()):
                if field.lower() in key.lower():
                    sanitized[key] = "[REDACTED]"
        
        return sanitized