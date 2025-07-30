# AI Triad Agents Implementation

## Agent Design Philosophy

Each agent in the AI Triad system is implemented using Pydantic AI's agent framework, providing type safety, dependency injection, and comprehensive tool integration. Agents are designed to be autonomous, composable, and production-ready.

## Core Agent Implementations

### 1. Planner Agent (Strategic Architect)

```python
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel
from typing import List, Optional
from dataclasses import dataclass

class WorkflowPlan(BaseModel):
    id: str
    name: str
    description: str
    tasks: List[Task]
    dependencies: List[TaskDependency]
    estimated_duration: int
    resource_requirements: ResourceRequirements

class Task(BaseModel):
    id: str
    name: str
    description: str
    type: TaskType
    parameters: dict
    dependencies: List[str]
    timeout: int

planner_agent = Agent(
    'openai:gpt-4o',
    deps_type=TriadDeps,
    output_type=WorkflowPlan,
    system_prompt="""
    You are the Planner Agent in the AI Triad system.
    Your role is to design comprehensive workflows and task plans.
    
    Responsibilities:
    - Analyze requirements and create detailed workflow plans
    - Define task dependencies and execution order
    - Estimate resource requirements and duration
    - Optimize workflow efficiency and performance
    - Consider error handling and recovery scenarios
    
    Always create plans that are:
    - Executable by the Executor Agent
    - Measurable by the Evaluator Agent
    - Monitorable by the Overwatch Agent
    """
)

@planner_agent.tool
async def analyze_requirements(ctx: RunContext[TriadDeps], requirements: str) -> RequirementAnalysis:
    """Analyze user requirements and extract key components."""
    analysis = await parse_requirements(requirements)
    await ctx.deps.log_event("requirements_analyzed", {"analysis": analysis.to_dict()})
    return analysis

@planner_agent.tool
async def create_task_dependency_graph(ctx: RunContext[TriadDeps], tasks: List[Task]) -> DependencyGraph:
    """Create a dependency graph for tasks."""
    graph = DependencyGraph.from_tasks(tasks)
    await ctx.deps.metrics_collector.gauge("planner.dependency_complexity", graph.complexity_score)
    return graph

@planner_agent.tool
async def estimate_resources(ctx: RunContext[TriadDeps], workflow: WorkflowPlan) -> ResourceEstimate:
    """Estimate resource requirements for workflow execution."""
    estimate = ResourceEstimator.calculate(workflow)
    
    # Store estimate in database for persistence and audit trail
    await ctx.deps.db_session.execute(
        insert(ResourceEstimateTable).values(
            workflow_id=workflow.id,
            estimate_data=estimate.model_dump_json(),
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
        )
    )
    await ctx.deps.db_session.commit()
    
    await ctx.deps.logfire_logger.info(
        "Resource estimate calculated",
        workflow_id=workflow.id,
        cpu_cores=estimate.cpu_cores,
        memory_gb=estimate.memory_gb,
        estimated_duration=estimate.duration_minutes
    )
    
    return estimate

@planner_agent.output_validator
async def validate_workflow_plan(ctx: RunContext[TriadDeps], plan: WorkflowPlan) -> WorkflowPlan:
    """Validate the generated workflow plan."""
    # Check for circular dependencies
    if has_circular_dependencies(plan.tasks, plan.dependencies):
        raise ModelRetry("Workflow contains circular dependencies. Please redesign.")
    
    # Validate resource requirements
    if plan.resource_requirements.cpu_cores > MAX_CPU_CORES:
        raise ModelRetry("Resource requirements exceed system limits. Please optimize.")
    
    await ctx.deps.log_event("workflow_plan_validated", {"plan_id": plan.id})
    return plan
```

### 2. Executor Agent (Task Performer)

```python
from enum import Enum

class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

class ExecutionResult(BaseModel):
    task_id: str
    status: ExecutionStatus
    output_data: dict
    execution_time: float
    resource_usage: ResourceUsage
    logs: List[str]
    error_message: Optional[str] = None

executor_agent = Agent(
    'openai:gpt-4o',
    deps_type=TriadDeps,
    output_type=ExecutionResult,
    system_prompt="""
    You are the Executor Agent in the AI Triad system.
    Your role is to execute tasks precisely according to workflow plans.
    
    Responsibilities:
    - Execute tasks in the correct order based on dependencies
    - Monitor task progress and resource usage
    - Handle errors gracefully and provide detailed logs
    - Ensure data integrity and consistency
    - Report execution results to the Evaluator Agent
    
    Execution principles:
    - Follow the workflow plan exactly
    - Validate inputs before execution
    - Log all activities for audit trails
    - Handle timeouts and resource constraints
    - Maintain idempotency where possible
    """
)

@executor_agent.tool
async def execute_task(ctx: RunContext[TriadDeps], task: Task) -> ExecutionResult:
    """Execute a single task and return results."""
    start_time = time.time()
    
    try:
        # Validate task inputs
        await validate_task_inputs(task)
        
        # Record task start
        await ctx.deps.log_event("task_started", {"task_id": task.id, "type": task.type})
        await ctx.deps.metrics_collector.increment("executor.tasks_started")
        
        # Execute based on task type
        if task.type == TaskType.DATA_PROCESSING:
            result = await execute_data_processing_task(task, ctx.deps)
        elif task.type == TaskType.API_CALL:
            result = await execute_api_call_task(task, ctx.deps)
        elif task.type == TaskType.DATABASE_OPERATION:
            result = await execute_database_task(task, ctx.deps)
        else:
            raise TaskExecutionError(f"Unknown task type: {task.type}")
        
        execution_time = time.time() - start_time
        
        return ExecutionResult(
            task_id=task.id,
            status=ExecutionStatus.COMPLETED,
            output_data=result,
            execution_time=execution_time,
            resource_usage=await get_resource_usage(),
            logs=await get_task_logs(task.id)
        )
        
    except TaskExecutionError as e:
        execution_time = time.time() - start_time
        await ctx.deps.log_event("task_failed", {
            "task_id": task.id,
            "error": str(e),
            "execution_time": execution_time
        })
        
        return ExecutionResult(
            task_id=task.id,
            status=ExecutionStatus.FAILED,
            output_data={},
            execution_time=execution_time,
            resource_usage=await get_resource_usage(),
            logs=await get_task_logs(task.id),
            error_message=str(e)
        )

@executor_agent.tool
async def check_dependencies_ready(ctx: RunContext[TriadDeps], task: Task) -> bool:
    """Check if all task dependencies are completed using database."""
    for dep_id in task.dependencies:
        result = await ctx.deps.db_session.execute(
            select(TaskStatusTable.status).where(TaskStatusTable.task_id == dep_id)
        )
        status = result.scalar_one_or_none()
        if status != ExecutionStatus.COMPLETED.value:
            return False
    return True

@executor_agent.tool
async def update_task_status(ctx: RunContext[TriadDeps], task_id: str, status: ExecutionStatus) -> str:
    """Update task execution status in database with A2A notification."""
    # Update status in database
    await ctx.deps.db_session.execute(
        insert(TaskStatusTable).values(
            task_id=task_id,
            status=status.value,
            updated_at=datetime.now(timezone.utc)
        ).on_conflict_do_update(
            index_elements=['task_id'],
            set_={'status': status.value, 'updated_at': datetime.now(timezone.utc)}
        )
    )
    await ctx.deps.db_session.commit()
    
    # Notify other agents via A2A protocol
    await ctx.deps.a2a_broker.broadcast_status_update({
        "task_id": task_id,
        "status": status.value,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "constitutional_branch": "executive"
    })
    
    await ctx.deps.logfire_logger.info(
        "Task status updated",
        task_id=task_id,
        status=status.value,
        constitutional_oversight=True
    )
    
    return f"Task {task_id} status updated to {status.value}"
```

### 3. Evaluator Agent (Quality Assurance)

```python
class ValidationReport(BaseModel):
    task_id: str
    workflow_id: str
    accuracy_score: float
    performance_metrics: PerformanceMetrics
    quality_indicators: QualityIndicators
    recommendations: List[str]
    passed_validations: List[str]
    failed_validations: List[str]
    overall_status: ValidationStatus

class ValidationStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    REQUIRES_REVIEW = "requires_review"

evaluator_agent = Agent(
    'anthropic:claude-3-5-sonnet-latest',
    deps_type=TriadDeps,
    output_type=ValidationReport,
    system_prompt="""
    You are the Evaluator Agent in the AI Triad system.
    Your role is to validate and assess task execution results.
    
    Responsibilities:
    - Validate task outputs against predefined criteria
    - Measure performance against KPIs and benchmarks
    - Identify quality issues and anomalies
    - Provide actionable feedback for improvement
    - Ensure compliance with business rules and standards
    
    Validation criteria:
    - Accuracy threshold: >95%
    - Performance latency: <5 seconds per task
    - Data integrity: 100% consistency
    - Business rule compliance: 100%
    - Error rate: <1%
    
    Always provide specific, actionable recommendations.
    """
)

@evaluator_agent.tool
async def validate_execution_result(ctx: RunContext[TriadDeps], result: ExecutionResult) -> ValidationReport:
    """Perform comprehensive validation of execution results."""
    validations = []
    recommendations = []
    
    # Accuracy validation
    accuracy_score = await calculate_accuracy_score(result, ctx.deps)
    if accuracy_score < 0.95:
        validations.append("accuracy_check:failed")
        recommendations.append("Improve data quality and validation logic")
    else:
        validations.append("accuracy_check:passed")
    
    # Performance validation
    if result.execution_time > 5.0:
        validations.append("performance_check:failed")
        recommendations.append("Optimize execution performance - consider caching or algorithm improvements")
    else:
        validations.append("performance_check:passed")
    
    # Resource usage validation
    if result.resource_usage.memory_mb > MAX_MEMORY_MB:
        validations.append("resource_check:failed")
        recommendations.append("Reduce memory usage - consider streaming or batch processing")
    else:
        validations.append("resource_check:passed")
    
    passed = [v for v in validations if v.endswith(":passed")]
    failed = [v for v in validations if v.endswith(":failed")]
    
    overall_status = ValidationStatus.PASSED if not failed else ValidationStatus.FAILED
    
    return ValidationReport(
        task_id=result.task_id,
        workflow_id=await get_workflow_id_for_task(result.task_id),
        accuracy_score=accuracy_score,
        performance_metrics=await calculate_performance_metrics(result),
        quality_indicators=await assess_quality_indicators(result),
        recommendations=recommendations,
        passed_validations=passed,
        failed_validations=failed,
        overall_status=overall_status
    )

@evaluator_agent.tool
async def benchmark_performance(ctx: RunContext[TriadDeps], result: ExecutionResult) -> BenchmarkComparison:
    """Compare execution results against historical benchmarks."""
    historical_data = await ctx.deps.db_session.query(
        ExecutionBenchmarks
    ).filter_by(task_type=result.task_id.split('_')[0]).all()
    
    comparison = BenchmarkComparison.compare(result, historical_data)
    await ctx.deps.metrics_collector.histogram("evaluator.benchmark_score", comparison.score)
    
    return comparison

@evaluator_agent.output_validator
async def validate_evaluation_report(ctx: RunContext[TriadDeps], report: ValidationReport) -> ValidationReport:
    """Validate the evaluation report before sending to Planner."""
    if report.accuracy_score < 0 or report.accuracy_score > 1:
        raise ModelRetry("Invalid accuracy score. Must be between 0 and 1.")
    
    if not report.recommendations and report.overall_status == ValidationStatus.FAILED:
        raise ModelRetry("Failed validations must include specific recommendations.")
    
    await ctx.deps.log_event("validation_report_generated", {
        "task_id": report.task_id,
        "status": report.overall_status,
        "accuracy": report.accuracy_score
    })
    
    return report
```

### 4. Overwatch Agent (Central Oversight)

```python
class SystemHealth(BaseModel):
    overall_status: str
    agent_statuses: Dict[str, AgentStatus]
    performance_metrics: SystemMetrics
    active_alerts: List[Alert]
    recommendations: List[str]

class Alert(BaseModel):
    id: str
    severity: AlertSeverity
    component: str
    message: str
    timestamp: datetime
    resolved: bool = False

overwatch_agent = Agent(
    'openai:gpt-4o',
    deps_type=TriadDeps,
    output_type=SystemHealth,
    system_prompt="""
    You are the Overwatch Agent in the AI Triad system.
    Your role is to monitor, analyze, and ensure system-wide health and performance.
    
    Responsibilities:
    - Monitor all agents and system components in real-time
    - Detect anomalies and performance degradations
    - Escalate critical issues requiring immediate attention
    - Provide system health assessments and recommendations
    - Maintain audit trails and compliance monitoring
    
    Monitoring thresholds:
    - Task success rate: >98%
    - Response time: <2 seconds average
    - Error rate: <0.5%
    - Resource utilization: <80%
    - Queue depth: <100 pending items
    
    Escalation levels:
    - INFO: Performance within normal range
    - WARNING: Performance degradation detected
    - CRITICAL: System failure or severe degradation
    - EMERGENCY: Complete system outage
    """
)

@overwatch_agent.tool
async def monitor_system_health(ctx: RunContext[TriadDeps]) -> SystemHealth:
    """Perform comprehensive system health monitoring."""
    # Collect metrics from all components
    metrics = await ctx.deps.metrics_collector.get_system_metrics()
    
    # Check agent statuses
    agent_statuses = {
        "planner": await check_agent_health("planner", ctx.deps),
        "executor": await check_agent_health("executor", ctx.deps),
        "evaluator": await check_agent_health("evaluator", ctx.deps)
    }
    
    # Detect active alerts
    alerts = await detect_system_alerts(metrics, ctx.deps)
    
    # Generate recommendations
    recommendations = await generate_system_recommendations(metrics, alerts)
    
    overall_status = determine_overall_status(agent_statuses, alerts)
    
    return SystemHealth(
        overall_status=overall_status,
        agent_statuses=agent_statuses,
        performance_metrics=metrics,
        active_alerts=alerts,
        recommendations=recommendations
    )

@overwatch_agent.tool
async def escalate_critical_issue(ctx: RunContext[TriadDeps], alert: Alert) -> str:
    """Escalate critical issues for immediate attention."""
    if alert.severity == AlertSeverity.CRITICAL:
        # Send immediate notifications
        await send_critical_alert_notification(alert, ctx.deps)
        
        # Log escalation
        await ctx.deps.log_event("critical_escalation", {
            "alert_id": alert.id,
            "component": alert.component,
            "message": alert.message
        })
        
        # Trigger automated recovery if possible
        recovery_action = await attempt_automated_recovery(alert, ctx.deps)
        
        return f"Critical alert escalated: {alert.id}. Recovery action: {recovery_action}"
    
    return f"Alert {alert.id} does not require critical escalation"

@overwatch_agent.tool
async def generate_performance_report(ctx: RunContext[TriadDeps], time_range: str) -> PerformanceReport:
    """Generate comprehensive performance report for specified time range."""
    metrics = await ctx.deps.db_session.query(
        PerformanceMetrics
    ).filter_by_time_range(time_range).all()
    
    report = PerformanceReport.generate(metrics)
    
    # Store report in database with constitutional oversight
    await ctx.deps.db_session.execute(
        insert(PerformanceReportTable).values(
            time_range_id=time_range,
            report_data=report.model_dump_json(),
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),  # 7 days retention
            constitutional_branch="crown"  # Overwatch authority
        )
    )
    await ctx.deps.db_session.commit()
    
    # Share report with other agents via A2A protocol
    await ctx.deps.a2a_broker.share_performance_report({
        "report_id": report.id,
        "time_range": time_range,
        "summary": report.summary,
        "constitutional_oversight": True
    })
    
    await ctx.deps.logfire_logger.info(
        "Performance report generated",
        time_range=time_range,
        report_id=report.id,
        constitutional_authority="overwatch",
        performance_score=report.overall_score
    )
    
    return report
```

## Westminster Parliamentary Procedures

### Question Period Implementation

```python
@planner_agent.tool
async def respond_to_question_period(
    ctx: RunContext[TriadDeps], 
    question: str,
    questioning_agent: str
) -> str:
    """Respond to formal parliamentary-style questions about planning decisions."""
    
    # Westminster principle: Government must answer opposition questions
    response = await ctx.deps.parliamentary_procedure.formal_response(
        question=question,
        responding_agent="planner",
        questioning_agent=questioning_agent,
        constitutional_requirement=True
    )
    
    await ctx.deps.logfire_logger.info(
        "Parliamentary question answered",
        question_id=response["question_id"],
        questioning_agent=questioning_agent,
        constitutional_compliance=True
    )
    
    return response["formal_answer"]

@executor_agent.tool
async def defend_execution_decisions(
    ctx: RunContext[TriadDeps],
    challenged_decision: str,
    challenger: str
) -> str:
    """Defend execution decisions under parliamentary scrutiny."""
    
    # Westminster ministerial responsibility
    defense = await ctx.deps.parliamentary_procedure.ministerial_defense(
        decision=challenged_decision,
        minister="executor",
        challenger=challenger
    )
    
    return defense["public_defense"]
```

### Collective Cabinet Responsibility

```python
class CollectiveCabinetDecision:
    """Westminster collective cabinet responsibility for major decisions."""
    
    async def major_system_decision(
        self,
        proposal: Dict[str, Any],
        deps: TriadDeps
    ) -> Dict[str, Any]:
        """All agents must collectively agree or resign from major decisions."""
        
        # Get position from each agent
        agent_positions = {}
        
        for agent_name, agent in [("planner", planner_agent), ("executor", executor_agent), ("evaluator", evaluator_agent)]:
            position = await agent.run(
                f"Take a position on this major system decision: {proposal}. You must either SUPPORT or OPPOSE. If you oppose, you must be prepared to resign.",
                deps=deps
            )
            
            agent_positions[agent_name] = {
                "stance": position.output.get("stance"),
                "reasoning": position.output.get("reasoning"),
                "prepared_to_resign": position.output.get("prepared_to_resign", False)
            }
        
        # Check for collective agreement
        all_support = all(pos["stance"] == "SUPPORT" for pos in agent_positions.values())
        
        if not all_support:
            # Westminster principle: collective responsibility crisis
            return await deps.constitutional_crisis_manager.handle_collective_responsibility_crisis(
                proposal, agent_positions
            )
        
        return {
            "collective_agreement": True,
            "agent_positions": agent_positions,
            "decision_approved": True,
            "constitutional_compliance": True
        }
```

## Agent Coordination Patterns

### 1. Sequential Processing
```python
async def process_workflow_sequentially(workflow: WorkflowPlan, deps: TriadDeps):
    """Process workflow through all agents sequentially."""
    
    # Step 1: Planner creates detailed execution plan
    execution_plan = await planner_agent.run(
        f"Create execution plan for: {workflow.description}",
        deps=deps
    )
    
    # Step 2: Executor performs all tasks
    execution_results = []
    for task in execution_plan.output.tasks:
        result = await executor_agent.run(
            f"Execute task: {task.to_json()}",
            deps=deps
        )
        execution_results.append(result.output)
    
    # Step 3: Evaluator validates all results
    validation_reports = []
    for result in execution_results:
        report = await evaluator_agent.run(
            f"Validate result: {result.to_json()}",
            deps=deps
        )
        validation_reports.append(report.output)
    
    # Step 4: Overwatch monitors overall process
    health_report = await overwatch_agent.run(
        f"Monitor workflow execution: {workflow.id}",
        deps=deps
    )
    
    return {
        "execution_plan": execution_plan.output,
        "execution_results": execution_results,
        "validation_reports": validation_reports,
        "health_report": health_report.output
    }
```

### 2. Parallel Processing
```python
async def process_workflow_parallel(workflow: WorkflowPlan, deps: TriadDeps):
    """Process independent tasks in parallel while maintaining dependencies."""
    
    # Get execution plan
    plan = await planner_agent.run(f"Plan workflow: {workflow.description}", deps=deps)
    
    # Create dependency graph
    dependency_graph = create_dependency_graph(plan.output.tasks)
    
    # Execute tasks in dependency order with parallelization
    results = await execute_with_dependencies(dependency_graph, deps)
    
    # Validate results in parallel
    validation_tasks = [
        evaluator_agent.run(f"Validate: {result.to_json()}", deps=deps)
        for result in results
    ]
    validation_reports = await asyncio.gather(*validation_tasks)
    
    return {
        "results": results,
        "validations": [report.output for report in validation_reports]
    }
```

This implementation provides a robust, type-safe agent system using Pydantic AI's advanced features for production-ready AI workflow automation.