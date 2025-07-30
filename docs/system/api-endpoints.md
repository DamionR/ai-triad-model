# Constitutional API Endpoints and Parliamentary FastAPI Integration

## Overview

The AI Triad backend exposes RESTful APIs through FastAPI with **complete Westminster parliamentary authentication and authorization**. All API endpoints follow constitutional principles including **parliamentary authentication**, **question period interfaces**, **collective responsibility validation**, and **Crown authority verification** while maintaining type safety and comprehensive validation using Pydantic models.

## 🏛️ Constitutional API Architecture

### Parliamentary Authentication System

```python
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from enum import Enum

class ConstitutionalAuthority(str, Enum):
    """Westminster constitutional authority levels for API access."""
    LEGISLATIVE = "legislative"  # Planner agent authority
    EXECUTIVE = "executive"      # Executor agent authority  
    JUDICIAL = "judicial"        # Evaluator agent authority
    CROWN = "crown"             # Overwatch agent authority
    PARLIAMENTARY = "parliamentary"  # General parliamentary access
    PUBLIC = "public"           # Public/citizen access

class ParliamentarySecurityContext(BaseModel):
    """Security context with Westminster constitutional authority."""
    user_id: str
    constitutional_authority: ConstitutionalAuthority
    parliamentary_session_id: str
    agent_role: Optional[str] = None
    can_question: bool = True  # Question Period rights
    can_vote_confidence: bool = False  # No-confidence vote rights
    crown_reserve_powers: bool = False  # Crown reserve power access
    
async def verify_constitutional_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> ParliamentarySecurityContext:
    """Verify JWT token with Westminster constitutional validation."""
    
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        
        # Validate constitutional authority
        constitutional_authority = ConstitutionalAuthority(
            payload.get("constitutional_authority", "public")
        )
        
        return ParliamentarySecurityContext(
            user_id=payload["user_id"],
            constitutional_authority=constitutional_authority,
            parliamentary_session_id=payload.get("parliamentary_session", "default"),
            agent_role=payload.get("agent_role"),
            can_question=payload.get("can_question", True),
            can_vote_confidence=payload.get("can_vote_confidence", False),
            crown_reserve_powers=payload.get("crown_reserve_powers", False)
        )
        
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid constitutional credentials"
        )
```

## FastAPI Application Structure

### Main Application Setup

```python
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio
from contextlib import asynccontextmanager

from .dependencies import create_production_dependencies, TriadDeps
from .agents import planner_agent, executor_agent, evaluator_agent, overwatch_agent
from .models import *

# Lifespan management for dependencies
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.deps = await create_production_dependencies()
    yield
    # Shutdown
    await app.state.deps.close()

app = FastAPI(
    title="AI Triad Constitutional Parliamentary API",
    description="Westminster parliamentary AI system with constitutional governance, democratic accountability, and transparent decision-making",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Parliamentary Procedures",
            "description": "Question Period, votes of confidence, collective responsibility"
        },
        {
            "name": "Legislative Branch",
            "description": "Planner Agent operations and parliamentary planning procedures"
        },
        {
            "name": "Executive Branch", 
            "description": "Executor Agent operations and ministerial responsibility"
        },
        {
            "name": "Judicial Branch",
            "description": "Evaluator Agent operations and constitutional review"
        },
        {
            "name": "Crown Authority",
            "description": "Overwatch Agent operations and Crown reserve powers"
        },
        {
            "name": "Constitutional Crisis",
            "description": "Emergency procedures and constitutional crisis management"
        }
    ]
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "*.yourdomain.com"]
)

# Security
security = HTTPBearer()

async def get_deps() -> TriadDeps:
    """Get application dependencies."""
    return app.state.deps

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify JWT token and return user ID."""
    # Implement JWT token verification
    # Return user_id or raise HTTPException(401)
    pass
```

### Request/Response Models

```python
# Base Models
class BaseRequest(BaseModel):
    """Base request model with common fields."""
    request_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)

class BaseResponse(BaseModel):
    """Base response model with common fields."""
    success: bool
    message: str
    request_id: str
    timestamp: datetime
    execution_time: Optional[float] = None

# Planner API Models
class CreateWorkflowRequest(BaseRequest):
    name: str = Field(..., description="Workflow name")
    description: str = Field(..., description="Detailed workflow description")
    requirements: str = Field(..., description="Workflow requirements in natural language")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Workflow constraints")
    priority: WorkflowPriority = Field(default=WorkflowPriority.MEDIUM)
    deadline: Optional[datetime] = None

class CreateWorkflowResponse(BaseResponse):
    workflow_plan: WorkflowPlan
    estimated_duration: int
    resource_requirements: ResourceRequirements

class OptimizeWorkflowRequest(BaseRequest):
    workflow_id: str
    optimization_criteria: List[str] = Field(default=["performance", "cost", "accuracy"])

class OptimizeWorkflowResponse(BaseResponse):
    original_plan: WorkflowPlan
    optimized_plan: WorkflowPlan
    optimization_report: OptimizationReport

# Executor API Models
class ExecuteWorkflowRequest(BaseRequest):
    workflow_id: str
    execution_parameters: Dict[str, Any] = Field(default_factory=dict)
    async_execution: bool = Field(default=True, description="Execute workflow asynchronously")

class ExecuteWorkflowResponse(BaseResponse):
    execution_id: str
    status: ExecutionStatus
    estimated_completion: Optional[datetime] = None

class ExecuteTaskRequest(BaseRequest):
    task_id: str
    task_parameters: Dict[str, Any] = Field(default_factory=dict)
    override_timeout: Optional[int] = None

class ExecuteTaskResponse(BaseResponse):
    execution_result: ExecutionResult

class GetExecutionStatusRequest(BaseRequest):
    execution_id: str

class GetExecutionStatusResponse(BaseResponse):
    execution_status: ExecutionStatus
    progress_percentage: float
    current_task: Optional[str] = None
    completed_tasks: List[str]
    failed_tasks: List[str]
    logs: List[str]

# Evaluator API Models
class ValidateResultRequest(BaseRequest):
    execution_id: str
    validation_criteria: List[str] = Field(default=["accuracy", "performance", "compliance"])
    custom_rules: List[ValidationRule] = Field(default_factory=list)

class ValidateResultResponse(BaseResponse):
    validation_report: ValidationReport
    recommendations: List[str]
    compliance_status: ComplianceStatus

class BenchmarkPerformanceRequest(BaseRequest):
    execution_id: str
    benchmark_type: BenchmarkType = Field(default=BenchmarkType.HISTORICAL)
    comparison_period: str = Field(default="30d")

class BenchmarkPerformanceResponse(BaseResponse):
    benchmark_report: BenchmarkReport
    performance_score: float
    ranking: Optional[int] = None

# Overwatch API Models
class GetSystemHealthRequest(BaseRequest):
    include_detailed_metrics: bool = Field(default=False)
    component_filter: Optional[List[str]] = None

class GetSystemHealthResponse(BaseResponse):
    system_health: SystemHealth
    alerts: List[Alert]
    recommendations: List[str]

class GetPerformanceReportRequest(BaseRequest):
    time_range: str = Field(..., description="Time range (e.g., '1h', '1d', '1w')")
    metrics: List[str] = Field(default=["success_rate", "execution_time", "error_rate"])
    group_by: Optional[str] = Field(default="agent")

class GetPerformanceReportResponse(BaseResponse):
    performance_report: PerformanceReport
    trends: TrendAnalysis
    insights: List[str]
```

## API Endpoints

### 1. Planner Agent Endpoints

```python
from fastapi import APIRouter, BackgroundTasks

planner_router = APIRouter(prefix="/api/v1/planner", tags=["planner"])

@planner_router.post("/workflows", response_model=CreateWorkflowResponse)
async def create_workflow(
    request: CreateWorkflowRequest,
    background_tasks: BackgroundTasks,
    deps: TriadDeps = Depends(get_deps),
    user_id: str = Depends(verify_token)
):
    """Create a new workflow plan using the Planner agent."""
    start_time = time.time()
    
    try:
        # Log request
        await deps.log_event("workflow_creation_requested", {
            "user_id": user_id,
            "workflow_name": request.name,
            "request_id": request.request_id
        })
        
        # Run Planner agent
        result = await planner_agent.run(
            f"""Create workflow plan:
            Name: {request.name}
            Description: {request.description}
            Requirements: {request.requirements}
            Constraints: {request.constraints}
            Priority: {request.priority}
            Deadline: {request.deadline}
            """,
            deps=deps
        )
        
        workflow_plan = result.output
        execution_time = time.time() - start_time
        
        # Store workflow in database
        background_tasks.add_task(
            store_workflow_plan,
            workflow_plan,
            user_id,
            deps
        )
        
        return CreateWorkflowResponse(
            success=True,
            message="Workflow plan created successfully",
            request_id=request.request_id,
            timestamp=datetime.now(timezone.utc),
            execution_time=execution_time,
            workflow_plan=workflow_plan,
            estimated_duration=workflow_plan.estimated_duration,
            resource_requirements=workflow_plan.resource_requirements
        )
        
    except Exception as e:
        await deps.log_event("workflow_creation_failed", {
            "user_id": user_id,
            "error": str(e),
            "request_id": request.request_id
        })
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create workflow: {str(e)}"
        )

@planner_router.post("/workflows/{workflow_id}/optimize", response_model=OptimizeWorkflowResponse)
async def optimize_workflow(
    workflow_id: str,
    request: OptimizeWorkflowRequest,
    deps: TriadDeps = Depends(get_deps),
    user_id: str = Depends(verify_token)
):
    """Optimize an existing workflow plan."""
    start_time = time.time()
    
    try:
        # Get existing workflow
        workflow = await get_workflow_by_id(workflow_id, deps)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Run optimization
        result = await planner_agent.run(
            f"""Optimize workflow:
            Original Plan: {workflow.to_json()}
            Optimization Criteria: {request.optimization_criteria}
            """,
            deps=deps
        )
        
        optimized_plan = result.output
        execution_time = time.time() - start_time
        
        return OptimizeWorkflowResponse(
            success=True,
            message="Workflow optimized successfully",
            request_id=request.request_id,
            timestamp=datetime.now(timezone.utc),
            execution_time=execution_time,
            original_plan=workflow,
            optimized_plan=optimized_plan,
            optimization_report=await generate_optimization_report(workflow, optimized_plan)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to optimize workflow: {str(e)}"
        )

@planner_router.get("/workflows", response_model=List[WorkflowSummary])
async def list_workflows(
    limit: int = 10,
    offset: int = 0,
    status_filter: Optional[str] = None,
    deps: TriadDeps = Depends(get_deps),
    user_id: str = Depends(verify_token)
):
    """List workflows for the authenticated user."""
    workflows = await get_user_workflows(user_id, limit, offset, status_filter, deps)
    return workflows

@planner_router.get("/workflows/{workflow_id}", response_model=WorkflowDetail)
async def get_workflow(
    workflow_id: str,
    deps: TriadDeps = Depends(get_deps),
    user_id: str = Depends(verify_token)
):
    """Get detailed workflow information."""
    workflow = await get_workflow_detail(workflow_id, user_id, deps)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow
```

### 2. Executor Agent Endpoints

```python
executor_router = APIRouter(prefix="/api/v1/executor", tags=["executor"])

@executor_router.post("/execute", response_model=ExecuteWorkflowResponse)
async def execute_workflow(
    request: ExecuteWorkflowRequest,
    background_tasks: BackgroundTasks,
    deps: TriadDeps = Depends(get_deps),
    user_id: str = Depends(verify_token)
):
    """Execute a workflow using the Executor agent."""
    start_time = time.time()
    
    try:
        # Get workflow plan
        workflow = await get_workflow_by_id(request.workflow_id, deps)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Create execution record
        execution_id = str(uuid.uuid4())
        
        if request.async_execution:
            # Start async execution
            background_tasks.add_task(
                execute_workflow_async,
                execution_id,
                workflow,
                request.execution_parameters,
                deps
            )
            
            estimated_completion = datetime.now(timezone.utc) + timedelta(seconds=workflow.estimated_duration)
            
            return ExecuteWorkflowResponse(
                success=True,
                message="Workflow execution started",
                request_id=request.request_id,
                timestamp=datetime.now(timezone.utc),
                execution_time=time.time() - start_time,
                execution_id=execution_id,
                status=ExecutionStatus.RUNNING,
                estimated_completion=estimated_completion
            )
        else:
            # Synchronous execution
            result = await executor_agent.run(
                f"""Execute workflow:
                Workflow: {workflow.to_json()}
                Parameters: {request.execution_parameters}
                """,
                deps=deps
            )
            
            execution_time = time.time() - start_time
            
            return ExecuteWorkflowResponse(
                success=True,
                message="Workflow executed successfully",
                request_id=request.request_id,
                timestamp=datetime.now(timezone.utc),
                execution_time=execution_time,
                execution_id=execution_id,
                status=ExecutionStatus.COMPLETED
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute workflow: {str(e)}"
        )

@executor_router.get("/executions/{execution_id}/status", response_model=GetExecutionStatusResponse)
async def get_execution_status(
    execution_id: str,
    deps: TriadDeps = Depends(get_deps),
    user_id: str = Depends(verify_token)
):
    """Get execution status and progress."""
    execution_status = await get_execution_status_from_db(execution_id, deps)
    if not execution_status:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return GetExecutionStatusResponse(
        success=True,
        message="Execution status retrieved",
        request_id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc),
        execution_status=execution_status.status,
        progress_percentage=execution_status.progress,
        current_task=execution_status.current_task,
        completed_tasks=execution_status.completed_tasks,
        failed_tasks=execution_status.failed_tasks,
        logs=execution_status.logs
    )

@executor_router.post("/executions/{execution_id}/cancel")
async def cancel_execution(
    execution_id: str,
    deps: TriadDeps = Depends(get_deps),
    user_id: str = Depends(verify_token)
):
    """Cancel a running execution."""
    success = await cancel_workflow_execution(execution_id, deps)
    if not success:
        raise HTTPException(status_code=404, detail="Execution not found or cannot be cancelled")
    
    return {"success": True, "message": "Execution cancelled successfully"}

@executor_router.post("/tasks/execute", response_model=ExecuteTaskResponse)
async def execute_single_task(
    request: ExecuteTaskRequest,
    deps: TriadDeps = Depends(get_deps),
    user_id: str = Depends(verify_token)
):
    """Execute a single task."""
    start_time = time.time()
    
    try:
        # Get task details
        task = await get_task_by_id(request.task_id, deps)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Execute task
        result = await executor_agent.run(
            f"""Execute single task:
            Task: {task.to_json()}
            Parameters: {request.task_parameters}
            Timeout: {request.override_timeout or task.timeout}
            """,
            deps=deps
        )
        
        execution_time = time.time() - start_time
        
        return ExecuteTaskResponse(
            success=True,
            message="Task executed successfully",
            request_id=request.request_id,
            timestamp=datetime.now(timezone.utc),
            execution_time=execution_time,
            execution_result=result.output
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute task: {str(e)}"
        )
```

### 3. Evaluator Agent Endpoints

```python
evaluator_router = APIRouter(prefix="/api/v1/evaluator", tags=["evaluator"])

@evaluator_router.post("/validate", response_model=ValidateResultResponse)
async def validate_execution_result(
    request: ValidateResultRequest,
    deps: TriadDeps = Depends(get_deps),
    user_id: str = Depends(verify_token)
):
    """Validate execution results using the Evaluator agent."""
    start_time = time.time()
    
    try:
        # Get execution result
        execution = await get_execution_by_id(request.execution_id, deps)
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        # Run validation
        result = await evaluator_agent.run(
            f"""Validate execution result:
            Execution: {execution.to_json()}
            Validation Criteria: {request.validation_criteria}
            Custom Rules: {[rule.dict() for rule in request.custom_rules]}
            """,
            deps=deps
        )
        
        validation_report = result.output
        execution_time = time.time() - start_time
        
        # Determine compliance status
        compliance_status = determine_compliance_status(validation_report)
        
        return ValidateResultResponse(
            success=True,
            message="Validation completed successfully",
            request_id=request.request_id,
            timestamp=datetime.now(timezone.utc),
            execution_time=execution_time,
            validation_report=validation_report,
            recommendations=validation_report.recommendations,
            compliance_status=compliance_status
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to validate result: {str(e)}"
        )

@evaluator_router.post("/benchmark", response_model=BenchmarkPerformanceResponse)
async def benchmark_performance(
    request: BenchmarkPerformanceRequest,
    deps: TriadDeps = Depends(get_deps),
    user_id: str = Depends(verify_token)
):
    """Benchmark execution performance against historical data."""
    start_time = time.time()
    
    try:
        # Get execution data
        execution = await get_execution_by_id(request.execution_id, deps)
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        # Run benchmarking
        result = await evaluator_agent.run(
            f"""Benchmark performance:
            Execution: {execution.to_json()}
            Benchmark Type: {request.benchmark_type}
            Comparison Period: {request.comparison_period}
            """,
            deps=deps
        )
        
        benchmark_report = result.output
        execution_time = time.time() - start_time
        
        return BenchmarkPerformanceResponse(
            success=True,
            message="Benchmarking completed successfully",
            request_id=request.request_id,
            timestamp=datetime.now(timezone.utc),
            execution_time=execution_time,
            benchmark_report=benchmark_report,
            performance_score=benchmark_report.overall_score,
            ranking=benchmark_report.percentile_ranking
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to benchmark performance: {str(e)}"
        )

@evaluator_router.get("/reports/{execution_id}", response_model=ValidationReport)
async def get_validation_report(
    execution_id: str,
    deps: TriadDeps = Depends(get_deps),
    user_id: str = Depends(verify_token)
):
    """Get existing validation report for an execution."""
    report = await get_validation_report_by_execution_id(execution_id, deps)
    if not report:
        raise HTTPException(status_code=404, detail="Validation report not found")
    return report
```

### 4. Overwatch Agent Endpoints

```python
overwatch_router = APIRouter(prefix="/api/v1/overwatch", tags=["overwatch"])

@overwatch_router.get("/health", response_model=GetSystemHealthResponse)
async def get_system_health(
    request: GetSystemHealthRequest = Depends(),
    deps: TriadDeps = Depends(get_deps),
    user_id: str = Depends(verify_token)
):
    """Get comprehensive system health status."""
    start_time = time.time()
    
    try:
        # Run system health check
        result = await overwatch_agent.run(
            f"""Check system health:
            Include Detailed Metrics: {request.include_detailed_metrics}
            Component Filter: {request.component_filter}
            """,
            deps=deps
        )
        
        system_health = result.output
        execution_time = time.time() - start_time
        
        # Get active alerts
        alerts = await get_active_alerts(deps)
        
        # Generate recommendations
        recommendations = await generate_health_recommendations(system_health, alerts)
        
        return GetSystemHealthResponse(
            success=True,
            message="System health retrieved successfully",
            request_id=request.request_id,
            timestamp=datetime.now(timezone.utc),
            execution_time=execution_time,
            system_health=system_health,
            alerts=alerts,
            recommendations=recommendations
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system health: {str(e)}"
        )

@overwatch_router.get("/performance", response_model=GetPerformanceReportResponse)
async def get_performance_report(
    request: GetPerformanceReportRequest = Depends(),
    deps: TriadDeps = Depends(get_deps),
    user_id: str = Depends(verify_token)
):
    """Get performance report for specified time range."""
    start_time = time.time()
    
    try:
        # Run performance analysis
        result = await overwatch_agent.run(
            f"""Generate performance report:
            Time Range: {request.time_range}
            Metrics: {request.metrics}
            Group By: {request.group_by}
            """,
            deps=deps
        )
        
        performance_report = result.output
        execution_time = time.time() - start_time
        
        # Analyze trends
        trends = await analyze_performance_trends(performance_report)
        
        # Generate insights
        insights = await generate_performance_insights(performance_report, trends)
        
        return GetPerformanceReportResponse(
            success=True,
            message="Performance report generated successfully",
            request_id=request.request_id,
            timestamp=datetime.now(timezone.utc),
            execution_time=execution_time,
            performance_report=performance_report,
            trends=trends,
            insights=insights
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate performance report: {str(e)}"
        )

@overwatch_router.get("/alerts", response_model=List[Alert])
async def get_alerts(
    severity: Optional[str] = None,
    component: Optional[str] = None,
    resolved: Optional[bool] = None,
    limit: int = 50,
    deps: TriadDeps = Depends(get_deps),
    user_id: str = Depends(verify_token)
):
    """Get system alerts with optional filtering."""
    alerts = await get_filtered_alerts(severity, component, resolved, limit, deps)
    return alerts

@overwatch_router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    resolution_note: str,
    deps: TriadDeps = Depends(get_deps),
    user_id: str = Depends(verify_token)
):
    """Mark an alert as resolved."""
    success = await resolve_alert_by_id(alert_id, resolution_note, user_id, deps)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"success": True, "message": "Alert resolved successfully"}
```

### Application Assembly

```python
# Include all routers
app.include_router(planner_router)
app.include_router(executor_router)
app.include_router(evaluator_router)
app.include_router(overwatch_router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc)}

# Metrics endpoint for Prometheus
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# WebSocket for real-time updates
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket connection for real-time updates."""
    await websocket.accept()
    
    try:
        # Subscribe to user-specific events
        async for event in subscribe_to_user_events(user_id, app.state.deps):
            await websocket.send_json(event)
    except WebSocketDisconnect:
        pass
    finally:
        await unsubscribe_from_user_events(user_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

This comprehensive API structure provides a complete REST interface to the AI Triad system, with proper error handling, authentication, monitoring, and real-time capabilities.