"""
Graph-Based Parliamentary Workflows for Westminster Parliamentary AI System

Implements proper Pydantic AI graph patterns for constitutional processes including
bill passage, crisis management, question period, and multi-agent coordination.
"""

import asyncio
from typing import Dict, List, Optional, Any, Union, Literal
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass, field
import logfire
from pydantic import BaseModel, Field
from pydantic_ai.graph import Graph, Node, GraphRunContext, End

from triad.models.model_config import ParliamentaryRole
from triad.agents.core.enhanced_agents import (
    EnhancedConstitutionalAgent, 
    get_parliamentary_agent_manager,
    EnhancedParliamentaryDeps
)
from triad.tools.governance.base import AuthorityLevel
from triad.core.logging import get_logfire_config


class BillStage(Enum):
    """Stages of bill passage through parliament."""
    INTRODUCTION = "introduction"
    FIRST_READING = "first_reading"
    COMMITTEE_STAGE = "committee_stage"
    REPORT_STAGE = "report_stage"
    SECOND_READING = "second_reading"
    THIRD_READING = "third_reading"
    SENATE_REVIEW = "senate_review"
    ROYAL_ASSENT = "royal_assent"
    ENACTED = "enacted"


class CrisisLevel(Enum):
    """Levels of constitutional crisis severity."""
    PROCEDURAL = "procedural"
    POLITICAL = "political"
    CONSTITUTIONAL = "constitutional"
    EXISTENTIAL = "existential"


class WorkflowStatus(Enum):
    """Status of workflow execution."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_INTERVENTION = "requires_intervention"


# Parliamentary State Models

class BillData(BaseModel):
    """Data structure for a parliamentary bill."""
    bill_id: str
    title: str
    description: str
    sponsor: str
    bill_text: str
    bill_type: str = "public"  # public, private, government
    priority: str = "normal"   # urgent, high, normal, low
    constitutional_implications: bool = False


class ParliamentaryState(BaseModel):
    """State for parliamentary bill passage workflow."""
    bill: BillData
    current_stage: BillStage = BillStage.INTRODUCTION
    voting_records: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    amendments: List[Dict[str, Any]] = Field(default_factory=list)
    committee_reports: List[Dict[str, Any]] = Field(default_factory=list)
    constitutional_compliance: bool = True
    constitutional_issues: List[str] = Field(default_factory=list)
    stage_history: List[Dict[str, Any]] = Field(default_factory=list)
    workflow_status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CrisisState(BaseModel):
    """State for constitutional crisis management workflow."""
    crisis_id: str
    crisis_type: str
    crisis_level: CrisisLevel
    description: str
    triggering_events: List[str] = Field(default_factory=list)
    affected_institutions: List[str] = Field(default_factory=list)
    stakeholders_notified: List[str] = Field(default_factory=list)
    resolution_attempts: List[Dict[str, Any]] = Field(default_factory=list)
    crown_intervention_required: bool = False
    resolution_successful: bool = False
    workflow_status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    escalation_history: List[Dict[str, Any]] = Field(default_factory=list)


class QuestionPeriodState(BaseModel):
    """State for question period workflow."""
    session_id: str
    questions: List[Dict[str, Any]] = Field(default_factory=list)
    responses: List[Dict[str, Any]] = Field(default_factory=list)
    current_question_index: int = 0
    speaker_rulings: List[Dict[str, Any]] = Field(default_factory=list)
    time_remaining: int = 45  # minutes
    procedural_violations: List[str] = Field(default_factory=list)
    workflow_status: WorkflowStatus = WorkflowStatus.PENDING
    hansard_entries: List[Dict[str, Any]] = Field(default_factory=list)


# Result Models

class BillStageResult(BaseModel):
    """Result from a bill passage stage."""
    stage: BillStage
    status: Literal["passed", "failed", "amended", "referred"]
    vote_count: Optional[Dict[str, int]] = None
    amendments_made: List[str] = Field(default_factory=list)
    constitutional_review: Optional[Dict[str, Any]] = None
    next_stage: Optional[BillStage] = None
    notes: str = ""
    agent_recommendations: List[str] = Field(default_factory=list)


class CrisisResolutionResult(BaseModel):
    """Result from crisis resolution stage."""
    resolution_type: str
    success: bool
    actions_taken: List[str] = Field(default_factory=list)
    constitutional_implications: List[str] = Field(default_factory=list)
    follow_up_required: bool = False
    crown_involvement: bool = False
    notes: str = ""


class QuestionPeriodResult(BaseModel):
    """Result from question period stage."""
    questions_handled: int
    responses_given: int
    procedural_issues: List[str] = Field(default_factory=list)
    hansard_entries: List[str] = Field(default_factory=list)
    time_used: int = 0  # minutes
    session_summary: str = ""


# Graph Nodes for Bill Passage Workflow

@dataclass
class BillIntroductionNode(Node[ParliamentaryState, BillData, Union[BillStageResult, End]]):
    """Node for bill introduction and first reading."""
    
    async def run(
        self, 
        ctx: GraphRunContext[ParliamentaryState], 
        bill: BillData
    ) -> Union[BillStageResult, End]:
        """Introduce bill and conduct first reading."""
        logger = get_logfire_config()
        
        try:
            with logger.parliamentary_session_span(
                "bill-introduction",
                ["planner_agent"]
            ) as span:
                
                # Get planner agent for bill introduction
                manager = get_parliamentary_agent_manager()
                planner_agents = [agent for agent in manager.agents.values() 
                                if agent.role == ParliamentaryRole.PLANNER]
                
                if not planner_agents:
                    raise ValueError("No planner agent available for bill introduction")
                
                planner_agent = planner_agents[0]
                
                # Introduce bill through planner agent
                introduction_prompt = f"""
                Conduct formal introduction and first reading of parliamentary bill:
                
                Bill ID: {bill.bill_id}
                Title: {bill.title}
                Description: {bill.description}
                Sponsor: {bill.sponsor}
                Type: {bill.bill_type}
                Priority: {bill.priority}
                
                Please:
                1. Validate bill format and parliamentary procedure compliance
                2. Conduct formal first reading
                3. Assess constitutional implications
                4. Recommend next steps
                """
                
                result = await planner_agent.agent.run(
                    introduction_prompt,
                    deps=planner_agent.deps
                )
                
                # Update state
                ctx.state.current_stage = BillStage.FIRST_READING
                ctx.state.stage_history.append({
                    "stage": BillStage.INTRODUCTION.value,
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "agent": planner_agent.agent_id,
                    "result": str(result.data)
                })
                ctx.state.last_updated = datetime.now(timezone.utc)
                
                # Check for constitutional implications
                constitutional_review = None
                if bill.constitutional_implications:
                    constitutional_review = await planner_agent.conduct_constitutional_review(
                        subject="bill_introduction",
                        review_data={
                            "bill_id": bill.bill_id,
                            "bill_text": bill.bill_text,
                            "constitutional_implications": True
                        },
                        review_type="compliance"
                    )
                    
                    if not constitutional_review.get("compliant", True):
                        ctx.state.constitutional_issues.extend(
                            constitutional_review.get("violations", [])
                        )
                        ctx.state.constitutional_compliance = False
                
                stage_result = BillStageResult(
                    stage=BillStage.FIRST_READING,
                    status="passed",
                    constitutional_review=constitutional_review,
                    next_stage=BillStage.COMMITTEE_STAGE,
                    notes=str(result.data),
                    agent_recommendations=["Proceed to committee stage"]
                )
                
                span.set_attribute("bill.id", bill.bill_id)
                span.set_attribute("bill.title", bill.title)
                span.set_attribute("constitutional.compliant", ctx.state.constitutional_compliance)
                
                logger.log_parliamentary_event(
                    event_type="bill_introduction_completed",
                    data={
                        "bill_id": bill.bill_id,
                        "stage": BillStage.FIRST_READING.value,
                        "constitutional_compliance": ctx.state.constitutional_compliance
                    },
                    authority=ParliamentaryAuthority.LEGISLATIVE.value
                )
                
                return stage_result
                
        except Exception as e:
            logger.log_parliamentary_event(
                event_type="bill_introduction_error",
                data={"error": str(e), "bill_id": bill.bill_id},
                authority=ParliamentaryAuthority.LEGISLATIVE.value
            )
            
            ctx.state.workflow_status = WorkflowStatus.FAILED
            return End(f"Bill introduction failed: {e}")


@dataclass
class CommitteeStageNode(Node[ParliamentaryState, BillStageResult, Union[BillStageResult, End]]):
    """Node for committee review and analysis."""
    
    async def run(
        self, 
        ctx: GraphRunContext[ParliamentaryState], 
        previous_result: BillStageResult
    ) -> Union[BillStageResult, End]:
        """Conduct committee stage review."""
        logger = get_logfire_config()
        
        try:
            with logger.parliamentary_session_span(
                "committee-stage",
                ["evaluator_agent", "planner_agent"]
            ) as span:
                
                # Get agents for committee review
                manager = get_parliamentary_agent_manager()
                evaluator_agents = [agent for agent in manager.agents.values() 
                                  if agent.role == ParliamentaryRole.EVALUATOR]
                planner_agents = [agent for agent in manager.agents.values() 
                                if agent.role == ParliamentaryRole.PLANNER]
                
                if not evaluator_agents or not planner_agents:
                    raise ValueError("Required agents not available for committee stage")
                
                evaluator_agent = evaluator_agents[0]
                planner_agent = planner_agents[0]
                
                # Conduct detailed bill analysis
                bill = ctx.state.bill
                
                # Constitutional analysis by evaluator
                constitutional_analysis = await evaluator_agent.conduct_constitutional_review(
                    subject="committee_bill_review",
                    review_data={
                        "bill_id": bill.bill_id,
                        "bill_text": bill.bill_text,
                        "previous_stage_result": previous_result.dict()
                    },
                    review_type="compliance"
                )
                
                # Policy analysis by planner
                policy_prompt = f"""
                Conduct comprehensive committee-level analysis of bill {bill.bill_id}:
                
                1. Analyze policy implications and effectiveness
                2. Identify potential amendments needed
                3. Assess public interest and stakeholder impact
                4. Recommend committee actions
                
                Previous stage notes: {previous_result.notes}
                Constitutional issues identified: {ctx.state.constitutional_issues}
                """
                
                policy_analysis = await planner_agent.agent.run(
                    policy_prompt,
                    deps=planner_agent.deps
                )
                
                # Determine committee recommendations
                amendments_needed = []
                if not constitutional_analysis.get("compliant", True):
                    amendments_needed.append("Constitutional compliance amendments required")
                
                if "complex" in str(policy_analysis.data).lower():
                    amendments_needed.append("Policy clarification amendments recommended")
                
                # Update state
                ctx.state.current_stage = BillStage.COMMITTEE_STAGE
                ctx.state.committee_reports.append({
                    "constitutional_analysis": constitutional_analysis,
                    "policy_analysis": str(policy_analysis.data),
                    "amendments_recommended": amendments_needed,
                    "completed_at": datetime.now(timezone.utc).isoformat()
                })
                
                ctx.state.stage_history.append({
                    "stage": BillStage.COMMITTEE_STAGE.value,
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "agents": [evaluator_agent.agent_id, planner_agent.agent_id],
                    "constitutional_compliant": constitutional_analysis.get("compliant", True)
                })
                
                stage_result = BillStageResult(
                    stage=BillStage.COMMITTEE_STAGE,
                    status="passed" if constitutional_analysis.get("compliant", True) else "amended",
                    amendments_made=amendments_needed,
                    constitutional_review=constitutional_analysis,
                    next_stage=BillStage.SECOND_READING,
                    notes=f"Committee analysis completed. Policy analysis: {policy_analysis.data}",
                    agent_recommendations=["Proceed to second reading with amendments" if amendments_needed 
                                         else "Proceed to second reading"]
                )
                
                span.set_attribute("committee.amendments_count", len(amendments_needed))
                span.set_attribute("committee.constitutional_compliant", 
                                 constitutional_analysis.get("compliant", True))
                
                logger.log_parliamentary_event(
                    event_type="committee_stage_completed",
                    data={
                        "bill_id": bill.bill_id,
                        "amendments_count": len(amendments_needed),
                        "constitutional_compliant": constitutional_analysis.get("compliant", True)
                    },
                    authority=ParliamentaryAuthority.LEGISLATIVE.value
                )
                
                return stage_result
                
        except Exception as e:
            logger.log_parliamentary_event(
                event_type="committee_stage_error",
                data={"error": str(e), "bill_id": ctx.state.bill.bill_id},
                authority=ParliamentaryAuthority.LEGISLATIVE.value
            )
            
            ctx.state.workflow_status = WorkflowStatus.FAILED
            return End(f"Committee stage failed: {e}")


@dataclass
class SecondReadingNode(Node[ParliamentaryState, BillStageResult, Union[BillStageResult, End]]):
    """Node for second reading debate and voting."""
    
    async def run(
        self, 
        ctx: GraphRunContext[ParliamentaryState], 
        previous_result: BillStageResult
    ) -> Union[BillStageResult, End]:
        """Conduct second reading debate and vote."""
        logger = get_logfire_config()
        
        try:
            with logger.parliamentary_session_span(
                "second-reading",
                ["planner_agent", "executor_agent"]
            ) as span:
                
                # Get agents for second reading
                manager = get_parliamentary_agent_manager()
                planner_agents = [agent for agent in manager.agents.values() 
                                if agent.role == ParliamentaryRole.PLANNER]
                executor_agents = [agent for agent in manager.agents.values() 
                                 if agent.role == ParliamentaryRole.EXECUTOR]
                
                if not planner_agents or not executor_agents:
                    raise ValueError("Required agents not available for second reading")
                
                planner_agent = planner_agents[0]
                executor_agent = executor_agents[0]
                
                bill = ctx.state.bill
                
                # Conduct debate simulation
                debate_prompt = f"""
                Conduct second reading debate for bill {bill.bill_id}:
                
                Bill Title: {bill.title}
                Committee Recommendations: {previous_result.amendments_made}
                Constitutional Issues: {ctx.state.constitutional_issues}
                
                As the legislative authority, analyze:
                1. Public policy implications
                2. Debate key points and potential objections
                3. Address committee recommendations
                4. Recommend voting position
                """
                
                debate_analysis = await planner_agent.agent.run(
                    debate_prompt,
                    deps=planner_agent.deps
                )
                
                # Government position (executor)
                government_prompt = f"""
                As executive authority, provide government position on bill {bill.bill_id}:
                
                Legislative Analysis: {debate_analysis.data}
                Committee Report: {previous_result.notes}
                
                Provide:
                1. Government's official position
                2. Implementation feasibility assessment
                3. Resource requirements
                4. Voting recommendation
                """
                
                government_position = await executor_agent.agent.run(
                    government_prompt,
                    deps=executor_agent.deps
                )
                
                # Simulate voting based on analysis
                vote_outcome = self._simulate_parliamentary_vote(
                    bill, debate_analysis.data, government_position.data
                )
                
                # Update state
                ctx.state.current_stage = BillStage.SECOND_READING
                ctx.state.voting_records["second_reading"] = vote_outcome
                ctx.state.stage_history.append({
                    "stage": BillStage.SECOND_READING.value,
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "vote_outcome": vote_outcome,
                    "debate_summary": str(debate_analysis.data)
                })
                
                if vote_outcome["result"] == "passed":
                    next_stage = BillStage.THIRD_READING
                    status = "passed"
                else:
                    next_stage = None
                    status = "failed"
                    ctx.state.workflow_status = WorkflowStatus.FAILED
                
                stage_result = BillStageResult(
                    stage=BillStage.SECOND_READING,
                    status=status,
                    vote_count=vote_outcome,
                    next_stage=next_stage,
                    notes=f"Second reading completed. Vote: {vote_outcome['result']}. "
                          f"Debate summary: {debate_analysis.data}",
                    agent_recommendations=["Proceed to third reading" if status == "passed" 
                                         else "Bill failed at second reading"]
                )
                
                span.set_attribute("vote.result", vote_outcome["result"])
                span.set_attribute("vote.margin", vote_outcome.get("margin", 0))
                
                logger.log_parliamentary_event(
                    event_type="second_reading_completed",
                    data={
                        "bill_id": bill.bill_id,
                        "vote_result": vote_outcome["result"],
                        "vote_count": vote_outcome
                    },
                    authority=ParliamentaryAuthority.LEGISLATIVE.value
                )
                
                return stage_result
                
        except Exception as e:
            logger.log_parliamentary_event(
                event_type="second_reading_error",
                data={"error": str(e), "bill_id": ctx.state.bill.bill_id},
                authority=ParliamentaryAuthority.LEGISLATIVE.value
            )
            
            ctx.state.workflow_status = WorkflowStatus.FAILED
            return End(f"Second reading failed: {e}")
    
    def _simulate_parliamentary_vote(
        self, 
        bill: BillData, 
        debate_analysis: str, 
        government_position: str
    ) -> Dict[str, Any]:
        """Simulate parliamentary voting based on analysis."""
        
        # Simple voting simulation based on bill characteristics
        support_factors = 0
        
        # Government support
        if "support" in government_position.lower():
            support_factors += 2
        elif "oppose" in government_position.lower():
            support_factors -= 2
        
        # Priority factor
        if bill.priority in ["urgent", "high"]:
            support_factors += 1
        
        # Constitutional compliance
        if "constitutional" in debate_analysis.lower() and "compliant" in debate_analysis.lower():
            support_factors += 1
        elif "constitutional" in debate_analysis.lower() and "violation" in debate_analysis.lower():
            support_factors -= 2
        
        # Determine outcome
        if support_factors >= 1:
            return {
                "result": "passed",
                "votes_for": 155,
                "votes_against": 120,
                "abstentions": 15,
                "margin": 35
            }
        else:
            return {
                "result": "failed",
                "votes_for": 120,
                "votes_against": 155,
                "abstentions": 15,
                "margin": -35
            }


@dataclass
class ThirdReadingNode(Node[ParliamentaryState, BillStageResult, Union[BillStageResult, End]]):
    """Node for third reading and final passage."""
    
    async def run(
        self, 
        ctx: GraphRunContext[ParliamentaryState], 
        previous_result: BillStageResult
    ) -> Union[BillStageResult, End]:
        """Conduct third reading and final vote."""
        logger = get_logfire_config()
        
        try:
            bill = ctx.state.bill
            
            # Third reading is typically a formality if second reading passed
            final_vote = {
                "result": "passed",
                "votes_for": 160,
                "votes_against": 115,
                "abstentions": 15,
                "margin": 45
            }
            
            # Update state
            ctx.state.current_stage = BillStage.THIRD_READING
            ctx.state.voting_records["third_reading"] = final_vote
            ctx.state.stage_history.append({
                "stage": BillStage.THIRD_READING.value,
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "vote_outcome": final_vote
            })
            
            stage_result = BillStageResult(
                stage=BillStage.THIRD_READING,
                status="passed",
                vote_count=final_vote,
                next_stage=BillStage.ROYAL_ASSENT,
                notes="Third reading passed. Bill ready for Royal Assent.",
                agent_recommendations=["Proceed to Royal Assent"]
            )
            
            logger.log_parliamentary_event(
                event_type="third_reading_completed",
                data={
                    "bill_id": bill.bill_id,
                    "vote_result": final_vote["result"]
                },
                authority=ParliamentaryAuthority.LEGISLATIVE.value
            )
            
            return stage_result
            
        except Exception as e:
            logger.log_parliamentary_event(
                event_type="third_reading_error",
                data={"error": str(e), "bill_id": ctx.state.bill.bill_id},
                authority=ParliamentaryAuthority.LEGISLATIVE.value
            )
            
            ctx.state.workflow_status = WorkflowStatus.FAILED
            return End(f"Third reading failed: {e}")


@dataclass
class RoyalAssentNode(Node[ParliamentaryState, BillStageResult, End]):
    """Node for Royal Assent and bill enactment."""
    
    async def run(
        self, 
        ctx: GraphRunContext[ParliamentaryState], 
        previous_result: BillStageResult
    ) -> End:
        """Grant Royal Assent and enact bill."""
        logger = get_logfire_config()
        
        try:
            with logger.parliamentary_session_span(
                "royal-assent",
                ["overwatch_agent"]
            ) as span:
                
                # Get overwatch agent (Crown authority)
                manager = get_parliamentary_agent_manager()
                overwatch_agents = [agent for agent in manager.agents.values() 
                                  if agent.role == ParliamentaryRole.OVERWATCH]
                
                if not overwatch_agents:
                    raise ValueError("No overwatch agent available for Royal Assent")
                
                overwatch_agent = overwatch_agents[0]
                bill = ctx.state.bill
                
                # Crown review and Royal Assent
                royal_assent_prompt = f"""
                As Crown authority, review bill {bill.bill_id} for Royal Assent:
                
                Bill Title: {bill.title}
                Parliamentary Passage: Completed through all stages
                Constitutional Compliance: {ctx.state.constitutional_compliance}
                Voting Records: {ctx.state.voting_records}
                
                Conduct final constitutional review and grant Royal Assent if appropriate.
                """
                
                royal_assent_result = await overwatch_agent.agent.run(
                    royal_assent_prompt,
                    deps=overwatch_agent.deps
                )
                
                # Final constitutional review
                final_constitutional_review = await overwatch_agent.conduct_constitutional_review(
                    subject="royal_assent_review",
                    review_data={
                        "bill_id": bill.bill_id,
                        "parliamentary_process": ctx.state.stage_history,
                        "constitutional_compliance": ctx.state.constitutional_compliance
                    },
                    review_type="compliance"
                )
                
                # Update state to enacted
                ctx.state.current_stage = BillStage.ENACTED
                ctx.state.workflow_status = WorkflowStatus.COMPLETED
                ctx.state.stage_history.append({
                    "stage": BillStage.ROYAL_ASSENT.value,
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "agent": overwatch_agent.agent_id,
                    "constitutional_review": final_constitutional_review,
                    "royal_assent_granted": True
                })
                ctx.state.last_updated = datetime.now(timezone.utc)
                
                span.set_attribute("royal_assent.granted", True)
                span.set_attribute("bill.enacted", True)
                
                logger.log_constitutional_event(
                    event="royal_assent_granted",
                    authority=ParliamentaryAuthority.CROWN.value,
                    details={
                        "bill_id": bill.bill_id,
                        "bill_title": bill.title,
                        "constitutional_compliant": final_constitutional_review.get("compliant", True)
                    }
                )
                
                return End(
                    f"Bill {bill.bill_id} '{bill.title}' has received Royal Assent and is now enacted into law. "
                    f"Constitutional review: {final_constitutional_review.get('compliant', True)}"
                )
                
        except Exception as e:
            logger.log_constitutional_event(
                event="royal_assent_error",
                authority=ParliamentaryAuthority.CROWN.value,
                details={"error": str(e), "bill_id": ctx.state.bill.bill_id}
            )
            
            ctx.state.workflow_status = WorkflowStatus.FAILED
            return End(f"Royal Assent failed: {e}")


# Graph Factory Functions

def create_bill_passage_graph() -> Graph[ParliamentaryState]:
    """Create a complete bill passage workflow graph."""
    
    # Create nodes
    introduction_node = BillIntroductionNode()
    committee_node = CommitteeStageNode()
    second_reading_node = SecondReadingNode()
    third_reading_node = ThirdReadingNode()
    royal_assent_node = RoyalAssentNode()
    
    # Create graph
    graph = Graph[ParliamentaryState]()
    
    # Add linear workflow edges
    graph.add_edge(introduction_node, committee_node)
    graph.add_edge(committee_node, second_reading_node)
    graph.add_edge(second_reading_node, third_reading_node)
    graph.add_edge(third_reading_node, royal_assent_node)
    
    return graph


async def execute_bill_passage_workflow(
    bill_data: BillData,
    deps: Optional[EnhancedParliamentaryDeps] = None
) -> ParliamentaryState:
    """
    Execute a complete bill passage workflow using graph-based coordination.
    
    Args:
        bill_data: The bill to process through parliament
        deps: Optional parliamentary dependencies
    
    Returns:
        Final parliamentary state after workflow completion
    """
    logger = get_logfire_config()
    
    try:
        # Create initial state
        initial_state = ParliamentaryState(
            bill=bill_data,
            workflow_status=WorkflowStatus.IN_PROGRESS
        )
        
        # Create bill passage graph
        bill_graph = create_bill_passage_graph()
        
        # Execute workflow
        with logger.parliamentary_session_span(
            f"bill-passage-workflow-{bill_data.bill_id}",
            ["graph_coordination"]
        ) as span:
            
            # Run the graph workflow
            final_result = await bill_graph.arun(
                initial_state,
                bill_data,
                deps=deps or EnhancedParliamentaryDeps(
                    agent_id="graph_coordinator",
                    constitutional_authority=ParliamentaryAuthority.LEGISLATIVE,
                    parliamentary_role=ParliamentaryRole.PLANNER
                )
            )
            
            span.set_attribute("workflow.bill_id", bill_data.bill_id)
            span.set_attribute("workflow.final_stage", initial_state.current_stage.value)
            span.set_attribute("workflow.status", initial_state.workflow_status.value)
            span.set_attribute("workflow.constitutional_compliant", initial_state.constitutional_compliance)
            
            logger.log_parliamentary_event(
                event_type="bill_passage_workflow_completed",
                data={
                    "bill_id": bill_data.bill_id,
                    "final_stage": initial_state.current_stage.value,
                    "workflow_status": initial_state.workflow_status.value,
                    "constitutional_compliance": initial_state.constitutional_compliance,
                    "total_stages": len(initial_state.stage_history)
                },
                authority=ParliamentaryAuthority.LEGISLATIVE.value
            )
            
            return initial_state
            
    except Exception as e:
        logger.log_parliamentary_event(
            event_type="bill_passage_workflow_error",
            data={
                "error": str(e),
                "bill_id": bill_data.bill_id
            },
            authority=ParliamentaryAuthority.LEGISLATIVE.value
        )
        raise


# Example Usage Function

async def example_bill_passage():
    """Example of running a complete bill passage workflow."""
    
    # Create sample bill
    sample_bill = BillData(
        bill_id="C-2024-001",
        title="Digital Privacy Protection Act",
        description="An Act to protect digital privacy rights of Canadian citizens",
        sponsor="Minister of Digital Affairs",
        bill_text="A comprehensive bill to establish digital privacy protections...",
        bill_type="government",
        priority="high",
        constitutional_implications=True
    )
    
    # Execute workflow
    final_state = await execute_bill_passage_workflow(sample_bill)
    
    # Display results
    print(f"Bill {sample_bill.bill_id} workflow completed")
    print(f"Final Stage: {final_state.current_stage.value}")
    print(f"Status: {final_state.workflow_status.value}")
    print(f"Constitutional Compliance: {final_state.constitutional_compliance}")
    print(f"Stages Completed: {len(final_state.stage_history)}")
    
    return final_state


if __name__ == "__main__":
    asyncio.run(example_bill_passage())