# MCP and Tools Integration Guide

This document explains the clean separation between MCP (Model Context Protocol) functionality and Parliamentary Tools in the Westminster Parliamentary AI System.

## Architecture Overview

The integration is designed with clear separation of concerns:

```
┌─────────────────────────────────────────────────────┐
│                Parliamentary Tools                   │
│  ┌─────────────────┐  ┌─────────────────────────────┐ │
│  │ Constitutional  │  │   Parliamentary MCP        │ │
│  │   Toolsets      │  │     Toolset                │ │
│  │                 │  │                             │ │
│  │ - Oversight     │  │ - MCP + Constitutional      │ │
│  │ - Compliance    │  │ - Security Validation       │ │
│  │ - Crisis Mgmt   │  │ - Parliamentary Context     │ │
│  └─────────────────┘  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│                   Core MCP Layer                    │
│  ┌─────────────────┐  ┌─────────────────────────────┐ │
│  │   MCP Client    │  │      MCP Tools             │ │
│  │                 │  │                             │ │
│  │ - Connections   │  │ - Basic Tool Calls          │ │
│  │ - Tool Calls    │  │ - Server Management         │ │
│  │ - Server Mgmt   │  │ - Connection Status         │ │
│  └─────────────────┘  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

## Component Responsibilities

### Core MCP Layer (`triad/mcp/`)

**Purpose**: Provides low-level MCP functionality without parliamentary oversight.

#### MCPClient (`triad/mcp/client.py`)
- Server connection management
- Tool execution
- Protocol handling
- Basic error handling

#### MCPTools (`triad/mcp/tools.py`)
- Basic tool calling for Pydantic AI
- Server connection/disconnection
- Tool listing and status
- **No constitutional oversight**

### Parliamentary Tools Layer (`triad/tools/`)

**Purpose**: Provides parliamentary-compliant access to tools and MCP servers.

#### Parliamentary Toolsets (`triad/tools/parliamentary_toolsets.py`)
- Constitutional oversight tools
- Legislative analysis tools
- Democratic process tools
- Security validation

#### Parliamentary MCP Toolset (`triad/tools/parliamentary_mcp_toolset.py`)
- MCP access with constitutional oversight
- Security clearance validation
- Parliamentary context enforcement
- Democratic accountability

#### MCP Integration (`triad/tools/mcp_integration.py`)
- Parliamentary MCP client with security
- Constitutional authority validation
- Server configuration management
- Agent-specific tool registration

## Usage Patterns

### For Basic MCP Operations (No Parliamentary Oversight)
```python
from triad.mcp import MCPClient, MCPTools

# Basic MCP client
mcp_client = MCPClient()
mcp_tools = MCPTools(mcp_client)

# Register basic tools with agent
register_mcp_tools(agent, mcp_tools)
```

### For Parliamentary AI Agents (With Constitutional Oversight)
```python
from triad.tools import (
    ParliamentaryMCPToolset,
    ParliamentaryContext,
    ParliamentaryAuthority,
    register_parliamentary_mcp_tools
)

# Create parliamentary context
context = ParliamentaryContext(
    agent_id="constitutional_evaluator",
    constitutional_authority=ParliamentaryAuthority.JUDICIAL,
    security_clearance=ToolSecurityLevel.CONSTITUTIONAL
)

# Register parliamentary MCP tools
agent = await register_parliamentary_mcp_tools(agent, context)
```

### For Constitutional Agents
```python
from triad.tools import setup_constitutional_agent_mcp_tools

# Automatic role-based tool setup
agent = await setup_constitutional_agent_mcp_tools(
    agent=agent,
    agent_role="evaluator",  # planner, executor, evaluator, overwatch
    parliamentary_context=context
)
```

## MCP Server Configuration

### Parliamentary Servers (High Security)
```python
# Constitutional Law Server
{
    "name": "constitutional_law",
    "security_level": ToolSecurityLevel.CONSTITUTIONAL,
    "constitutional_authority_required": ParliamentaryAuthority.JUDICIAL,
    "tools": [
        "search_constitutional_cases",
        "interpret_charter_rights", 
        "analyze_constitutional_compliance"
    ]
}

# Legislative Database Server
{
    "name": "legislative_db", 
    "security_level": ToolSecurityLevel.PARLIAMENTARY,
    "constitutional_authority_required": ParliamentaryAuthority.LEGISLATIVE,
    "tools": [
        "search_bills",
        "get_bill_text",
        "track_amendments"
    ]
}
```

### Public Servers (Lower Security)
```python
# Hansard Archive Server
{
    "name": "hansard_archive",
    "security_level": ToolSecurityLevel.PUBLIC,
    "tools": [
        "search_debates",
        "get_session_transcript",
        "analyze_speaking_patterns"
    ]
}
```

## Security and Validation

### Constitutional Authority Validation
```python
# Each tool validates authority
if ctx.deps.constitutional_authority not in [
    ParliamentaryAuthority.JUDICIAL, 
    ParliamentaryAuthority.CROWN
]:
    return {
        "success": False,
        "error": "Insufficient constitutional authority",
        "required_authority": "judicial or crown"
    }
```

### Security Clearance Validation
```python
# Security level validation
security_levels = [
    ToolSecurityLevel.PUBLIC,
    ToolSecurityLevel.PARLIAMENTARY, 
    ToolSecurityLevel.MINISTERIAL,
    ToolSecurityLevel.CONSTITUTIONAL,
    ToolSecurityLevel.CROWN
]

if (security_levels.index(context.security_clearance) < 
    security_levels.index(server_config.security_level)):
    raise PermissionError("Insufficient security clearance")
```

## Tool Registration by Agent Role

### Planner Agent (Legislative Authority)
- Legislative database access
- Policy analysis tools
- Citizen engagement tools

### Executor Agent (Executive Authority)  
- Policy analysis tools
- Government data access
- Implementation tracking

### Evaluator Agent (Judicial Authority)
- Constitutional law database
- Legislative database (read-only)
- Hansard archive access

### Overwatch Agent (Crown Authority)
- All constitutional tools
- Crisis management tools
- Full system oversight

## Logging and Accountability

All parliamentary MCP operations include:
- Constitutional authority logging
- Security clearance validation
- Parliamentary session tracking
- Democratic accountability metadata
- Audit trail maintenance

## Best Practices

1. **Use Parliamentary Tools for AI Agents**: Always use `triad.tools` for AI agents requiring constitutional oversight.

2. **Use Core MCP for Infrastructure**: Use `triad.mcp` only for low-level infrastructure or non-parliamentary operations.

3. **Validate Authority**: Always validate constitutional authority before sensitive operations.

4. **Log All Operations**: Ensure comprehensive logging for democratic accountability.

5. **Separation of Concerns**: Keep MCP protocol handling separate from parliamentary oversight logic.

6. **Security First**: Apply appropriate security clearance levels to all tools and servers.

This clean separation ensures that:
- Core MCP functionality remains focused and testable
- Parliamentary oversight is comprehensive and consistent  
- Security validation is properly enforced
- Constitutional principles are maintained throughout
- Democratic accountability is preserved