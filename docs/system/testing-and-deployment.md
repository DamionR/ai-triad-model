# Constitutional Testing and Westminster Deployment

## Overview

The AI Triad Model implements comprehensive **constitutional compliance testing** using Pydantic AI's testing capabilities and modern deployment practices with **Westminster governance validation**, Docker, and CI/CD pipelines. All testing ensures constitutional adherence, parliamentary procedure compliance, and democratic accountability validation.

## Testing Architecture with Pydantic AI

### Pydantic AI Testing Framework

The AI Triad Model uses Pydantic AI's dedicated testing framework for comprehensive agent testing with mock models and proper dependency injection.

```python
# tests/conftest.py
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from pydantic_ai.models.test import TestModel
from pydantic_ai import RunContext

from backend.dependencies import TriadDeps
from backend.models import Base
from backend.agents import planner_agent, executor_agent, evaluator_agent, overwatch_agent

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_db():
    """Create test database session."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False}
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
    
    await engine.dispose()

@pytest.fixture
async def test_deps(test_db):
    """Create test dependencies with constitutional components."""
    mcp_client = AsyncMock()
    a2a_broker = AsyncMock()
    logfire_logger = AsyncMock()
    parliamentary_procedure = AsyncMock()
    constitutional_crisis_manager = AsyncMock()
    crown_prerogative = AsyncMock()
    
    return TriadDeps(
        db_session=test_db,
        mcp_client=mcp_client,
        a2a_broker=a2a_broker,
        logfire_logger=logfire_logger,
        parliamentary_procedure=parliamentary_procedure,
        constitutional_crisis_manager=constitutional_crisis_manager,
        crown_prerogative=crown_prerogative
    )

@pytest.fixture
def mock_constitutional_responses():
    """Mock constitutional and parliamentary responses for testing."""
    return {
        "planner_responses": [
            """{"id": "workflow_123", "name": "Test Workflow", "tasks": [], "constitutional_compliance": true, "parliamentary_approved": true}""",
            """{"question_period_response": "The planning decision was made following proper legislative procedure with full cabinet consultation.", "constitutional_authority": "legislative"}"""
        ],
        "executor_responses": [
            """{"task_id": "task_123", "status": "completed", "execution_time": 1.5, "ministerial_responsibility": true, "collective_cabinet_approval": true}""",
            """{"confidence_vote_response": "I maintain the confidence of the system and stand by my execution decisions.", "prepared_to_resign": false}"""
        ],
        "evaluator_responses": [
            """{"accuracy_score": 0.98, "validation_status": "passed", "constitutional_compliance": true, "westminster_adherence": true}""",
            """{"constitutional_review": "All decisions comply with Westminster parliamentary principles and democratic accountability requirements."}"""
        ],
        "overwatch_responses": [
            """{"constitutional_oversight": "active", "crown_authority": "monitoring", "parliamentary_compliance": true, "emergency_powers": "standby"}""",
            """{"reserve_power_decision": "Royal assent granted for system decision following proper constitutional procedure.", "constitutional_crisis": false}"""
        ]
        "overwatch_responses": [
            """{"overall_status": "healthy", "active_alerts": [], "recommendations": []}""",
            """{"performance_summary": {"avg_execution_time": 2.3, "success_rate": 0.995}}"""
        ]
    }
```

### Agent Testing with Pydantic AI TestModel

```python
# tests/test_agents.py
import pytest
from pydantic_ai.models.test import TestModel
from pydantic_ai import ModelRetry

from backend.agents import planner_agent, executor_agent, evaluator_agent, overwatch_agent
from backend.models import WorkflowPlan, ExecutionResult, ValidationReport, SystemHealth

class TestPlannerAgent:
    """Test suite for Planner Agent using Pydantic AI TestModel."""
    
    @pytest.mark.asyncio
    async def test_create_workflow_plan(self, test_deps):
        """Test workflow plan creation with TestModel."""
        # Define expected workflow plan response
        expected_plan = {
            "id": "workflow_123",
            "name": "Data Processing Workflow",
            "description": "Automated data pipeline",
            "tasks": [
                {"id": "task_1", "name": "Extract Data", "type": "extraction"},
                {"id": "task_2", "name": "Transform Data", "type": "transformation"},
                {"id": "task_3", "name": "Load Data", "type": "loading"}
            ],
            "dependencies": [
                {"from": "task_1", "to": "task_2"},
                {"from": "task_2", "to": "task_3"}
            ],
            "estimated_duration": 1800
        }
        
        # Create TestModel with structured response
        test_model = TestModel(
            lambda messages: WorkflowPlan.model_validate(expected_plan)
        )
        
        # Test agent with overridden model
        with planner_agent.override(model=test_model):
            result = await planner_agent.run(
                "Create a workflow for data processing pipeline",
                deps=test_deps
            )
            
            assert result.output is not None
            assert isinstance(result.output, WorkflowPlan)
            assert result.output.id == "workflow_123"
            assert result.output.name == "Data Processing Workflow"
            assert len(result.output.tasks) == 3
            assert len(result.output.dependencies) == 2
    
    @pytest.mark.asyncio
    async def test_workflow_validation_failure(self, test_deps):
        """Test workflow validation with circular dependencies using TestModel."""
        # Create invalid workflow plan with circular dependencies
        invalid_plan = {
            "id": "workflow_invalid",
            "name": "Invalid Workflow",
            "tasks": [
                {"id": "task1", "name": "Task 1", "dependencies": ["task2"]},
                {"id": "task2", "name": "Task 2", "dependencies": ["task1"]}
            ]
        }
        
        # TestModel that returns invalid structure triggering validation failure
        test_model = TestModel(
            lambda messages: WorkflowPlan.model_validate(invalid_plan)
        )
        
        with planner_agent.override(model=test_model):
            # Should raise ModelRetry due to output validation failure
            with pytest.raises(ModelRetry):
                await planner_agent.run(
                    "Create workflow with circular dependencies",
                    deps=test_deps
                )
    
    @pytest.mark.asyncio
    async def test_optimize_workflow(self, test_deps):
        """Test workflow optimization using TestModel."""
        optimized_plan = {
            "id": "workflow_optimized_123",
            "name": "Optimized Data Processing Workflow",
            "optimization_applied": True,
            "improvements": ["reduced_complexity", "parallel_execution"],
            "estimated_duration": 1200  # Reduced from 1800
        }
        
        test_model = TestModel(
            lambda messages: WorkflowPlan.model_validate(optimized_plan)
        )
        
        with planner_agent.override(model=test_model):
            result = await planner_agent.run(
                "Optimize existing workflow for performance",
                deps=test_deps
            )
            
            assert result.output is not None
            assert result.output.optimization_applied is True
            assert "reduced_complexity" in result.output.improvements
            assert result.output.estimated_duration < 1800

class TestExecutorAgent:
    """Test suite for Executor Agent using Pydantic AI TestModel."""
    
    @pytest.mark.asyncio
    async def test_execute_task_success(self, test_deps):
        """Test successful task execution with TestModel."""
        execution_result = {
            "task_id": "task_123",
            "status": "completed",
            "execution_time": 1.5,
            "output_data": {"processed_records": 1000},
            "resource_usage": {"cpu_percent": 45, "memory_mb": 256}
        }
        
        test_model = TestModel(
            lambda messages: ExecutionResult.model_validate(execution_result)
        )
        
        with executor_agent.override(model=test_model):
            result = await executor_agent.run(
                "Execute data processing task",
                deps=test_deps
            )
            
            assert result.output is not None
            assert isinstance(result.output, ExecutionResult)
            assert result.output.status == "completed"
            assert result.output.execution_time == 1.5
            assert result.output.output_data["processed_records"] == 1000
    
    @pytest.mark.asyncio
    async def test_task_timeout_handling(self, test_deps):
        """Test task timeout handling with TestModel."""
        timeout_result = {
            "task_id": "task_timeout",
            "status": "timeout",
            "error_message": "Task exceeded timeout limit",
            "execution_time": 300.0,  # Max timeout
            "partial_results": {"processed_records": 500}
        }
        
        test_model = TestModel(
            lambda messages: ExecutionResult.model_validate(timeout_result)
        )
        
        with executor_agent.override(model=test_model):
            result = await executor_agent.run(
                "Execute long-running task",
                deps=test_deps
            )
            
            assert result.output.status == "timeout"
            assert "timeout" in result.output.error_message.lower()
            assert result.output.partial_results is not None

class TestEvaluatorAgent:
    """Test suite for Evaluator Agent using Pydantic AI TestModel."""
    
    @pytest.mark.asyncio
    async def test_validate_execution_result(self, test_deps):
        """Test execution result validation with TestModel."""
        validation_report = {
            "task_id": "validation_123",
            "accuracy_score": 0.98,
            "validation_status": "passed",
            "recommendations": [],
            "validation_details": {
                "data_quality": 0.99,
                "performance": 0.97,
                "compliance": 1.0
            }
        }
        
        test_model = TestModel(
            lambda messages: ValidationReport.model_validate(validation_report)
        )
        
        with evaluator_agent.override(model=test_model):
            result = await evaluator_agent.run(
                "Validate execution result with accuracy check",
                deps=test_deps
            )
            
            assert result.output is not None
            assert isinstance(result.output, ValidationReport)
            assert result.output.accuracy_score == 0.98
            assert result.output.validation_status == "passed"
            assert result.output.validation_details["compliance"] == 1.0
    
    @pytest.mark.asyncio
    async def test_low_accuracy_retry(self, test_deps):
        """Test validation retry for low accuracy using TestModel."""
        low_accuracy_report = {
            "task_id": "validation_failed",
            "accuracy_score": 0.85,  # Below 0.95 threshold
            "validation_status": "failed",
            "recommendations": ["improve_data_quality", "re_validate"],
            "validation_details": {
                "data_quality": 0.80,
                "performance": 0.90,
                "compliance": 0.85
            }
        }
        
        test_model = TestModel(
            lambda messages: ValidationReport.model_validate(low_accuracy_report)
        )
        
        with evaluator_agent.override(model=test_model):
            # Should trigger ModelRetry due to output validator checking accuracy < 0.95
            with pytest.raises(ModelRetry):
                await evaluator_agent.run(
                    "Validate result with low accuracy",
                    deps=test_deps
                )

class TestOverwatchAgent:
    """Test suite for Overwatch Agent."""
    
    @pytest.mark.asyncio
    async def test_system_health_monitoring(self, test_deps, mock_model_responses):
        """Test system health monitoring."""
        test_model = TestModel(mock_model_responses["overwatch_responses"])
        
        with overwatch_agent.override(model=test_model):
            result = await overwatch_agent.run(
                "Monitor system health and performance",
                deps=test_deps
            )
            
            assert result.output is not None
            assert isinstance(result.output, SystemHealth)
            assert result.output.overall_status == "healthy"
    
    @pytest.mark.asyncio
    async def test_alert_escalation(self, test_deps):
        """Test critical alert escalation."""
        critical_alert_response = """{"overall_status": "critical", "active_alerts": [
            {"severity": "critical", "component": "database", "message": "Connection failure"}
        ]}"""
        
        test_model = TestModel([critical_alert_response])
        
        with overwatch_agent.override(model=test_model):
            result = await overwatch_agent.run(
                "Check system with critical issues",
                deps=test_deps
            )
            
            assert result.output.overall_status == "critical"
            assert len(result.output.active_alerts) > 0
```

### Tool Testing

```python
# tests/test_tools.py
import pytest
from unittest.mock import AsyncMock, patch

from backend.tools import CreateWorkflowPlanTool, ExecuteDataProcessingTool, ValidateDataQualityTool
from backend.models import Task, WorkflowPlan, ExecutionResult, QualityReport

class TestWorkflowTools:
    """Test suite for workflow tools."""
    
    @pytest.mark.asyncio
    async def test_create_workflow_plan_tool(self, test_deps):
        """Test workflow plan creation tool."""
        tool = CreateWorkflowPlanTool()
        
        requirements = "Process customer data and generate reports"
        constraints = {"max_duration": 3600, "max_memory": 1024}
        
        with patch.object(tool, '_parse_requirements') as mock_parse, \
             patch.object(tool, '_generate_tasks') as mock_generate, \
             patch.object(tool, '_create_dependencies') as mock_deps:
            
            mock_parse.return_value = AsyncMock(name="Data Processing")
            mock_generate.return_value = [Task(id="task1", name="Process Data")]
            mock_deps.return_value = []
            
            result = await tool.execute(test_deps, requirements, constraints)
            
            assert isinstance(result, WorkflowPlan)
            assert result.name == "Data Processing"
            mock_parse.assert_called_once_with(requirements)
            mock_generate.assert_called_once()

class TestExecutionTools:
    """Test suite for execution tools."""
    
    @pytest.mark.asyncio
    async def test_data_processing_tool_success(self, test_deps):
        """Test successful data processing execution."""
        tool = ExecuteDataProcessingTool()
        
        task = Task(
            id="task_123",
            name="Process CSV File",
            parameters={"processing_type": "batch", "file_path": "/data/input.csv"}
        )
        
        with patch.object(tool, '_execute_batch_processing') as mock_batch:
            mock_batch.return_value = {"processed_rows": 1000, "output_file": "/data/output.csv"}
            
            result = await tool.execute(test_deps, task)
            
            assert isinstance(result, ExecutionResult)
            assert result.status == "completed"
            assert result.output_data["processed_rows"] == 1000
            mock_batch.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_data_processing_tool_failure(self, test_deps):
        """Test data processing execution failure."""
        tool = ExecuteDataProcessingTool()
        
        task = Task(
            id="task_456",
            name="Process Invalid File",
            parameters={"processing_type": "batch", "file_path": "/invalid/path.csv"}
        )
        
        with patch.object(tool, '_execute_batch_processing') as mock_batch:
            mock_batch.side_effect = FileNotFoundError("File not found")
            
            result = await tool.execute(test_deps, task)
            
            assert isinstance(result, ExecutionResult)
            assert result.status == "failed"
            assert "File not found" in result.error_message

class TestValidationTools:
    """Test suite for validation tools."""
    
    @pytest.mark.asyncio
    async def test_data_quality_validation(self, test_deps):
        """Test data quality validation tool."""
        tool = ValidateDataQualityTool()
        
        data = {"customer_id": "123", "email": "test@example.com", "age": 25}
        schema = AsyncMock(version="1.0")
        
        with patch.object(tool, '_validate_schema') as mock_schema, \
             patch.object(tool, '_validate_completeness') as mock_complete, \
             patch.object(tool, '_validate_accuracy') as mock_accuracy:
            
            mock_schema.return_value = AsyncMock(passed=True, score=1.0)
            mock_complete.return_value = AsyncMock(passed=True, score=1.0)
            mock_accuracy.return_value = AsyncMock(passed=True, score=0.98)
            
            result = await tool.execute(test_deps, data, schema)
            
            assert isinstance(result, QualityReport)
            assert result.overall_score > 0.9
            assert len(result.passed_checks) == 3
```

### API Testing

```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from backend.main import app
from backend.models import WorkflowPlan, ExecutionResult

@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)

@pytest.fixture
def auth_headers():
    """Create auth headers for testing."""
    return {"Authorization": "Bearer test_token"}

class TestPlannerAPI:
    """Test suite for Planner API endpoints."""
    
    def test_create_workflow_success(self, client, auth_headers):
        """Test successful workflow creation."""
        request_data = {
            "name": "Test Workflow",
            "description": "Test workflow description",
            "requirements": "Process data and generate reports",
            "constraints": {},
            "priority": "medium"
        }
        
        with patch('backend.agents.planner_agent.run') as mock_run:
            mock_run.return_value = AsyncMock(
                output=WorkflowPlan(
                    id="workflow_123",
                    name="Test Workflow",
                    description="Test workflow",
                    tasks=[],
                    dependencies=[],
                    estimated_duration=3600
                )
            )
            
            response = client.post(
                "/api/v1/planner/workflows",
                json=request_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            assert response.json()["success"] is True
            assert response.json()["workflow_plan"]["id"] == "workflow_123"
    
    def test_create_workflow_unauthorized(self, client):
        """Test workflow creation without auth."""
        request_data = {
            "name": "Test Workflow",
            "description": "Test workflow description",
            "requirements": "Process data",
        }
        
        response = client.post("/api/v1/planner/workflows", json=request_data)
        assert response.status_code == 403

class TestExecutorAPI:
    """Test suite for Executor API endpoints."""
    
    def test_execute_workflow_async(self, client, auth_headers):
        """Test async workflow execution."""
        request_data = {
            "workflow_id": "workflow_123",
            "execution_parameters": {},
            "async_execution": True
        }
        
        with patch('backend.api.routes.executor.get_workflow_by_id') as mock_get:
            mock_get.return_value = AsyncMock(estimated_duration=3600)
            
            response = client.post(
                "/api/v1/executor/execute",
                json=request_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            assert response.json()["success"] is True
            assert "execution_id" in response.json()
    
    def test_get_execution_status(self, client, auth_headers):
        """Test execution status retrieval."""
        execution_id = "exec_123"
        
        with patch('backend.api.routes.executor.get_execution_status_from_db') as mock_get:
            mock_get.return_value = AsyncMock(
                status="running",
                progress=0.5,
                current_task="task_2",
                completed_tasks=["task_1"],
                failed_tasks=[],
                logs=["Started execution", "Completed task_1"]
            )
            
            response = client.get(
                f"/api/v1/executor/executions/{execution_id}/status",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            assert response.json()["execution_status"] == "running"
            assert response.json()["progress_percentage"] == 0.5

class TestEvaluatorAPI:
    """Test suite for Evaluator API endpoints."""
    
    def test_validate_result(self, client, auth_headers):
        """Test result validation."""
        request_data = {
            "execution_id": "exec_123",
            "validation_criteria": ["accuracy", "performance"],
            "custom_rules": []
        }
        
        with patch('backend.agents.evaluator_agent.run') as mock_run, \
             patch('backend.api.routes.evaluator.get_execution_by_id') as mock_get:
            
            mock_get.return_value = AsyncMock(id="exec_123")
            mock_run.return_value = AsyncMock(
                output=AsyncMock(
                    accuracy_score=0.98,
                    validation_status="passed",
                    recommendations=[]
                )
            )
            
            response = client.post(
                "/api/v1/evaluator/validate",
                json=request_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            assert response.json()["success"] is True
            assert response.json()["validation_report"]["accuracy_score"] == 0.98

class TestOverwatchAPI:
    """Test suite for Overwatch API endpoints."""
    
    def test_get_system_health(self, client, auth_headers):
        """Test system health retrieval."""
        with patch('backend.agents.overwatch_agent.run') as mock_run:
            mock_run.return_value = AsyncMock(
                output=AsyncMock(
                    overall_status="healthy",
                    agent_statuses={},
                    performance_metrics={},
                    active_alerts=[],
                    recommendations=[]
                )
            )
            
            response = client.get("/api/v1/overwatch/health", headers=auth_headers)
            
            assert response.status_code == 200
            assert response.json()["success"] is True
            assert response.json()["system_health"]["overall_status"] == "healthy"
```

## Testing Strategy with Pydantic AI

### Test Categories
- **Agent Tests**: Core agent behavior testing using Pydantic AI TestModel
- **Integration Tests**: A2A protocol and MCP integration testing
- **API Tests**: FastAPI endpoint testing with agent mocking
- **Performance Tests**: Load and stress testing with constitutional oversight

### Pydantic AI Testing Tools
- **TestModel**: Pydantic AI's dedicated testing framework for agent mocking
- **Agent.override()**: Context manager for replacing agent models during testing  
- **RunContext**: Type-safe dependency injection for test scenarios
- **Pytest**: Primary testing framework for test orchestration
- **pytest-asyncio**: Async test support for agent testing
- **TestClient**: FastAPI test client for API endpoint testing

### Key Testing Patterns with Pydantic AI

#### 1. **TestModel with Lambda Functions**
```python
# Structured response testing
test_model = TestModel(
    lambda messages: WorkflowPlan.model_validate(expected_data)
)
```

#### 2. **Agent Override Context Manager**
```python
# Safe model replacement during testing
with planner_agent.override(model=test_model):
    result = await planner_agent.run("test prompt", deps=test_deps)
```

#### 3. **Output Validation Testing**
```python
# Test validation failures and ModelRetry exceptions
with pytest.raises(ModelRetry):
    await agent.run("invalid input", deps=test_deps)
```

#### 4. **Constitutional Testing**
All tests maintain the constitutional principles:
- **Planning Phase**: TestModel validates workflow structure
- **Execution Phase**: TestModel validates execution results
- **Evaluation Phase**: TestModel validates assessment accuracy
- **Oversight Phase**: All phases logged through test dependencies

### Integration Testing with MCP and A2A
```python
# Test MCP integration with existing systems
@pytest.mark.asyncio
async def test_mcp_legacy_database_integration(test_deps):
    """Test integration with legacy database via MCP."""
    expected_result = {"records_found": 150, "query_time": 0.5}
    
    # Mock MCP client response
    test_deps.mcp_client.call_tool.return_value = expected_result
    
    test_model = TestModel(
        lambda messages: {"integration_status": "success", "data": expected_result}
    )
    
    with planner_agent.override(model=test_model):
        result = await planner_agent.run(
            "Query legacy customer database for active accounts",
            deps=test_deps
        )
        
        # Verify constitutional compliance
        assert test_deps.logfire_logger.info.called
        assert "constitutional_oversight" in str(test_deps.logfire_logger.info.call_args)
```

## Deployment Architecture

### Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create app user
RUN groupadd -r app && useradd -r -g app app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Change ownership
RUN chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:password@db:5432/triad
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=triad
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    restart: unless-stopped

volumes:
  postgres_data:
  prometheus_data:
  grafana_data:
```

### Docker Production Deployment

#### Production Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.prod
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:${POSTGRES_PASSWORD}@db:5432/triad
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - LOGFIRE_TOKEN=${LOGFIRE_TOKEN}
      - JWT_SECRET=${JWT_SECRET}
      - ENVIRONMENT=production
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=triad
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "5432:5432"
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.25'

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
```

#### Production Dockerfile

```dockerfile
# Dockerfile.prod
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

# Create and use app user
RUN groupadd -r app && useradd -r -g app app

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install 'pydantic-ai-slim[a2a]' logfire

# Copy application code
COPY . .

# Change ownership
RUN chown -R app:app /app

# Multi-stage build - production stage
FROM python:3.11-slim as production

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install runtime dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r app && useradd -r -g app app

# Copy from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder --chown=app:app /app /app

# Switch to app user
USER app
WORKDIR /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run application with Logfire instrumentation
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### Nginx Configuration

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server app:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;

        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/ssl/certs/cert.pem;
        ssl_certificate_key /etc/ssl/certs/key.pem;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;
        add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

        # Gzip compression
        gzip on;
        gzip_vary on;
        gzip_min_length 1024;
        gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;

        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        location /health {
            proxy_pass http://backend/health;
            access_log off;
        }
    }
}
```

### CI/CD Pipeline

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_triad
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run linting
      run: |
        flake8 backend/
        black --check backend/
        isort --check-only backend/
    
    - name: Run type checking
      run: mypy backend/
    
    - name: Run tests
      env:
        DATABASE_URL: postgresql+asyncpg://postgres:test@localhost:5432/test_triad
        OPENAI_API_KEY: test_key
        ANTHROPIC_API_KEY: test_key
      run: |
        pytest tests/ -v --cov=backend --cov-report=xml
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: |
          ghcr.io/${{ github.repository }}/backend:latest
          ghcr.io/${{ github.repository }}/backend:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
    
    - name: Deploy to Production Server
      env:
        DEPLOY_HOST: ${{ secrets.DEPLOY_HOST }}
        DEPLOY_USER: ${{ secrets.DEPLOY_USER }}
        DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
      run: |
        # Setup SSH
        mkdir -p ~/.ssh
        echo "$DEPLOY_KEY" > ~/.ssh/deploy_key
        chmod 600 ~/.ssh/deploy_key
        
        # Deploy via SSH
        ssh -i ~/.ssh/deploy_key -o StrictHostKeyChecking=no $DEPLOY_USER@$DEPLOY_HOST << 'EOF'
          cd /opt/triad-model
          
          # Pull latest images
          docker-compose -f docker-compose.prod.yml pull
          
          # Update and restart services
          docker-compose -f docker-compose.prod.yml up -d --remove-orphans
          
          # Clean up old images
          docker image prune -f
        EOF
```

### Monitoring and Observability with Logfire

#### Logfire Setup

```python
# backend/config/logfire.py
import logfire
from typing import Optional

class LogfireConfig:
    """Logfire configuration for the AI Triad system."""
    
    def __init__(self):
        self.token: Optional[str] = None
        self.service_name = "ai-triad-backend"
        self.service_version = "1.0.0"
        self.environment = "production"
    
    def configure(self):
        """Configure Logfire with optimal settings for AI applications."""
        logfire.configure(
            service_name=self.service_name,
            service_version=self.service_version,
            environment=self.environment,
            # Exclude binary content for privacy
            exclude_binary_content=True,
            # Optimize for AI workloads
            log_level="INFO",
            collect_system_metrics=True,
        )
        
        # Instrument Pydantic AI automatically
        logfire.instrument_pydantic_ai()
        
        # Instrument FastAPI
        logfire.instrument_fastapi()
        
        # Instrument HTTP clients for A2A communication
        logfire.instrument_httpx()
        
        # Instrument database operations
        logfire.instrument_sqlalchemy()

# backend/main.py
import logfire
from .config.logfire import LogfireConfig

# Configure Logfire at startup
logfire_config = LogfireConfig()
logfire_config.configure()

app = FastAPI(title="AI Triad Backend")

# Automatic instrumentation is already active
```

#### Environment Configuration

```bash
# .env.production
LOGFIRE_TOKEN=your_logfire_token_here
LOGFIRE_SERVICE_NAME=ai-triad-backend
LOGFIRE_ENVIRONMENT=production
LOGFIRE_SERVICE_VERSION=1.0.0

# Optional: Custom OpenTelemetry endpoint
OTEL_EXPORTER_OTLP_ENDPOINT=https://your-custom-endpoint.com
```

#### Production Deployment Script

```bash
#!/bin/bash
# deploy.sh

set -e

echo "🚀 Deploying AI Triad Backend to Production"

# Check required environment variables
if [ -z "$LOGFIRE_TOKEN" ]; then
    echo "❌ LOGFIRE_TOKEN is required"
    exit 1
fi

# Pull latest code
git pull origin main

# Build production images
echo "🔨 Building production images..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Stop existing services
echo "🛑 Stopping existing services..."
docker-compose -f docker-compose.prod.yml down

# Start services with health checks
echo "🟢 Starting production services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for health checks
echo "🔍 Waiting for services to be healthy..."
timeout 60 bash -c 'until docker-compose -f docker-compose.prod.yml ps | grep -q "Up (healthy)"; do sleep 2; done'

# Run database migrations
echo "🗄️ Running database migrations..."
docker-compose -f docker-compose.prod.yml exec app alembic upgrade head

# Verify deployment
echo "✅ Verifying deployment..."
curl -f http://localhost:8000/health || (echo "❌ Health check failed" && exit 1)

echo "🎉 Deployment successful!"
echo "📊 Monitor at: https://logfire.pydantic.dev"
```

This comprehensive testing and deployment setup ensures the AI Triad backend is production-ready with proper CI/CD, monitoring, and scalability.