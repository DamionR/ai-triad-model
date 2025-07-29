# Graph Workflows and Sub-Agent Spawning

## Overview

The AI Triad system uses Pydantic AI Graphs to enable sophisticated workflow orchestration and sub-agent spawning while **preserving the fundamental constitutional principles** of the Triad Model. This allows main agents to decompose complex tasks into specialized sub-workflows, creating dynamic, stateful execution graphs with precise control flow **that maintain the sacred separation of powers**.

## 🍁 Constitutional Compliance in Sub-Agent Architecture

### Preserving the Westminster Principles

Even with complex graph workflows and sub-agent spawning, the system **MUST maintain the fundamental Triad constitutional principles**:

1. **Sub-Agent Separation of Powers**: Sub-agents follow the same Legislative → Executive → Judicial flow
2. **Constitutional Oversight**: All sub-agent workflows report to main Overwatch authority
3. **Mandatory Validation**: No sub-agent execution completes without evaluation
4. **Accountability Chain**: Clear chain of command from sub-agents to main constitutional agents

### **Sub-Agent Constitutional Framework:**

```
Main Triad (Constitutional Level)
     Planner → Executor → Evaluator
          ↓        ↓        ↓
Sub-Triad (Operational Level)
  Sub-Planner → Sub-Executor → Sub-Evaluator
       ↑              ↑            ↑
Constitutional Reporting Chain to Overwatch
```

**KEY PRINCIPLE**: Sub-agents are **not autonomous** - they are **extensions of the main constitutional agents** and must operate within the same checks and balances framework.

## Graph Architecture

### Core Components

```python
from pydantic_ai.graph import Graph, GraphRunContext
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import asyncio

class TriadGraphState(BaseModel):
    """Shared state across all graph nodes with constitutional compliance."""
    workflow_id: str
    main_agent: str  # planner, executor, evaluator, overwatch
    constitutional_branch: str  # legislative, executive, judicial, crown
    task_context: Dict[str, Any]
    sub_agent_results: Dict[str, Any] = {}
    validation_chain: List[Dict[str, Any]] = []  # Constitutional validation chain
    execution_metadata: Dict[str, Any] = {}
    error_history: List[str] = []
    
    def enforce_constitutional_flow(self) -> bool:
        """Ensure sub-agents follow constitutional separation of powers."""
        # Must have planning → execution → evaluation flow
        required_flow = ["planning", "execution", "evaluation"]
        completed_phases = [result.get("phase") for result in self.sub_agent_results.values()]
        
        for phase in required_flow:
            if phase not in completed_phases:
                return False
        return True

class SubAgentRequest(BaseModel):
    """Request for spawning a sub-agent with constitutional compliance."""
    sub_agent_type: str
    constitutional_phase: str  # "planning", "execution", "evaluation"
    parent_branch: str  # "legislative", "executive", "judicial"
    task_description: str
    specialized_parameters: Dict[str, Any]
    requires_validation: bool = True  # Must go through evaluation
    priority: int = 1
    timeout_seconds: int = 300
    
    def validate_constitutional_authority(self, parent_agent: str) -> bool:
        """Ensure sub-agent request comes from appropriate constitutional authority."""
        authority_mapping = {
            "planner": "legislative",
            "executor": "executive", 
            "evaluator": "judicial",
            "overwatch": "crown"
        }
        
        return authority_mapping.get(parent_agent) == self.parent_branch
```

## Constitutional Enforcement System

### Sub-Agent Triad Validation Node

```python
class ConstitutionalValidationNode(Node[TriadGraphState, Dict[str, Any], Dict[str, Any]]):
    """Ensures all sub-agent workflows maintain constitutional separation of powers."""
    
    async def run(self, ctx: GraphRunContext[TriadGraphState], sub_agent_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate sub-agent result through constitutional Triad process."""
        
        with logfire.span("constitutional_validation") as span:
            span.set_attribute("workflow_id", ctx.state.workflow_id)
            span.set_attribute("main_branch", ctx.state.constitutional_branch)
            span.set_attribute("sub_agent_type", sub_agent_result.get("sub_agent_type"))
            
            # MANDATORY: All sub-agent results must go through evaluation
            if not sub_agent_result.get("evaluated", False):
                await self._enforce_evaluation(ctx, sub_agent_result)
            
            # Validate constitutional chain
            validation_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "sub_agent_type": sub_agent_result.get("sub_agent_type"),
                "constitutional_phase": sub_agent_result.get("constitutional_phase"),
                "validated_by": "constitutional_validator",
                "compliance_status": "approved",
                "validation_details": sub_agent_result.get("validation_report", {})
            }
            
            ctx.state.validation_chain.append(validation_entry)
            
            # Report to Overwatch (Crown authority)
            await self._report_to_overwatch(ctx, validation_entry)
            
            span.set_attribute("constitutional_compliance", True)
            
            return {
                **sub_agent_result,
                "constitutional_validation": validation_entry,
                "triad_compliant": True
            }
    
    async def _enforce_evaluation(self, ctx: GraphRunContext[TriadGraphState], sub_agent_result: Dict[str, Any]):
        """Mandatory evaluation for all sub-agent results."""
        
        # Create sub-evaluator if not already evaluated
        if ctx.state.constitutional_branch != "judicial":
            # Spawn evaluation sub-agent
            eval_request = SubAgentRequest(
                sub_agent_type="constitutional_evaluator",
                constitutional_phase="evaluation",
                parent_branch="judicial",
                task_description=f"Validate sub-agent result: {sub_agent_result}",
                specialized_parameters={"validation_type": "constitutional_compliance"},
                requires_validation=False  # Evaluators don't evaluate themselves
            )
            
            # This maintains the constitutional principle that ALL execution must be evaluated
            evaluation_result = await self._spawn_constitutional_evaluator(ctx, eval_request)
            sub_agent_result["evaluation_result"] = evaluation_result
            sub_agent_result["evaluated"] = True
    
    async def _report_to_overwatch(self, ctx: GraphRunContext[TriadGraphState], validation_entry: Dict[str, Any]):
        """Report constitutional validation to Overwatch (Crown authority)."""
        
        await ctx.deps.logfire_logger.info(
            "Constitutional validation reported to Overwatch",
            workflow_id=ctx.state.workflow_id,
            validation_entry=validation_entry,
            constitutional_compliance=True
        )
        
        # In a real system, this would trigger Overwatch monitoring
        # ensuring the Crown has oversight of all constitutional processes

class SubAgentTriadOrchestrator:
    """Orchestrator that enforces constitutional Triad principles for sub-agents."""
    
    def __init__(self, main_agents: Dict[str, Agent], deps: TriadDeps):
        self.main_agents = main_agents
        self.deps = deps
        self.constitutional_validator = ConstitutionalValidationNode()
    
    async def spawn_constitutional_sub_agent(self, request: SubAgentRequest, ctx: GraphRunContext[TriadGraphState]) -> Dict[str, Any]:
        """Spawn sub-agent while enforcing constitutional compliance."""
        
        # Validate constitutional authority
        if not request.validate_constitutional_authority(ctx.state.main_agent):
            raise ConstitutionalViolationError(
                f"Agent {ctx.state.main_agent} cannot spawn {request.constitutional_phase} sub-agent"
            )
        
        with logfire.span("constitutional_sub_agent_spawn") as span:
            span.set_attribute("main_agent", ctx.state.main_agent)
            span.set_attribute("sub_agent_type", request.sub_agent_type)
            span.set_attribute("constitutional_phase", request.constitutional_phase)
            
            # Spawn the sub-agent
            sub_agent_result = await self._execute_sub_agent(request, ctx)
            
            # CONSTITUTIONAL REQUIREMENT: All sub-agent results must be validated
            if request.requires_validation:
                validated_result = await self.constitutional_validator.run(ctx, sub_agent_result)
                return validated_result
            
            return sub_agent_result
    
    async def enforce_full_triad_cycle(self, initial_request: SubAgentRequest, ctx: GraphRunContext[TriadGraphState]) -> Dict[str, Any]:
        """Enforce complete Planning → Execution → Evaluation cycle for complex sub-agent workflows."""
        
        triad_results = {}
        
        with logfire.span("sub_agent_triad_cycle") as span:
            span.set_attribute("workflow_id", ctx.state.workflow_id)
            span.set_attribute("initial_phase", initial_request.constitutional_phase)
            
            # 1. Planning Phase (Legislative)
            if initial_request.constitutional_phase == "planning":
                planning_result = await self.spawn_constitutional_sub_agent(initial_request, ctx)
                triad_results["planning"] = planning_result
                
                # 2. Execution Phase (Executive) - Must execute the plan
                execution_request = SubAgentRequest(
                    sub_agent_type=f"executor_{initial_request.sub_agent_type}",
                    constitutional_phase="execution",
                    parent_branch="executive",
                    task_description=f"Execute plan: {planning_result['output']}",
                    specialized_parameters=planning_result.get("execution_parameters", {}),
                    requires_validation=True
                )
                
                execution_result = await self.spawn_constitutional_sub_agent(execution_request, ctx)
                triad_results["execution"] = execution_result
                
                # 3. Evaluation Phase (Judicial) - Must validate execution
                evaluation_request = SubAgentRequest(
                    sub_agent_type=f"evaluator_{initial_request.sub_agent_type}",
                    constitutional_phase="evaluation", 
                    parent_branch="judicial",
                    task_description=f"Validate execution: {execution_result['output']}",
                    specialized_parameters=execution_result.get("validation_parameters", {}),
                    requires_validation=False  # Evaluators are final authority
                )
                
                evaluation_result = await self.spawn_constitutional_sub_agent(evaluation_request, ctx)
                triad_results["evaluation"] = evaluation_result
                
                # 4. Overwatch Review (Crown) - Constitutional oversight
                await self._submit_to_overwatch_review(ctx, triad_results)
            
            span.set_attribute("triad_cycle_complete", True)
            span.set_attribute("constitutional_compliance", ctx.state.enforce_constitutional_flow())
            
            return {
                "full_triad_cycle": triad_results,
                "constitutional_compliance": True,
                "oversight_authority": "overwatch_reviewed"
            }

## Planner Agent Graph Workflows

### Complex Planning with Constitutional Sub-Agent Decomposition

```python
from pydantic_ai.graph import Graph, Node

class PlannerSubAgentNode(Node[TriadGraphState, SubAgentRequest, Dict[str, Any]]):
    """Node for spawning specialized planning sub-agents."""
    
    async def run(self, ctx: GraphRunContext[TriadGraphState], request: SubAgentRequest) -> Dict[str, Any]:
        """Spawn and run a specialized planning sub-agent."""
        
        # Create specialized planner sub-agent based on domain
        sub_agent = await self._create_specialized_planner(request.sub_agent_type)
        
        with logfire.span(f"planner_sub_agent_{request.sub_agent_type}") as span:
            span.set_attribute("main_workflow_id", ctx.state.workflow_id)
            span.set_attribute("sub_agent_type", request.sub_agent_type)
            span.set_attribute("task_description", request.task_description)
            
            try:
                # Run specialized planning with timeout
                result = await asyncio.wait_for(
                    sub_agent.run(request.task_description, deps=ctx.deps),
                    timeout=request.timeout_seconds
                )
                
                # Store result in shared state
                ctx.state.sub_agent_results[f"{request.sub_agent_type}_{len(ctx.state.sub_agent_results)}"] = {
                    "result": result.output,
                    "execution_time": result.execution_time,
                    "success": True
                }
                
                span.set_attribute("sub_agent_success", True)
                
                await ctx.deps.logfire_logger.info(
                    f"Planner sub-agent completed successfully",
                    workflow_id=ctx.state.workflow_id,
                    sub_agent_type=request.sub_agent_type,
                    execution_time=result.execution_time
                )
                
                return result.output
                
            except asyncio.TimeoutError:
                error_msg = f"Sub-agent {request.sub_agent_type} timed out after {request.timeout_seconds}s"
                ctx.state.error_history.append(error_msg)
                span.set_attribute("sub_agent_timeout", True)
                
                await ctx.deps.logfire_logger.warning(
                    "Planner sub-agent timeout",
                    workflow_id=ctx.state.workflow_id,
                    sub_agent_type=request.sub_agent_type,
                    timeout_seconds=request.timeout_seconds
                )
                
                raise
            
            except Exception as e:
                error_msg = f"Sub-agent {request.sub_agent_type} failed: {str(e)}"
                ctx.state.error_history.append(error_msg)
                span.set_attribute("sub_agent_error", str(e))
                
                await ctx.deps.logfire_logger.error(
                    "Planner sub-agent error",
                    workflow_id=ctx.state.workflow_id,
                    sub_agent_type=request.sub_agent_type,
                    error=str(e)
                )
                
                raise
    
    async def _create_specialized_planner(self, sub_agent_type: str) -> Agent:
        """Create specialized planning sub-agents for different domains."""
        
        specialized_prompts = {
            "data_pipeline_planner": """
            You are a specialized data pipeline planning agent.
            Focus on data flow, ETL processes, validation steps, and performance optimization.
            Consider data quality, schema validation, and error handling in your plans.
            """,
            
            "api_integration_planner": """
            You are a specialized API integration planning agent.
            Focus on API endpoints, authentication, rate limiting, error handling, and retry logic.
            Consider API versioning, payload validation, and response handling.
            """,
            
            "security_workflow_planner": """
            You are a specialized security workflow planning agent.
            Focus on authentication, authorization, encryption, audit trails, and compliance.
            Consider threat modeling, vulnerability assessment, and security monitoring.
            """,
            
            "performance_optimization_planner": """
            You are a specialized performance optimization planning agent.
            Focus on resource utilization, caching strategies, load balancing, and scalability.
            Consider bottleneck analysis, performance monitoring, and optimization techniques.
            """
        }
        
        system_prompt = specialized_prompts.get(sub_agent_type, 
            "You are a general-purpose planning sub-agent. Create detailed, actionable plans.")
        
        from backend.tools import SpecializedPlanningToolset
        
        return Agent(
            'openai:gpt-4o',
            system_prompt=system_prompt,
            deps_type=TriadDeps,
            tools=[SpecializedPlanningToolset(sub_agent_type)]
        )

class PlannerAggregationNode(Node[TriadGraphState, None, Dict[str, Any]]):
    """Node for aggregating sub-agent results into final plan."""
    
    async def run(self, ctx: GraphRunContext[TriadGraphState], _: None) -> Dict[str, Any]:
        """Aggregate all sub-agent planning results into cohesive workflow."""
        
        with logfire.span("planner_aggregation") as span:
            span.set_attribute("workflow_id", ctx.state.workflow_id)
            span.set_attribute("sub_agent_count", len(ctx.state.sub_agent_results))
            
            # Collect all sub-agent results
            sub_results = list(ctx.state.sub_agent_results.values())
            
            # Create aggregation prompt
            aggregation_prompt = f"""
            Aggregate the following specialized planning results into a cohesive, executable workflow:
            
            Sub-agent results:
            {[result["result"] for result in sub_results]}
            
            Original task context: {ctx.state.task_context}
            
            Create a unified workflow plan that:
            1. Integrates all specialized recommendations
            2. Resolves any conflicts between sub-plans
            3. Optimizes the overall execution flow
            4. Maintains quality and security standards
            """
            
            # Use main planner for aggregation
            aggregation_agent = Agent(
                'openai:gpt-4o',
                system_prompt="You are an expert workflow aggregation agent. Combine specialized plans into optimal unified workflows.",
                deps_type=TriadDeps
            )
            
            result = await aggregation_agent.run(aggregation_prompt, deps=ctx.deps)
            
            await ctx.deps.logfire_logger.info(
                "Planner aggregation completed",
                workflow_id=ctx.state.workflow_id,
                final_plan_complexity=len(result.output.get("tasks", [])),
                sub_agent_contributions=len(sub_results)
            )
            
            return result.output

# Graph definition for complex planning
def create_planner_graph() -> Graph[TriadGraphState]:
    """Create graph for complex planning with sub-agent spawning."""
    
    graph = Graph[TriadGraphState]()
    
    # Add nodes
    domain_analyzer = DomainAnalysisNode()
    sub_agent_spawner = PlannerSubAgentNode()
    aggregator = PlannerAggregationNode()
    
    # Define workflow
    graph.add_edge(domain_analyzer, sub_agent_spawner)
    graph.add_edge(sub_agent_spawner, aggregator)
    
    return graph
```

## Executor Agent Graph Workflows

### Parallel Task Execution with Specialized Sub-Agents

```python
class ExecutorSubAgentNode(Node[TriadGraphState, SubAgentRequest, Dict[str, Any]]):
    """Node for spawning specialized execution sub-agents."""
    
    async def run(self, ctx: GraphRunContext[TriadGraphState], request: SubAgentRequest) -> Dict[str, Any]:
        """Spawn specialized executor sub-agent for specific task types."""
        
        sub_agent = await self._create_specialized_executor(request.sub_agent_type)
        
        with logfire.span(f"executor_sub_agent_{request.sub_agent_type}") as span:
            span.set_attribute("main_workflow_id", ctx.state.workflow_id)
            span.set_attribute("sub_agent_type", request.sub_agent_type)
            
            # Execute with resource monitoring
            resource_monitor = ResourceMonitor()
            start_resources = await resource_monitor.capture_snapshot()
            
            try:
                result = await asyncio.wait_for(
                    sub_agent.run(request.task_description, deps=ctx.deps),
                    timeout=request.timeout_seconds
                )
                
                end_resources = await resource_monitor.capture_snapshot()
                resource_usage = resource_monitor.calculate_usage(start_resources, end_resources)
                
                # Store detailed execution result
                execution_result = {
                    "output": result.output,
                    "execution_time": result.execution_time,
                    "resource_usage": resource_usage,
                    "success": True,
                    "sub_agent_type": request.sub_agent_type
                }
                
                ctx.state.sub_agent_results[f"exec_{request.sub_agent_type}_{len(ctx.state.sub_agent_results)}"] = execution_result
                
                span.set_attribute("execution_success", True)
                span.set_attribute("resource_cpu_percent", resource_usage.get("cpu_percent", 0))
                span.set_attribute("resource_memory_mb", resource_usage.get("memory_mb", 0))
                
                return execution_result
                
            except Exception as e:
                await ctx.deps.logfire_logger.error(
                    "Executor sub-agent failed",
                    workflow_id=ctx.state.workflow_id,
                    sub_agent_type=request.sub_agent_type,
                    error=str(e)
                )
                raise
    
    async def _create_specialized_executor(self, sub_agent_type: str) -> Agent:
        """Create specialized execution sub-agents."""
        
        specialized_configs = {
            "data_processor": {
                "prompt": "You are a specialized data processing executor. Handle ETL, transformations, and data quality checks with precision.",
                "tools": ["DataProcessingToolset", "ValidationToolset"]
            },
            
            "api_integrator": {
                "prompt": "You are a specialized API integration executor. Handle REST/GraphQL calls, authentication, and error recovery.",
                "tools": ["APIIntegrationToolset", "RetryToolset"]
            },
            
            "file_processor": {
                "prompt": "You are a specialized file processing executor. Handle file I/O, format conversions, and batch operations.",
                "tools": ["FileProcessingToolset", "CompressionToolset"]
            },
            
            "database_operator": {
                "prompt": "You are a specialized database operations executor. Handle queries, transactions, and data migrations safely.",
                "tools": ["DatabaseToolset", "TransactionToolset"]
            }
        }
        
        config = specialized_configs.get(sub_agent_type, {
            "prompt": "You are a general-purpose execution sub-agent.",
            "tools": ["GeneralExecutionToolset"]
        })
        
        # Import tools dynamically
        tools = []
        for tool_name in config["tools"]:
            tool_class = getattr(__import__(f"backend.tools", fromlist=[tool_name]), tool_name)
            tools.append(tool_class())
        
        return Agent(
            'openai:gpt-4o',
            system_prompt=config["prompt"],
            deps_type=TriadDeps,
            tools=tools
        )

class ParallelExecutionNode(Node[TriadGraphState, List[SubAgentRequest], List[Dict[str, Any]]]):
    """Node for parallel execution of multiple sub-agents."""
    
    async def run(self, ctx: GraphRunContext[TriadGraphState], requests: List[SubAgentRequest]) -> List[Dict[str, Any]]:
        """Execute multiple sub-agents in parallel with resource management."""
        
        with logfire.span("parallel_execution") as span:
            span.set_attribute("workflow_id", ctx.state.workflow_id)
            span.set_attribute("parallel_task_count", len(requests))
            
            # Create semaphore for resource management
            max_concurrent = min(len(requests), 5)  # Limit concurrent sub-agents
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def execute_with_semaphore(request: SubAgentRequest) -> Dict[str, Any]:
                async with semaphore:
                    executor_node = ExecutorSubAgentNode()
                    return await executor_node.run(ctx, request)
            
            # Execute all sub-agents in parallel
            try:
                results = await asyncio.gather(
                    *[execute_with_semaphore(req) for req in requests],
                    return_exceptions=True
                )
                
                # Process results and exceptions
                successful_results = []
                failed_results = []
                
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        failed_results.append({
                            "request_index": i,
                            "sub_agent_type": requests[i].sub_agent_type,
                            "error": str(result)
                        })
                    else:
                        successful_results.append(result)
                
                span.set_attribute("successful_executions", len(successful_results))
                span.set_attribute("failed_executions", len(failed_results))
                
                # Log execution summary
                await ctx.deps.logfire_logger.info(
                    "Parallel execution completed",
                    workflow_id=ctx.state.workflow_id,
                    total_tasks=len(requests),
                    successful=len(successful_results),
                    failed=len(failed_results),
                    failed_details=failed_results
                )
                
                return successful_results
                
            except Exception as e:
                await ctx.deps.logfire_logger.error(
                    "Parallel execution failed",
                    workflow_id=ctx.state.workflow_id,
                    error=str(e)
                )
                raise

# Graph definition for parallel execution
def create_executor_graph() -> Graph[TriadGraphState]:
    """Create graph for parallel execution with specialized sub-agents."""
    
    graph = Graph[TriadGraphState]()
    
    # Add nodes
    task_analyzer = TaskAnalysisNode()
    sub_agent_dispatcher = SubAgentDispatcherNode()
    parallel_executor = ParallelExecutionNode()
    result_aggregator = ExecutionAggregatorNode()
    
    # Define execution flow
    graph.add_edge(task_analyzer, sub_agent_dispatcher)
    graph.add_edge(sub_agent_dispatcher, parallel_executor)
    graph.add_edge(parallel_executor, result_aggregator)
    
    return graph
```

## Evaluator Agent Graph Workflows

### Multi-Dimensional Validation with Specialized Sub-Evaluators

```python
class EvaluatorSubAgentNode(Node[TriadGraphState, SubAgentRequest, Dict[str, Any]]):
    """Node for spawning specialized validation sub-agents."""
    
    async def run(self, ctx: GraphRunContext[TriadGraphState], request: SubAgentRequest) -> Dict[str, Any]:
        """Spawn specialized evaluator sub-agent for specific validation aspects."""
        
        sub_agent = await self._create_specialized_evaluator(request.sub_agent_type)
        
        with logfire.span(f"evaluator_sub_agent_{request.sub_agent_type}") as span:
            span.set_attribute("main_workflow_id", ctx.state.workflow_id)
            span.set_attribute("validation_type", request.sub_agent_type)
            
            try:
                result = await sub_agent.run(request.task_description, deps=ctx.deps)
                
                validation_result = {
                    "validation_type": request.sub_agent_type,
                    "validation_score": result.output.get("score", 0.0),
                    "validation_details": result.output.get("details", {}),
                    "recommendations": result.output.get("recommendations", []),
                    "passed": result.output.get("passed", False),
                    "critical_issues": result.output.get("critical_issues", [])
                }
                
                ctx.state.sub_agent_results[f"eval_{request.sub_agent_type}"] = validation_result
                
                span.set_attribute("validation_passed", validation_result["passed"])
                span.set_attribute("validation_score", validation_result["validation_score"])
                span.set_attribute("critical_issue_count", len(validation_result["critical_issues"]))
                
                return validation_result
                
            except Exception as e:
                await ctx.deps.logfire_logger.error(
                    "Evaluator sub-agent failed",
                    workflow_id=ctx.state.workflow_id,
                    validation_type=request.sub_agent_type,
                    error=str(e)
                )
                raise
    
    async def _create_specialized_evaluator(self, sub_agent_type: str) -> Agent:
        """Create specialized validation sub-agents."""
        
        specialized_validators = {
            "data_quality_validator": {
                "prompt": """You are a specialized data quality validation agent.
                Focus on data completeness, accuracy, consistency, validity, and uniqueness.
                Identify data anomalies, schema violations, and quality degradation.""",
                "tools": ["DataQualityToolset", "StatisticalAnalysisToolset"]
            },
            
            "performance_validator": {
                "prompt": """You are a specialized performance validation agent.
                Focus on execution time, resource usage, throughput, and scalability.
                Identify performance bottlenecks and optimization opportunities.""",
                "tools": ["PerformanceAnalysisToolset", "ResourceMonitoringToolset"]
            },
            
            "security_validator": {
                "prompt": """You are a specialized security validation agent.
                Focus on authentication, authorization, data protection, and compliance.
                Identify security vulnerabilities and compliance violations.""",
                "tools": ["SecurityScanningToolset", "ComplianceCheckToolset"]
            },
            
            "business_rule_validator": {
                "prompt": """You are a specialized business rule validation agent.
                Focus on business logic correctness, constraint compliance, and rule adherence.
                Identify business rule violations and logical inconsistencies.""",
                "tools": ["BusinessRuleToolset", "LogicValidationToolset"]
            }
        }
        
        config = specialized_validators.get(sub_agent_type, {
            "prompt": "You are a general-purpose validation sub-agent.",
            "tools": ["GeneralValidationToolset"]
        })
        
        # Import and instantiate tools
        tools = []
        for tool_name in config["tools"]:
            try:
                tool_class = getattr(__import__(f"backend.tools", fromlist=[tool_name]), tool_name)
                tools.append(tool_class())
            except ImportError:
                # Fallback to general tools if specialized tools not available
                pass
        
        return Agent(
            'anthropic:claude-3-5-sonnet-latest',  # Use Claude for detailed validation
            system_prompt=config["prompt"],
            deps_type=TriadDeps,
            tools=tools
        )

# Graph definition for comprehensive validation
def create_evaluator_graph() -> Graph[TriadGraphState]:
    """Create graph for multi-dimensional validation with specialized sub-evaluators."""
    
    graph = Graph[TriadGraphState]()
    
    # Add validation nodes
    validation_planner = ValidationPlanningNode()
    parallel_validator = ParallelValidationNode()
    validation_aggregator = ValidationAggregationNode()
    recommendation_generator = RecommendationGeneratorNode()
    
    # Define validation flow
    graph.add_edge(validation_planner, parallel_validator)
    graph.add_edge(parallel_validator, validation_aggregator)
    graph.add_edge(validation_aggregator, recommendation_generator)
    
    return graph
```

## Graph Orchestration System

### Main Agent Graph Integration

```python
class TriadGraphOrchestrator:
    """Orchestrator for managing graph workflows across all main agents."""
    
    def __init__(self, deps: TriadDeps):
        self.deps = deps
        self.graphs = {
            "planner": create_planner_graph(),
            "executor": create_executor_graph(),
            "evaluator": create_evaluator_graph()
        }
    
    async def execute_complex_workflow(self, workflow_request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute complex workflow using appropriate graph-based sub-agent spawning."""
        
        workflow_id = workflow_request.get("id", str(uuid.uuid4()))
        main_agent = workflow_request.get("agent", "planner")
        
        with logfire.span("complex_workflow_execution") as span:
            span.set_attribute("workflow_id", workflow_id)
            span.set_attribute("main_agent", main_agent)
            span.set_attribute("complexity_level", workflow_request.get("complexity", "medium"))
            
            # Initialize graph state
            initial_state = TriadGraphState(
                workflow_id=workflow_id,
                main_agent=main_agent,
                task_context=workflow_request.get("context", {}),
                execution_metadata={
                    "start_time": datetime.utcnow().isoformat(),
                    "complexity_level": workflow_request.get("complexity", "medium"),
                    "priority": workflow_request.get("priority", 1)
                }
            )
            
            try:
                # Select and execute appropriate graph
                graph = self.graphs[main_agent]
                
                # Execute graph with state persistence
                final_state = await graph.run(
                    initial_state,
                    deps=self.deps
                )
                
                execution_result = {
                    "workflow_id": workflow_id,
                    "main_agent": main_agent,
                    "final_state": final_state,
                    "sub_agent_results": final_state.sub_agent_results,
                    "execution_metadata": final_state.execution_metadata,
                    "success": True,
                    "error_history": final_state.error_history
                }
                
                span.set_attribute("workflow_success", True)
                span.set_attribute("sub_agent_count", len(final_state.sub_agent_results))
                
                await self.deps.logfire_logger.info(
                    "Complex workflow completed successfully",
                    workflow_id=workflow_id,
                    main_agent=main_agent,
                    sub_agent_count=len(final_state.sub_agent_results),
                    total_errors=len(final_state.error_history)
                )
                
                return execution_result
                
            except Exception as e:
                span.set_attribute("workflow_failed", True)
                span.set_attribute("error", str(e))
                
                await self.deps.logfire_logger.error(
                    "Complex workflow failed",
                    workflow_id=workflow_id,
                    main_agent=main_agent,
                    error=str(e)
                )
                
                return {
                    "workflow_id": workflow_id,
                    "main_agent": main_agent,
                    "success": False,
                    "error": str(e),
                    "partial_results": initial_state.sub_agent_results
                }
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get real-time status of executing workflow."""
        
        # Query graph execution state from storage
        workflow_state = await self._get_workflow_state(workflow_id)
        
        if not workflow_state:
            return {"error": "Workflow not found"}
        
        return {
            "workflow_id": workflow_id,
            "status": workflow_state.get("status", "unknown"),
            "progress": self._calculate_progress(workflow_state),
            "active_sub_agents": workflow_state.get("active_sub_agents", []),
            "completed_sub_agents": len(workflow_state.get("sub_agent_results", {})),
            "error_count": len(workflow_state.get("error_history", []))
        }
    
    def _calculate_progress(self, workflow_state: Dict[str, Any]) -> float:
        """Calculate workflow progress percentage."""
        total_tasks = workflow_state.get("total_expected_tasks", 1)
        completed_tasks = len(workflow_state.get("sub_agent_results", {}))
        
        return min(completed_tasks / total_tasks, 1.0) * 100

# Integration with main agents
async def integrate_graph_workflows(main_agents: Dict[str, Agent], deps: TriadDeps):
    """Integrate graph workflows with main agents."""
    
    orchestrator = TriadGraphOrchestrator(deps)
    
    # Add graph execution tools to main agents
    @main_agents["planner"].tool
    async def execute_complex_planning(ctx: RunContext[TriadDeps], requirements: str, complexity: str = "medium") -> str:
        """Execute complex planning using graph-based sub-agent spawning."""
        workflow_request = {
            "id": str(uuid.uuid4()),
            "agent": "planner",
            "context": {"requirements": requirements},
            "complexity": complexity
        }
        
        result = await orchestrator.execute_complex_workflow(workflow_request)
        return f"Complex planning completed. Workflow ID: {result['workflow_id']}"
    
    @main_agents["executor"].tool
    async def execute_parallel_tasks(ctx: RunContext[TriadDeps], task_list: List[Dict[str, Any]]) -> str:
        """Execute multiple tasks in parallel using specialized sub-agents."""
        workflow_request = {
            "id": str(uuid.uuid4()),
            "agent": "executor",
            "context": {"tasks": task_list},
            "complexity": "high" if len(task_list) > 5 else "medium"
        }
        
        result = await orchestrator.execute_complex_workflow(workflow_request)
        return f"Parallel execution completed. Workflow ID: {result['workflow_id']}"
    
    @main_agents["evaluator"].tool
    async def comprehensive_validation(ctx: RunContext[TriadDeps], validation_targets: List[str]) -> str:
        """Perform comprehensive validation using specialized sub-evaluators."""
        workflow_request = {
            "id": str(uuid.uuid4()),
            "agent": "evaluator",
            "context": {"validation_targets": validation_targets},
            "complexity": "high" if len(validation_targets) > 3 else "medium"
        }
        
        result = await orchestrator.execute_complex_workflow(workflow_request)
        return f"Comprehensive validation completed. Workflow ID: {result['workflow_id']}"
    
    return orchestrator
```

This graph-based sub-agent spawning system provides:

- **Dynamic Task Decomposition**: Main agents can spawn specialized sub-agents for complex tasks
- **Stateful Workflow Management**: Persistent state across the entire workflow execution
- **Parallel Execution**: Multiple sub-agents can work simultaneously with resource management
- **Specialized Capabilities**: Sub-agents optimized for specific domains and tasks
- **Comprehensive Monitoring**: Full observability through Logfire integration
- **Error Recovery**: Robust error handling and partial result preservation

The system enables the AI Triad to handle significantly more complex workflows by leveraging specialized sub-agents while maintaining control and observability.