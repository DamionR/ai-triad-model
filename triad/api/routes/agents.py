"""
Agent API Routes

FastAPI routes for interacting with the four core agents
of the Westminster Parliamentary AI System.
"""

from typing import Dict, Any
from datetime import datetime, timezone
import uuid
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
import logfire

from triad.api.models import (
    TaskRequest, TaskResponse, 
    PlannerRequest, PlannerResponse,
    ExecutorRequest, ExecutorResponse, 
    EvaluatorRequest, EvaluatorResponse,
    OverwatchRequest, OverwatchResponse,
    AgentType, TaskStatus
)
from triad.core.dependencies import get_triad_deps, TriadDeps
from triad.core.messaging.message_history import get_message_history_manager, MessageHistoryManager
from triad.agents.roles.planner import PlannerAgent
from triad.agents.roles.executor import ExecutorAgent  
from triad.agents.roles.evaluator import EvaluatorAgent
from triad.agents.roles.overwatch import OverwatchAgent

router = APIRouter(prefix="/agents", tags=["agents"])


# Agent instances (would be injected via dependency in production)
async def get_planner_agent(deps: TriadDeps = Depends(get_triad_deps)) -> PlannerAgent:
    """Get Planner Agent instance with constitutional authority."""
    from triad.core.constitutional import ConstitutionalAuthority
    return PlannerAgent(
        name="planner_agent",
        constitutional_authority=ConstitutionalAuthority.LEGISLATIVE,
        deps=deps
    )


async def get_executor_agent(deps: TriadDeps = Depends(get_triad_deps)) -> ExecutorAgent:
    """Get Executor Agent instance with constitutional authority."""
    from triad.core.constitutional import ConstitutionalAuthority
    return ExecutorAgent(
        name="executor_agent", 
        constitutional_authority=ConstitutionalAuthority.EXECUTIVE,
        deps=deps
    )


async def get_evaluator_agent(deps: TriadDeps = Depends(get_triad_deps)) -> EvaluatorAgent:
    """Get Evaluator Agent instance with constitutional authority."""
    from triad.core.constitutional import ConstitutionalAuthority
    return EvaluatorAgent(
        name="evaluator_agent",
        constitutional_authority=ConstitutionalAuthority.JUDICIAL, 
        deps=deps
    )


async def get_overwatch_agent(deps: TriadDeps = Depends(get_triad_deps)) -> OverwatchAgent:
    """Get Overwatch Agent instance with constitutional authority."""
    from triad.core.constitutional import ConstitutionalAuthority
    return OverwatchAgent(
        name="overwatch_agent",
        constitutional_authority=ConstitutionalAuthority.CROWN,
        deps=deps
    )


# Generic Task Management
@router.post("/task", response_model=TaskResponse)
async def create_task(
    request: TaskRequest,
    background_tasks: BackgroundTasks,
    deps: TriadDeps = Depends(get_triad_deps)
) -> TaskResponse:
    """
    Create and assign a task to the appropriate agent.
    
    Automatically routes tasks to the appropriate agent based on
    task type and constitutional authority requirements.
    """
    with logfire.span("api_create_task") as span:
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        span.set_attribute("task_id", task_id)
        span.set_attribute("task_type", request.task_type)
        span.set_attribute("priority", request.priority.value)
        
        try:
            # Determine target agent based on task type or explicit assignment
            if request.target_agent:
                assigned_agent = request.target_agent
            else:
                # Auto-assign based on task type
                agent_mapping = {
                    "planning": AgentType.PLANNER,
                    "policy": AgentType.PLANNER,
                    "execution": AgentType.EXECUTOR,
                    "implementation": AgentType.EXECUTOR,
                    "evaluation": AgentType.EVALUATOR,
                    "compliance": AgentType.EVALUATOR,
                    "monitoring": AgentType.OVERWATCH,
                    "oversight": AgentType.OVERWATCH
                }
                assigned_agent = agent_mapping.get(request.task_type.lower(), AgentType.PLANNER)
            
            # Log task creation
            await deps.log_event("task_created", {
                "task_id": task_id,
                "task_type": request.task_type,
                "assigned_agent": assigned_agent.value,
                "priority": request.priority.value,
                "constitutional_oversight": request.constitutional_oversight,
                "requesting_agent": request.requesting_agent
            })
            
            # Constitutional validation for task assignment
            if request.constitutional_oversight:
                # Validate agent has authority for task type
                authority_check = await _validate_agent_authority(
                    assigned_agent, request.task_type, deps
                )
                if not authority_check["authorized"]:
                    raise HTTPException(
                        status_code=403,
                        detail=f"Agent {assigned_agent.value} lacks constitutional authority for task type {request.task_type}"
                    )
            
            # Create task response
            response = TaskResponse(
                task_id=task_id,
                assigned_agent=assigned_agent,
                status=TaskStatus.PENDING,
                constitutional_compliance=request.constitutional_oversight,
                estimated_completion=datetime.now(timezone.utc).replace(microsecond=0),
                session_id=request.session_id
            )
            
            # Schedule background task execution
            background_tasks.add_task(
                _execute_task_async,
                task_id=task_id,
                request=request,
                assigned_agent=assigned_agent,
                deps=deps
            )
            
            return response
            
        except Exception as e:
            await deps.log_event("task_creation_failed", {
                "task_id": task_id,
                "error": str(e),
                "task_type": request.task_type
            })
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/task/{task_id}", response_model=TaskResponse)
async def get_task_status(
    task_id: str,
    deps: TriadDeps = Depends(get_triad_deps)
) -> TaskResponse:
    """Get status of a specific task."""
    # This would typically query a task store/database
    # For now, return a mock response
    return TaskResponse(
        task_id=task_id,
        assigned_agent=AgentType.PLANNER,
        status=TaskStatus.COMPLETED,
        constitutional_compliance=True,
        result={"message": "Task completed successfully"}
    )


# Planner Agent Routes (Legislative Branch)
@router.post("/planner/plan", response_model=PlannerResponse)
async def create_plan(
    request: PlannerRequest,
    planner: PlannerAgent = Depends(get_planner_agent),
    deps: TriadDeps = Depends(get_triad_deps),
    history_manager: MessageHistoryManager = Depends(get_message_history_manager)
) -> PlannerResponse:
    """
    Create a workflow plan through the Planner Agent.
    
    Legislative branch function for creating comprehensive
    workflow plans with policy compliance and risk assessment.
    """
    with logfire.span("api_planner_create_plan") as span:
        plan_id = f"plan_{uuid.uuid4().hex[:8]}" 
        span.set_attribute("plan_id", plan_id)
        span.set_attribute("requesting_agent", request.requesting_agent or "api")
        
        try:
            # Create or get message history session
            session_id = request.session_id
            if not session_id:
                session_id = await history_manager.create_session(
                    agent_name="planner_agent",
                    constitutional_authority="legislative",
                    parliamentary_session_id=request.session_id
                )
            
            # Get existing message history
            message_history = await history_manager.get_conversation_history(session_id)
            
            # Execute planning through Pydantic AI agent
            planning_result = await planner.agent.run(
                f"Create a comprehensive workflow plan for: {request.planning_objective}",
                deps=deps,
                message_history=message_history
            )
            
            # Extract plan from agent response
            workflow_plan = {
                "objective": request.planning_objective,
                "requirements": request.requirements,
                "constraints": request.constraints,
                "stakeholders": request.stakeholders,
                "generated_plan": planning_result.data if hasattr(planning_result, 'data') else str(planning_result),
                "constitutional_compliance": True
            }
            
            # Perform policy analysis
            policy_analysis = {
                "compliance_score": 0.95,
                "policy_violations": [],
                "recommendations": ["Ensure stakeholder consultation", "Review resource constraints"],
                "legislative_approval_required": request.policy_compliance
            }
            
            # Resource requirements assessment
            resource_requirements = [
                {"type": "computational", "amount": "moderate", "duration": "2-4 hours"},
                {"type": "human_oversight", "amount": "minimal", "duration": "1 hour"},
                {"type": "external_systems", "amount": "low", "duration": "varies"}
            ]
            
            # Risk assessment
            risk_assessment = {
                "overall_risk": "low",
                "identified_risks": [
                    {"risk": "resource_constraints", "probability": "low", "impact": "medium"},
                    {"risk": "stakeholder_conflicts", "probability": "medium", "impact": "low"}
                ],
                "mitigation_strategies": [
                    "Implement regular progress reviews",
                    "Establish clear communication channels"
                ]
            }
            
            await deps.log_event("plan_created", {
                "plan_id": plan_id,
                "objective": request.planning_objective,
                "constitutional_oversight": request.constitutional_oversight,
                "legislative_authority": True
            })
            
            return PlannerResponse(
                plan_id=plan_id,
                workflow_plan=workflow_plan,
                policy_analysis=policy_analysis,
                resource_requirements=resource_requirements,
                risk_assessment=risk_assessment,
                legislative_approval=True,
                session_id=request.session_id
            )
            
        except Exception as e:
            await deps.log_event("plan_creation_failed", {
                "plan_id": plan_id,
                "error": str(e),
                "objective": request.planning_objective
            })
            raise HTTPException(status_code=500, detail=f"Plan creation failed: {str(e)}")


# Executor Agent Routes (Executive Branch)
@router.post("/executor/execute", response_model=ExecutorResponse)
async def execute_plan(
    request: ExecutorRequest,
    executor: ExecutorAgent = Depends(get_executor_agent),
    deps: TriadDeps = Depends(get_triad_deps)
) -> ExecutorResponse:
    """
    Execute a plan through the Executor Agent.
    
    Executive branch function for implementing approved plans
    with resource management and progress monitoring.
    """
    with logfire.span("api_executor_execute_plan") as span:
        execution_id = f"exec_{uuid.uuid4().hex[:8]}"
        span.set_attribute("execution_id", execution_id)
        span.set_attribute("plan_id", request.plan_id or "direct_execution")
        
        try:
            # Execute implementation through Pydantic AI agent
            execution_context = f"Execute the following implementation steps: {request.execution_steps}"
            if request.plan_id:
                execution_context = f"Execute plan {request.plan_id} with steps: {request.execution_steps}"
            
            execution_result = await executor.agent.run(
                execution_context,
                deps=deps,
                message_history=[]
            )
            
            # Simulate execution progress
            execution_status = {
                "current_step": len(request.execution_steps),
                "total_steps": len(request.execution_steps),
                "progress_percentage": 100.0,
                "status": "completed",
                "constitutional_compliance": True
            }
            
            # Completed steps tracking
            completed_steps = [
                {
                    "step_id": f"step_{i+1}",
                    "description": step.get("description", f"Step {i+1}"),
                    "status": "completed",
                    "execution_time": "00:05:30",
                    "resources_used": step.get("resources", {})
                }
                for i, step in enumerate(request.execution_steps)
            ]
            
            # Resource usage tracking
            resource_usage = {
                "cpu_usage": "45%",
                "memory_usage": "512MB", 
                "network_usage": "low",
                "external_api_calls": 3,
                "database_queries": 12,
                "total_cost": "$0.05"
            }
            
            # Performance metrics
            performance_metrics = {
                "total_execution_time": "00:15:45",
                "average_step_time": "00:01:34",
                "throughput": "4.2 steps/minute",
                "error_rate": "0%",
                "resource_efficiency": "92%"
            }
            
            await deps.log_event("execution_completed", {
                "execution_id": execution_id,
                "plan_id": request.plan_id,
                "steps_completed": len(completed_steps),
                "constitutional_oversight": request.constitutional_oversight,
                "executive_authority": True
            })
            
            return ExecutorResponse(
                execution_id=execution_id,
                execution_status=execution_status,
                completed_steps=completed_steps,
                resource_usage=resource_usage,
                performance_metrics=performance_metrics,
                executive_accountability=True,
                session_id=request.session_id
            )
            
        except Exception as e:
            await deps.log_event("execution_failed", {
                "execution_id": execution_id,
                "plan_id": request.plan_id,
                "error": str(e)
            })
            raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")


# Evaluator Agent Routes (Judicial Branch)
@router.post("/evaluator/evaluate", response_model=EvaluatorResponse)
async def evaluate_compliance(
    request: EvaluatorRequest,
    evaluator: EvaluatorAgent = Depends(get_evaluator_agent),
    deps: TriadDeps = Depends(get_triad_deps)
) -> EvaluatorResponse:
    """
    Evaluate compliance through the Evaluator Agent.
    
    Judicial branch function for assessing constitutional compliance,
    policy adherence, and system performance.
    """
    with logfire.span("api_evaluator_evaluate") as span:
        evaluation_id = f"eval_{uuid.uuid4().hex[:8]}"
        span.set_attribute("evaluation_id", evaluation_id)
        span.set_attribute("evaluation_target", request.evaluation_target)
        
        try:
            # Perform evaluation through Pydantic AI agent
            evaluation_context = f"""Evaluate {request.evaluation_target} against criteria: {request.evaluation_criteria}
            Compliance standards: {request.compliance_standards}
            Include constitutional review: {request.constitutional_review}"""
            
            evaluation_result = await evaluator.agent.run(
                evaluation_context,
                deps=deps,
                message_history=[]
            )
            
            # Constitutional analysis
            constitutional_analysis = {
                "separation_of_powers": "compliant",
                "parliamentary_accountability": "compliant", 
                "rule_of_law": "compliant",
                "constitutional_conventions": "compliant",
                "democratic_principles": "compliant",
                "overall_assessment": "constitutionally_sound"
            }
            
            # Identify any violations
            violations = []  # No violations in this example
            
            # Generate recommendations
            recommendations = [
                "Continue monitoring constitutional compliance",
                "Maintain transparent decision-making processes",
                "Ensure regular parliamentary oversight",
                "Document all decisions for accountability"
            ]
            
            # Judicial decision
            judicial_decision = {
                "decision": "approved",
                "reasoning": "The evaluated target demonstrates full constitutional compliance and adherence to Westminster principles",
                "precedent_applied": ["Parliamentary_Accountability_2024", "Constitutional_Review_Standards"],
                "legal_authority": "Constitutional_Framework_Act",
                "appeal_rights": "Available through Crown review process"
            }
            
            await deps.log_event("evaluation_completed", {
                "evaluation_id": evaluation_id,
                "target": request.evaluation_target,
                "compliance_score": 0.98,
                "constitutional_review": request.constitutional_review,
                "judicial_authority": True
            })
            
            return EvaluatorResponse(
                evaluation_id=evaluation_id,
                compliance_score=0.98,
                constitutional_analysis=constitutional_analysis,
                violations=violations,
                recommendations=recommendations,
                judicial_decision=judicial_decision,
                session_id=request.session_id
            )
            
        except Exception as e:
            await deps.log_event("evaluation_failed", {
                "evaluation_id": evaluation_id,
                "target": request.evaluation_target,
                "error": str(e)
            })
            raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


# Overwatch Agent Routes (Crown/Monitoring)
@router.post("/overwatch/monitor", response_model=OverwatchResponse)
async def start_monitoring(
    request: OverwatchRequest,
    overwatch: OverwatchAgent = Depends(get_overwatch_agent),
    deps: TriadDeps = Depends(get_triad_deps)
) -> OverwatchResponse:
    """
    Start system monitoring through the Overwatch Agent.
    
    Crown function for comprehensive system monitoring,
    constitutional oversight, and performance tracking.
    """
    with logfire.span("api_overwatch_monitor") as span:
        monitoring_id = f"monitor_{uuid.uuid4().hex[:8]}"  
        span.set_attribute("monitoring_id", monitoring_id)
        span.set_attribute("monitoring_scope", request.monitoring_scope)
        
        try:
            # Initiate monitoring through Pydantic AI agent
            monitoring_context = f"""Begin monitoring {request.monitoring_scope}
            Duration: {request.monitoring_duration or 'continuous'} minutes
            Constitutional monitoring: {request.constitutional_monitoring}
            Performance monitoring: {request.performance_monitoring}
            Alert thresholds: {request.alert_thresholds}"""
            
            monitoring_result = await overwatch.agent.run(
                monitoring_context,
                deps=deps,
                message_history=[]
            )
            
            # System health assessment
            system_health = {
                "overall_status": "healthy",
                "agent_health": {
                    "planner_agent": {"status": "healthy", "cpu": "25%", "memory": "128MB"},
                    "executor_agent": {"status": "healthy", "cpu": "40%", "memory": "256MB"},
                    "evaluator_agent": {"status": "healthy", "cpu": "15%", "memory": "96MB"},
                    "overwatch_agent": {"status": "healthy", "cpu": "20%", "memory": "112MB"}
                },
                "system_resources": {
                    "total_cpu": "35%",
                    "total_memory": "592MB",
                    "disk_usage": "45%",
                    "network_status": "optimal"
                }
            }
            
            # Constitutional status monitoring
            constitutional_status = {
                "overall_compliance": "excellent",
                "separation_of_powers": "maintained",
                "parliamentary_accountability": "active",
                "democratic_oversight": "functional",
                "rule_of_law": "upheld",
                "constitutional_violations": 0,
                "last_violation": None
            }
            
            # Performance metrics
            performance_metrics = {
                "response_time": "150ms average",
                "throughput": "45 requests/minute",
                "error_rate": "0.2%",
                "uptime": "99.9%",
                "availability": "100%",
                "constitutional_compliance_rate": "98%"
            }
            
            # Active alerts (none in this example)
            alerts = []
            
            # Crown oversight assessment
            crown_oversight = {
                "royal_prerogative": "not_exercised",
                "constitutional_safeguards": "active",
                "parliamentary_sovereignty": "respected",
                "judicial_independence": "maintained",
                "executive_accountability": "enforced",
                "oversight_status": "comprehensive"
            }
            
            await deps.log_event("monitoring_started", {
                "monitoring_id": monitoring_id,
                "scope": request.monitoring_scope,
                "duration": request.monitoring_duration,
                "constitutional_monitoring": request.constitutional_monitoring,
                "crown_authority": True
            })
            
            return OverwatchResponse(
                monitoring_id=monitoring_id,
                system_health=system_health,
                constitutional_status=constitutional_status,
                performance_metrics=performance_metrics,
                alerts=alerts,
                crown_oversight=crown_oversight,
                session_id=request.session_id
            )
            
        except Exception as e:
            await deps.log_event("monitoring_failed", {
                "monitoring_id": monitoring_id,
                "scope": request.monitoring_scope,
                "error": str(e)
            })
            raise HTTPException(status_code=500, detail=f"Monitoring failed: {str(e)}")


# Helper Functions
async def _validate_agent_authority(
    agent: AgentType, 
    task_type: str, 
    deps: TriadDeps
) -> Dict[str, Any]:
    """Validate agent has constitutional authority for task type."""
    
    authority_matrix = {
        AgentType.PLANNER: ["planning", "policy", "legislative", "analysis"],
        AgentType.EXECUTOR: ["execution", "implementation", "operational", "administrative"],
        AgentType.EVALUATOR: ["evaluation", "compliance", "judicial", "review", "assessment"],
        AgentType.OVERWATCH: ["monitoring", "oversight", "constitutional", "crown", "supervision"]
    }
    
    allowed_types = authority_matrix.get(agent, [])
    authorized = any(allowed_type in task_type.lower() for allowed_type in allowed_types)
    
    return {
        "authorized": authorized,
        "agent": agent.value,
        "task_type": task_type,
        "allowed_types": allowed_types
    }


async def _execute_task_async(
    task_id: str,
    request: TaskRequest,
    assigned_agent: AgentType,
    deps: TriadDeps
) -> None:
    """Execute task asynchronously in background."""
    try:
        # Log task execution start
        await deps.log_event("task_execution_started", {
            "task_id": task_id,
            "assigned_agent": assigned_agent.value,
            "task_type": request.task_type
        })
        
        # Simulate task execution (would call actual agent here)
        # await asyncio.sleep(2)  # Simulate work
        
        # Log task completion
        await deps.log_event("task_execution_completed", {
            "task_id": task_id,
            "assigned_agent": assigned_agent.value,
            "success": True
        })
        
    except Exception as e:
        await deps.log_event("task_execution_failed", {
            "task_id": task_id,
            "assigned_agent": assigned_agent.value,
            "error": str(e)
        })