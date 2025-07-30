# Westminster Parliamentary AI - Multi-Agent Architecture Guide

This guide explains the proper Pydantic AI multi-agent implementation patterns used in the Westminster Parliamentary AI System, including agent delegation, message passing, graph-based workflows, and constitutional coordination.

## Overview

The Westminster Parliamentary AI System now implements proper Pydantic AI multi-agent patterns to ensure:

- **Agent Delegation**: Proper delegation tools with usage tracking
- **Message Passing**: Context preservation across agent interactions  
- **Graph-Based Workflows**: Constitutional processes as state machines
- **Programmatic Hand-off**: Sequential agent coordination with context
- **Usage Tracking**: Comprehensive usage monitoring across all agents
- **Constitutional Oversight**: Multi-agent coordination with Westminster principles

## Architecture Components

### 1. Multi-Agent Patterns Implementation

#### Agent Delegation Pattern
```python
from triad.agents.multi_agent_patterns import ParliamentaryDelegationAgent

# Create agent with delegation capabilities
planner_agent = ParliamentaryDelegationAgent(ParliamentaryRole.PLANNER)

# Use delegation through agent tools
result = await planner_agent.run_with_delegation_support(
    prompt="Analyze constitutional implications of digital privacy bill",
    deps=planner_agent.deps
)
# Agent automatically has access to delegation tools:
# - delegate_to_sub_committee()
# - coordinate_with_constitutional_branch()
# - escalate_constitutional_crisis()
# - delegate_within_ministry()
# - consult_external_expert()
```

#### Message Passing Pattern
```python
from pydantic_ai.messages import UserMessage, ModelMessage, SystemMessage

# Proper message history management
accumulated_messages = [
    SystemMessage(content="Parliamentary coordination task"),
    UserMessage(content="Analyze Bill C-123")
]

# Pass message history between agents
result1 = await agent1.run_with_delegation_support(
    prompt="First analysis",
    message_history=accumulated_messages,
    deps=agent1.deps
)

# Add result to message history
accumulated_messages.append(
    ModelMessage(content=f"Agent 1 response: {result1.data}", role="assistant")
)

# Pass to next agent with accumulated context
result2 = await agent2.run_with_delegation_support(
    prompt="Build on previous analysis", 
    message_history=accumulated_messages,
    deps=agent2.deps
)
```

#### Usage Tracking Pattern
```python
# Proper usage tracking across delegations
@agent.tool
async def delegate_to_sub_committee(
    ctx: RunContext[EnhancedParliamentaryDeps],
    committee_type: str,
    task_description: str
) -> str:
    """Delegate with proper usage tracking."""
    
    # Get sub-agent
    sub_agent = await self._get_or_create_sub_agent(committee_type)
    
    # Execute with usage tracking - critical pattern
    result = await sub_agent.run(
        task_description,
        deps=ctx.deps,
        usage=ctx.usage  # Pass usage object for tracking
    )
    
    return f"Committee {committee_type}: {result.data}"
```

### 2. Graph-Based Parliamentary Workflows

#### Bill Passage Graph
```python
from triad.graphs.parliamentary_workflows import execute_bill_passage_workflow, BillData

# Create bill data
bill = BillData(
    bill_id="C-2024-001",
    title="Digital Privacy Protection Act",
    description="Comprehensive digital privacy legislation",
    sponsor="Minister of Digital Affairs",
    bill_text="Full bill text...",
    constitutional_implications=True
)

# Execute complete graph workflow
final_state = await execute_bill_passage_workflow(bill)

print(f"Bill Status: {final_state.workflow_status.value}")
print(f"Final Stage: {final_state.current_stage.value}")
print(f"Constitutional Compliance: {final_state.constitutional_compliance}")
```

#### Graph Workflow Stages
The bill passage graph implements these nodes:
1. **BillIntroductionNode**: First reading and constitutional validation
2. **CommitteeStageNode**: Detailed analysis by multiple agents
3. **SecondReadingNode**: Parliamentary debate simulation
4. **ThirdReadingNode**: Final passage vote
5. **RoyalAssentNode**: Crown authority final approval

Each node:
- Uses appropriate constitutional agents
- Maintains state consistency
- Implements proper error handling
- Logs constitutional compliance

### 3. Programmatic Agent Hand-off

#### Sequential Coordination
```python
from triad.agents.multi_agent_patterns import get_multi_agent_coordinator, CoordinationPattern

coordinator = get_multi_agent_coordinator()

# Sequential hand-off with proper message passing
result = await coordinator.execute_programmatic_handoff(
    task="Analyze national digital ID system implications",
    agent_sequence=[
        ParliamentaryRole.PLANNER,    # Legislative analysis
        ParliamentaryRole.EXECUTOR,   # Implementation assessment
        ParliamentaryRole.EVALUATOR,  # Constitutional review
        ParliamentaryRole.OVERWATCH   # Final oversight
    ],
    coordination_type=CoordinationPattern.SEQUENTIAL
)

print(f"Coordination ID: {result['coordination_id']}")
print(f"Final Synthesis: {result['final_synthesis']}")
```

#### Collaborative Coordination
```python
# All agents work simultaneously with shared context
collaborative_result = await coordinator.execute_programmatic_handoff(
    task="Emergency response to constitutional crisis",
    agent_sequence=[
        ParliamentaryRole.PLANNER,
        ParliamentaryRole.EXECUTOR, 
        ParliamentaryRole.EVALUATOR,
        ParliamentaryRole.OVERWATCH
    ],
    coordination_type=CoordinationPattern.COLLABORATIVE
)
```

#### Oversight Coordination
```python
# Primary agents work, then oversight review
oversight_result = await coordinator.execute_programmatic_handoff(
    task="Major policy reform analysis",
    agent_sequence=[
        ParliamentaryRole.PLANNER,   # Primary analysis
        ParliamentaryRole.EXECUTOR,  # Primary analysis
        ParliamentaryRole.OVERWATCH  # Oversight review
    ],
    coordination_type=CoordinationPattern.OVERSIGHT
)
```

## Constitutional Agent Delegation Authorities

### 1. Within Branch Delegation
```python
# Planner agent delegates within legislative branch
await planner_agent.run_with_delegation_support(
    prompt="Delegate budget analysis to finance sub-committee"
)
# Uses delegate_within_ministry tool automatically
```

### 2. Cross Branch Coordination
```python
# Executive agent coordinates with judicial branch
await executor_agent.run_with_delegation_support(
    prompt="Coordinate implementation plan with constitutional review requirements"
)
# Uses coordinate_with_constitutional_branch tool automatically
```

### 3. Crisis Escalation
```python
# Any agent can escalate constitutional crisis
await evaluator_agent.run_with_delegation_support(
    prompt="Constitutional crisis detected: Government refused confidence vote result"
)
# Uses escalate_constitutional_crisis tool to Crown authority
```

### 4. External Expert Consultation
```python
# Consult external expertise
await planner_agent.run_with_delegation_support(
    prompt="Need expert constitutional law opinion on Charter implications"
)
# Uses consult_external_expert tool for specialized knowledge
```

## Delegation Authority Hierarchy

### Security Clearance Levels
- **PUBLIC**: Public documents, Hansard records
- **PARLIAMENTARY**: Legislative databases, parliamentary procedures  
- **MINISTERIAL**: Government data, policy analysis, implementation plans
- **CONSTITUTIONAL**: Constitutional law, Charter interpretation, legal precedents
- **CROWN**: Crisis management, constitutional emergencies, royal prerogative

### Constitutional Authority Matrix
```
DELEGATION FROM → TO:
┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
│             │ LEGISLATIVE │ EXECUTIVE   │ JUDICIAL    │ CROWN       │
├─────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│ LEGISLATIVE │ ✓ Within    │ ✓ Cross     │ ✓ Cross     │ ✓ Escalate  │
│ EXECUTIVE   │ ✓ Cross     │ ✓ Within    │ ✓ Cross     │ ✓ Escalate  │
│ JUDICIAL    │ ✓ Cross     │ ✓ Cross     │ ✓ Within    │ ✓ Escalate  │  
│ CROWN       │ ✓ Oversight │ ✓ Oversight │ ✓ Oversight │ ✓ Within    │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
```

## Advanced Multi-Agent Workflows

### Question Period Workflow
```python
from triad.graphs.parliamentary_workflows import QuestionPeriodState

# Create question period with multiple agents
question_period_state = QuestionPeriodState(
    session_id="qp_2024_001", 
    questions=[
        {"question": "Government position on Bill C-123?", "member": "Hon. Smith"},
        {"question": "Budget implications analysis?", "member": "Hon. Jones"}
    ]
)

# Execute with Speaker → Minister → Clerk coordination
qp_result = await execute_question_period_workflow(question_period_state)
```

### Constitutional Crisis Workflow
```python
from triad.graphs.parliamentary_workflows import CrisisState, CrisisLevel

# Detect and manage constitutional crisis
crisis_state = CrisisState(
    crisis_id="crisis_2024_001",
    crisis_type="confidence_vote_failure",
    crisis_level=CrisisLevel.CONSTITUTIONAL,
    description="Government lost confidence vote but refused to resign"
)

# Execute crisis management graph with all constitutional authorities
crisis_result = await execute_constitutional_crisis_workflow(crisis_state)
```

### Policy Development Workflow
```python
# Multi-stage policy development
policy_workflow = await coordinator.execute_programmatic_handoff(
    task="Develop comprehensive climate change policy framework",
    agent_sequence=[
        ParliamentaryRole.PLANNER,    # Draft policy framework
        ParliamentaryRole.EXECUTOR,   # Implementation planning
        ParliamentaryRole.EVALUATOR,  # Constitutional compliance
        ParliamentaryRole.PLANNER,    # Incorporate feedback
        ParliamentaryRole.OVERWATCH   # Final constitutional review
    ],
    coordination_type=CoordinationPattern.SEQUENTIAL
)
```

## Performance Monitoring and Usage Tracking

### Usage Tracking Across Agents
```python
# Monitor usage across entire coordination
coordination_result = await coordinator.execute_programmatic_handoff(...)

# Access usage data
for agent_id, result in coordination_result["agent_results"].items():
    print(f"Agent {agent_id} usage: {result.get('usage_data', {})}")
```

### Agent Performance Metrics
```python
# Get comprehensive agent status
agent_status = await agent.get_agent_status()

print(f"Tasks Completed: {agent_status['performance']['tasks_completed']}")
print(f"Constitutional Reviews: {agent_status['performance']['constitutional_reviews_conducted']}")
print(f"Delegations Executed: {agent_status['performance'].get('delegations_executed', 0)}")
```

### System-Wide Monitoring
```python
# Monitor entire multi-agent system
system_status = await coordinator.get_system_status()

print(f"Active Agents: {system_status['agent_count']}")  
print(f"Active Coordination Sessions: {len(system_status.get('coordination_sessions', {}))}")
print(f"Total Delegations: {system_status.get('total_delegations', 0)}")
```

## Best Practices

### 1. Proper Message History Management
- Always pass message history between related agent calls
- Accumulate context as agents build on each other's work
- Use structured message types (UserMessage, ModelMessage, SystemMessage)

### 2. Usage Tracking Discipline
- Always pass `ctx.usage` in delegation tools
- Monitor usage across entire workflows
- Set usage limits for complex multi-agent operations

### 3. Constitutional Compliance
- Validate delegation authority before execution
- Maintain separation of powers in cross-branch coordination
- Log all constitutional decisions and rationale

### 4. Error Handling and Fallbacks
- Implement robust error handling in all delegation paths
- Provide fallback mechanisms for agent failures
- Maintain workflow state consistency even with partial failures

### 5. Graph Workflow Design
- Use graphs for complex, multi-stage constitutional processes
- Implement proper state management with Pydantic models
- Design conditional edges for different parliamentary outcomes

### 6. Coordination Pattern Selection
- **Sequential**: For building analysis step-by-step
- **Collaborative**: For simultaneous multi-perspective analysis
- **Oversight**: For primary work + constitutional review
- **Hierarchical**: For strict constitutional authority chains

## Constitutional Workflow Examples

### Complete Bill Analysis Pipeline
```python
async def comprehensive_bill_analysis(bill_text: str):
    """Complete bill analysis using all multi-agent patterns."""
    
    # 1. Create bill data
    bill = BillData(
        bill_id="C-2024-002",
        title="AI Governance Act", 
        bill_text=bill_text,
        constitutional_implications=True
    )
    
    # 2. Execute graph-based bill passage
    bill_state = await execute_bill_passage_workflow(bill)
    
    # 3. Multi-agent coordination for detailed analysis
    analysis_result = await coordinator.execute_programmatic_handoff(
        task=f"Detailed analysis of {bill.title}",
        agent_sequence=[ParliamentaryRole.EVALUATOR, ParliamentaryRole.PLANNER],
        coordination_type=CoordinationPattern.SEQUENTIAL
    )
    
    # 4. Constitutional crisis check
    if not bill_state.constitutional_compliance:
        crisis_state = CrisisState(
            crisis_id=f"bill_crisis_{bill.bill_id}",
            crisis_type="constitutional_violation",
            crisis_level=CrisisLevel.CONSTITUTIONAL,
            description=f"Bill {bill.bill_id} violates constitutional principles"
        )
        
        crisis_result = await execute_constitutional_crisis_workflow(crisis_state)
        
        return {
            "bill_analysis": bill_state,
            "detailed_analysis": analysis_result,
            "constitutional_crisis": crisis_result
        }
    
    return {
        "bill_analysis": bill_state,
        "detailed_analysis": analysis_result,
        "constitutional_compliance": True
    }
```

The Westminster Parliamentary AI System now implements proper Pydantic AI multi-agent patterns while maintaining constitutional principles, democratic accountability, and Westminster parliamentary traditions. This provides a robust foundation for AI-assisted democratic governance with proper agent coordination, usage tracking, and constitutional oversight.