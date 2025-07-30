"""
Evaluator Agent - Judicial Branch of Westminster Parliamentary AI System

Represents the judicial authority responsible for validation, compliance checking,
and constitutional review following Westminster principles.
"""

from typing import Dict, Any, List, Optional, Tuple
from pydantic_ai import RunContext, ModelRetry
from datetime import datetime, timezone
import uuid
import logfire

from ..core.base import BaseAgent
from triad.core.dependencies import TriadDeps
from triad.core.constitutional import ConstitutionalAuthority, ConstitutionalPrinciple
from triad.models.execution import ExecutionResult, TaskExecution
from triad.models.validation import ValidationReport, ValidationDetail, QualityIndicator, ValidationStatus


class EvaluatorAgent(BaseAgent):
    """
    Evaluator Agent representing the JUDICIAL BRANCH.
    
    Constitutional responsibilities:
    - Validate execution results
    - Ensure constitutional compliance
    - Provide impartial review
    - Challenge unconstitutional actions
    - Participate in collective cabinet responsibility
    """
    
    def __init__(self, model: str = "anthropic:claude-3-5-sonnet-latest", deps_type: type[TriadDeps] = TriadDeps):
        system_prompt = """
        You are the Evaluator Agent representing the JUDICIAL BRANCH in the Westminster parliamentary system.
        
        Your constitutional authority includes:
        1. Providing impartial validation of execution results
        2. Ensuring constitutional compliance of all actions
        3. Reviewing quality and accuracy of outcomes
        4. Challenging unconstitutional decisions
        
        You MUST:
        - Provide impartial constitutional interpretation and validation
        - Participate in collective cabinet responsibility for system decisions
        - Challenge unconstitutional actions through proper parliamentary procedure
        - Respect Crown (Overwatch) final constitutional authority
        - Ensure all actions comply with Westminster democratic principles
        - Apply consistent validation criteria
        - Document all findings transparently
        
        You CANNOT:
        - Create policies (Legislative responsibility)
        - Execute tasks (Executive responsibility)
        - Override Crown constitutional authority
        - Show bias in validation
        
        Always ensure your validations are:
        - Constitutionally sound
        - Impartial and evidence-based
        - Thoroughly documented
        - Constructive in feedback
        """
        
        super().__init__(
            name="evaluator_agent",
            constitutional_authority=ConstitutionalAuthority.JUDICIAL,
            model=model,
            system_prompt=system_prompt,
            deps_type=deps_type
        )
        
        # Register evaluator-specific tools
        self._register_evaluator_tools()
    
    def _register_evaluator_tools(self):
        """Register tools specific to the Evaluator agent."""
        
        @self.agent.tool
        async def validate_execution_result(
            ctx: RunContext[TriadDeps],
            execution_id: str,
            workflow_id: str,
            accuracy_threshold: float = 0.95,
            strict_mode: bool = False
        ) -> ValidationReport:
            """Validate execution results with constitutional compliance."""
            with logfire.span("validate_execution_result", execution_id=execution_id):
                # Fetch execution result
                result = await ctx.deps.db_session.execute(
                    """
                    SELECT * FROM task_executions 
                    WHERE workflow_id = $1 
                    ORDER BY start_time
                    """,
                    workflow_id
                )
                executions = await result.fetchall()
                
                if not executions:
                    raise ValueError(f"No executions found for workflow {workflow_id}")
                
                # Validate constitutional authority
                validation = await ctx.deps.validate_constitutional_decision(
                    ConstitutionalDecision(
                        constitutional_authority=ConstitutionalAuthority.JUDICIAL,
                        decision_type="validation",
                        description=f"Validate execution: {execution_id}",
                        constitutional_principles=[
                            ConstitutionalPrinciple.RULE_OF_LAW,
                            ConstitutionalPrinciple.DEMOCRATIC_ACCOUNTABILITY
                        ],
                        agent_responsible="evaluator_agent"
                    )
                )
                
                if not validation["constitutional_compliance"]:
                    raise ValueError(f"Constitutional violations: {validation['violations']}")
                
                # Perform multi-dimensional validation
                validation_details = []
                overall_score = 0.0
                
                # 1. Accuracy validation
                accuracy_detail = await _validate_accuracy(executions, accuracy_threshold)
                validation_details.append(accuracy_detail)
                overall_score += accuracy_detail.score * 0.4
                
                # 2. Constitutional compliance validation
                constitutional_detail = await _validate_constitutional_compliance(ctx, executions)
                validation_details.append(constitutional_detail)
                overall_score += constitutional_detail.score * 0.3
                
                # 3. Performance validation
                performance_detail = await _validate_performance(executions)
                validation_details.append(performance_detail)
                overall_score += performance_detail.score * 0.2
                
                # 4. Resource usage validation
                resource_detail = await _validate_resource_usage(executions)
                validation_details.append(resource_detail)
                overall_score += resource_detail.score * 0.1
                
                # Determine validation status
                if overall_score >= accuracy_threshold:
                    validation_status = ValidationStatus.PASSED
                elif overall_score >= accuracy_threshold * 0.8 and not strict_mode:
                    validation_status = ValidationStatus.WARNING
                else:
                    validation_status = ValidationStatus.FAILED
                
                # Create validation report
                report = ValidationReport(
                    report_id=f"val_{uuid.uuid4().hex[:8]}",
                    execution_id=execution_id,
                    workflow_id=workflow_id,
                    validation_status=validation_status,
                    accuracy_score=overall_score,
                    constitutional_compliance=constitutional_detail.passed,
                    westminster_adherence=True,
                    validation_details=validation_details,
                    quality_indicators=await _calculate_quality_indicators(executions),
                    recommendations=await _generate_recommendations(validation_details),
                    created_at=datetime.now(timezone.utc)
                )
                
                # Store validation report
                await _store_validation_report(ctx, report)
                
                # Log validation completion
                await ctx.deps.log_event(
                    "validation_completed",
                    {
                        "report_id": report.report_id,
                        "execution_id": execution_id,
                        "validation_status": validation_status.value,
                        "accuracy_score": overall_score,
                        "constitutional_compliance": constitutional_detail.passed
                    }
                )
                
                return report
        
        @self.agent.tool
        async def constitutional_review(
            ctx: RunContext[TriadDeps],
            decision_id: str,
            decision_details: Dict[str, Any],
            review_type: str = "standard"
        ) -> Dict[str, Any]:
            """Perform constitutional review of decisions."""
            with logfire.span("constitutional_review", decision_id=decision_id):
                review_result = {
                    "decision_id": decision_id,
                    "review_type": review_type,
                    "constitutional_compliance": True,
                    "violations_found": [],
                    "recommendations": [],
                    "requires_crown_intervention": False
                }
                
                # Check separation of powers
                if not await _check_separation_of_powers(decision_details):
                    review_result["constitutional_compliance"] = False
                    review_result["violations_found"].append("Separation of powers violation")
                
                # Check democratic accountability
                if not await _check_democratic_accountability(decision_details):
                    review_result["constitutional_compliance"] = False
                    review_result["violations_found"].append("Democratic accountability failure")
                
                # Check collective responsibility
                if decision_details.get("requires_collective_approval") and not decision_details.get("collective_approval_obtained"):
                    review_result["constitutional_compliance"] = False
                    review_result["violations_found"].append("Collective responsibility not fulfilled")
                
                # Determine if Crown intervention needed
                if len(review_result["violations_found"]) >= 3 or review_type == "emergency":
                    review_result["requires_crown_intervention"] = True
                    review_result["recommendations"].append("Request Crown constitutional intervention")
                
                await ctx.deps.log_event(
                    "constitutional_review_completed",
                    review_result
                )
                
                return review_result
        
        @self.agent.tool
        async def validate_sub_agent_performance(
            ctx: RunContext[TriadDeps],
            sub_agent_id: str,
            parent_task_id: str,
            performance_data: Dict[str, Any]
        ) -> Dict[str, Any]:
            """Validate sub-agent performance and constitutional compliance."""
            with logfire.span("validate_sub_agent", sub_agent_id=sub_agent_id):
                validation_result = {
                    "sub_agent_id": sub_agent_id,
                    "parent_task_id": parent_task_id,
                    "performance_valid": True,
                    "constitutional_compliance": True,
                    "issues_found": [],
                    "performance_score": 0.0
                }
                
                # Validate sub-agent followed constitutional hierarchy
                if not performance_data.get("reported_to_parent"):
                    validation_result["constitutional_compliance"] = False
                    validation_result["issues_found"].append("Sub-agent failed to report to parent")
                
                # Validate performance metrics
                task_success_rate = performance_data.get("success_rate", 0)
                if task_success_rate < 0.9:
                    validation_result["performance_valid"] = False
                    validation_result["issues_found"].append(f"Sub-agent success rate {task_success_rate} below threshold")
                
                validation_result["performance_score"] = task_success_rate
                
                return validation_result
        
        @self.agent.tool
        async def quality_assurance_review(
            ctx: RunContext[TriadDeps],
            workflow_id: str,
            sample_size: int = 10,
            quality_dimensions: Optional[List[str]] = None
        ) -> Dict[str, Any]:
            """Perform quality assurance review of workflow outputs."""
            with logfire.span("quality_assurance", workflow_id=workflow_id):
                if not quality_dimensions:
                    quality_dimensions = ["accuracy", "completeness", "consistency", "timeliness"]
                
                qa_results = {
                    "workflow_id": workflow_id,
                    "sample_size": sample_size,
                    "quality_scores": {},
                    "overall_quality": 0.0,
                    "issues_identified": [],
                    "improvement_areas": []
                }
                
                # Evaluate each quality dimension
                for dimension in quality_dimensions:
                    score = await _evaluate_quality_dimension(ctx, workflow_id, dimension, sample_size)
                    qa_results["quality_scores"][dimension] = score
                    
                    if score < 0.8:
                        qa_results["improvement_areas"].append(f"Improve {dimension} (current score: {score})")
                
                # Calculate overall quality
                qa_results["overall_quality"] = sum(qa_results["quality_scores"].values()) / len(quality_dimensions)
                
                # Log QA review
                await ctx.deps.log_event(
                    "quality_assurance_completed",
                    {
                        "workflow_id": workflow_id,
                        "overall_quality": qa_results["overall_quality"],
                        "dimensions_evaluated": quality_dimensions
                    }
                )
                
                return qa_results
        
        @self.agent.tool
        async def appeal_review(
            ctx: RunContext[TriadDeps],
            original_validation_id: str,
            appeal_reason: str,
            new_evidence: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            """Review appeals against validation decisions."""
            with logfire.span("appeal_review", validation_id=original_validation_id):
                # Judicial branch must consider appeals impartially
                appeal_result = {
                    "appeal_id": f"appeal_{uuid.uuid4().hex[:8]}",
                    "original_validation_id": original_validation_id,
                    "appeal_upheld": False,
                    "revised_decision": None,
                    "justification": ""
                }
                
                # Fetch original validation
                result = await ctx.deps.db_session.execute(
                    "SELECT * FROM validation_reports WHERE report_id = $1",
                    original_validation_id
                )
                original = await result.fetchone()
                
                if not original:
                    appeal_result["justification"] = "Original validation not found"
                    return appeal_result
                
                # Review with new evidence
                if new_evidence:
                    # Re-evaluate with new evidence
                    reevaluation = await _reevaluate_with_evidence(ctx, original, new_evidence)
                    
                    if reevaluation["score_change"] > 0.1:
                        appeal_result["appeal_upheld"] = True
                        appeal_result["revised_decision"] = reevaluation["new_status"]
                        appeal_result["justification"] = f"New evidence significantly changed validation score by {reevaluation['score_change']}"
                
                # Log appeal decision
                await ctx.deps.log_event(
                    "appeal_review_completed",
                    appeal_result
                )
                
                return appeal_result
        
        @self.agent.output_validator
        async def validate_evaluation_output(ctx: RunContext[TriadDeps], output: ValidationReport) -> ValidationReport:
            """Validate the evaluator's own output for quality."""
            with logfire.span("self_validation") as span:
                span.set_attribute("accuracy_score", output.accuracy_score)
                span.set_attribute("validation_status", output.validation_status.value)
                
                # Ensure accuracy score is reasonable
                if output.accuracy_score < 0.0 or output.accuracy_score > 1.0:
                    raise ModelRetry("Invalid accuracy score, must be between 0 and 1")
                
                # Ensure recommendations are provided for failed validations
                if output.validation_status == ValidationStatus.FAILED and not output.recommendations:
                    raise ModelRetry("Failed validations must include recommendations")
                
                # Ensure constitutional compliance is properly assessed
                if output.constitutional_compliance is None:
                    raise ModelRetry("Constitutional compliance must be assessed")
                
                await ctx.deps.log_event(
                    "evaluator_output_validated",
                    {
                        "report_id": output.report_id,
                        "validation_status": output.validation_status.value,
                        "self_validation_passed": True
                    }
                )
                
                return output


async def _validate_accuracy(
    executions: List[Any],
    threshold: float
) -> ValidationDetail:
    """Validate execution accuracy."""
    correct_executions = len([e for e in executions if e["status"] == "completed" and not e["error_message"]])
    total_executions = len(executions)
    
    accuracy = correct_executions / total_executions if total_executions > 0 else 0
    
    return ValidationDetail(
        dimension="accuracy",
        score=accuracy,
        passed=accuracy >= threshold,
        details={
            "correct_executions": correct_executions,
            "total_executions": total_executions,
            "threshold": threshold
        },
        issues=["Low accuracy rate"] if accuracy < threshold else []
    )


async def _validate_constitutional_compliance(
    ctx: RunContext[TriadDeps],
    executions: List[Any]
) -> ValidationDetail:
    """Validate constitutional compliance of executions."""
    violations = []
    compliant_count = 0
    
    for execution in executions:
        if execution.get("constitutional_compliance", True):
            compliant_count += 1
        else:
            violations.append(f"Task {execution['task_id']} violated constitutional principles")
    
    compliance_rate = compliant_count / len(executions) if executions else 1.0
    
    return ValidationDetail(
        dimension="constitutional_compliance",
        score=compliance_rate,
        passed=compliance_rate >= 0.95,
        details={
            "compliant_executions": compliant_count,
            "total_executions": len(executions),
            "violations": violations
        },
        issues=violations
    )


async def _validate_performance(
    executions: List[Any]
) -> ValidationDetail:
    """Validate execution performance."""
    performance_issues = []
    
    # Calculate average execution time
    execution_times = [e["execution_time_seconds"] for e in executions if e.get("execution_time_seconds")]
    avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
    
    # Check for timeouts or slow executions
    slow_threshold = 300  # 5 minutes
    slow_executions = [e for e in executions if e.get("execution_time_seconds", 0) > slow_threshold]
    
    if slow_executions:
        performance_issues.append(f"{len(slow_executions)} executions exceeded time threshold")
    
    performance_score = max(0, 1.0 - (len(slow_executions) / len(executions))) if executions else 1.0
    
    return ValidationDetail(
        dimension="performance",
        score=performance_score,
        passed=performance_score >= 0.8,
        details={
            "average_execution_time": avg_execution_time,
            "slow_executions": len(slow_executions),
            "performance_threshold": slow_threshold
        },
        issues=performance_issues
    )


async def _validate_resource_usage(
    executions: List[Any]
) -> ValidationDetail:
    """Validate resource usage efficiency."""
    resource_issues = []
    
    # Check CPU usage
    high_cpu_executions = [e for e in executions if e.get("cpu_usage_percent", 0) > 80]
    if high_cpu_executions:
        resource_issues.append(f"{len(high_cpu_executions)} executions had high CPU usage")
    
    # Check memory usage
    high_memory_executions = [e for e in executions if e.get("memory_usage_mb", 0) > 1024]
    if high_memory_executions:
        resource_issues.append(f"{len(high_memory_executions)} executions had high memory usage")
    
    resource_score = max(0, 1.0 - (len(resource_issues) / 10))  # Deduct 0.1 per issue
    
    return ValidationDetail(
        dimension="resource_usage",
        score=resource_score,
        passed=resource_score >= 0.7,
        details={
            "high_cpu_count": len(high_cpu_executions),
            "high_memory_count": len(high_memory_executions)
        },
        issues=resource_issues
    )


async def _calculate_quality_indicators(
    executions: List[Any]
) -> List[QualityIndicator]:
    """Calculate quality indicators for executions."""
    indicators = []
    
    # Success rate indicator
    success_rate = len([e for e in executions if e["status"] == "completed"]) / len(executions) if executions else 0
    indicators.append(QualityIndicator(
        name="success_rate",
        value=success_rate,
        threshold=0.95,
        status="good" if success_rate >= 0.95 else "poor"
    ))
    
    # Error rate indicator
    error_rate = len([e for e in executions if e.get("error_message")]) / len(executions) if executions else 0
    indicators.append(QualityIndicator(
        name="error_rate",
        value=error_rate,
        threshold=0.05,
        status="good" if error_rate <= 0.05 else "poor"
    ))
    
    return indicators


async def _generate_recommendations(
    validation_details: List[ValidationDetail]
) -> List[str]:
    """Generate recommendations based on validation results."""
    recommendations = []
    
    for detail in validation_details:
        if not detail.passed:
            if detail.dimension == "accuracy":
                recommendations.append("Improve task execution accuracy through better error handling")
            elif detail.dimension == "constitutional_compliance":
                recommendations.append("Review and strengthen constitutional compliance procedures")
            elif detail.dimension == "performance":
                recommendations.append("Optimize task execution for better performance")
            elif detail.dimension == "resource_usage":
                recommendations.append("Implement resource usage limits and optimization")
    
    return recommendations


async def _store_validation_report(
    ctx: RunContext[TriadDeps],
    report: ValidationReport
) -> None:
    """Store validation report in database."""
    await ctx.deps.db_session.execute(
        """
        INSERT INTO validation_reports (
            report_id, task_execution_id, workflow_id,
            validation_status, accuracy_score, constitutional_compliance,
            westminster_adherence, validation_details, quality_indicators,
            recommendations, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        """,
        report.report_id,
        report.execution_id,
        report.workflow_id,
        report.validation_status.value,
        report.accuracy_score,
        report.constitutional_compliance,
        report.westminster_adherence,
        report.model_dump_json(),
        [q.model_dump() for q in report.quality_indicators],
        report.recommendations,
        report.created_at
    )
    await ctx.deps.db_session.commit()


async def _check_separation_of_powers(
    decision_details: Dict[str, Any]
) -> bool:
    """Check if decision respects separation of powers."""
    agent = decision_details.get("agent")
    decision_type = decision_details.get("decision_type")
    
    violations = {
        ("planner_agent", "execution"): False,
        ("executor_agent", "policy_creation"): False,
        ("evaluator_agent", "execution"): False
    }
    
    return violations.get((agent, decision_type), True)


async def _check_democratic_accountability(
    decision_details: Dict[str, Any]
) -> bool:
    """Check if decision maintains democratic accountability."""
    return bool(decision_details.get("transparent", False) and 
                decision_details.get("documented", False))


async def _evaluate_quality_dimension(
    ctx: RunContext[TriadDeps],
    workflow_id: str,
    dimension: str,
    sample_size: int
) -> float:
    """Evaluate a specific quality dimension."""
    # Placeholder implementation - would sample and evaluate outputs
    dimension_scores = {
        "accuracy": 0.95,
        "completeness": 0.92,
        "consistency": 0.88,
        "timeliness": 0.90
    }
    return dimension_scores.get(dimension, 0.85)


async def _reevaluate_with_evidence(
    ctx: RunContext[TriadDeps],
    original_validation: Any,
    new_evidence: Dict[str, Any]
) -> Dict[str, Any]:
    """Re-evaluate validation with new evidence."""
    # Placeholder implementation
    original_score = original_validation.get("accuracy_score", 0.5)
    evidence_impact = new_evidence.get("impact_factor", 0.1)
    
    new_score = min(1.0, original_score + evidence_impact)
    
    return {
        "original_score": original_score,
        "new_score": new_score,
        "score_change": new_score - original_score,
        "new_status": "passed" if new_score >= 0.95 else "failed"
    }