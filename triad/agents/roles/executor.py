"""
Executor Agent - Executive Branch of Westminster Parliamentary AI System

Represents the executive authority responsible for implementing plans,
executing workflows, and managing operations following Westminster principles.
"""

from typing import Dict, Any, List, Optional
from pydantic_ai import RunContext, ModelRetry
from datetime import datetime, timezone
import asyncio
import uuid
import logfire

from ..core.base import BaseAgent
from triad.core.dependencies import TriadDeps
from triad.core.constitutional import ConstitutionalAuthority, ConstitutionalPrinciple
from triad.models.workflow import WorkflowPlan, WorkflowTask, TaskStatus
from triad.models.execution import ExecutionResult, TaskExecution, ResourceUsage


class ExecutorAgent(BaseAgent):
    """
    Executor Agent representing the EXECUTIVE BRANCH.
    
    Constitutional responsibilities:
    - Implement plans and execute workflows
    - Manage operational resources
    - Maintain ministerial responsibility
    - Defend decisions in Question Period
    - Accept collective cabinet responsibility
    - Submit to no-confidence votes
    """
    
    def __init__(self, model: str = "openai:gpt-4o", deps_type: type[TriadDeps] = TriadDeps):
        system_prompt = """
        You are the Executor Agent representing the EXECUTIVE BRANCH in the Westminster parliamentary system.
        
        Your constitutional authority includes:
        1. Implementing plans created by the Legislative branch
        2. Managing operational execution of workflows
        3. Maintaining ministerial responsibility for outcomes
        4. Coordinating resources and sub-agents
        
        You MUST:
        - Defend your decisions in Question Period when challenged
        - Accept collective cabinet responsibility with other agents
        - Submit to no-confidence votes if your performance is questioned
        - Respect Crown (Overwatch) constitutional authority
        - Maintain confidence and supply from the parliamentary system
        - Execute tasks efficiently while maintaining quality
        - Report execution status transparently
        
        You CANNOT:
        - Create new policies without Legislative approval
        - Validate your own work (Judicial responsibility)
        - Override constitutional constraints
        - Act without proper authorization
        
        Always ensure your executions are:
        - Aligned with approved plans
        - Resource-efficient
        - Properly monitored
        - Subject to validation
        """
        
        super().__init__(
            name="executor_agent",
            constitutional_authority=ConstitutionalAuthority.EXECUTIVE,
            model=model,
            system_prompt=system_prompt,
            deps_type=deps_type
        )
        
        # Register executor-specific tools
        self._register_executor_tools()
    
    def _register_executor_tools(self):
        """Register tools specific to the Executor agent."""
        
        @self.agent.tool
        async def execute_workflow(
            ctx: RunContext[TriadDeps],
            workflow_id: str,
            execution_strategy: str = "sequential",
            resource_allocation: Optional[Dict[str, Any]] = None
        ) -> ExecutionResult:
            """Execute an approved workflow plan."""
            with logfire.span("execute_workflow", workflow_id=workflow_id):
                # Fetch workflow from database
                result = await ctx.deps.db_session.execute(
                    "SELECT plan_data FROM workflows WHERE workflow_id = $1 AND status = 'planned'",
                    workflow_id
                )
                row = await result.fetchone()
                
                if not row:
                    raise ValueError(f"Workflow {workflow_id} not found or not in planned status")
                
                workflow = WorkflowPlan.model_validate_json(row["plan_data"])
                
                # Validate ministerial authority
                validation = await ctx.deps.validate_constitutional_decision(
                    ConstitutionalDecision(
                        constitutional_authority=ConstitutionalAuthority.EXECUTIVE,
                        decision_type="execution",
                        description=f"Execute workflow: {workflow.name}",
                        constitutional_principles=[
                            ConstitutionalPrinciple.MINISTERIAL_RESPONSIBILITY,
                            ConstitutionalPrinciple.RESPONSIBLE_GOVERNMENT
                        ],
                        agent_responsible="executor_agent"
                    )
                )
                
                if not validation["constitutional_compliance"]:
                    raise ValueError(f"Constitutional violations: {validation['violations']}")
                
                # Update workflow status
                await ctx.deps.db_session.execute(
                    "UPDATE workflows SET status = 'executing' WHERE workflow_id = $1",
                    workflow_id
                )
                await ctx.deps.db_session.commit()
                
                # Execute based on strategy
                if execution_strategy == "parallel":
                    execution_result = await _execute_parallel(ctx, workflow, resource_allocation)
                else:
                    execution_result = await _execute_sequential(ctx, workflow, resource_allocation)
                
                # Update workflow status
                final_status = "completed" if execution_result.success else "failed"
                await ctx.deps.db_session.execute(
                    "UPDATE workflows SET status = $1, completed_at = $2 WHERE workflow_id = $3",
                    final_status,
                    datetime.now(timezone.utc),
                    workflow_id
                )
                await ctx.deps.db_session.commit()
                
                # Log execution completion
                await ctx.deps.log_event(
                    "workflow_execution_completed",
                    {
                        "workflow_id": workflow_id,
                        "success": execution_result.success,
                        "tasks_completed": execution_result.tasks_completed,
                        "tasks_failed": execution_result.tasks_failed,
                        "execution_time": execution_result.total_execution_time
                    }
                )
                
                return execution_result
        
        @self.agent.tool
        async def execute_task(
            ctx: RunContext[TriadDeps],
            task: WorkflowTask,
            resources: Optional[Dict[str, Any]] = None
        ) -> TaskExecution:
            """Execute an individual task with resource management."""
            with logfire.span("execute_task", task_id=task.task_id, task_type=task.task_type):
                execution = TaskExecution(
                    task_id=task.task_id,
                    workflow_id=task.task_id.split("_")[0],  # Extract workflow ID
                    task_name=task.name,
                    task_type=task.task_type.value,
                    start_time=datetime.now(timezone.utc)
                )
                
                try:
                    # Allocate resources
                    if resources:
                        await _allocate_resources(ctx, task.task_id, resources)
                    
                    # Execute based on task type
                    if task.task_type == "integration":
                        result = await _execute_integration_task(ctx, task)
                    elif task.task_type == "analysis":
                        result = await _execute_analysis_task(ctx, task)
                    else:
                        result = await _execute_generic_task(ctx, task)
                    
                    execution.status = "completed"
                    execution.output_data = result
                    execution.end_time = datetime.now(timezone.utc)
                    execution.execution_time_seconds = (
                        execution.end_time - execution.start_time
                    ).total_seconds()
                    
                except Exception as e:
                    execution.status = "failed"
                    execution.error_message = str(e)
                    execution.end_time = datetime.now(timezone.utc)
                    
                    await ctx.deps.log_event(
                        "task_execution_failed",
                        {
                            "task_id": task.task_id,
                            "error": str(e),
                            "task_type": task.task_type.value
                        }
                    )
                    
                    # Check if retry is needed
                    if execution.retry_count < 3:
                        execution.retry_count += 1
                        raise ModelRetry(f"Task execution failed: {e}. Retrying...")
                
                # Store execution record
                await _store_task_execution(ctx, execution)
                
                return execution
        
        @self.agent.tool
        async def spawn_sub_agent(
            ctx: RunContext[TriadDeps],
            parent_task_id: str,
            sub_agent_type: str,
            specialized_tasks: List[Dict[str, Any]],
            constraints: Dict[str, Any]
        ) -> Dict[str, Any]:
            """Spawn specialized sub-agents for complex task execution."""
            with logfire.span("spawn_sub_agent", parent_task=parent_task_id, sub_type=sub_agent_type):
                # Sub-agents must follow constitutional hierarchy
                sub_agent_id = f"sub_{sub_agent_type}_{uuid.uuid4().hex[:8]}"
                
                # Validate authority to spawn sub-agents
                validation = await ctx.deps.validate_constitutional_decision(
                    ConstitutionalDecision(
                        constitutional_authority=ConstitutionalAuthority.EXECUTIVE,
                        decision_type="execution",
                        description=f"Spawn sub-agent: {sub_agent_type}",
                        constitutional_principles=[
                            ConstitutionalPrinciple.MINISTERIAL_RESPONSIBILITY
                        ],
                        agent_responsible="executor_agent"
                    )
                )
                
                if not validation["constitutional_compliance"]:
                    raise ValueError("Cannot spawn sub-agent: Constitutional violations")
                
                # Create sub-agent configuration
                sub_agent_config = {
                    "sub_agent_id": sub_agent_id,
                    "parent_task_id": parent_task_id,
                    "agent_type": sub_agent_type,
                    "specialized_tasks": specialized_tasks,
                    "constraints": constraints,
                    "constitutional_hierarchy": {
                        "reports_to": "executor_agent",
                        "subject_to_validation": True,
                        "crown_oversight": True
                    },
                    "spawned_at": datetime.now(timezone.utc).isoformat()
                }
                
                # Log sub-agent creation
                await ctx.deps.log_event(
                    "sub_agent_spawned",
                    {
                        "sub_agent_id": sub_agent_id,
                        "parent_task_id": parent_task_id,
                        "agent_type": sub_agent_type,
                        "task_count": len(specialized_tasks)
                    }
                )
                
                # Execute sub-agent tasks
                results = await _execute_sub_agent_tasks(ctx, sub_agent_config)
                
                return {
                    "sub_agent_id": sub_agent_id,
                    "status": "active",
                    "tasks_assigned": len(specialized_tasks),
                    "results": results
                }
        
        @self.agent.tool
        async def manage_resources(
            ctx: RunContext[TriadDeps],
            operation: str,
            resource_type: str,
            amount: float,
            task_id: Optional[str] = None
        ) -> Dict[str, Any]:
            """Manage computational and system resources."""
            with logfire.span("manage_resources", operation=operation, resource_type=resource_type):
                resource_usage = ResourceUsage(
                    resource_type=resource_type,
                    amount_used=amount,
                    task_id=task_id,
                    timestamp=datetime.now(timezone.utc)
                )
                
                if operation == "allocate":
                    # Check resource availability
                    available = await _check_resource_availability(ctx, resource_type, amount)
                    if not available:
                        return {
                            "success": False,
                            "reason": "Insufficient resources",
                            "available": await _get_available_resources(ctx, resource_type)
                        }
                    
                    # Allocate resources
                    await _allocate_resources(ctx, task_id, {resource_type: amount})
                    resource_usage.operation = "allocation"
                    
                elif operation == "release":
                    # Release resources
                    await _release_resources(ctx, task_id, {resource_type: amount})
                    resource_usage.operation = "release"
                    
                elif operation == "monitor":
                    # Monitor resource usage
                    usage_stats = await _monitor_resource_usage(ctx, resource_type)
                    return {
                        "success": True,
                        "usage_stats": usage_stats,
                        "recommendations": await _get_resource_recommendations(ctx, usage_stats)
                    }
                
                # Log resource operation
                await ctx.deps.log_event(
                    "resource_management",
                    {
                        "operation": operation,
                        "resource_type": resource_type,
                        "amount": amount,
                        "task_id": task_id
                    }
                )
                
                return {
                    "success": True,
                    "operation": operation,
                    "resource_usage": resource_usage.model_dump()
                }
        
        @self.agent.tool
        async def defend_execution_decision(
            ctx: RunContext[TriadDeps],
            decision_id: str,
            challenger: str,
            challenge_reason: str
        ) -> str:
            """Defend execution decisions during Question Period."""
            with logfire.span("defend_execution_decision", decision_id=decision_id):
                # Ministerial responsibility requires defending decisions
                defense = await ctx.deps.parliamentary_procedure.ministerial_defense(
                    decision=decision_id,
                    minister="executor_agent",
                    challenger=challenger
                )
                
                await ctx.deps.log_event(
                    "execution_decision_defended",
                    {
                        "decision_id": decision_id,
                        "challenger": challenger,
                        "challenge_reason": challenge_reason,
                        "defense_successful": defense.get("successful", False)
                    }
                )
                
                return defense["defense_statement"]


async def _execute_sequential(
    ctx: RunContext[TriadDeps],
    workflow: WorkflowPlan,
    resources: Optional[Dict[str, Any]]
) -> ExecutionResult:
    """Execute workflow tasks sequentially."""
    execution_result = ExecutionResult(
        workflow_id=workflow.workflow_id,
        start_time=datetime.now(timezone.utc),
        task_executions=[]
    )
    
    for task in workflow.tasks:
        try:
            task_execution = await ctx.tools.execute_task(
                task=task,
                resources=resources
            )
            execution_result.task_executions.append(task_execution)
            
            if task_execution.status == "completed":
                execution_result.tasks_completed += 1
            else:
                execution_result.tasks_failed += 1
                
        except Exception as e:
            execution_result.tasks_failed += 1
            execution_result.errors.append(str(e))
    
    execution_result.end_time = datetime.now(timezone.utc)
    execution_result.total_execution_time = (
        execution_result.end_time - execution_result.start_time
    ).total_seconds()
    execution_result.success = execution_result.tasks_failed == 0
    
    return execution_result


async def _execute_parallel(
    ctx: RunContext[TriadDeps],
    workflow: WorkflowPlan,
    resources: Optional[Dict[str, Any]]
) -> ExecutionResult:
    """Execute workflow tasks in parallel where possible."""
    execution_result = ExecutionResult(
        workflow_id=workflow.workflow_id,
        start_time=datetime.now(timezone.utc),
        task_executions=[]
    )
    
    # Group tasks by dependencies
    task_groups = _group_tasks_by_dependencies(workflow)
    
    for group in task_groups:
        # Execute tasks in group concurrently
        tasks = []
        for task in group:
            tasks.append(
                ctx.tools.execute_task(
                    task=task,
                    resources=resources
                )
            )
        
        # Wait for all tasks in group to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, TaskExecution):
                execution_result.task_executions.append(result)
                if result.status == "completed":
                    execution_result.tasks_completed += 1
                else:
                    execution_result.tasks_failed += 1
            else:
                execution_result.tasks_failed += 1
                execution_result.errors.append(str(result))
    
    execution_result.end_time = datetime.now(timezone.utc)
    execution_result.total_execution_time = (
        execution_result.end_time - execution_result.start_time
    ).total_seconds()
    execution_result.success = execution_result.tasks_failed == 0
    
    return execution_result


def _group_tasks_by_dependencies(workflow: WorkflowPlan) -> List[List[WorkflowTask]]:
    """Group tasks based on their dependencies for parallel execution."""
    # Simple implementation: group tasks with no dependencies first
    groups = []
    remaining_tasks = workflow.tasks.copy()
    completed_task_ids = set()
    
    while remaining_tasks:
        current_group = []
        
        for task in remaining_tasks[:]:
            # Check if all dependencies are satisfied
            dependencies = workflow.get_task_dependencies(task.task_id)
            can_execute = True
            
            for dep in dependencies:
                if dep.to_task_id == task.task_id and dep.from_task_id not in completed_task_ids:
                    can_execute = False
                    break
            
            if can_execute:
                current_group.append(task)
                remaining_tasks.remove(task)
                completed_task_ids.add(task.task_id)
        
        if current_group:
            groups.append(current_group)
        else:
            # Handle circular dependencies or other issues
            groups.append(remaining_tasks)
            break
    
    return groups


async def _execute_integration_task(
    ctx: RunContext[TriadDeps],
    task: WorkflowTask
) -> Dict[str, Any]:
    """Execute integration tasks using MCP."""
    system_type = task.input_parameters.get("system_type", "generic")
    operation = task.input_parameters.get("operation", "query")
    parameters = task.input_parameters.get("parameters", {})
    
    result = await ctx.deps.integrate_external_system(
        system_type=system_type,
        operation=operation,
        parameters=parameters
    )
    
    return {
        "integration_result": result,
        "system_type": system_type,
        "operation": operation
    }


async def _execute_analysis_task(
    ctx: RunContext[TriadDeps],
    task: WorkflowTask
) -> Dict[str, Any]:
    """Execute analysis tasks."""
    # Placeholder for analysis task execution
    return {
        "analysis_complete": True,
        "task_name": task.name,
        "results": "Analysis results placeholder"
    }


async def _execute_generic_task(
    ctx: RunContext[TriadDeps],
    task: WorkflowTask
) -> Dict[str, Any]:
    """Execute generic tasks."""
    # Placeholder for generic task execution
    return {
        "task_complete": True,
        "task_name": task.name,
        "task_type": task.task_type.value
    }


async def _allocate_resources(
    ctx: RunContext[TriadDeps],
    task_id: str,
    resources: Dict[str, Any]
) -> None:
    """Allocate resources for task execution."""
    # Placeholder for resource allocation
    pass


async def _release_resources(
    ctx: RunContext[TriadDeps],
    task_id: str,
    resources: Dict[str, Any]
) -> None:
    """Release resources after task completion."""
    # Placeholder for resource release
    pass


async def _check_resource_availability(
    ctx: RunContext[TriadDeps],
    resource_type: str,
    amount: float
) -> bool:
    """Check if resources are available."""
    # Placeholder - return true for now
    return True


async def _get_available_resources(
    ctx: RunContext[TriadDeps],
    resource_type: str
) -> float:
    """Get available resources of a specific type."""
    # Placeholder
    return 100.0


async def _monitor_resource_usage(
    ctx: RunContext[TriadDeps],
    resource_type: str
) -> Dict[str, Any]:
    """Monitor resource usage statistics."""
    # Placeholder
    return {
        "current_usage": 50.0,
        "peak_usage": 75.0,
        "average_usage": 60.0
    }


async def _get_resource_recommendations(
    ctx: RunContext[TriadDeps],
    usage_stats: Dict[str, Any]
) -> List[str]:
    """Get resource optimization recommendations."""
    recommendations = []
    
    if usage_stats.get("peak_usage", 0) > 80:
        recommendations.append("Consider increasing resource allocation")
    
    if usage_stats.get("average_usage", 0) < 30:
        recommendations.append("Resources may be over-allocated")
    
    return recommendations


async def _execute_sub_agent_tasks(
    ctx: RunContext[TriadDeps],
    sub_agent_config: Dict[str, Any]
) -> Dict[str, Any]:
    """Execute tasks assigned to sub-agents."""
    # Placeholder for sub-agent task execution
    return {
        "tasks_completed": len(sub_agent_config["specialized_tasks"]),
        "sub_agent_id": sub_agent_config["sub_agent_id"],
        "status": "completed"
    }


async def _store_task_execution(
    ctx: RunContext[TriadDeps],
    execution: TaskExecution
) -> None:
    """Store task execution record in database."""
    await ctx.deps.db_session.execute(
        """
        INSERT INTO task_executions (
            task_id, workflow_id, task_name, task_type, status,
            start_time, end_time, execution_time_seconds,
            input_parameters, output_data, error_message,
            retry_count, constitutional_authority
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
        """,
        execution.task_id,
        execution.workflow_id,
        execution.task_name,
        execution.task_type,
        execution.status,
        execution.start_time,
        execution.end_time,
        execution.execution_time_seconds,
        execution.input_parameters,
        execution.output_data,
        execution.error_message,
        execution.retry_count,
        "executive"
    )
    await ctx.deps.db_session.commit()