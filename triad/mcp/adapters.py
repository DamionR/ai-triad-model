"""
MCP System Adapters

Adapters for integrating with various external systems
while maintaining Westminster constitutional oversight.
"""

from typing import Dict, Any, List, Optional, Protocol
from abc import ABC, abstractmethod
from datetime import datetime, timezone
import asyncio
import json
import uuid
import logfire


class SystemAdapter(Protocol):
    """Protocol for system adapters with constitutional requirements."""
    
    supports_audit_trail: bool
    
    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize adapter with constitutional configuration."""
        ...
    
    async def execute_operation(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute operation with constitutional oversight."""
        ...
    
    async def validate_operation(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate operation for constitutional compliance."""
        ...
    
    async def audit_trail(self, operation: str, parameters: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Record operation in audit trail."""
        ...


class BaseSystemAdapter(ABC):
    """
    Base system adapter with constitutional compliance.
    
    Provides common functionality for all system adapters
    including audit trails and constitutional oversight.
    """
    
    supports_audit_trail = True
    
    def __init__(self, system_name: str, logfire_logger: logfire):
        self.system_name = system_name
        self.logfire_logger = logfire_logger
        self.constitutional_oversight = True
        self.parliamentary_accountability = True
        
        # Audit trail storage
        self.audit_records: List[Dict[str, Any]] = []
        self.operation_count = 0
        self.error_count = 0
        
        # Constitutional safeguards
        self.dangerous_operations = ["delete", "drop", "truncate", "destroy"]
        self.requires_approval = ["update", "modify", "change", "create"]
    
    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize adapter with constitutional configuration."""
        self.constitutional_oversight = config.get("constitutional_oversight", True)
        self.parliamentary_accountability = config.get("parliamentary_accountability", True)
        
        await self.logfire_logger.info(
            "System adapter initialized",
            system_name=self.system_name,
            constitutional_oversight=self.constitutional_oversight
        )
        
        # Perform system-specific initialization
        await self._system_initialize(config)
    
    @abstractmethod
    async def _system_initialize(self, config: Dict[str, Any]) -> None:
        """System-specific initialization."""
        pass
    
    async def execute_operation(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute operation with constitutional oversight."""
        operation_id = f"op_{uuid.uuid4().hex[:8]}"
        start_time = datetime.now(timezone.utc)
        
        with logfire.span("system_adapter_operation") as span:
            span.set_attribute("system_name", self.system_name)
            span.set_attribute("operation", operation)
            span.set_attribute("operation_id", operation_id)
            
            try:
                # Constitutional validation
                if self.constitutional_oversight:
                    validation_result = await self.validate_operation(operation, parameters)
                    if not validation_result["compliant"]:
                        result = {
                            "success": False,
                            "error": "Constitutional compliance failure",
                            "violations": validation_result["violations"],
                            "operation_id": operation_id
                        }
                        
                        await self.audit_trail(operation, parameters, result)
                        return result
                
                # Execute system-specific operation
                result = await self._execute_system_operation(operation, parameters)
                
                # Ensure result format
                if not isinstance(result, dict):
                    result = {"data": result}
                
                result.update({
                    "success": result.get("success", True),
                    "operation_id": operation_id,
                    "system_name": self.system_name,
                    "constitutional_validated": self.constitutional_oversight,
                    "execution_time_seconds": (datetime.now(timezone.utc) - start_time).total_seconds()
                })
                
                self.operation_count += 1
                
                await self.logfire_logger.info(
                    "System operation completed",
                    system_name=self.system_name,
                    operation=operation,
                    operation_id=operation_id,
                    success=result["success"]
                )
                
                # Record in audit trail
                await self.audit_trail(operation, parameters, result)
                
                return result
                
            except Exception as e:
                self.error_count += 1
                error_result = {
                    "success": False,
                    "error": str(e),
                    "operation_id": operation_id,
                    "system_name": self.system_name,
                    "constitutional_validated": self.constitutional_oversight
                }
                
                await self.logfire_logger.error(
                    "System operation failed",
                    system_name=self.system_name,
                    operation=operation,
                    operation_id=operation_id,
                    error=str(e)
                )
                
                await self.audit_trail(operation, parameters, error_result)
                return error_result
    
    @abstractmethod
    async def _execute_system_operation(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute system-specific operation."""
        pass
    
    async def validate_operation(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate operation for constitutional compliance."""
        violations = []
        
        # Check for dangerous operations
        if operation.lower() in self.dangerous_operations:
            if not parameters.get("ministerial_approval", False):
                violations.append(f"Dangerous operation '{operation}' requires ministerial approval")
        
        # Check for operations requiring approval
        if operation.lower() in self.requires_approval:
            if not parameters.get("audit_trail", True):
                violations.append(f"Operation '{operation}' requires audit trail")
        
        # Check requesting agent
        if not parameters.get("requesting_agent"):
            violations.append("Operation must identify requesting agent for accountability")
        
        # System-specific validation
        additional_violations = await self._validate_system_operation(operation, parameters)
        violations.extend(additional_violations)
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "operation": operation,
            "system_name": self.system_name
        }
    
    async def _validate_system_operation(self, operation: str, parameters: Dict[str, Any]) -> List[str]:
        """System-specific validation. Override in subclasses."""
        return []
    
    async def audit_trail(self, operation: str, parameters: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Record operation in audit trail."""
        audit_record = {
            "audit_id": f"audit_{uuid.uuid4().hex[:8]}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system_name": self.system_name,
            "operation": operation,
            "parameters": self._sanitize_parameters(parameters),
            "result": {
                "success": result.get("success", False),
                "operation_id": result.get("operation_id"),
                "error": result.get("error")
            },
            "requesting_agent": parameters.get("requesting_agent", "unknown"),
            "constitutional_oversight": self.constitutional_oversight,
            "parliamentary_accountability": self.parliamentary_accountability
        }
        
        self.audit_records.append(audit_record)
        
        # Limit audit record size
        if len(self.audit_records) > 1000:
            self.audit_records = self.audit_records[-500:]
        
        await self.logfire_logger.info(
            "Operation recorded in audit trail",
            audit_id=audit_record["audit_id"],
            system_name=self.system_name,
            operation=operation
        )
    
    def _sanitize_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from parameters before logging."""
        sanitized = parameters.copy()
        
        # Remove common sensitive fields
        sensitive_fields = ["password", "token", "key", "secret", "credential", "auth"]
        
        for field in sensitive_fields:
            for key in list(sanitized.keys()):
                if field.lower() in key.lower():
                    sanitized[key] = "[REDACTED]"
        
        return sanitized
    
    async def get_audit_records(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        operation: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get audit records for parliamentary oversight."""
        filtered_records = self.audit_records
        
        # Apply filters
        if start_date:
            filtered_records = [
                r for r in filtered_records
                if datetime.fromisoformat(r["timestamp"]) >= start_date
            ]
        
        if end_date:
            filtered_records = [
                r for r in filtered_records
                if datetime.fromisoformat(r["timestamp"]) <= end_date
            ]
        
        if operation:
            filtered_records = [
                r for r in filtered_records
                if r["operation"] == operation
            ]
        
        return filtered_records
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get adapter statistics for monitoring."""
        success_rate = 0.0
        if self.operation_count > 0:
            success_count = self.operation_count - self.error_count
            success_rate = success_count / self.operation_count
        
        return {
            "system_name": self.system_name,
            "operation_count": self.operation_count,
            "error_count": self.error_count,
            "success_rate": success_rate,
            "audit_records_count": len(self.audit_records),
            "constitutional_oversight": self.constitutional_oversight,
            "parliamentary_accountability": self.parliamentary_accountability
        }


class LegacyDatabaseAdapter(BaseSystemAdapter):
    """
    Adapter for legacy database systems.
    
    Provides constitutional oversight for database operations
    while maintaining compatibility with legacy systems.
    """
    
    def __init__(self, database_config: Dict[str, Any], logfire_logger: logfire):
        super().__init__("legacy_database", logfire_logger)
        self.database_config = database_config
        self.connection_pool = None
        self.read_only_mode = database_config.get("read_only", False)
    
    async def _system_initialize(self, config: Dict[str, Any]) -> None:
        """Initialize database connection with constitutional safeguards."""
        # Initialize connection pool (simulated)
        self.connection_pool = {
            "host": self.database_config.get("host", "localhost"),
            "database": self.database_config.get("database", "legacy_db"),
            "read_only": self.read_only_mode,
            "constitutional_oversight": True
        }
        
        await self.logfire_logger.info(
            "Legacy database adapter initialized",
            host=self.connection_pool["host"],
            database=self.connection_pool["database"],
            read_only=self.read_only_mode
        )
    
    async def _execute_system_operation(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute database operation with constitutional oversight."""
        
        if operation == "query":
            return await self._execute_query(parameters)
        elif operation == "update":
            if self.read_only_mode:
                return {
                    "success": False,
                    "error": "Database is in read-only mode for constitutional protection"
                }
            return await self._execute_update(parameters)
        elif operation == "insert":
            if self.read_only_mode:
                return {
                    "success": False,
                    "error": "Database is in read-only mode for constitutional protection"
                }
            return await self._execute_insert(parameters)
        else:
            return {
                "success": False,
                "error": f"Unsupported database operation: {operation}"
            }
    
    async def _execute_query(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute database query."""
        query = parameters.get("query", "")
        query_parameters = parameters.get("parameters", {})
        
        # Simulate query execution
        await asyncio.sleep(0.1)  # Simulate DB latency
        
        # Return simulated results
        return {
            "success": True,
            "data": {
                "rows": [
                    {"id": 1, "name": "Example Record 1", "status": "active"},
                    {"id": 2, "name": "Example Record 2", "status": "inactive"}
                ],
                "row_count": 2,
                "query": query,
                "execution_time_ms": 100
            }
        }
    
    async def _execute_update(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute database update with backup."""
        table = parameters.get("table", "")
        updates = parameters.get("updates", {})
        conditions = parameters.get("conditions", {})
        
        # Constitutional safeguard: backup before update
        if parameters.get("backup_original", True):
            backup_result = await self._create_backup(table, conditions)
            if not backup_result["success"]:
                return backup_result
        
        # Simulate update execution
        await asyncio.sleep(0.2)
        
        return {
            "success": True,
            "data": {
                "updated_rows": 1,
                "table": table,
                "updates": updates,
                "backup_created": parameters.get("backup_original", True)
            }
        }
    
    async def _execute_insert(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute database insert."""
        table = parameters.get("table", "")
        data = parameters.get("data", {})
        
        # Simulate insert execution
        await asyncio.sleep(0.1)
        
        return {
            "success": True,
            "data": {
                "inserted_id": 123,
                "table": table,
                "inserted_data": data
            }
        }
    
    async def _create_backup(self, table: str, conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Create backup before modifications."""
        backup_id = f"backup_{uuid.uuid4().hex[:8]}"
        
        # Simulate backup creation
        await asyncio.sleep(0.1)
        
        return {
            "success": True,
            "backup_id": backup_id,
            "table": table,
            "conditions": conditions,
            "backup_location": f"/backups/{backup_id}.sql"
        }
    
    async def _validate_system_operation(self, operation: str, parameters: Dict[str, Any]) -> List[str]:
        """Validate database-specific operations."""
        violations = []
        
        if operation in ["update", "delete"]:
            if not parameters.get("conditions"):
                violations.append("Update/delete operations must include WHERE conditions to prevent accidental mass changes")
        
        if operation == "query":
            query = parameters.get("query", "").lower()
            if any(dangerous in query for dangerous in ["drop", "truncate", "alter"]):
                violations.append("Query contains potentially dangerous DDL operations")
        
        return violations


class APIAdapter(BaseSystemAdapter):
    """
    Adapter for external API integrations.
    
    Provides constitutional oversight for API calls
    with rate limiting and error handling.
    """
    
    def __init__(self, api_config: Dict[str, Any], logfire_logger: logfire):
        super().__init__("external_api", logfire_logger)
        self.api_config = api_config
        self.base_url = api_config.get("base_url", "")
        self.api_key = api_config.get("api_key", "")
        self.rate_limit = api_config.get("rate_limit", 100)  # requests per minute
        
        # Rate limiting tracking
        self.request_count = 0
        self.rate_limit_window_start = datetime.now(timezone.utc)
    
    async def _system_initialize(self, config: Dict[str, Any]) -> None:
        """Initialize API adapter with constitutional configuration."""
        if not self.base_url:
            raise ValueError("API base URL is required")
        
        await self.logfire_logger.info(
            "API adapter initialized",
            base_url=self.base_url,
            rate_limit=self.rate_limit
        )
    
    async def _execute_system_operation(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute API operation with rate limiting."""
        
        # Check rate limit
        if not await self._check_rate_limit():
            return {
                "success": False,
                "error": "Rate limit exceeded",
                "rate_limit": self.rate_limit,
                "retry_after_seconds": 60
            }
        
        if operation == "get":
            return await self._execute_get(parameters)
        elif operation == "post":
            return await self._execute_post(parameters)
        elif operation == "put":
            return await self._execute_put(parameters)
        elif operation == "delete":
            return await self._execute_delete(parameters)
        else:
            return {
                "success": False,
                "error": f"Unsupported API operation: {operation}"
            }
    
    async def _check_rate_limit(self) -> bool:
        """Check if request is within rate limit."""
        current_time = datetime.now(timezone.utc)
        
        # Reset counter if window has passed
        if (current_time - self.rate_limit_window_start).total_seconds() >= 60:
            self.request_count = 0
            self.rate_limit_window_start = current_time
        
        if self.request_count >= self.rate_limit:
            return False
        
        self.request_count += 1
        return True
    
    async def _execute_get(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute GET request."""
        endpoint = parameters.get("endpoint", "")
        query_params = parameters.get("params", {})
        
        # Simulate API call
        await asyncio.sleep(0.2)
        
        return {
            "success": True,
            "data": {
                "endpoint": endpoint,
                "params": query_params,
                "response": {"status": "success", "data": "API response data"},
                "status_code": 200
            }
        }
    
    async def _execute_post(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute POST request."""
        endpoint = parameters.get("endpoint", "")
        payload = parameters.get("data", {})
        
        # Simulate API call
        await asyncio.sleep(0.3)
        
        return {
            "success": True,
            "data": {
                "endpoint": endpoint,
                "payload": payload,
                "response": {"status": "created", "id": 12345},
                "status_code": 201
            }
        }
    
    async def _execute_put(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute PUT request."""
        endpoint = parameters.get("endpoint", "")
        payload = parameters.get("data", {})
        
        # Simulate API call
        await asyncio.sleep(0.3)
        
        return {
            "success": True,
            "data": {
                "endpoint": endpoint,
                "payload": payload,
                "response": {"status": "updated"},
                "status_code": 200
            }
        }
    
    async def _execute_delete(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute DELETE request with additional safeguards."""
        endpoint = parameters.get("endpoint", "")
        
        # Additional constitutional safeguard for DELETE
        if not parameters.get("confirm_delete", False):
            return {
                "success": False,
                "error": "DELETE operations require explicit confirmation for constitutional protection"
            }
        
        # Simulate API call
        await asyncio.sleep(0.2)
        
        return {
            "success": True,
            "data": {
                "endpoint": endpoint,
                "response": {"status": "deleted"},
                "status_code": 204
            }
        }
    
    async def _validate_system_operation(self, operation: str, parameters: Dict[str, Any]) -> List[str]:
        """Validate API-specific operations."""
        violations = []
        
        if not parameters.get("endpoint"):
            violations.append("API operations must specify endpoint")
        
        if operation == "delete":
            if not parameters.get("confirm_delete", False):
                violations.append("DELETE operations require explicit confirmation")
        
        # Check for sensitive data in logs
        if "password" in str(parameters).lower() or "secret" in str(parameters).lower():
            violations.append("Parameters may contain sensitive data that should be redacted")
        
        return violations


class FileSystemAdapter(BaseSystemAdapter):
    """
    Adapter for file system operations.
    
    Provides constitutional oversight for file operations
    with backup and audit capabilities.
    """
    
    def __init__(self, fs_config: Dict[str, Any], logfire_logger: logfire):
        super().__init__("file_system", logfire_logger)
        self.fs_config = fs_config
        self.base_path = fs_config.get("base_path", "/tmp/triad")
        self.read_only = fs_config.get("read_only", False)
        self.backup_enabled = fs_config.get("backup_enabled", True)
    
    async def _system_initialize(self, config: Dict[str, Any]) -> None:
        """Initialize file system adapter."""
        await self.logfire_logger.info(
            "File system adapter initialized",
            base_path=self.base_path,
            read_only=self.read_only,
            backup_enabled=self.backup_enabled
        )
    
    async def _execute_system_operation(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file system operation."""
        
        if operation == "read":
            return await self._read_file(parameters)
        elif operation == "write":
            if self.read_only:
                return {
                    "success": False,
                    "error": "File system is in read-only mode"
                }
            return await self._write_file(parameters)
        elif operation == "delete":
            if self.read_only:
                return {
                    "success": False,
                    "error": "File system is in read-only mode"
                }
            return await self._delete_file(parameters)
        elif operation == "list":
            return await self._list_files(parameters)
        else:
            return {
                "success": False,
                "error": f"Unsupported file system operation: {operation}"
            }
    
    async def _read_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Read file contents."""
        file_path = parameters.get("path", "")
        
        # Simulate file read
        await asyncio.sleep(0.1)
        
        return {
            "success": True,
            "data": {
                "path": file_path,
                "content": "Simulated file content",
                "size_bytes": 1024,
                "last_modified": datetime.now(timezone.utc).isoformat()
            }
        }
    
    async def _write_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Write file with backup."""
        file_path = parameters.get("path", "")
        content = parameters.get("content", "")
        
        # Create backup if enabled
        if self.backup_enabled and parameters.get("backup_original", True):
            backup_result = await self._backup_file(file_path)
            if not backup_result["success"]:
                return backup_result
        
        # Simulate file write
        await asyncio.sleep(0.2)
        
        return {
            "success": True,
            "data": {
                "path": file_path,
                "bytes_written": len(content),
                "backup_created": self.backup_enabled
            }
        }
    
    async def _delete_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Delete file with backup."""
        file_path = parameters.get("path", "")
        
        # Create backup before deletion
        if self.backup_enabled:
            backup_result = await self._backup_file(file_path)
            if not backup_result["success"]:
                return backup_result
        
        # Simulate file deletion
        await asyncio.sleep(0.1)
        
        return {
            "success": True,
            "data": {
                "path": file_path,
                "deleted": True,
                "backup_created": self.backup_enabled
            }
        }
    
    async def _list_files(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """List files in directory."""
        directory = parameters.get("path", "")
        
        # Simulate directory listing
        await asyncio.sleep(0.1)
        
        return {
            "success": True,
            "data": {
                "directory": directory,
                "files": [
                    {"name": "file1.txt", "size": 1024, "type": "file"},
                    {"name": "file2.json", "size": 2048, "type": "file"},
                    {"name": "subdirectory", "size": 0, "type": "directory"}
                ]
            }
        }
    
    async def _backup_file(self, file_path: str) -> Dict[str, Any]:
        """Create backup of file."""
        backup_id = f"backup_{uuid.uuid4().hex[:8]}"
        
        # Simulate backup creation
        await asyncio.sleep(0.1)
        
        return {
            "success": True,
            "backup_id": backup_id,
            "original_path": file_path,
            "backup_path": f"/backups/{backup_id}_{file_path.split('/')[-1]}"
        }
    
    async def _validate_system_operation(self, operation: str, parameters: Dict[str, Any]) -> List[str]:
        """Validate file system operations."""
        violations = []
        
        file_path = parameters.get("path", "")
        
        # Check for dangerous paths
        dangerous_paths = ["/etc", "/bin", "/usr/bin", "/system"]
        if any(dangerous in file_path for dangerous in dangerous_paths):
            violations.append(f"Operation on dangerous system path: {file_path}")
        
        # Check for path traversal
        if ".." in file_path:
            violations.append("Path traversal detected in file path")
        
        if operation == "delete":
            if not parameters.get("confirm_delete", False):
                violations.append("File deletion requires explicit confirmation")
        
        return violations