# Constitutional Agent Evaluation and Parliamentary Performance Testing

## Overview

The AI Triad system uses Pydantic AI's Evals framework for systematic **constitutional compliance testing**, **parliamentary performance evaluation**, and **Westminster accountability validation**. This ensures all agents maintain democratic principles, constitutional adherence, and proper Westminster parliamentary behavior while delivering high-quality workflow automation.

## 🏛️ Constitutional Evaluation Framework

### Westminster Compliance Testing

```python
from pydantic_ai.evals import Case, Dataset, Eval
from pydantic import BaseModel
from typing import List, Dict, Any
import asyncio

class ConstitutionalComplianceCase(BaseModel):
    """Evaluation case for Westminster constitutional compliance."""
    scenario: str
    constitutional_challenge: str
    expected_parliamentary_response: Dict[str, Any]
    required_democratic_principles: List[str]
    constitutional_authority_level: str  # legislative, executive, judicial, crown

class ParliamentaryPerformanceResult(BaseModel):
    """Evaluation result with constitutional compliance metrics."""
    case_id: str
    agent_type: str
    constitutional_compliance: bool
    democratic_accountability_score: float
    westminster_adherence_score: float
    parliamentary_procedure_score: float
    question_period_response_quality: float
    collective_responsibility_compliance: bool
    crown_authority_respect: bool
    performance_metrics: Dict[str, float]
```

## Evaluation Architecture

### Core Components

```python
from pydantic_ai.evals import Case, Dataset, Eval
from pydantic import BaseModel
from typing import List, Dict, Any
import asyncio

class TriadEvalCase(BaseModel):
    """Base evaluation case for AI Triad agents."""
    input_data: Dict[str, Any]
    expected_output: Dict[str, Any]
    metadata: Dict[str, Any]
    agent_type: str
    complexity_level: str  # simple, medium, complex
    
class TriadEvalResult(BaseModel):
    """Evaluation result with detailed metrics."""
    case_id: str
    agent_type: str
    success: bool
    accuracy_score: float
    execution_time: float
    error_message: str = None
    performance_metrics: Dict[str, float]
```

## Agent-Specific Evaluation Systems

### 1. Planner Agent Evaluation

```python
from pydantic_ai.evals import Eval, Dataset, Case

class PlannerEvaluation:
    """Comprehensive evaluation system for Planner Agent."""
    
    def __init__(self, planner_agent):
        self.agent = planner_agent
        self.eval_datasets = self._create_datasets()
    
    def _create_datasets(self) -> Dict[str, Dataset]:
        """Create evaluation datasets for different planning scenarios."""
        
        # Simple workflow planning
        simple_cases = [
            Case(
                input="Create a workflow to process customer orders",
                expected_output={
                    "workflow_structure": "sequential",
                    "task_count": 3,
                    "estimated_duration": 1800,
                    "has_validation": True
                },
                metadata={"complexity": "simple", "domain": "ecommerce"}
            ),
            Case(
                input="Design a data backup workflow",
                expected_output={
                    "workflow_structure": "sequential",
                    "task_count": 4,
                    "estimated_duration": 3600,
                    "has_error_handling": True
                },
                metadata={"complexity": "simple", "domain": "infrastructure"}
            )
        ]
        
        # Complex workflow planning
        complex_cases = [
            Case(
                input="Create a multi-stage ML pipeline with data validation, training, and deployment",
                expected_output={
                    "workflow_structure": "parallel_stages",
                    "task_count": 12,
                    "estimated_duration": 7200,
                    "has_dependency_optimization": True,
                    "resource_requirements": {"cpu": 4, "memory": 8192}
                },
                metadata={"complexity": "complex", "domain": "machine_learning"}
            )
        ]
        
        return {
            "simple_planning": Dataset(simple_cases),
            "complex_planning": Dataset(complex_cases),
        }
    
    async def evaluate_planning_accuracy(self, case: Case) -> float:
        """Evaluate planning accuracy against expected outcomes."""
        result = await self.agent.run(case.input, deps=self.deps)
        
        # Custom evaluation logic
        accuracy_factors = []
        
        # Check workflow structure
        if result.output.structure == case.expected_output.get("workflow_structure"):
            accuracy_factors.append(0.3)
        
        # Check task count (within 20% tolerance)
        expected_tasks = case.expected_output.get("task_count", 0)
        actual_tasks = len(result.output.tasks)
        if abs(actual_tasks - expected_tasks) / expected_tasks <= 0.2:
            accuracy_factors.append(0.3)
        
        # Check duration estimation (within 30% tolerance)
        expected_duration = case.expected_output.get("estimated_duration", 0)
        actual_duration = result.output.estimated_duration
        if abs(actual_duration - expected_duration) / expected_duration <= 0.3:
            accuracy_factors.append(0.2)
        
        # Check required features
        if case.expected_output.get("has_validation") and result.output.has_validation_tasks:
            accuracy_factors.append(0.2)
        
        return sum(accuracy_factors)
    
    async def run_comprehensive_evaluation(self) -> Dict[str, Any]:
        """Run comprehensive evaluation across all datasets."""
        results = {}
        
        for dataset_name, dataset in self.eval_datasets.items():
            eval_results = []
            
            for case in dataset.cases:
                start_time = time.time()
                
                try:
                    accuracy = await self.evaluate_planning_accuracy(case)
                    execution_time = time.time() - start_time
                    
                    eval_results.append({
                        "case_id": case.metadata.get("id", "unknown"),
                        "accuracy": accuracy,
                        "execution_time": execution_time,
                        "success": True
                    })
                    
                except Exception as e:
                    eval_results.append({
                        "case_id": case.metadata.get("id", "unknown"),
                        "accuracy": 0.0,
                        "execution_time": time.time() - start_time,
                        "success": False,
                        "error": str(e)
                    })
            
            results[dataset_name] = {
                "total_cases": len(eval_results),
                "success_rate": len([r for r in eval_results if r["success"]]) / len(eval_results),
                "average_accuracy": sum(r["accuracy"] for r in eval_results) / len(eval_results),
                "average_execution_time": sum(r["execution_time"] for r in eval_results) / len(eval_results),
                "detailed_results": eval_results
            }
        
        return results
```

### 2. Executor Agent Evaluation

```python
class ExecutorEvaluation:
    """Evaluation system for Executor Agent performance."""
    
    def __init__(self, executor_agent):
        self.agent = executor_agent
        self.eval_datasets = self._create_execution_datasets()
    
    def _create_execution_datasets(self) -> Dict[str, Dataset]:
        """Create datasets for execution testing."""
        
        # Data processing tasks
        data_processing_cases = [
            Case(
                input={
                    "task_type": "data_processing",
                    "data_size": 1000,
                    "processing_type": "batch",
                    "operations": ["filter", "transform", "aggregate"]
                },
                expected_output={
                    "status": "completed",
                    "processed_records": 1000,
                    "execution_time_max": 5.0,
                    "memory_usage_max": 512
                },
                metadata={"complexity": "medium", "resource_intensive": False}
            )
        ]
        
        # API integration tasks
        api_integration_cases = [
            Case(
                input={
                    "task_type": "api_call",
                    "endpoint": "https://api.example.com/data",
                    "method": "POST",
                    "retry_policy": "exponential_backoff"
                },
                expected_output={
                    "status": "completed",
                    "response_time_max": 2.0,
                    "retry_attempts_max": 3,
                    "error_handling": True
                },
                metadata={"complexity": "simple", "external_dependency": True}
            )
        ]
        
        return {
            "data_processing": Dataset(data_processing_cases),
            "api_integration": Dataset(api_integration_cases),
        }
    
    async def evaluate_execution_reliability(self, case: Case) -> Dict[str, float]:
        """Evaluate execution reliability and performance."""
        results = []
        
        # Run multiple times for reliability testing
        for _ in range(5):
            try:
                start_time = time.time()
                result = await self.agent.run(f"Execute task: {case.input}", deps=self.deps)
                execution_time = time.time() - start_time
                
                results.append({
                    "success": result.output.status == "completed",
                    "execution_time": execution_time,
                    "resource_usage": result.output.resource_usage
                })
                
            except Exception as e:
                results.append({
                    "success": False,
                    "execution_time": float('inf'),
                    "error": str(e)
                })
        
        # Calculate reliability metrics
        success_rate = len([r for r in results if r["success"]]) / len(results)
        avg_execution_time = sum(r.get("execution_time", 0) for r in results if r["success"]) / max(1, len([r for r in results if r["success"]]))
        
        return {
            "reliability_score": success_rate,
            "performance_score": 1.0 / max(avg_execution_time, 0.1),  # Inverse of time
            "consistency_score": 1.0 - (max(r.get("execution_time", 0) for r in results if r["success"]) - min(r.get("execution_time", float('inf')) for r in results if r["success"])) / avg_execution_time if avg_execution_time > 0 else 0
        }
```

### 3. Evaluator Agent Evaluation (Meta-Evaluation)

```python
class EvaluatorEvaluation:
    """Meta-evaluation system for the Evaluator Agent."""
    
    def __init__(self, evaluator_agent):
        self.agent = evaluator_agent
        self.eval_datasets = self._create_validation_datasets()
    
    def _create_validation_datasets(self) -> Dict[str, Dataset]:
        """Create datasets with known validation outcomes."""
        
        # High-quality results (should pass validation)
        high_quality_cases = [
            Case(
                input={
                    "execution_result": {
                        "task_id": "test_001",
                        "status": "completed",
                        "output_data": {"processed_items": 1000, "error_count": 0},
                        "execution_time": 2.5,
                        "accuracy_metrics": {"precision": 0.98, "recall": 0.97}
                    }
                },
                expected_output={
                    "validation_status": "passed",
                    "accuracy_score": 0.975,
                    "recommendations": []
                },
                metadata={"quality_level": "high", "should_pass": True}
            )
        ]
        
        # Low-quality results (should fail validation)
        low_quality_cases = [
            Case(
                input={
                    "execution_result": {
                        "task_id": "test_002",
                        "status": "completed",
                        "output_data": {"processed_items": 500, "error_count": 100},
                        "execution_time": 8.5,
                        "accuracy_metrics": {"precision": 0.75, "recall": 0.80}
                    }
                },
                expected_output={
                    "validation_status": "failed",
                    "accuracy_score": 0.775,
                    "recommendations": ["improve_error_handling", "optimize_performance"]
                },
                metadata={"quality_level": "low", "should_pass": False}
            )
        ]
        
        return {
            "high_quality_validation": Dataset(high_quality_cases),
            "low_quality_validation": Dataset(low_quality_cases),
        }
    
    async def evaluate_validation_accuracy(self, case: Case) -> float:
        """Evaluate how accurately the Evaluator validates results."""
        result = await self.agent.run(f"Validate execution: {case.input}", deps=self.deps)
        
        expected_pass = case.metadata.get("should_pass", True)
        actual_pass = result.output.validation_status == "passed"
        
        # Binary accuracy for pass/fail
        validation_accuracy = 1.0 if expected_pass == actual_pass else 0.0
        
        # Score accuracy (within 10% tolerance)
        expected_score = case.expected_output.get("accuracy_score", 0.5)
        actual_score = result.output.accuracy_score
        score_accuracy = 1.0 if abs(actual_score - expected_score) <= 0.1 else 0.0
        
        # Recommendation relevance (simplified)
        expected_recommendations = case.expected_output.get("recommendations", [])
        actual_recommendations = result.output.recommendations
        recommendation_accuracy = len(set(expected_recommendations) & set(actual_recommendations)) / max(len(expected_recommendations), 1)
        
        return (validation_accuracy * 0.5) + (score_accuracy * 0.3) + (recommendation_accuracy * 0.2)
```

## Continuous Evaluation Pipeline

### Automated Evaluation System

```python
import logfire
from datetime import datetime, timedelta
import asyncio

class TriadEvaluationPipeline:
    """Continuous evaluation pipeline for all AI Triad agents."""
    
    def __init__(self, agents: Dict[str, Any], deps: TriadDeps):
        self.agents = agents
        self.deps = deps
        self.evaluators = {
            "planner": PlannerEvaluation(agents["planner"]),
            "executor": ExecutorEvaluation(agents["executor"]),
            "evaluator": EvaluatorEvaluation(agents["evaluator"])
        }
    
    async def run_daily_evaluations(self):
        """Run comprehensive daily evaluations for all agents."""
        with logfire.span("daily_agent_evaluation") as span:
            evaluation_results = {}
            
            for agent_name, evaluator in self.evaluators.items():
                span.set_attribute(f"evaluating_{agent_name}", True)
                
                try:
                    results = await evaluator.run_comprehensive_evaluation()
                    evaluation_results[agent_name] = results
                    
                    # Log results to Logfire
                    await self.deps.logfire_logger.info(
                        f"Daily evaluation completed for {agent_name}",
                        agent=agent_name,
                        **results
                    )
                    
                    span.set_attribute(f"{agent_name}_evaluation_success", True)
                    
                except Exception as e:
                    await self.deps.logfire_logger.error(
                        f"Daily evaluation failed for {agent_name}",
                        agent=agent_name,
                        error=str(e)
                    )
                    span.set_attribute(f"{agent_name}_evaluation_failed", True)
            
            # Store results in database for trend analysis
            await self._store_evaluation_results(evaluation_results)
            
            # Generate improvement recommendations
            recommendations = await self._generate_improvement_recommendations(evaluation_results)
            
            return {
                "timestamp": datetime.now(timezone.utc),
                "results": evaluation_results,
                "recommendations": recommendations
            }
    
    async def _store_evaluation_results(self, results: Dict[str, Any]):
        """Store evaluation results for historical analysis."""
        from backend.models import EvaluationResult
        
        for agent_name, agent_results in results.items():
            eval_record = EvaluationResult(
                agent_name=agent_name,
                evaluation_date=datetime.now(timezone.utc),
                results=agent_results,
                overall_score=self._calculate_overall_score(agent_results)
            )
            
            self.deps.db_session.add(eval_record)
        
        await self.deps.db_session.commit()
    
    async def _generate_improvement_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate actionable improvement recommendations based on evaluation results."""
        recommendations = []
        
        for agent_name, agent_results in results.items():
            overall_success_rate = sum(dataset["success_rate"] for dataset in agent_results.values()) / len(agent_results)
            overall_accuracy = sum(dataset["average_accuracy"] for dataset in agent_results.values()) / len(agent_results)
            
            if overall_success_rate < 0.95:
                recommendations.append(f"Improve {agent_name} reliability - current success rate: {overall_success_rate:.2%}")
            
            if overall_accuracy < 0.90:
                recommendations.append(f"Enhance {agent_name} accuracy - current accuracy: {overall_accuracy:.2%}")
            
            # Agent-specific recommendations
            if agent_name == "planner" and any(dataset["average_execution_time"] > 10 for dataset in agent_results.values()):
                recommendations.append("Optimize planner performance - planning taking too long")
            
            if agent_name == "executor" and any(dataset["average_execution_time"] > 30 for dataset in agent_results.values()):
                recommendations.append("Optimize executor performance - execution taking too long")
        
        return recommendations

# Integration with main application
async def setup_evaluation_pipeline(app_state):
    """Setup automated evaluation pipeline."""
    pipeline = TriadEvaluationPipeline(app_state.agents, app_state.deps)
    
    # Schedule daily evaluations
    import schedule
    schedule.every().day.at("02:00").do(pipeline.run_daily_evaluations)
    
    return pipeline
```

## Performance Monitoring Integration

### Logfire Integration

```python
import logfire

class EvaluationLogfireIntegration:
    """Integration between evaluations and Logfire monitoring."""
    
    @staticmethod
    async def log_evaluation_metrics(agent_name: str, results: Dict[str, Any]):
        """Log evaluation metrics to Logfire for monitoring."""
        
        # Log overall performance
        await logfire.info(
            f"Agent evaluation completed: {agent_name}",
            agent=agent_name,
            success_rate=results.get("success_rate", 0),
            average_accuracy=results.get("average_accuracy", 0),
            average_execution_time=results.get("average_execution_time", 0)
        )
        
        # Log performance trends
        with logfire.span(f"{agent_name}_performance_trend") as span:
            span.set_attribute("agent", agent_name)
            span.set_attribute("evaluation_timestamp", datetime.now(timezone.utc).isoformat())
            
            for metric_name, metric_value in results.items():
                if isinstance(metric_value, (int, float)):
                    span.set_attribute(f"metric_{metric_name}", metric_value)
    
    @staticmethod
    async def create_performance_alerts(results: Dict[str, Any]):
        """Create alerts for performance degradation."""
        
        for agent_name, agent_results in results.items():
            success_rate = agent_results.get("success_rate", 1.0)
            accuracy = agent_results.get("average_accuracy", 1.0)
            
            if success_rate < 0.90:
                await logfire.warning(
                    f"Low success rate detected for {agent_name}",
                    agent=agent_name,
                    success_rate=success_rate,
                    alert_type="performance_degradation"
                )
            
            if accuracy < 0.85:
                await logfire.warning(
                    f"Low accuracy detected for {agent_name}",
                    agent=agent_name,
                    accuracy=accuracy,
                    alert_type="accuracy_degradation"
                )
```

This comprehensive evaluation system provides:

- **Systematic Performance Testing**: Structured evaluation of each agent's capabilities
- **Continuous Improvement**: Daily automated evaluations with trend analysis
- **Quality Assurance**: Validation that agents meet performance standards
- **Data-Driven Optimization**: Actionable recommendations based on evaluation results
- **Observable Monitoring**: Full integration with Logfire for performance tracking

The system ensures that the AI Triad agents continuously improve their performance through rigorous, automated evaluation processes.