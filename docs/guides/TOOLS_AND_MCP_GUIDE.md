# Westminster Parliamentary AI - Tools and MCP Integration Guide

This comprehensive guide explains how to use tools and Model Context Protocol (MCP) integration within the Westminster Parliamentary AI System for enhanced democratic governance and constitutional oversight.

## Overview

The Westminster Parliamentary AI System integrates sophisticated toolsets and MCP capabilities to provide:

- **Constitutional Oversight Tools**: Compliance validation, constitutional interpretation, and crisis detection
- **Legislative Analysis Tools**: Bill analysis, amendment tracking, and parliamentary procedure management
- **MCP Server Integration**: Access to external databases, APIs, and specialized services
- **Democratic Process Automation**: Question period management, voting procedures, and citizen engagement
- **Multi-Agent Coordination**: Collaborative task execution with constitutional accountability

## Architecture Components

### 1. Parliamentary Toolsets

The system provides specialized toolsets for different aspects of parliamentary governance:

#### Constitutional Toolset
- **Compliance Validation**: Validate actions against constitutional principles
- **Bill Analysis**: Comprehensive legislative analysis with constitutional review
- **Crisis Detection**: Identify and respond to constitutional crises
- **Precedent Lookup**: Access constitutional and legal precedents
- **Constitutional Interpretation**: Interpret constitutional provisions in modern context

#### Legislative Toolset
- **Bill Progress Tracking**: Monitor legislation through parliamentary stages
- **Committee Scheduling**: Manage committee reviews and hearings
- **Amendment Analysis**: Track and analyze proposed amendments

#### Parliamentary Procedure Toolset
- **Procedure Validation**: Ensure compliance with Westminster conventions
- **Question Period Management**: Facilitate parliamentary question periods
- **Debate Management**: Coordinate parliamentary debates and voting

### 2. MCP Server Integration

The system connects to specialized MCP servers for external data access:

#### Available MCP Servers
- **Legislative Database Server**: Bills, acts, regulations, and legislative history
- **Constitutional Law Server**: Constitutional cases, Charter rights, legal precedents  
- **Hansard Archive Server**: Parliamentary debate records and proceedings
- **Citizen Engagement Server**: Public consultations, petitions, feedback
- **Policy Analysis Server**: Policy research and impact analysis
- **Parliamentary Procedure Server**: Procedural guidance and validation

## Quick Start Guide

### 1. Setting Up Enhanced Agents

```python
from triad.agents.enhanced_agents import create_enhanced_constitutional_agents
from triad.models.model_config import ParliamentaryRole

# Create all four constitutional agents with tools and MCP
agents = await create_enhanced_constitutional_agents()

# Access individual agents
planner = agents[ParliamentaryRole.PLANNER]
executor = agents[ParliamentaryRole.EXECUTOR]
evaluator = agents[ParliamentaryRole.EVALUATOR]
overwatch = agents[ParliamentaryRole.OVERWATCH]
```

### 2. Using Constitutional Tools

```python
# Conduct constitutional compliance review
compliance_result = await evaluator.conduct_constitutional_review(
    subject="proposed_legislation",
    review_data={
        "bill_text": "...",
        "constitutional_basis": "Charter Section 7"
    },
    review_type="compliance"
)

print(f"Constitutional Compliance: {compliance_result['compliant']}")
if compliance_result['violations']:
    print(f"Violations Found: {compliance_result['violations']}")
```

### 3. Accessing MCP Servers

```python
# The agents automatically have access to MCP servers based on their role
# Example: Planner agent analyzing a bill using legislative database
response = await planner.run_with_context(
    "Analyze Bill C-123 for potential constitutional issues and public impact",
    session_id="session_001"
)

# The agent will automatically use:
# - Legislative database to retrieve bill text
# - Constitutional law server for compliance analysis
# - Citizen engagement server for public consultation data
```

## Detailed Usage Examples

### Constitutional Oversight Workflow

```python
from triad.agents.enhanced_agents import get_parliamentary_agent_manager
from triad.models.model_config import ParliamentaryRole

manager = get_parliamentary_agent_manager()

# Start parliamentary session
session_id = await manager.start_parliamentary_session(
    session_type="constitutional_review",
    participating_agents=["evaluator_001", "overwatch_002"],
    agenda=["Review Bill C-456", "Assess constitutional compliance"]
)

# Coordinate agents for constitutional review
coordination_result = await manager.coordinate_agents(
    task="Review the constitutional implications of Bill C-456 regarding privacy rights",
    participating_roles=[ParliamentaryRole.EVALUATOR, ParliamentaryRole.OVERWATCH],
    coordination_type="oversight"
)

# Review results
for agent_id, result in coordination_result["results"].items():
    print(f"Agent {agent_id}: {result['constitutional_metadata']}")
```

### Legislative Analysis Pipeline

```python
from triad.tools.parliamentary_toolsets import get_toolset
from triad.tools.mcp_integration import get_parliamentary_mcp_client

# Get legislative toolset
legislative_tools = get_toolset("legislative")

# Track bill through parliamentary process
bill_progress = await legislative_tools._tools["track_bill_progress"](
    parliamentary_context,
    bill_number="C-123",
    current_stage="second_reading"
)

print(f"Bill Progress: {bill_progress['progress_percentage']}%")
print(f"Next Stage: {bill_progress['next_stage']}")

# Schedule committee review
committee_schedule = await legislative_tools._tools["schedule_committee_review"](
    parliamentary_context,
    bill_number="C-123",
    committee_name="Justice Committee",
    priority="high"
)

print(f"Estimated Review Duration: {committee_schedule['estimated_review_duration']}")
```

### Question Period Management

```python
from triad.tools.parliamentary_toolsets import ParliamentaryProcedureToolset

procedure_tools = ParliamentaryProcedureToolset()

# Start question period
qp_start = await procedure_tools._tools["manage_question_period"](
    parliamentary_context,
    action="start"
)

# Add a question
question_data = {
    "question_text": "What is the government's position on Bill C-123?",
    "member_name": "Hon. Member Smith",
    "ministry": "Justice",
    "advance_notice": True
}

qp_add = await procedure_tools._tools["manage_question_period"](
    parliamentary_context,
    action="add_question",
    question_data=question_data
)

# Validate the question follows parliamentary procedure
validation = await procedure_tools._tools["validate_parliamentary_procedure"](
    parliamentary_context,
    procedure_type="question_period",
    procedure_data=question_data
)

if validation["is_valid"]:
    print("Question accepted for Question Period")
else:
    print(f"Question rejected: {validation['violations']}")
```

### Crisis Detection and Response

```python
# Detect potential constitutional crisis
crisis_data = {
    "confidence_vote": "failed",
    "government_response": "refused_to_resign",
    "opposition_action": "non_confidence_motion"
}

crisis_assessment = await evaluator.conduct_constitutional_review(
    subject="government_confidence_crisis",
    review_data=crisis_data,
    review_type="crisis"
)

if crisis_assessment["is_constitutional_crisis"]:
    print(f"CONSTITUTIONAL CRISIS DETECTED")
    print(f"Severity: {crisis_assessment['severity_score']}")
    print(f"Immediate Actions Required:")
    for action in crisis_assessment["immediate_actions"]:
        print(f"  - {action}")
    
    # Escalate to Crown authority if needed
    if crisis_assessment["escalation_required"]:
        await overwatch.run_with_context(
            f"Constitutional crisis requiring Crown intervention: {crisis_assessment}",
            session_id=session_id
        )
```

### Multi-Agent Parliamentary Session

```python
# Create a complex parliamentary session with multiple agents
agents = await create_enhanced_constitutional_agents()
manager = get_parliamentary_agent_manager()

# Start comprehensive parliamentary session
session_id = await manager.start_parliamentary_session(
    session_type="bill_review_session",
    participating_agents=[agent.agent_id for agent in agents.values()],
    agenda=[
        "Constitutional review of Bill C-789",
        "Policy impact assessment", 
        "Public consultation analysis",
        "Parliamentary procedure validation"
    ]
)

# Coordinate all agents for comprehensive bill analysis
comprehensive_analysis = await manager.coordinate_agents(
    task="""Conduct a comprehensive analysis of Bill C-789 (Digital Privacy Protection Act) including:
    1. Constitutional compliance review
    2. Policy impact assessment  
    3. Parliamentary procedure requirements
    4. Public consultation summary""",
    participating_roles=[
        ParliamentaryRole.EVALUATOR,  # Constitutional review
        ParliamentaryRole.PLANNER,   # Policy analysis
        ParliamentaryRole.EXECUTOR,  # Implementation assessment
        ParliamentaryRole.OVERWATCH  # Overall oversight
    ],
    coordination_type="collaborative"
)

# Process results from each constitutional authority
for role, agent in agents.items():
    result = comprehensive_analysis["results"][agent.agent_id]
    print(f"\n{role.value.upper()} ANALYSIS:")
    print(f"Constitutional Authority: {agent.parliamentary_context.constitutional_authority.value}")
    print(f"Response: {result['response']}")
    print(f"Constitutional Metadata: {result['constitutional_metadata']}")
```

## MCP Server Configuration

### Setting Up Custom MCP Servers

```python
from triad.tools.mcp_integration import ParliamentaryMCPClient, MCPServerConfig, MCPServerType

mcp_client = ParliamentaryMCPClient()

# Add custom government database server
custom_server = MCPServerConfig(
    name="government_data",
    server_type=MCPServerType.GOVERNMENT_DATA,
    connection_params={
        "command": "python",
        "args": ["path/to/government_data_server.py"],
        "env": {
            "GOV_DATABASE_URL": "https://api.gov.ca/data",
            "API_KEY": "${GOV_API_KEY}"
        }
    },
    security_level=ToolSecurityLevel.MINISTERIAL,
    constitutional_authority_required=ParliamentaryAuthority.EXECUTIVE,
    description="Access to government databases and statistics",
    available_tools=[
        "query_census_data",
        "get_economic_indicators", 
        "access_department_records"
    ]
)

mcp_client.servers["government_data"] = custom_server
```

### Connecting to External APIs

```python
# Configure external API access through MCP
external_api_server = MCPServerConfig(
    name="international_treaties",
    server_type=MCPServerType.EXTERNAL_API,
    connection_params={
        "base_url": "https://api.treaties.un.org/",
        "authentication": "bearer_token",
        "headers": {"Authorization": "Bearer ${UN_API_TOKEN}"}
    },
    security_level=ToolSecurityLevel.PARLIAMENTARY,
    description="Access to UN treaty database",
    available_tools=[
        "search_treaties",
        "get_treaty_text",
        "check_ratification_status"
    ]
)
```

## Security and Permissions

### Constitutional Authority Levels

The system enforces constitutional authority requirements:

- **PUBLIC**: Accessible to all agents (Hansard records, public documents)
- **PARLIAMENTARY**: Requires parliamentary agent status (legislative databases)
- **MINISTERIAL**: Requires executive authority (policy analysis, government data)
- **CONSTITUTIONAL**: Requires judicial authority (constitutional law, Charter interpretation)
- **CROWN**: Requires Crown authority (crisis management, constitutional interpretation)

### Security Validation

```python
from triad.tools.parliamentary_toolsets import ParliamentaryContext, ToolSecurityLevel

# Create context with appropriate security clearance
high_security_context = ParliamentaryContext(
    agent_id="evaluator_001",
    constitutional_authority=ParliamentaryAuthority.JUDICIAL,
    security_clearance=ToolSecurityLevel.CONSTITUTIONAL,
    constitutional_oversight=True
)

# Access to constitutional law server will be granted
# Access to lower-security servers also granted
# Access to higher-security (Crown) servers will be denied
```

## Performance Monitoring

### Agent Performance Tracking

```python
# Get comprehensive system status
system_status = await manager.get_system_status()

print(f"Active Agents: {system_status['agent_count']}")
print(f"Active Parliamentary Sessions: {system_status['active_sessions']}")

# Check individual agent performance
for agent_id, status in system_status['agents'].items():
    performance = status['performance']
    print(f"\nAgent {agent_id}:")
    print(f"  Role: {status['role']}")
    print(f"  Tasks Completed: {performance['tasks_completed']}")
    print(f"  Constitutional Reviews: {performance['constitutional_reviews_conducted']}")
    print(f"  Parliamentary Procedures: {performance['parliamentary_procedures_managed']}")
```

### MCP Server Health Monitoring

```python
# Monitor MCP server health
mcp_status = await mcp_client.get_server_status()

print(f"Total MCP Servers: {mcp_status['total_servers']}")
print(f"Active Connections: {mcp_status['active_connections']}")

for server_name, server_info in mcp_status['servers'].items():
    print(f"\nServer: {server_name}")
    print(f"  Type: {server_info['server_type']}")
    print(f"  Connected: {server_info['connected']}")
    print(f"  Security Level: {server_info['security_level']}")
    print(f"  Available Tools: {len(server_info['available_tools'])}")
```

## Troubleshooting

### Common Issues

1. **Permission Denied for MCP Server**
   ```
   PermissionError: Server constitutional_law requires judicial authority
   ```
   **Solution**: Ensure agent has appropriate constitutional authority and security clearance

2. **Tool Not Available**
   ```
   ValueError: Tool analyze_constitutional_compliance not available on server legislative_db
   ```
   **Solution**: Check server configuration and available tools list

3. **Constitutional Validation Failed**
   ```
   Constitutional violation: Separation of powers violation
   ```
   **Solution**: Review the action against constitutional principles and proper authority

### Debug Mode

```python
# Enable comprehensive logging
import logging
logging.getLogger('triad').setLevel(logging.DEBUG)

# Check agent initialization status
agent_status = await agent.get_agent_status()
if not agent_status['initialized']:
    print("Agent not properly initialized")
    await agent.initialize()

# Validate MCP connections
mcp_status = await mcp_client.get_server_status()
for server_name, status in mcp_status['servers'].items():
    if status['enabled'] and not status['connected']:
        print(f"Server {server_name} should be connected but isn't")
```

## Best Practices

### 1. Constitutional Compliance
- Always validate actions through constitutional toolset
- Ensure proper authority levels for sensitive operations
- Maintain audit trails for all constitutional decisions

### 2. Multi-Agent Coordination
- Use appropriate coordination types (collaborative, sequential, oversight)
- Include oversight agents for constitutional compliance
- Document all inter-agent interactions

### 3. Tool Usage
- Prefer built-in parliamentary tools over direct MCP calls
- Validate inputs before tool execution
- Handle tool errors gracefully with constitutional fallbacks

### 4. Session Management
- Start parliamentary sessions for complex multi-agent tasks
- Maintain session context throughout workflows
- Properly close sessions to free resources

### 5. Security
- Apply principle of least privilege for tool access
- Validate all external data sources
- Monitor for unusual activity patterns

The Westminster Parliamentary AI System's tools and MCP integration provide a robust foundation for democratic governance with constitutional oversight, ensuring that AI-assisted parliamentary operations maintain the highest standards of accountability, transparency, and constitutional compliance.