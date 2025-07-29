# Tools and Dependencies System

## Overview

The AI Triad backend leverages Pydantic AI's dependency injection and tool system to create modular, reusable components that can be shared across agents while maintaining type safety and testability.

## Dependency Architecture

### Core Dependencies Container

```python
from dataclasses import dataclass
from typing import Protocol, runtime_checkable
import asyncio
import logfire
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic_ai.a2a import A2ABroker, A2AClient
from mcp import MCPClient

@dataclass
class TriadDeps:
    """Core dependencies container for all agents with modern stack."""
    db_session: AsyncSession
    a2a_broker: A2ABroker
    a2a_client: A2AClient
    mcp_client: MCPClient
    logfire_logger: logfire.Logger
    config: TriadConfig
    
    async def log_event(self, event_type: str, data: dict):
        """Centralized event logging with Logfire and constitutional oversight."""
        await self.logfire_logger.info(
            f"Event: {event_type}",
            event_type=event_type,
            constitutional_oversight=True,
            **data
        )
        
        # Westminster parliamentary procedure: Log for constitutional record
        await self.log_constitutional_record(event_type, data)
        
        # Notify other agents via A2A protocol
        await self.a2a_broker.broadcast_event({
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
            "constitutional_branch": data.get("agent", "unknown")
        })
    
    async def log_constitutional_record(self, event_type: str, data: dict):
        """Log events for constitutional parliamentary record (Hansard equivalent)."""
        constitutional_record = {
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
            "constitutional_authority": data.get("agent", "system"),
            "parliamentary_session": await self.get_current_parliamentary_session(),
            "recorded_by": "constitutional_clerk"
        }
        
        # Store in constitutional record database
        await self.db_session.execute(
            insert(ConstitutionalRecordTable).values(**constitutional_record)
        )
        await self.db_session.commit()
    
    async def exercise_crown_prerogative(
        self, 
        prerogative_type: str, 
        justification: str,
        affected_agents: List[str]
    ) -> Dict[str, Any]:
        """Exercise Crown prerogative powers (Governor General equivalent)."""
        
        # Westminster Crown powers: dismissal, dissolution, appointment, assent
        if prerogative_type not in ["dismiss", "dissolve", "appoint", "refuse_assent", "emergency_powers"]:
            raise ConstitutionalError(f"Invalid Crown prerogative: {prerogative_type}")
        
        crown_action = {
            "prerogative_type": prerogative_type,
            "justification": justification,
            "affected_agents": affected_agents,
            "exercised_by": "overwatch_agent",
            "timestamp": datetime.utcnow().isoformat(),
            "constitutional_authority": "crown"
        }
        
        # Log constitutional intervention
        await self.logfire_logger.warning(
            "Crown prerogative exercised",
            **crown_action,
            constitutional_intervention=True
        )
        
        # Execute prerogative power
        if prerogative_type == "dismiss":
            result = await self.dismiss_agents(affected_agents)
        elif prerogative_type == "dissolve":
            result = await self.dissolve_government()
        elif prerogative_type == "emergency_powers":
            result = await self.activate_emergency_governance()
        
        return {**crown_action, "result": result}
    
    async def integrate_external_system(self, system_type: str, operation: str, parameters: dict) -> dict:
        """Universal integration with existing systems via MCP."""
        with logfire.span("external_system_integration") as span:
            span.set_attribute("system_type", system_type)
            span.set_attribute("operation", operation)
            span.set_attribute("constitutional_oversight", True)
            
            result = await self.mcp_client.call_tool(
                f"{system_type}_adapter",
                operation,
                {**parameters, "constitutional_validation": True}
            )
            
            return result
    
    async def close(self):
        """Cleanup resources."""
        await self.db_session.close()
        await self.a2a_broker.close()
        await self.a2a_client.close()
        await self.mcp_client.close()

class TriadConfig:
    """Configuration settings for the Triad system."""
    DATABASE_URL: str
    LOGFIRE_TOKEN: str
    A2A_BROKER_URL: str
    MCP_SERVER_URLS: Dict[str, str]
    MODEL_CONFIGS: Dict[str, ModelConfig]
    PERFORMANCE_THRESHOLDS: PerformanceThresholds
    MONITORING_SETTINGS: MonitoringSettings
    INTEGRATION_ADAPTERS: Dict[str, str]  # MCP adapter configurations
    
class PerformanceThresholds:
    TASK_TIMEOUT_SECONDS: int = 300
    MAX_MEMORY_MB: int = 1024
    MAX_CPU_PERCENT: float = 80.0
    ACCURACY_THRESHOLD: float = 0.95
    ERROR_RATE_THRESHOLD: float = 0.01

class MetricsCollector:
    """Prometheus metrics collection."""
    
    def __init__(self):
        self.task_counter = Counter('triad_tasks_total', 'Total tasks processed', ['agent', 'status'])
        self.execution_time = Histogram('triad_execution_seconds', 'Task execution time', ['agent'])
        self.error_rate = Gauge('triad_error_rate', 'Current error rate', ['agent'])
        self.resource_usage = Gauge('triad_resource_usage', 'Resource usage', ['resource_type'])
    
    async def increment(self, metric_name: str, labels: Dict[str, str] = None):
        """Increment a counter metric."""
        if metric_name.startswith('tasks'):
            self.task_counter.labels(**(labels or {})).inc()
    
    async def histogram(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """Record histogram value."""
        if metric_name.startswith('execution'):
            self.execution_time.labels(**(labels or {})).observe(value)
    
    async def gauge(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """Set gauge value."""
        if metric_name.startswith('error_rate'):
            self.error_rate.labels(**(labels or {})).set(value)
        elif metric_name.startswith('resource'):
            self.resource_usage.labels(**(labels or {})).set(value)
```

### Database Dependencies

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, DateTime, JSON, Float, Boolean

class Base(DeclarativeBase):
    pass

class WorkflowModel(Base):
    __tablename__ = "workflows"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    plan_data = Column(JSON)
    metrics = Column(JSON)

class TaskExecutionModel(Base):
    __tablename__ = "task_executions"
    
    id = Column(String, primary_key=True)
    workflow_id = Column(String, nullable=False)
    task_id = Column(String, nullable=False)
    status = Column(String, nullable=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    execution_time = Column(Float)
    output_data = Column(JSON)
    error_message = Column(String)
    resource_usage = Column(JSON)

class ValidationReportModel(Base):
    __tablename__ = "validation_reports"
    
    id = Column(String, primary_key=True)
    task_execution_id = Column(String, nullable=False)
    accuracy_score = Column(Float, nullable=False)
    validation_status = Column(String, nullable=False)
    recommendations = Column(JSON)
    created_at = Column(DateTime, nullable=False)

async def create_database_dependency() -> AsyncSession:
    """Create database session dependency."""
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        yield session

async def create_a2a_broker() -> A2ABroker:
    """Create A2A broker for agent communication."""
    broker = A2ABroker(config.A2A_BROKER_URL)
    await broker.connect()
    try:
        yield broker
    finally:
        await broker.close()

async def create_mcp_client() -> MCPClient:
    """Create MCP client for external system integration."""
    client = MCPClient()
    # Connect to all configured MCP servers
    for adapter_name, server_url in config.MCP_SERVER_URLS.items():
        await client.connect_server(adapter_name, server_url)
    
    try:
        yield client
    finally:
        await client.close_all_servers()

async def create_logfire_logger() -> logfire.Logger:
    """Create Logfire logger with Triad-specific configuration."""
    logfire.configure(
        service_name="ai-triad-system",
        service_version="1.0.0",
        environment="production",
        token=config.LOGFIRE_TOKEN
    )
    
    # Instrument Pydantic AI automatically
    logfire.instrument_pydantic_ai()
    
    logger = logfire.get_logger("triad-system")
    return logger
```

## Tool System Architecture

### Base Tool Classes

```python
from abc import ABC, abstractmethod
from pydantic_ai.tools import Tool
from typing import Any, Dict, List, Optional

class BaseTriadTool(ABC):
    """Base class for all Triad tools."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, ctx: RunContext[TriadDeps], **kwargs) -> Any:
        """Execute the tool with given parameters."""
        pass
    
    async def validate_inputs(self, **kwargs) -> bool:
        """Validate tool inputs before execution."""
        return True
    
    async def log_execution(self, ctx: RunContext[TriadDeps], result: Any, **kwargs):
        """Log tool execution for audit trail."""
        await ctx.deps.log_event(f"tool_executed", {
            "tool_name": self.name,
            "parameters": kwargs,
            "result_type": type(result).__name__
        })

class WorkflowTool(BaseTriadTool):
    """Base class for workflow-related tools."""
    pass

class ExecutionTool(BaseTriadTool):
    """Base class for execution-related tools."""
    pass

class ValidationTool(BaseTriadTool):
    """Base class for validation-related tools."""
    pass

class MonitoringTool(BaseTriadTool):
    """Base class for monitoring-related tools."""
    pass
```

### Workflow Tools

```python
class WorkflowToolset:
    """Collection of workflow management tools."""
    
    @staticmethod
    def create_workflow_plan(ctx: RunContext[TriadDeps], requirements: str, constraints: Dict[str, Any]) -> WorkflowPlan:
        """Create a comprehensive workflow plan from requirements."""
        
    @staticmethod
    def optimize_task_dependencies(ctx: RunContext[TriadDeps], tasks: List[Task]) -> List[TaskDependency]:
        """Optimize task dependency graph for maximum parallelization."""
        
    @staticmethod
    def estimate_workflow_duration(ctx: RunContext[TriadDeps], workflow: WorkflowPlan) -> DurationEstimate:
        """Estimate total workflow execution duration."""
        
    @staticmethod
    def validate_workflow_feasibility(ctx: RunContext[TriadDeps], workflow: WorkflowPlan) -> FeasibilityReport:
        """Validate that workflow is feasible with current resources."""

# Implementation example
class CreateWorkflowPlanTool(WorkflowTool):
    """Tool for creating detailed workflow plans."""
    
    def __init__(self):
        super().__init__(
            name="create_workflow_plan",
            description="Create a comprehensive workflow plan from requirements and constraints"
        )
    
    async def execute(self, ctx: RunContext[TriadDeps], requirements: str, constraints: Dict[str, Any]) -> WorkflowPlan:
        """Create workflow plan with dependency analysis."""
        
        # Parse requirements
        parsed_requirements = await self._parse_requirements(requirements)
        
        # Generate tasks based on requirements
        tasks = await self._generate_tasks(parsed_requirements, constraints)
        
        # Create dependency graph
        dependencies = await self._create_dependencies(tasks)
        
        # Estimate resources
        resource_estimate = await self._estimate_resources(tasks, ctx.deps)
        
        # Create workflow plan
        workflow_plan = WorkflowPlan(
            id=generate_uuid(),
            name=parsed_requirements.name,
            description=requirements,
            tasks=tasks,
            dependencies=dependencies,
            estimated_duration=await self._estimate_duration(tasks, dependencies),
            resource_requirements=resource_estimate
        )
        
        # Store in database
        await self._store_workflow_plan(workflow_plan, ctx.deps)
        
        await self.log_execution(ctx, workflow_plan, requirements=requirements, constraints=constraints)
        
        return workflow_plan
    
    async def _parse_requirements(self, requirements: str) -> ParsedRequirements:
        """Parse natural language requirements into structured format."""
        # Implementation using NLP or rule-based parsing
        pass
    
    async def _generate_tasks(self, requirements: ParsedRequirements, constraints: Dict[str, Any]) -> List[Task]:
        """Generate tasks based on parsed requirements."""
        # Implementation of task generation logic
        pass
    
    async def _create_dependencies(self, tasks: List[Task]) -> List[TaskDependency]:
        """Analyze tasks and create dependency relationships."""
        # Implementation of dependency analysis
        pass
```

### Execution Tools

```python
class ExecutionToolset:
    """Collection of task execution tools."""
    
    @staticmethod
    def execute_data_processing_task(ctx: RunContext[TriadDeps], task: Task) -> ExecutionResult:
        """Execute data processing tasks."""
        
    @staticmethod
    def execute_api_call_task(ctx: RunContext[TriadDeps], task: Task) -> ExecutionResult:
        """Execute API call tasks."""
        
    @staticmethod
    def execute_database_task(ctx: RunContext[TriadDeps], task: Task) -> ExecutionResult:
        """Execute database operation tasks."""
        
    @staticmethod
    def monitor_task_progress(ctx: RunContext[TriadDeps], task_id: str) -> TaskProgress:
        """Monitor real-time progress of task execution."""

class ExecuteDataProcessingTool(ExecutionTool):
    """Tool for executing data processing tasks."""
    
    def __init__(self):
        super().__init__(
            name="execute_data_processing",
            description="Execute data processing tasks with monitoring and error handling"
        )
    
    async def execute(self, ctx: RunContext[TriadDeps], task: Task) -> ExecutionResult:
        """Execute data processing task with comprehensive monitoring."""
        
        start_time = time.time()
        
        try:
            # Validate task parameters
            await self.validate_inputs(**task.parameters)
            
            # Set up monitoring
            progress_tracker = TaskProgressTracker(task.id)
            
            # Execute based on processing type
            if task.parameters['processing_type'] == 'batch':
                result = await self._execute_batch_processing(task, progress_tracker, ctx.deps)
            elif task.parameters['processing_type'] == 'stream':
                result = await self._execute_stream_processing(task, progress_tracker, ctx.deps)
            else:
                raise ValueError(f"Unknown processing type: {task.parameters['processing_type']}")
            
            execution_time = time.time() - start_time
            
            # Record metrics
            await ctx.deps.metrics_collector.histogram(
                "execution_time",
                execution_time,
                {"task_type": "data_processing"}
            )
            
            execution_result = ExecutionResult(
                task_id=task.id,
                status=ExecutionStatus.COMPLETED,
                output_data=result,
                execution_time=execution_time,
                resource_usage=await self._get_resource_usage(),
                logs=progress_tracker.get_logs()
            )
            
            await self.log_execution(ctx, execution_result, task=task.dict())
            
            return execution_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            await ctx.deps.log_event("task_execution_failed", {
                "task_id": task.id,
                "error": str(e),
                "execution_time": execution_time
            })
            
            return ExecutionResult(
                task_id=task.id,
                status=ExecutionStatus.FAILED,
                output_data={},
                execution_time=execution_time,
                resource_usage=await self._get_resource_usage(),
                logs=[],
                error_message=str(e)
            )
```

### Validation Tools

```python
class ValidationToolset:
    """Collection of validation and quality assurance tools."""
    
    @staticmethod
    def validate_data_quality(ctx: RunContext[TriadDeps], data: Dict[str, Any], schema: DataSchema) -> QualityReport:
        """Validate data quality against defined schema and rules."""
        
    @staticmethod
    def benchmark_performance(ctx: RunContext[TriadDeps], result: ExecutionResult, benchmarks: List[Benchmark]) -> BenchmarkReport:
        """Compare execution performance against historical benchmarks."""
        
    @staticmethod
    def validate_business_rules(ctx: RunContext[TriadDeps], result: ExecutionResult, rules: List[BusinessRule]) -> RuleValidationReport:
        """Validate results against business rules and compliance requirements."""

class ValidateDataQualityTool(ValidationTool):
    """Tool for comprehensive data quality validation."""
    
    def __init__(self):
        super().__init__(
            name="validate_data_quality",
            description="Perform comprehensive data quality validation against schema and business rules"
        )
    
    async def execute(self, ctx: RunContext[TriadDeps], data: Dict[str, Any], schema: DataSchema) -> QualityReport:
        """Validate data quality with detailed reporting."""
        
        validation_results = []
        
        # Schema validation
        schema_result = await self._validate_schema(data, schema)
        validation_results.append(schema_result)
        
        # Data completeness check
        completeness_result = await self._validate_completeness(data, schema)
        validation_results.append(completeness_result)
        
        # Data accuracy validation
        accuracy_result = await self._validate_accuracy(data, schema)
        validation_results.append(accuracy_result)
        
        # Consistency checks
        consistency_result = await self._validate_consistency(data, schema)
        validation_results.append(consistency_result)
        
        # Calculate overall quality score
        quality_score = self._calculate_quality_score(validation_results)
        
        quality_report = QualityReport(
            overall_score=quality_score,
            validation_results=validation_results,
            recommendations=await self._generate_recommendations(validation_results),
            passed_checks=[r for r in validation_results if r.passed],
            failed_checks=[r for r in validation_results if not r.passed]
        )
        
        await self.log_execution(ctx, quality_report, data_size=len(data), schema_version=schema.version)
        
        return quality_report
```

### Monitoring Tools

```python
class MonitoringToolset:
    """Collection of system monitoring and observability tools."""
    
    @staticmethod
    def collect_system_metrics(ctx: RunContext[TriadDeps]) -> SystemMetrics:
        """Collect comprehensive system metrics."""
        
    @staticmethod
    def detect_anomalies(ctx: RunContext[TriadDeps], metrics: SystemMetrics) -> List[Anomaly]:
        """Detect system anomalies and performance issues."""
        
    @staticmethod
    def generate_health_report(ctx: RunContext[TriadDeps]) -> HealthReport:
        """Generate comprehensive system health report."""

class SystemHealthMonitorTool(MonitoringTool):
    """Tool for comprehensive system health monitoring."""
    
    def __init__(self):
        super().__init__(
            name="monitor_system_health",
            description="Monitor system health and performance across all components"
        )
    
    async def execute(self, ctx: RunContext[TriadDeps]) -> SystemHealth:
        """Perform comprehensive system health check."""
        
        # Collect metrics from all components with constitutional oversight
        db_health = await self._check_database_health(ctx.deps.db_session)
        a2a_health = await self._check_a2a_health(ctx.deps.a2a_broker)
        mcp_health = await self._check_mcp_health(ctx.deps.mcp_client)
        agent_health = await self._check_agent_health(ctx.deps)
        resource_metrics = await self._collect_resource_metrics()
        integration_health = await self._check_integration_health(ctx.deps)
        
        # Analyze performance trends with Logfire
        performance_analysis = await self._analyze_performance_trends(ctx.deps)
        
        # Detect active issues with constitutional oversight
        active_alerts = await self._detect_active_alerts(ctx.deps)
        
        # Generate recommendations with modern stack considerations
        recommendations = await self._generate_health_recommendations(
            db_health, a2a_health, mcp_health, agent_health, resource_metrics, integration_health, active_alerts
        )
        
        system_health = SystemHealth(
            overall_status=self._determine_overall_status([db_health, a2a_health, mcp_health, agent_health]),
            component_health={
                "database": db_health,
                "a2a_protocol": a2a_health,
                "mcp_integration": mcp_health,
                "agents": agent_health,
                "resources": resource_metrics,
                "external_integrations": integration_health
            },
            performance_analysis=performance_analysis,
            active_alerts=active_alerts,
            recommendations=recommendations,
            timestamp=datetime.utcnow()
        )
        
        await self.log_execution(ctx, system_health)
        
        return system_health
```

## Tool Registration and Usage

### Agent Tool Registration

```python
from .tools import WorkflowToolset, ExecutionToolset, ValidationToolset, MonitoringToolset

# Planner agent with workflow and monitoring tools
planner_agent = Agent(
    'openai:gpt-4o',
    deps_type=TriadDeps,
    tools=[
        CreateWorkflowPlanTool(),
        OptimizeTaskDependenciesTool(),
        EstimateWorkflowDurationTool(),
        SystemHealthMonitorTool()
    ]
)

# Executor agent with execution and monitoring tools
executor_agent = Agent(
    'openai:gpt-4o',
    deps_type=TriadDeps,
    tools=[
        ExecuteDataProcessingTool(),
        ExecuteApiCallTool(),
        ExecuteDatabaseTaskTool(),
        MonitorTaskProgressTool(),
        SystemHealthMonitorTool()
    ]
)

# Evaluator agent with validation and monitoring tools
evaluator_agent = Agent(
    'anthropic:claude-3-5-sonnet-latest',
    deps_type=TriadDeps,
    tools=[
        ValidateDataQualityTool(),
        BenchmarkPerformanceTool(),
        ValidateBusinessRulesTool(),
        SystemHealthMonitorTool()
    ]
)

# Overwatch agent with comprehensive monitoring tools
overwatch_agent = Agent(
    'openai:gpt-4o',
    deps_type=TriadDeps,
    tools=[
        SystemHealthMonitorTool(),
        DetectAnomalies Tool(),
        GenerateHealthReportTool(),
        EscalateCriticalIssueTool(),
        GeneratePerformanceReportTool()
    ]
)
```

### Dependency Injection in Production

```python
async def create_production_dependencies() -> TriadDeps:
    """Create production dependencies with proper resource management."""
    
    # Database setup
    db_engine = create_async_engine(settings.DATABASE_URL)
    db_session = async_sessionmaker(db_engine)()
    
    # A2A Protocol setup for agent communication
    a2a_broker = A2ABroker(settings.A2A_BROKER_URL)
    await a2a_broker.connect()
    
    a2a_client = A2AClient(settings.A2A_BROKER_URL)
    await a2a_client.connect()
    
    # MCP setup for external system integration
    mcp_client = MCPClient()
    for adapter_name, server_url in settings.MCP_SERVER_URLS.items():
        await mcp_client.connect_server(adapter_name, server_url)
    
    # Logfire setup for comprehensive observability
    logfire.configure(
        service_name="ai-triad-system",
        service_version="1.0.0",
        environment=settings.ENVIRONMENT,
        token=settings.LOGFIRE_TOKEN
    )
    logfire.instrument_pydantic_ai()
    logfire_logger = logfire.get_logger("triad-system")
    
    # Configuration
    config = TriadConfig.from_environment()
    
    return TriadDeps(
        db_session=db_session,
        a2a_broker=a2a_broker,
        a2a_client=a2a_client,
        mcp_client=mcp_client,
        logfire_logger=logfire_logger,
        config=config
    )

# Usage in FastAPI application
@app.on_event("startup")
async def startup_event():
    app.state.deps = await create_production_dependencies()

@app.on_event("shutdown")
async def shutdown_event():
    await app.state.deps.close()
```

This comprehensive tool and dependency system provides a robust foundation for the AI Triad backend, ensuring modularity, testability, and production readiness.