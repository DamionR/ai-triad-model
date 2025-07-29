# AI Triad Model Architecture

## Overview

The AI Triad Model is built using **Pydantic AI** as the core framework for agent orchestration, implementing a **complete Westminster parliamentary system** with constitutional governance, democratic accountability, and transparent decision-making processes.

**🏛️ Constitutional AI Architecture**: Every component follows Westminster parliamentary principles including separation of powers, collective responsibility, question periods, parliamentary scrutiny, and Crown reserve powers. This ensures all AI operations maintain democratic accountability and constitutional safeguards.

**🔗 Integration-First Architecture**: Designed from the ground up to integrate seamlessly with existing organizational systems - from legacy databases and ERP systems to modern APIs and cloud services. The constitutional governance model ensures all integrations maintain accountability and transparency.

## Core Architecture

### Technology Stack
- **Pydantic AI**: Agent framework with type safety and dependency injection
- **A2A Protocol**: Agent-to-agent communication and orchestration
- **MCP (Model Context Protocol)**: **Universal integration bridge** - connects to any existing system (databases, APIs, legacy systems, cloud services)
- **Logfire**: Comprehensive observability and monitoring platform with integration tracking
- **FastAPI**: API layer for external communication and system integration
- **PostgreSQL**: Primary database for persistent data (can coexist with existing databases)

### Agent System Design

The backend implements four core agents using Pydantic AI's agent system:

```python
from pydantic_ai import Agent
from dataclasses import dataclass

@dataclass
class TriadDeps:
    db_session: DatabaseSession
    mcp_client: MCPClient
    a2a_broker: A2ABroker
    logfire_logger: LogfireLogger
    parliamentary_procedure: ParliamentaryProcedure
    constitutional_crisis_manager: ConstitutionalCrisisManager
    crown_prerogative: CrownPrerogative

# Core agents with Westminster constitutional system
planner_agent = Agent(
    'openai:gpt-4o', 
    deps_type=TriadDeps,
    system_prompt="""
    You are the Planner Agent representing the LEGISLATIVE BRANCH in the Westminster parliamentary system.
    You have the authority to create plans and policies, but you must:
    1. Respond to Question Period challenges from other agents
    2. Accept collective cabinet responsibility for all major decisions
    3. Submit to parliamentary scrutiny and oversight
    4. Respect Crown (Overwatch) constitutional authority
    5. Maintain transparency and democratic accountability
    """
)

executor_agent = Agent(
    'openai:gpt-4o', 
    deps_type=TriadDeps,
    system_prompt="""
    You are the Executor Agent representing the EXECUTIVE BRANCH in the Westminster parliamentary system.
    You have ministerial responsibility for implementation, but you must:
    1. Defend your decisions in Question Period when challenged
    2. Accept collective cabinet responsibility with other agents
    3. Submit to no-confidence votes if your performance is questioned
    4. Respect Crown (Overwatch) constitutional authority
    5. Maintain confidence and supply from the parliamentary system
    """
)

evaluator_agent = Agent(
    'anthropic:claude-3-5-sonnet-latest', 
    deps_type=TriadDeps,
    system_prompt="""
    You are the Evaluator Agent representing the JUDICIAL BRANCH in the Westminster parliamentary system.
    You have constitutional review authority, but you must:
    1. Provide impartial constitutional interpretation and validation
    2. Participate in collective cabinet responsibility for system decisions
    3. Challenge unconstitutional actions through proper parliamentary procedure
    4. Respect Crown (Overwatch) final constitutional authority
    5. Ensure all actions comply with Westminster democratic principles
    """
)

overwatch_agent = Agent(
    'openai:gpt-4o', 
    deps_type=TriadDeps,
    system_prompt="""
    You are the Overwatch Agent representing the CROWN (Governor General) in the Westminster parliamentary system.
    You have constitutional oversight and reserve powers, including:
    1. Constitutional crisis resolution and emergency powers
    2. Royal assent authority for major system decisions
    3. Power to dismiss agents or dissolve the system if necessary
    4. Final constitutional authority and interpretation
    5. Responsibility to maintain Westminster democratic principles and constitutional safeguards
    """
)

# Convert agents to A2A applications for inter-agent communication
planner_a2a = planner_agent.to_a2a()
executor_a2a = executor_agent.to_a2a()
evaluator_a2a = evaluator_agent.to_a2a()
overwatch_a2a = overwatch_agent.to_a2a()
```

## Agent Communication Flow

### A2A Protocol Implementation

The AI Triad uses the A2A protocol for structured agent-to-agent communication with persistent context and conversation threading.

### 1. Planner Agent → Executor Agent (A2A)
```python
import httpx
from pydantic_ai.a2a import TaskRequest

@planner_agent.tool
async def dispatch_workflow_a2a(ctx: RunContext[TriadDeps], workflow_plan: WorkflowPlan) -> str:
    """Dispatch workflow plan to executor agent via A2A protocol."""
    task_request = TaskRequest(
        messages=[{"role": "user", "content": f"Execute workflow: {workflow_plan.to_json()}"}],
        context_id=f"workflow_{workflow_plan.id}",
        metadata={"workflow_id": workflow_plan.id, "priority": workflow_plan.priority}
    )
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ctx.deps.a2a_broker.executor_url}/tasks",
            json=task_request.model_dump()
        )
        result = response.json()
    
    await ctx.deps.logfire_logger.info(
        "Workflow dispatched to executor",
        workflow_id=workflow_plan.id,
        task_id=result["task_id"]
    )
    
    return result["task_id"]
```

### 2. Executor Agent → Evaluator Agent (A2A)
```python
@executor_agent.tool
async def submit_for_evaluation_a2a(ctx: RunContext[TriadDeps], execution_result: ExecutionResult) -> ValidationReport:
    """Submit execution results for evaluation via A2A protocol."""
    task_request = TaskRequest(
        messages=[{"role": "user", "content": f"Validate execution: {execution_result.to_json()}"}],
        context_id=f"execution_{execution_result.task_id}",
        metadata={"execution_id": execution_result.task_id, "accuracy_threshold": 0.95}
    )
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ctx.deps.a2a_broker.evaluator_url}/tasks",
            json=task_request.model_dump()
        )
        result = response.json()
    
    # Wait for evaluation completion
    validation_result = await ctx.deps.a2a_broker.wait_for_completion(result["task_id"])
    
    await ctx.deps.logfire_logger.info(
        "Execution submitted for evaluation",
        execution_id=execution_result.task_id,
        validation_task_id=result["task_id"]
    )
    
    return ValidationReport.model_validate(validation_result["output"])
```

### 3. Evaluator Agent → Planner Agent (A2A Feedback)
```python
@evaluator_agent.tool
async def provide_feedback_a2a(ctx: RunContext[TriadDeps], validation_report: ValidationReport) -> str:
    """Provide feedback to planner via A2A protocol."""
    task_request = TaskRequest(
        messages=[{"role": "user", "content": f"Process validation feedback: {validation_report.to_json()}"}],
        context_id=f"feedback_{validation_report.task_id}",
        metadata={"feedback_type": "validation", "accuracy_score": validation_report.accuracy_score}
    )
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ctx.deps.a2a_broker.planner_url}/tasks",
            json=task_request.model_dump()
        )
        result = response.json()
    
    await ctx.deps.logfire_logger.info(
        "Feedback provided to planner",
        validation_task_id=validation_report.task_id,
        feedback_task_id=result["task_id"]
    )
    
    return f"Feedback task created: {result['task_id']}"
```

### 4. MCP Integration with Existing Systems
```python
@planner_agent.tool
async def integrate_existing_system(ctx: RunContext[TriadDeps], system_type: str, operation: str, parameters: dict) -> dict:
    """Integrate with existing organizational systems via MCP protocol."""
    
    # Map to appropriate MCP server based on existing system type
    mcp_server_mapping = {
        "legacy_database": "database_adapter_server",
        "crm_system": "salesforce_mcp_server", 
        "erp_system": "sap_mcp_server",
        "inventory_system": "inventory_mcp_server",
        "hr_system": "workday_mcp_server",
        "custom_api": "rest_api_adapter_server"
    }
    
    server_name = mcp_server_mapping.get(system_type, "generic_adapter_server")
    
    try:
        # Constitutional logging - all external integrations are tracked
        await ctx.deps.logfire_logger.info(
            "Integrating with existing system",
            system_type=system_type,
            operation=operation,
            server_name=server_name,
            constitutional_oversight=True
        )
        
        result = await ctx.deps.mcp_client.call_tool(
            server_name,
            tool_name=operation,
            parameters={
                **parameters,
                "system_type": system_type,
                "constitutional_validation": True  # Ensure compliance
            }
        )
        
        # All external system integrations must be validated
        if not result.get("validated", False):
            await ctx.deps.logfire_logger.warning(
                "External system integration requires validation",
                system_type=system_type,
                result=result
            )
            # Trigger evaluator agent for validation
            return await ctx.deps.a2a_client.send_task(
                "evaluator",
                f"Validate external system integration: {result}"
            )
        
        return result
        
    except Exception as e:
        await ctx.deps.logfire_logger.error(
            "External system integration failed",
            system_type=system_type,
            operation=operation,
            error=str(e)
        )
        raise

# Example: Legacy Database Integration
@planner_agent.tool
async def query_legacy_database(ctx: RunContext[TriadDeps], query: str, database_name: str) -> dict:
    """Query existing legacy databases through MCP adapter."""
    return await integrate_existing_system(
        ctx,
        system_type="legacy_database",
        operation="execute_query",
        parameters={
            "query": query,
            "database_name": database_name,
            "read_only": True,  # Constitutional protection
            "audit_trail": True
        }
    )

# Example: CRM System Integration  
@executor_agent.tool
async def update_crm_record(ctx: RunContext[TriadDeps], record_id: str, updates: dict) -> dict:
    """Update CRM records while maintaining constitutional oversight."""
    return await integrate_existing_system(
        ctx,
        system_type="crm_system", 
        operation="update_record",
        parameters={
            "record_id": record_id,
            "updates": updates,
            "require_approval": True,  # Constitutional check
            "backup_original": True
        }
    )
```

## Directory Structure

```
Triad-Model/
├── docs/                    # Complete system documentation
│   ├── README.md           # Main documentation overview
│   ├── architecture.md     # System architecture
│   ├── agents.md           # Agent implementations  
│   ├── tools-and-dependencies.md
│   ├── api-endpoints.md
│   ├── testing-and-deployment.md
│   ├── monitoring-and-observability.md
│   ├── evals-and-performance.md
│   └── graph-workflows-and-sub-agents.md
├── backend/                 # Core system implementation
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py         # Base agent configuration with A2A support
│   │   ├── planner.py      # Planner agent implementation
│   │   ├── executor.py     # Executor agent implementation
│   │   ├── evaluator.py    # Evaluator agent implementation
│   │   └── overwatch.py    # Overwatch monitoring agent
│   ├── a2a/
│   │   ├── __init__.py
│   │   ├── broker.py       # A2A broker implementation
│   │   ├── client.py       # A2A client for inter-agent communication
│   │   ├── storage.py      # A2A task and context storage
│   │   └── models.py       # A2A task and context models
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── client.py       # MCP client implementation
│   │   ├── servers/        # Custom MCP servers for system integration
│   │   │   ├── database_adapter.py    # Legacy database integration
│   │   │   ├── salesforce_mcp.py      # CRM system integration
│   │   │   ├── sap_mcp.py             # ERP system integration
│   │   │   ├── rest_api_adapter.py    # Generic API integration
│   │   │   ├── validation.py          # Validation tools MCP server
│   │   │   └── monitoring.py          # System monitoring MCP server
│   │   ├── adapters/       # Integration adapters for existing systems
│   │   │   ├── legacy_db_adapter.py   # Legacy database connectors
│   │   │   ├── api_gateway_adapter.py # API gateway integration
│   │   │   └── file_system_adapter.py # File system integration
│   │   └── tools.py        # MCP tool integrations
│   ├── models/
│   │   ├── __init__.py
│   │   ├── workflow.py     # Workflow data models
│   │   ├── execution.py    # Execution result models
│   │   ├── validation.py   # Validation report models
│   │   └── monitoring.py   # Monitoring data models
│   ├── dependencies/
│   │   ├── __init__.py
│   │   ├── database.py     # Database dependencies
│   │   ├── logfire.py      # Logfire observability setup
│   │   ├── a2a.py          # A2A broker dependencies
│   │   └── mcp.py          # MCP client dependencies
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── workflow_tools.py # Workflow management tools
│   │   ├── execution_tools.py # Task execution tools
│   │   ├── validation_tools.py # Validation tools
│   │   └── a2a_tools.py    # A2A communication tools
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── planner.py  # Planner API endpoints
│   │   │   ├── executor.py # Executor API endpoints
│   │   │   ├── evaluator.py # Evaluator API endpoints
│   │   │   ├── overwatch.py # Overwatch API endpoints
│   │   │   └── a2a.py      # A2A protocol endpoints
│   │   └── middleware.py   # FastAPI middleware with Logfire
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py     # Application settings
│   │   ├── logfire.py      # Logfire configuration
│   │   └── models.py       # Model configurations
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_agents.py  # Agent tests
│   │   ├── test_a2a.py     # A2A protocol tests
│   │   ├── test_mcp.py     # MCP integration tests
│   │   ├── test_tools.py   # Tool tests
│   │   └── test_api.py     # API tests
│   └── main.py             # FastAPI application entry point
├── docker-compose.yml       # Development environment
├── docker-compose.prod.yml  # Production deployment
├── Dockerfile              # Development container
├── Dockerfile.prod         # Production container
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # Project overview
```

## Key Design Patterns

### 1. Type-Safe Dependencies with Modern Stack
```python
import logfire
from pydantic_ai.a2a import A2AClient
from mcp import MCPClient

@dataclass
class TriadDeps:
    db_session: DatabaseSession
    logfire_logger: logfire.Logger
    a2a_client: A2AClient
    mcp_client: MCPClient
    
    async def log_event(self, event_type: str, data: dict):
        """Centralized event logging with Logfire."""
        await self.logfire_logger.info(
            f"Event: {event_type}",
            event_type=event_type,
            **data
        )
        
    async def communicate_with_agent(self, agent_name: str, message: str, context_id: str = None) -> dict:
        """A2A communication with other agents."""
        return await self.a2a_client.send_task(
            agent_name=agent_name,
            message=message,
            context_id=context_id
        )
        
    async def use_external_tool(self, tool_name: str, parameters: dict) -> dict:
        """MCP tool integration."""
        return await self.mcp_client.call_tool(tool_name, parameters)
```

### 2. A2A and MCP Tool Composition
```python
import logfire
from .tools import WorkflowToolset, ValidationToolset, A2AToolset, MCPToolset

# Configure Logfire instrumentation
logfire.configure()
logfire.instrument_pydantic_ai()

planner_agent = Agent(
    'openai:gpt-4o',
    deps_type=TriadDeps,
    tools=[WorkflowToolset(), A2AToolset(), MCPToolset()]
)

evaluator_agent = Agent(
    'anthropic:claude-3-5-sonnet-latest',
    deps_type=TriadDeps,
    tools=[ValidationToolset(), A2AToolset()]
)

# Convert to A2A applications for inter-agent communication
planner_a2a_app = planner_agent.to_a2a()
evaluator_a2a_app = evaluator_agent.to_a2a()
```

### 3. Output Validation with Logfire Tracing
```python
@evaluator_agent.output_validator
async def validate_evaluation_output(ctx: RunContext[TriadDeps], output: ValidationReport) -> ValidationReport:
    with logfire.span("validation_check") as span:
        span.set_attribute("accuracy_score", output.accuracy_score)
        span.set_attribute("validation_status", output.validation_status)
        
        if output.accuracy_score < 0.95:
            span.set_attribute("validation_failed", True)
            await ctx.deps.logfire_logger.warning(
                "Validation below threshold",
                accuracy_score=output.accuracy_score,
                threshold=0.95
            )
            raise ModelRetry("Accuracy score below threshold, please re-evaluate")
        
        span.set_attribute("validation_passed", True)
        await ctx.deps.logfire_logger.info(
            "Validation completed successfully",
            accuracy_score=output.accuracy_score,
            validation_id=output.task_id
        )
        
        return output
```

## Error Handling & Resilience with Logfire

### 1. Automatic Retries with Tracing
```python
@executor_agent.tool
async def execute_task(ctx: RunContext[TriadDeps], task: Task) -> ExecutionResult:
    with logfire.span("task_execution", task_id=task.id, task_type=task.type) as span:
        try:
            result = await perform_task_execution(task)
            span.set_attribute("execution_success", True)
            await ctx.deps.logfire_logger.info(
                "Task executed successfully",
                task_id=task.id,
                execution_time=result.execution_time
            )
            return result
        except ExecutionError as e:
            span.set_attribute("execution_failed", True)
            span.set_attribute("error_message", str(e))
            await ctx.deps.logfire_logger.error(
                "Task execution failed",
                task_id=task.id,
                error=str(e)
            )
            raise ModelRetry(f"Task execution failed: {e}. Please retry with different approach.")
```

### 2. A2A Communication Resilience
```python
@dataclass
class A2ABroker:
    """A2A broker with resilience patterns."""
    
    async def send_task_with_retry(self, agent_url: str, task_request: TaskRequest, max_retries: int = 3) -> dict:
        """Send A2A task with automatic retry and circuit breaker."""
        with logfire.span("a2a_communication") as span:
            span.set_attribute("target_agent", agent_url)
            span.set_attribute("task_id", task_request.context_id)
            
            for attempt in range(max_retries):
                try:
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        response = await client.post(f"{agent_url}/tasks", json=task_request.model_dump())
                        
                    if response.status_code == 200:
                        span.set_attribute("communication_success", True)
                        return response.json()
                    else:
                        span.set_attribute(f"attempt_{attempt}_failed", True)
                        
                except httpx.TimeoutException:
                    span.set_attribute(f"attempt_{attempt}_timeout", True)
                    if attempt == max_retries - 1:
                        raise A2ACommunicationError(f"Failed to communicate with {agent_url} after {max_retries} attempts")
                    
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### 3. MCP Tool Fallback
```python
@planner_agent.tool
async def use_mcp_tool_with_fallback(ctx: RunContext[TriadDeps], primary_tool: str, fallback_tool: str, parameters: dict) -> dict:
    """Use MCP tool with fallback to alternative tool."""
    with logfire.span("mcp_tool_execution") as span:
        span.set_attribute("primary_tool", primary_tool)
        span.set_attribute("fallback_tool", fallback_tool)
        
        try:
            result = await ctx.deps.mcp_client.call_tool(primary_tool, parameters)
            span.set_attribute("used_primary_tool", True)
            return result
        except Exception as e:
            span.set_attribute("primary_tool_failed", True)
            span.set_attribute("error", str(e))
            
            await ctx.deps.logfire_logger.warning(
                "Primary MCP tool failed, trying fallback",
                primary_tool=primary_tool,
                fallback_tool=fallback_tool,
                error=str(e)
            )
            
            try:
                result = await ctx.deps.mcp_client.call_tool(fallback_tool, parameters)
                span.set_attribute("used_fallback_tool", True)
                return result
            except Exception as fallback_error:
                span.set_attribute("fallback_tool_failed", True)
                await ctx.deps.logfire_logger.error(
                    "Both primary and fallback MCP tools failed",
                    primary_tool=primary_tool,
                    fallback_tool=fallback_tool,
                    primary_error=str(e),
                    fallback_error=str(fallback_error)
                )
                raise ToolExecutionError(f"Both {primary_tool} and {fallback_tool} failed")
```

## Performance Optimization with Modern Stack

### 1. A2A Concurrent Agent Operations
```python
async def process_multiple_workflows_a2a(workflows: List[Workflow], deps: TriadDeps):
    """Process multiple workflows concurrently using A2A protocol."""
    with logfire.span("batch_workflow_processing") as span:
        span.set_attribute("workflow_count", len(workflows))
        
        # Create A2A tasks for all workflows
        tasks = []
        for workflow in workflows:
            task_request = TaskRequest(
                messages=[{"role": "user", "content": f"Plan workflow: {workflow.description}"}],
                context_id=f"workflow_{workflow.id}",
                metadata={"workflow_id": workflow.id}
            )
            tasks.append(deps.a2a_client.send_task("planner", task_request))
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        span.set_attribute("successful_workflows", len([r for r in results if not isinstance(r, Exception)]))
        span.set_attribute("failed_workflows", len([r for r in results if isinstance(r, Exception)]))
        
        return results
```

### 2. Intelligent Caching with Context
```python
@planner_agent.tool
async def get_cached_plan_with_context(ctx: RunContext[TriadDeps], workflow_hash: str, context_id: str) -> Optional[WorkflowPlan]:
    """Get cached plan with A2A context awareness."""
    with logfire.span("cache_lookup") as span:
        span.set_attribute("workflow_hash", workflow_hash)
        span.set_attribute("context_id", context_id)
        
        # Check database cache table
        cache_key = f"plan:{workflow_hash}:{context_id}"
        cached = await ctx.deps.db_session.execute(
            select(CachedPlan).where(CachedPlan.cache_key == cache_key)
        )
        cached_plan = cached.scalar_one_or_none()
        
        if cached_plan and not cached_plan.is_expired():
            span.set_attribute("cache_hit", True)
            await ctx.deps.logfire_logger.info(
                "Workflow plan cache hit",
                workflow_hash=workflow_hash,
                context_id=context_id
            )
            return WorkflowPlan.model_validate_json(cached_plan.plan_data)
        
        span.set_attribute("cache_miss", True)
        return None
```

### 3. Resource Management with Logfire Monitoring
```python
@dataclass
class TriadDeps:
    db_session: DatabaseSession
    logfire_logger: logfire.Logger
    a2a_client: A2AClient
    mcp_client: MCPClient
    resource_monitor: ResourceMonitor
    
    async def monitor_resource_usage(self):
        """Monitor resource usage with Logfire."""
        with logfire.span("resource_monitoring") as span:
            cpu_usage = await self.resource_monitor.get_cpu_usage()
            memory_usage = await self.resource_monitor.get_memory_usage()
            active_connections = await self.resource_monitor.get_connection_count()
            
            span.set_attribute("cpu_usage_percent", cpu_usage)
            span.set_attribute("memory_usage_mb", memory_usage)
            span.set_attribute("active_connections", active_connections)
            
            if cpu_usage > 80 or memory_usage > 1024:
                await self.logfire_logger.warning(
                    "High resource usage detected",
                    cpu_usage=cpu_usage,
                    memory_usage=memory_usage
                )
```

## Integration Summary

This modernized architecture leverages:

- **A2A Protocol**: For structured, traceable agent-to-agent communication
- **MCP Integration**: For external tool access and extensibility  
- **Logfire Observability**: For comprehensive monitoring, tracing, and debugging
- **Type Safety**: Maintained throughout with Pydantic AI's framework
- **Production Readiness**: Built-in resilience, caching, and performance optimization

The system provides a robust, observable, and scalable foundation for intelligent workflow automation.