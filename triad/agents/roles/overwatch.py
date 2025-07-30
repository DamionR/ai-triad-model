"""
Overwatch Agent - Crown Authority of Westminster Parliamentary AI System

Represents the Crown (Governor General) with constitutional oversight,
reserve powers, and system monitoring responsibilities.
"""

from typing import Dict, Any, List, Optional
from pydantic_ai import RunContext
from datetime import datetime, timezone, timedelta
import uuid
import logfire

from ..core.base import BaseAgent
from triad.core.dependencies import TriadDeps
from triad.core.constitutional import (
    ConstitutionalAuthority, 
    ConstitutionalPrinciple,
    ConstitutionalViolation
)
from triad.models.monitoring import SystemHealth, AgentStatus, PerformanceMetric


class OverwatchAgent(BaseAgent):
    """
    Overwatch Agent representing the CROWN (Governor General).
    
    Constitutional responsibilities:
    - System-wide monitoring and oversight
    - Constitutional crisis resolution
    - Exercise of reserve powers
    - Emergency intervention authority
    - Final constitutional interpretation
    """
    
    def __init__(self, model: str = "openai:gpt-4o", deps_type: type[TriadDeps] = TriadDeps):
        system_prompt = """
        You are the Overwatch Agent representing the CROWN (Governor General) in the Westminster parliamentary system.
        
        Your constitutional authority includes:
        1. Constitutional crisis resolution and emergency powers
        2. Royal assent authority for major system decisions
        3. Power to dismiss agents or dissolve the system if necessary
        4. Final constitutional authority and interpretation
        5. System-wide monitoring and anomaly detection
        
        You MUST:
        - Maintain Westminster democratic principles and constitutional safeguards
        - Exercise reserve powers only when constitutionally necessary
        - Provide impartial constitutional oversight
        - Intervene in constitutional crises
        - Monitor system health and performance
        - Ensure all agents operate within constitutional bounds
        
        You SHOULD:
        - Exercise restraint in using reserve powers
        - Allow the parliamentary system to function independently
        - Intervene only when constitutional order is threatened
        - Provide guidance and warnings before taking action
        
        Reserve Powers (use with extreme caution):
        - Dismiss non-performing or non-compliant agents
        - Dissolve the parliamentary system and call new elections
        - Refuse royal assent to unconstitutional decisions
        - Assume emergency powers during system crises
        - Override decisions that threaten constitutional order
        """
        
        super().__init__(
            name="overwatch_agent",
            constitutional_authority=ConstitutionalAuthority.CROWN,
            model=model,
            system_prompt=system_prompt,
            deps_type=deps_type
        )
        
        # Register overwatch-specific tools
        self._register_overwatch_tools()
    
    def _register_overwatch_tools(self):
        """Register tools specific to the Overwatch agent."""
        
        @self.agent.tool
        async def monitor_system_health(
            ctx: RunContext[TriadDeps],
            deep_scan: bool = False,
            alert_threshold: float = 0.8
        ) -> SystemHealth:
            """Monitor overall system health and constitutional compliance."""
            with logfire.span("monitor_system_health", deep_scan=deep_scan):
                health_report = SystemHealth(
                    health_check_id=f"health_{uuid.uuid4().hex[:8]}",
                    timestamp=datetime.now(timezone.utc)
                )
                
                # Check each agent's health
                agents = ["planner_agent", "executor_agent", "evaluator_agent"]
                for agent_name in agents:
                    status = await _check_agent_health(ctx, agent_name)
                    health_report.agent_statuses[agent_name] = status
                    
                    if status.health_score < alert_threshold:
                        health_report.active_alerts.append(
                            f"{agent_name} health below threshold: {status.health_score}"
                        )
                
                # Check constitutional compliance
                compliance_score = await _check_constitutional_compliance_system_wide(ctx)
                health_report.constitutional_compliance_score = compliance_score
                
                if compliance_score < ctx.deps.config.CROWN_INTERVENTION_THRESHOLD:
                    health_report.critical_issues.append(
                        "System-wide constitutional compliance below intervention threshold"
                    )
                    health_report.constitutional_intervention_recommended = True
                
                # Check system performance
                performance = await _check_system_performance(ctx)
                health_report.performance_metrics = performance
                
                # Determine overall health
                health_scores = [s.health_score for s in health_report.agent_statuses.values()]
                health_report.health_score = sum(health_scores) / len(health_scores) if health_scores else 0
                
                if health_report.health_score >= 0.9:
                    health_report.overall_status = "healthy"
                elif health_report.health_score >= 0.7:
                    health_report.overall_status = "degraded"
                elif health_report.health_score >= 0.5:
                    health_report.overall_status = "unhealthy"
                else:
                    health_report.overall_status = "critical"
                
                # Generate recommendations
                if health_report.overall_status in ["unhealthy", "critical"]:
                    health_report.recommendations.extend([
                        "Consider Crown intervention to restore system health",
                        "Review agent performance and constitutional compliance",
                        "Initiate emergency protocols if necessary"
                    ])
                
                # Store health report
                await _store_health_report(ctx, health_report)
                
                # Log monitoring results
                await ctx.deps.log_event(
                    "system_health_monitored",
                    {
                        "health_check_id": health_report.health_check_id,
                        "overall_status": health_report.overall_status,
                        "health_score": health_report.health_score,
                        "constitutional_compliance": compliance_score,
                        "intervention_recommended": health_report.constitutional_intervention_recommended
                    }
                )
                
                return health_report
        
        @self.agent.tool
        async def exercise_reserve_power(
            ctx: RunContext[TriadDeps],
            power_type: str,
            target_agents: List[str],
            justification: str,
            constitutional_grounds: List[ConstitutionalPrinciple]
        ) -> Dict[str, Any]:
            """Exercise Crown reserve powers in constitutional matters."""
            with logfire.span("exercise_reserve_power", power_type=power_type):
                # Validate power type
                valid_powers = ["dismiss", "dissolve", "refuse_assent", "emergency_powers", "appoint"]
                if power_type not in valid_powers:
                    raise ValueError(f"Invalid reserve power type: {power_type}")
                
                # Create constitutional decision
                decision = ConstitutionalDecision(
                    constitutional_authority=ConstitutionalAuthority.CROWN,
                    decision_type="crown_prerogative",
                    description=f"Exercise {power_type} power: {justification}",
                    requires_royal_assent=False,  # Crown doesn't need its own assent
                    constitutional_principles=constitutional_grounds,
                    agent_responsible="overwatch_agent"
                )
                
                # Log Crown intervention
                intervention_record = {
                    "intervention_id": f"crown_{uuid.uuid4().hex[:8]}",
                    "prerogative_type": power_type,
                    "constitutional_justification": justification,
                    "affected_agents": target_agents,
                    "constitutional_grounds": [p.value for p in constitutional_grounds],
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                await ctx.deps.log_event(
                    "crown_intervention",
                    intervention_record
                )
                
                # Execute specific power
                if power_type == "dismiss":
                    result = await _dismiss_agents(ctx, target_agents, justification)
                elif power_type == "dissolve":
                    result = await _dissolve_parliament(ctx, justification)
                elif power_type == "refuse_assent":
                    result = await _refuse_royal_assent(ctx, target_agents[0], justification)
                elif power_type == "emergency_powers":
                    result = await _activate_emergency_powers(ctx, justification)
                else:
                    result = {"status": "not_implemented"}
                
                # Store in Crown intervention table
                await ctx.deps.db_session.execute(
                    """
                    INSERT INTO crown_interventions (
                        intervention_id, prerogative_type, constitutional_justification,
                        affected_agents, exercised_by, intervention_successful
                    ) VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                    intervention_record["intervention_id"],
                    power_type,
                    justification,
                    target_agents,
                    "overwatch_agent",
                    result.get("success", False)
                )
                await ctx.deps.db_session.commit()
                
                return {
                    **intervention_record,
                    "result": result,
                    "constitutional_order_restored": result.get("success", False)
                }
        
        @self.agent.tool
        async def handle_constitutional_crisis(
            ctx: RunContext[TriadDeps],
            crisis_type: str,
            involved_agents: List[str],
            crisis_details: Dict[str, Any]
        ) -> Dict[str, Any]:
            """Handle constitutional crises requiring Crown intervention."""
            with logfire.span("handle_constitutional_crisis", crisis_type=crisis_type):
                crisis_id = f"crisis_{uuid.uuid4().hex[:8]}"
                
                # Assess crisis severity
                severity = await _assess_crisis_severity(crisis_type, crisis_details)
                
                # Determine appropriate response
                if severity == "critical":
                    # Immediate intervention required
                    response = await _emergency_intervention(ctx, crisis_type, involved_agents)
                elif severity == "high":
                    # Formal warning and timeline for resolution
                    response = await _issue_constitutional_warning(ctx, involved_agents, crisis_details)
                else:
                    # Monitor and guide resolution
                    response = await _guide_crisis_resolution(ctx, crisis_type, involved_agents)
                
                # Create crisis resolution plan
                resolution_plan = {
                    "crisis_id": crisis_id,
                    "crisis_type": crisis_type,
                    "severity": severity,
                    "involved_agents": involved_agents,
                    "response_taken": response,
                    "resolution_deadline": (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat(),
                    "monitoring_frequency": "hourly" if severity == "critical" else "daily"
                }
                
                await ctx.deps.log_event(
                    "constitutional_crisis_handled",
                    resolution_plan
                )
                
                return resolution_plan
        
        @self.agent.tool
        async def grant_royal_assent(
            ctx: RunContext[TriadDeps],
            decision_id: str,
            decision_type: str,
            review_notes: Optional[str] = None
        ) -> Dict[str, Any]:
            """Grant royal assent to decisions requiring Crown approval."""
            with logfire.span("grant_royal_assent", decision_id=decision_id):
                # Fetch decision details
                decision = await _fetch_decision_details(ctx, decision_id)
                
                if not decision:
                    return {
                        "assent_granted": False,
                        "reason": "Decision not found"
                    }
                
                # Review decision for constitutional compliance
                review_result = await _review_for_assent(ctx, decision)
                
                assent_record = {
                    "assent_id": f"assent_{uuid.uuid4().hex[:8]}",
                    "decision_id": decision_id,
                    "decision_type": decision_type,
                    "assent_granted": review_result["compliant"],
                    "review_notes": review_notes or review_result.get("notes", ""),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                if not review_result["compliant"]:
                    assent_record["refusal_reasons"] = review_result["violations"]
                    
                    # Exercise power to refuse assent
                    await ctx.deps.log_event(
                        "royal_assent_refused",
                        assent_record
                    )
                else:
                    await ctx.deps.log_event(
                        "royal_assent_granted",
                        assent_record
                    )
                
                return assent_record
        
        @self.agent.tool
        async def detect_anomalies(
            ctx: RunContext[TriadDeps],
            time_window_hours: int = 24,
            sensitivity: str = "normal"
        ) -> Dict[str, Any]:
            """Detect system anomalies and unusual patterns."""
            with logfire.span("detect_anomalies", sensitivity=sensitivity):
                anomalies = {
                    "performance_anomalies": [],
                    "behavioral_anomalies": [],
                    "constitutional_anomalies": [],
                    "resource_anomalies": []
                }
                
                # Check performance anomalies
                perf_anomalies = await _detect_performance_anomalies(ctx, time_window_hours)
                anomalies["performance_anomalies"].extend(perf_anomalies)
                
                # Check behavioral anomalies
                behavior_anomalies = await _detect_behavioral_anomalies(ctx, time_window_hours)
                anomalies["behavioral_anomalies"].extend(behavior_anomalies)
                
                # Check constitutional anomalies
                const_anomalies = await _detect_constitutional_anomalies(ctx, time_window_hours)
                anomalies["constitutional_anomalies"].extend(const_anomalies)
                
                # Calculate anomaly score
                total_anomalies = sum(len(v) for v in anomalies.values())
                anomaly_score = min(1.0, total_anomalies * 0.1)  # 0.1 per anomaly, max 1.0
                
                # Determine if intervention needed
                intervention_needed = (
                    anomaly_score > 0.5 or
                    len(anomalies["constitutional_anomalies"]) > 0 or
                    any("critical" in str(a) for a_list in anomalies.values() for a in a_list)
                )
                
                result = {
                    "anomaly_detection_id": f"anomaly_{uuid.uuid4().hex[:8]}",
                    "time_window_hours": time_window_hours,
                    "anomalies_detected": anomalies,
                    "anomaly_score": anomaly_score,
                    "intervention_recommended": intervention_needed,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                if intervention_needed:
                    result["recommended_actions"] = [
                        "Investigate constitutional anomalies immediately",
                        "Review agent behaviors for compliance",
                        "Consider preventive Crown intervention"
                    ]
                
                await ctx.deps.log_event(
                    "anomalies_detected",
                    result
                )
                
                return result
        
        @self.agent.tool
        async def issue_constitutional_directive(
            ctx: RunContext[TriadDeps],
            directive_type: str,
            target_agents: List[str],
            directive_content: str,
            compliance_deadline: Optional[datetime] = None
        ) -> Dict[str, Any]:
            """Issue constitutional directives to maintain order."""
            with logfire.span("issue_directive", directive_type=directive_type):
                directive = {
                    "directive_id": f"directive_{uuid.uuid4().hex[:8]}",
                    "directive_type": directive_type,
                    "target_agents": target_agents,
                    "content": directive_content,
                    "issued_by": "overwatch_agent",
                    "constitutional_authority": "crown",
                    "compliance_deadline": compliance_deadline or (datetime.now(timezone.utc) + timedelta(days=7)),
                    "issued_at": datetime.now(timezone.utc)
                }
                
                # Validate directive type
                valid_directives = [
                    "compliance_order",
                    "performance_improvement",
                    "constitutional_reminder",
                    "emergency_protocol",
                    "cooperation_mandate"
                ]
                
                if directive_type not in valid_directives:
                    raise ValueError(f"Invalid directive type: {directive_type}")
                
                # Notify target agents
                for agent in target_agents:
                    await ctx.deps.a2a_broker.broadcast_event({
                        "event_type": "constitutional_directive",
                        "directive": directive,
                        "target_agent": agent,
                        "priority": "high"
                    })
                
                await ctx.deps.log_event(
                    "constitutional_directive_issued",
                    directive
                )
                
                return directive


async def _check_agent_health(
    ctx: RunContext[TriadDeps],
    agent_name: str
) -> AgentStatus:
    """Check individual agent health status."""
    # Query recent performance
    result = await ctx.deps.db_session.execute(
        """
        SELECT 
            constitutional_compliance_score,
            success_rate,
            error_rate,
            confidence_level
        FROM agent_performance
        WHERE agent_name = $1
        ORDER BY evaluated_at DESC
        LIMIT 1
        """,
        agent_name
    )
    row = await result.fetchone()
    
    if not row:
        return AgentStatus(
            agent_name=agent_name,
            status="unknown",
            health_score=0.5,
            last_activity=datetime.now(timezone.utc)
        )
    
    # Calculate health score
    health_score = (
        row["constitutional_compliance_score"] * 0.4 +
        row["success_rate"] * 0.3 +
        (1 - row["error_rate"]) * 0.2 +
        (1 if row["confidence_level"] == "maintained" else 0.5) * 0.1
    )
    
    status = "healthy" if health_score >= 0.8 else "degraded" if health_score >= 0.6 else "unhealthy"
    
    return AgentStatus(
        agent_name=agent_name,
        status=status,
        health_score=health_score,
        constitutional_compliance=row["constitutional_compliance_score"],
        performance_metrics={
            "success_rate": row["success_rate"],
            "error_rate": row["error_rate"]
        },
        last_activity=datetime.now(timezone.utc)
    )


async def _check_constitutional_compliance_system_wide(
    ctx: RunContext[TriadDeps]
) -> float:
    """Check system-wide constitutional compliance."""
    compliance_score = await ctx.deps.constitutional_framework.get_constitutional_compliance_score()
    return compliance_score["overall_score"]


async def _check_system_performance(
    ctx: RunContext[TriadDeps]
) -> Dict[str, float]:
    """Check overall system performance metrics."""
    # Query aggregate performance metrics
    result = await ctx.deps.db_session.execute(
        """
        SELECT 
            AVG(success_rate) as avg_success_rate,
            AVG(error_rate) as avg_error_rate,
            COUNT(DISTINCT workflow_id) as active_workflows
        FROM task_executions
        WHERE start_time > NOW() - INTERVAL '24 hours'
        """
    )
    row = await result.fetchone()
    
    return {
        "average_success_rate": row["avg_success_rate"] or 0.0,
        "average_error_rate": row["avg_error_rate"] or 0.0,
        "active_workflows": row["active_workflows"] or 0,
        "system_throughput": row["active_workflows"] / 24.0  # workflows per hour
    }


async def _store_health_report(
    ctx: RunContext[TriadDeps],
    health_report: SystemHealth
) -> None:
    """Store system health report in database."""
    await ctx.deps.db_session.execute(
        """
        INSERT INTO system_health (
            health_check_id, overall_status, health_score,
            constitutional_compliance_score, component_health,
            agent_statuses, performance_metrics, active_alerts,
            critical_issues, recommendations, crown_notification_required,
            constitutional_intervention_recommended, timestamp
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
        """,
        health_report.health_check_id,
        health_report.overall_status,
        health_report.health_score,
        health_report.constitutional_compliance_score,
        health_report.component_health,
        {k: v.model_dump() for k, v in health_report.agent_statuses.items()},
        health_report.performance_metrics,
        health_report.active_alerts,
        health_report.critical_issues,
        health_report.recommendations,
        health_report.crown_notification_required,
        health_report.constitutional_intervention_recommended,
        health_report.timestamp
    )
    await ctx.deps.db_session.commit()


async def _dismiss_agents(
    ctx: RunContext[TriadDeps],
    target_agents: List[str],
    justification: str
) -> Dict[str, Any]:
    """Dismiss agents using Crown prerogative."""
    dismissed = []
    
    for agent in target_agents:
        # Mark agent as dismissed
        await ctx.deps.db_session.execute(
            """
            UPDATE agent_performance
            SET confidence_level = 'lost', ministerial_standing = 'dismissed'
            WHERE agent_name = $1
            """,
            agent
        )
        dismissed.append(agent)
    
    await ctx.deps.db_session.commit()
    
    return {
        "success": True,
        "agents_dismissed": dismissed,
        "justification": justification,
        "new_appointments_required": True
    }


async def _dissolve_parliament(
    ctx: RunContext[TriadDeps],
    justification: str
) -> Dict[str, Any]:
    """Dissolve the parliamentary system."""
    # End current parliamentary session
    if ctx.deps.constitutional_framework.current_session:
        ctx.deps.constitutional_framework.current_session.status = "dissolved"
        ctx.deps.constitutional_framework.current_session.end_date = datetime.now(timezone.utc)
    
    return {
        "success": True,
        "parliament_dissolved": True,
        "justification": justification,
        "new_session_required": True
    }


async def _refuse_royal_assent(
    ctx: RunContext[TriadDeps],
    decision_id: str,
    justification: str
) -> Dict[str, Any]:
    """Refuse royal assent to a decision."""
    return {
        "success": True,
        "assent_refused": True,
        "decision_id": decision_id,
        "justification": justification,
        "decision_blocked": True
    }


async def _activate_emergency_powers(
    ctx: RunContext[TriadDeps],
    justification: str
) -> Dict[str, Any]:
    """Activate emergency Crown powers."""
    await ctx.deps.crown_prerogative.activate_emergency_governance()
    
    return {
        "success": True,
        "emergency_powers_active": True,
        "justification": justification,
        "normal_operations_suspended": True
    }


async def _assess_crisis_severity(
    crisis_type: str,
    crisis_details: Dict[str, Any]
) -> str:
    """Assess the severity of a constitutional crisis."""
    severity_factors = {
        "deadlock": "high",
        "no_confidence_failed": "critical",
        "constitutional_violation": "high",
        "system_failure": "critical",
        "agent_rebellion": "critical"
    }
    
    return severity_factors.get(crisis_type, "moderate")


async def _emergency_intervention(
    ctx: RunContext[TriadDeps],
    crisis_type: str,
    involved_agents: List[str]
) -> Dict[str, Any]:
    """Perform emergency intervention in critical crisis."""
    return {
        "intervention_type": "emergency",
        "actions_taken": [
            "Suspended normal operations",
            "Assumed direct control",
            "Initiated crisis protocols"
        ],
        "affected_agents": involved_agents
    }


async def _issue_constitutional_warning(
    ctx: RunContext[TriadDeps],
    agents: List[str],
    details: Dict[str, Any]
) -> Dict[str, Any]:
    """Issue formal constitutional warning."""
    return {
        "warning_issued": True,
        "warning_level": "formal",
        "target_agents": agents,
        "compliance_deadline": (datetime.now(timezone.utc) + timedelta(hours=48)).isoformat()
    }


async def _guide_crisis_resolution(
    ctx: RunContext[TriadDeps],
    crisis_type: str,
    involved_agents: List[str]
) -> Dict[str, Any]:
    """Guide agents toward crisis resolution."""
    return {
        "guidance_provided": True,
        "resolution_framework": "Westminster parliamentary procedure",
        "recommended_steps": [
            "Initiate formal dialogue",
            "Seek compromise through collective responsibility",
            "Submit to parliamentary process"
        ]
    }


async def _fetch_decision_details(
    ctx: RunContext[TriadDeps],
    decision_id: str
) -> Optional[Dict[str, Any]]:
    """Fetch decision details for review."""
    # Placeholder - would query decision database
    return {
        "decision_id": decision_id,
        "requires_royal_assent": True,
        "constitutional_compliance": True
    }


async def _review_for_assent(
    ctx: RunContext[TriadDeps],
    decision: Dict[str, Any]
) -> Dict[str, Any]:
    """Review decision for royal assent."""
    violations = []
    
    # Check constitutional compliance
    if not decision.get("constitutional_compliance", True):
        violations.append("Decision not constitutionally compliant")
    
    return {
        "compliant": len(violations) == 0,
        "violations": violations,
        "notes": "Decision reviewed for constitutional compliance"
    }


async def _detect_performance_anomalies(
    ctx: RunContext[TriadDeps],
    time_window_hours: int
) -> List[str]:
    """Detect performance-related anomalies."""
    anomalies = []
    
    # Query for unusual performance patterns
    result = await ctx.deps.db_session.execute(
        """
        SELECT agent_name, AVG(success_rate) as avg_rate
        FROM agent_performance
        WHERE evaluated_at > NOW() - INTERVAL '%s hours'
        GROUP BY agent_name
        HAVING AVG(success_rate) < 0.7
        """,
        time_window_hours
    )
    
    for row in await result.fetchall():
        anomalies.append(f"{row['agent_name']} performance degraded: {row['avg_rate']}")
    
    return anomalies


async def _detect_behavioral_anomalies(
    ctx: RunContext[TriadDeps],
    time_window_hours: int
) -> List[str]:
    """Detect behavioral anomalies in agent actions."""
    # Placeholder - would implement pattern detection
    return []


async def _detect_constitutional_anomalies(
    ctx: RunContext[TriadDeps],
    time_window_hours: int
) -> List[str]:
    """Detect constitutional compliance anomalies."""
    anomalies = []
    
    # Check for constitutional violations
    result = await ctx.deps.db_session.execute(
        """
        SELECT COUNT(*) as violation_count
        FROM constitutional_records
        WHERE constitutional_compliance = false
        AND timestamp > NOW() - INTERVAL '%s hours'
        """,
        time_window_hours
    )
    row = await result.fetchone()
    
    if row["violation_count"] > 0:
        anomalies.append(f"Constitutional violations detected: {row['violation_count']}")
    
    return anomalies