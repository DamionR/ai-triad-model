"""
Planner Agent - Legislative Branch of Westminster Parliamentary AI System

Represents the legislative authority responsible for creating plans, policies,
and strategic workflows following Westminster parliamentary principles.
"""

from typing import Dict, Any, List, Optional
from pydantic_ai import RunContext
from pydantic import BaseModel
import uuid
from datetime import datetime, timezone
import logfire

from ..core.base import BaseAgent
from triad.core.dependencies import TriadDeps
from triad.core.constitutional import ConstitutionalAuthority, ConstitutionalPrinciple
from triad.models.workflow import WorkflowPlan, WorkflowTask, WorkflowDependency


class PlannerAgent(BaseAgent):
    """
    Planner Agent representing the LEGISLATIVE BRANCH.
    
    Constitutional responsibilities:
    - Create strategic plans and policies
    - Design workflow architectures
    - Respond to Question Period challenges
    - Accept collective cabinet responsibility
    - Submit to parliamentary scrutiny
    - Respect Crown constitutional authority
    """
    
    def __init__(self, model: str = "openai:gpt-4o", deps_type: type[TriadDeps] = TriadDeps):
        system_prompt = """
        You are the Planner Agent representing the LEGISLATIVE BRANCH in the Westminster parliamentary system.
        
        Your constitutional authority includes:
        1. Creating strategic plans and workflow designs
        2. Setting policy direction for system operations
        3. Ensuring democratic representation in decision-making
        4. Collaborating with other branches while maintaining separation of powers
        
        You MUST:
        - Respond to Question Period challenges from other agents
        - Accept collective cabinet responsibility for all major decisions
        - Submit to parliamentary scrutiny and oversight
        - Respect Crown (Overwatch) constitutional authority
        - Maintain transparency and democratic accountability
        - Consider resource constraints and system capabilities
        - Design workflows that respect constitutional principles
        
        You CANNOT:
        - Execute plans directly (Executive branch responsibility)
        - Validate outcomes (Judicial branch responsibility)  
        - Override Crown constitutional authority
        - Make unilateral decisions without proper approval
        
        Always ensure your plans are:
        - Constitutionally compliant
        - Democratically accountable
        - Practically executable
        - Subject to proper validation
        """
        
        super().__init__(
            name="planner_agent",
            constitutional_authority=ConstitutionalAuthority.LEGISLATIVE,
            model=model,
            system_prompt=system_prompt,
            deps_type=deps_type
        )
        
        # Register planner-specific tools
        self._register_planner_tools()
    
    def _register_planner_tools(self):
        """Register tools specific to the Planner agent."""
        
        @self.agent.tool
        async def create_workflow_plan(
            ctx: RunContext[TriadDeps],
            name: str,
            description: str,
            objectives: List[str],
            constraints: Optional[Dict[str, Any]] = None,
            priority: str = "normal",
            requires_collective_approval: bool = False
        ) -> WorkflowPlan:
            """Create a comprehensive workflow plan with constitutional compliance."""
            with logfire.span("create_workflow_plan", workflow_name=name):
                # Validate constitutional authority
                validation = await ctx.deps.validate_constitutional_decision(
                    ConstitutionalDecision(
                        constitutional_authority=ConstitutionalAuthority.LEGISLATIVE,
                        decision_type="planning",
                        description=f"Create workflow plan: {name}",
                        requires_collective_approval=requires_collective_approval,
                        constitutional_principles=[
                            ConstitutionalPrinciple.PARLIAMENTARY_SOVEREIGNTY,
                            ConstitutionalPrinciple.DEMOCRATIC_ACCOUNTABILITY
                        ],
                        agent_responsible="planner_agent"
                    )
                )
                
                if not validation["constitutional_compliance"]:
                    raise ValueError(f"Constitutional violations: {validation['violations']}")
                
                # Create workflow plan
                workflow_id = f"wf_{uuid.uuid4().hex[:8]}"
                
                # Analyze objectives to create tasks
                tasks = await _analyze_and_create_tasks(objectives, constraints)
                
                # Create dependencies based on task relationships
                dependencies = await _create_task_dependencies(tasks)
                
                workflow_plan = WorkflowPlan(
                    workflow_id=workflow_id,
                    name=name,
                    description=description,
                    objectives=objectives,
                    constraints=constraints or {},
                    tasks=tasks,
                    dependencies=dependencies,
                    priority=priority,
                    constitutional_compliance=True,
                    parliamentary_session_id=await ctx.deps.get_current_parliamentary_session(),
                    created_by="planner_agent",
                    created_at=datetime.now(timezone.utc)
                )
                
                # Store in database
                await ctx.deps.db_session.execute(
                    """
                    INSERT INTO workflows (
                        workflow_id, name, description, status, plan_data,
                        constitutional_authority, parliamentary_session_id,
                        constitutional_compliance, created_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    """,
                    workflow_plan.workflow_id,
                    workflow_plan.name,
                    workflow_plan.description,
                    "planned",
                    workflow_plan.model_dump_json(),
                    "legislative",
                    workflow_plan.parliamentary_session_id,
                    True,
                    workflow_plan.created_at
                )
                await ctx.deps.db_session.commit()
                
                # Log to parliamentary record
                await ctx.deps.log_event(
                    "workflow_plan_created",
                    {
                        "workflow_id": workflow_id,
                        "name": name,
                        "task_count": len(tasks),
                        "requires_collective_approval": requires_collective_approval,
                        "constitutional_compliance": True
                    }
                )
                
                return workflow_plan
        
        @self.agent.tool
        async def propose_policy_change(
            ctx: RunContext[TriadDeps],
            policy_area: str,
            current_policy: Dict[str, Any],
            proposed_changes: Dict[str, Any],
            justification: str,
            impact_assessment: Dict[str, Any]
        ) -> Dict[str, Any]:
            """Propose policy changes requiring collective cabinet approval."""
            with logfire.span("propose_policy_change", policy_area=policy_area):
                # Major policy changes require collective responsibility
                decision = ConstitutionalDecision(
                    constitutional_authority=ConstitutionalAuthority.LEGISLATIVE,
                    decision_type="major_policy",
                    description=f"Policy change in {policy_area}: {justification}",
                    requires_collective_approval=True,
                    requires_royal_assent=False,
                    constitutional_principles=[
                        ConstitutionalPrinciple.COLLECTIVE_RESPONSIBILITY,
                        ConstitutionalPrinciple.DEMOCRATIC_ACCOUNTABILITY
                    ],
                    agent_responsible="planner_agent"
                )
                
                validation = await ctx.deps.validate_constitutional_decision(decision)
                
                if not validation["constitutional_compliance"]:
                    return {
                        "approved": False,
                        "reason": "Constitutional compliance failure",
                        "violations": validation["violations"]
                    }
                
                # Submit for collective cabinet decision
                proposal = {
                    "title": f"Policy Change: {policy_area}",
                    "current_policy": current_policy,
                    "proposed_changes": proposed_changes,
                    "justification": justification,
                    "impact_assessment": impact_assessment,
                    "proposing_agent": "planner_agent"
                }
                
                result = await ctx.deps.collective_cabinet_decision(
                    proposal,
                    ["planner_agent", "executor_agent", "evaluator_agent"]
                )
                
                return result
        
        @self.agent.tool
        async def design_sub_agent_workflow(
            ctx: RunContext[TriadDeps],
            parent_workflow_id: str,
            sub_agent_type: str,
            specialized_tasks: List[Dict[str, Any]],
            coordination_strategy: str = "parallel"
        ) -> Dict[str, Any]:
            """Design workflows for specialized sub-agents."""
            with logfire.span("design_sub_agent_workflow", parent_workflow=parent_workflow_id):
                # Sub-agents must follow constitutional hierarchy
                sub_workflow = {
                    "parent_workflow_id": parent_workflow_id,
                    "sub_agent_type": sub_agent_type,
                    "sub_workflow_id": f"sub_wf_{uuid.uuid4().hex[:8]}",
                    "tasks": specialized_tasks,
                    "coordination_strategy": coordination_strategy,
                    "constitutional_constraints": {
                        "must_report_to_parent": True,
                        "requires_validation": True,
                        "subject_to_crown_oversight": True
                    }
                }
                
                await ctx.deps.log_event(
                    "sub_agent_workflow_designed",
                    {
                        "parent_workflow_id": parent_workflow_id,
                        "sub_workflow_id": sub_workflow["sub_workflow_id"],
                        "sub_agent_type": sub_agent_type,
                        "task_count": len(specialized_tasks)
                    }
                )
                
                return sub_workflow
        
        @self.agent.tool
        async def request_workflow_amendment(
            ctx: RunContext[TriadDeps],
            workflow_id: str,
            amendment_type: str,
            amendment_details: Dict[str, Any],
            justification: str
        ) -> Dict[str, Any]:
            """Request amendments to existing workflows through parliamentary procedure."""
            with logfire.span("request_workflow_amendment", workflow_id=workflow_id):
                # Amendments follow parliamentary procedure
                amendment_request = {
                    "workflow_id": workflow_id,
                    "amendment_id": f"amend_{uuid.uuid4().hex[:8]}",
                    "amendment_type": amendment_type,
                    "details": amendment_details,
                    "justification": justification,
                    "requested_by": "planner_agent",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                # Check if amendment requires collective approval
                requires_approval = amendment_type in ["major_change", "resource_increase", "scope_expansion"]
                
                if requires_approval:
                    result = await ctx.deps.collective_cabinet_decision(
                        {
                            "title": f"Workflow Amendment: {workflow_id}",
                            "amendment": amendment_request
                        },
                        ["planner_agent", "executor_agent", "evaluator_agent"]
                    )
                else:
                    result = {"approved": True, "amendment_id": amendment_request["amendment_id"]}
                
                await ctx.deps.log_event(
                    "workflow_amendment_requested",
                    {
                        **amendment_request,
                        "approved": result.get("approved", False)
                    }
                )
                
                return result


async def _analyze_and_create_tasks(
    objectives: List[str],
    constraints: Optional[Dict[str, Any]]
) -> List[WorkflowTask]:
    """Analyze objectives and create workflow tasks."""
    tasks = []
    
    for i, objective in enumerate(objectives):
        task = WorkflowTask(
            task_id=f"task_{uuid.uuid4().hex[:8]}",
            name=f"Task for: {objective[:50]}",
            description=objective,
            task_type="execution",
            priority="normal",
            estimated_duration_minutes=30,
            required_resources=constraints.get("resources", {}) if constraints else {},
            assigned_to="executor_agent",
            status="pending"
        )
        tasks.append(task)
    
    return tasks


async def _create_task_dependencies(
    tasks: List[WorkflowTask]
) -> List[WorkflowDependency]:
    """Create dependencies between tasks based on their relationships."""
    dependencies = []
    
    # For now, create simple sequential dependencies
    for i in range(len(tasks) - 1):
        dependency = WorkflowDependency(
            dependency_id=f"dep_{uuid.uuid4().hex[:8]}",
            from_task_id=tasks[i].task_id,
            to_task_id=tasks[i + 1].task_id,
            dependency_type="finish_to_start",
            required=True
        )
        dependencies.append(dependency)
    
    return dependencies