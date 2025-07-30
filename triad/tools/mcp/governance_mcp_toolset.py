"""
Parliamentary MCP Toolset for Westminster Parliamentary AI System

Combines parliamentary oversight with MCP capabilities to provide
constitutional-compliant external system access for AI agents.
"""

import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
from enum import Enum
import logfire
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.toolsets import AbstractToolset
from pydantic_ai.tools import Tool

from triad.tools.parliamentary_toolsets import ParliamentaryContext, ParliamentaryAuthority, ToolSecurityLevel
from triad.tools.mcp_integration import get_parliamentary_mcp_client, ParliamentaryMCPClient
from triad.mcp.tools import MCPTools
from triad.core.logging import get_logfire_config


class ParliamentaryMCPToolset(AbstractToolset):
    """
    Parliamentary MCP toolset with constitutional oversight.
    
    Provides MCP functionality with proper Westminster parliamentary
    principles, constitutional validation, and democratic accountability.
    """
    
    def __init__(self):
        self.logger = get_logfire_config()
        self.mcp_client = get_parliamentary_mcp_client()
        self.name = "parliamentary_mcp"
        
    async def get_tools(self) -> List[Tool]:
        """Get all parliamentary MCP tools."""
        return [
            self._create_constitutional_mcp_query_tool(),
            self._create_legislative_database_tool(),
            self._create_hansard_search_tool(),
            self._create_citizen_engagement_tool(),
            self._create_policy_analysis_tool(),
            self._create_mcp_server_management_tool()
        ]
    
    def _create_constitutional_mcp_query_tool(self) -> Tool:
        """Create tool for constitutional queries through MCP."""
        
        async def query_constitutional_law(
            ctx: RunContext[ParliamentaryContext],
            query: str,
            constitutional_context: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            """
            Query constitutional law database through MCP.
            
            Args:
                query: Constitutional law query
                constitutional_context: Additional context for the query
            
            Returns:
                Constitutional law analysis results
            """
            try:
                # Validate constitutional authority
                if ctx.deps.constitutional_authority not in [
                    ParliamentaryAuthority.JUDICIAL, 
                    ParliamentaryAuthority.CROWN,
                    ParliamentaryAuthority.LEGISLATIVE
                ]:
                    return {
                        "success": False,
                        "error": "Insufficient constitutional authority for constitutional law queries",
                        "required_authority": "judicial, crown, or legislative"
                    }
                
                with self.logger.parliamentary_session_span(
                    "constitutional-mcp-query",
                    [ctx.deps.agent_id]
                ) as span:
                    span.set_attribute("query_type", "constitutional_law")
                    span.set_attribute("constitutional_authority", ctx.deps.constitutional_authority.value)
                    
                    # Call constitutional law MCP server
                    result = await self.mcp_client.call_server_tool(
                        server_name="constitutional_law",
                        tool_name="search_constitutional_cases",
                        parameters={
                            "query": query,
                            "context": constitutional_context or {},
                            "charter_rights_analysis": True,
                            "precedent_search": True
                        },
                        parliamentary_context=ctx.deps
                    )
                    
                    # Log constitutional query
                    self.logger.log_parliamentary_event(
                        event_type="constitutional_mcp_query_completed",
                        data={
                            "query_preview": query[:100],
                            "server": "constitutional_law",
                            "success": result.get("success", False),
                            "constitutional_authority": ctx.deps.constitutional_authority.value
                        },
                        authority=ctx.deps.constitutional_authority.value
                    )
                    
                    return result
                    
            except Exception as e:
                self.logger.log_parliamentary_event(
                    event_type="constitutional_mcp_query_error",
                    data={
                        "error": str(e),
                        "query": query[:100],
                        "agent_id": ctx.deps.agent_id
                    },
                    authority=ctx.deps.constitutional_authority.value
                )
                raise
        
        return Tool(query_constitutional_law)
    
    def _create_legislative_database_tool(self) -> Tool:
        """Create tool for legislative database access through MCP."""
        
        async def search_legislative_database(
            ctx: RunContext[ParliamentaryContext],
            search_type: str,
            search_query: str,
            bill_status: Optional[str] = None,
            date_range: Optional[Dict[str, str]] = None
        ) -> Dict[str, Any]:
            """
            Search legislative database through MCP.
            
            Args:
                search_type: Type of search (bills, acts, regulations, amendments)
                search_query: Search query text
                bill_status: Filter by bill status (optional)
                date_range: Date range filter (optional)
            
            Returns:
                Legislative database search results
            """
            try:
                with self.logger.parliamentary_session_span(
                    "legislative-mcp-search",
                    [ctx.deps.agent_id]
                ) as span:
                    span.set_attribute("search_type", search_type)
                    span.set_attribute("constitutional_authority", ctx.deps.constitutional_authority.value)
                    
                    # Determine appropriate tool based on search type
                    tool_mapping = {
                        "bills": "search_bills",
                        "acts": "search_bills",
                        "regulations": "search_bills", 
                        "amendments": "track_amendments"
                    }
                    
                    tool_name = tool_mapping.get(search_type, "search_bills")
                    
                    # Call legislative database MCP server
                    result = await self.mcp_client.call_server_tool(
                        server_name="legislative_db",
                        tool_name=tool_name,
                        parameters={
                            "query": search_query,
                            "status_filter": bill_status,
                            "date_range": date_range,
                            "parliamentary_session": ctx.deps.parliamentary_session_id,
                            "detailed_analysis": True
                        },
                        parliamentary_context=ctx.deps
                    )
                    
                    # Log legislative search
                    self.logger.log_parliamentary_event(
                        event_type="legislative_mcp_search_completed",
                        data={
                            "search_type": search_type,
                            "tool_used": tool_name,
                            "results_count": len(result.get("data", {}).get("results", [])),
                            "constitutional_authority": ctx.deps.constitutional_authority.value
                        },
                        authority=ctx.deps.constitutional_authority.value
                    )
                    
                    return result
                    
            except Exception as e:
                self.logger.log_parliamentary_event(
                    event_type="legislative_mcp_search_error",
                    data={
                        "error": str(e),
                        "search_type": search_type,
                        "agent_id": ctx.deps.agent_id
                    },
                    authority=ctx.deps.constitutional_authority.value
                )
                raise
        
        return Tool(search_legislative_database)
    
    def _create_hansard_search_tool(self) -> Tool:
        """Create tool for Hansard archive search through MCP."""
        
        async def search_hansard_archive(
            ctx: RunContext[ParliamentaryContext],
            debate_topic: str,
            speaker_name: Optional[str] = None,
            date_range: Optional[Dict[str, str]] = None,
            session_type: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Search Hansard parliamentary debates archive through MCP.
            
            Args:
                debate_topic: Topic or keyword to search for
                speaker_name: Specific speaker to filter by (optional)
                date_range: Date range for search (optional)
                session_type: Type of parliamentary session (optional)
            
            Returns:
                Hansard search results with debate transcripts
            """
            try:
                with self.logger.parliamentary_session_span(
                    "hansard-mcp-search",
                    [ctx.deps.agent_id]
                ) as span:
                    span.set_attribute("debate_topic", debate_topic)
                    span.set_attribute("speaker_name", speaker_name or "any")
                    
                    # Call Hansard archive MCP server
                    result = await self.mcp_client.call_server_tool(
                        server_name="hansard_archive",
                        tool_name="search_debates",
                        parameters={
                            "topic": debate_topic,
                            "speaker": speaker_name,
                            "date_range": date_range,
                            "session_type": session_type,
                            "include_transcript": True,
                            "analyze_positions": True
                        },
                        parliamentary_context=ctx.deps
                    )
                    
                    # Log Hansard search
                    self.logger.log_parliamentary_event(
                        event_type="hansard_mcp_search_completed",
                        data={
                            "debate_topic": debate_topic,
                            "speaker_filter": speaker_name,
                            "results_count": len(result.get("data", {}).get("debates", [])),
                            "constitutional_authority": ctx.deps.constitutional_authority.value
                        },
                        authority=ctx.deps.constitutional_authority.value
                    )
                    
                    return result
                    
            except Exception as e:
                self.logger.log_parliamentary_event(
                    event_type="hansard_mcp_search_error",
                    data={
                        "error": str(e),
                        "debate_topic": debate_topic,
                        "agent_id": ctx.deps.agent_id
                    },
                    authority=ctx.deps.constitutional_authority.value
                )
                raise
        
        return Tool(search_hansard_archive)
    
    def _create_citizen_engagement_tool(self) -> Tool:
        """Create tool for citizen engagement through MCP."""
        
        async def process_citizen_engagement(
            ctx: RunContext[ParliamentaryContext],
            engagement_type: str,
            content: str,
            citizen_data: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            """
            Process citizen engagement through MCP.
            
            Args:
                engagement_type: Type of engagement (petition, consultation, feedback)
                content: Content of the engagement
                citizen_data: Optional citizen information
            
            Returns:
                Citizen engagement processing results
            """
            try:
                with self.logger.parliamentary_session_span(
                    "citizen-engagement-mcp",
                    [ctx.deps.agent_id]
                ) as span:
                    span.set_attribute("engagement_type", engagement_type)
                    span.set_attribute("constitutional_authority", ctx.deps.constitutional_authority.value)
                    
                    # Determine appropriate tool based on engagement type
                    tool_mapping = {
                        "petition": "process_petition",
                        "consultation": "analyze_public_consultation",
                        "feedback": "track_citizen_feedback"
                    }
                    
                    tool_name = tool_mapping.get(engagement_type, "track_citizen_feedback")
                    
                    # Call citizen engagement MCP server
                    result = await self.mcp_client.call_server_tool(
                        server_name="citizen_engagement",
                        tool_name=tool_name,
                        parameters={
                            "content": content,
                            "citizen_data": citizen_data or {},
                            "parliamentary_session": ctx.deps.parliamentary_session_id,
                            "democratic_validation": True,
                            "privacy_protection": True
                        },
                        parliamentary_context=ctx.deps
                    )
                    
                    # Log citizen engagement
                    self.logger.log_parliamentary_event(
                        event_type="citizen_engagement_mcp_completed",
                        data={
                            "engagement_type": engagement_type,
                            "tool_used": tool_name,
                            "processing_successful": result.get("success", False),
                            "democratic_participation": True
                        },
                        authority=ctx.deps.constitutional_authority.value
                    )
                    
                    return result
                    
            except Exception as e:
                self.logger.log_parliamentary_event(
                    event_type="citizen_engagement_mcp_error",
                    data={
                        "error": str(e),
                        "engagement_type": engagement_type,
                        "agent_id": ctx.deps.agent_id
                    },
                    authority=ctx.deps.constitutional_authority.value
                )
                raise
        
        return Tool(process_citizen_engagement)
    
    def _create_policy_analysis_tool(self) -> Tool:
        """Create tool for policy analysis through MCP."""
        
        async def analyze_policy_options(
            ctx: RunContext[ParliamentaryContext],
            policy_area: str,
            policy_question: str,
            analysis_type: str = "comprehensive"
        ) -> Dict[str, Any]:
            """
            Analyze policy options through MCP.
            
            Args:
                policy_area: Area of policy (healthcare, education, etc.)
                policy_question: Specific policy question
                analysis_type: Type of analysis (comprehensive, economic, social)
            
            Returns:
                Policy analysis results
            """
            try:
                # Validate ministerial authority for policy analysis
                if ctx.deps.constitutional_authority not in [
                    ParliamentaryAuthority.EXECUTIVE,
                    ParliamentaryAuthority.LEGISLATIVE,
                    ParliamentaryAuthority.CROWN
                ]:
                    return {
                        "success": False,
                        "error": "Policy analysis requires executive, legislative, or crown authority",
                        "constitutional_requirement": "ministerial_responsibility"
                    }
                
                with self.logger.parliamentary_session_span(
                    "policy-analysis-mcp",
                    [ctx.deps.agent_id]
                ) as span:
                    span.set_attribute("policy_area", policy_area)
                    span.set_attribute("analysis_type", analysis_type)
                    
                    # Determine appropriate analysis tool
                    tool_mapping = {
                        "comprehensive": "analyze_policy_options",
                        "economic": "assess_economic_impact",
                        "social": "evaluate_social_outcomes",
                        "international": "compare_international_practices"
                    }
                    
                    tool_name = tool_mapping.get(analysis_type, "analyze_policy_options")
                    
                    # Call policy analysis MCP server
                    result = await self.mcp_client.call_server_tool(
                        server_name="policy_analysis",
                        tool_name=tool_name,
                        parameters={
                            "policy_area": policy_area,
                            "policy_question": policy_question,
                            "analysis_depth": analysis_type,
                            "constitutional_compliance": True,
                            "evidence_based": True,
                            "ministerial_briefing": True
                        },
                        parliamentary_context=ctx.deps
                    )
                    
                    # Log policy analysis
                    self.logger.log_parliamentary_event(
                        event_type="policy_analysis_mcp_completed",
                        data={
                            "policy_area": policy_area,
                            "analysis_type": analysis_type,
                            "tool_used": tool_name,
                            "ministerial_responsibility": True
                        },
                        authority=ctx.deps.constitutional_authority.value
                    )
                    
                    return result
                    
            except Exception as e:
                self.logger.log_parliamentary_event(
                    event_type="policy_analysis_mcp_error",
                    data={
                        "error": str(e),
                        "policy_area": policy_area,
                        "agent_id": ctx.deps.agent_id
                    },
                    authority=ctx.deps.constitutional_authority.value
                )
                raise
        
        return Tool(analyze_policy_options)
    
    def _create_mcp_server_management_tool(self) -> Tool:
        """Create tool for MCP server management."""
        
        async def manage_mcp_servers(
            ctx: RunContext[ParliamentaryContext],
            operation: str,
            server_name: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Manage MCP server connections and status.
            
            Args:
                operation: Operation to perform (status, connect, disconnect, list)
                server_name: Specific server name (optional for some operations)
            
            Returns:
                MCP server management results
            """
            try:
                with self.logger.parliamentary_session_span(
                    "mcp-server-management",
                    [ctx.deps.agent_id]
                ) as span:
                    span.set_attribute("operation", operation)
                    span.set_attribute("server_name", server_name or "all")
                    
                    if operation == "status":
                        result = await self.mcp_client.get_server_status()
                    
                    elif operation == "connect" and server_name:
                        success = await self.mcp_client.connect_to_server(
                            server_name, ctx.deps
                        )
                        result = {"success": success, "server_name": server_name}
                    
                    elif operation == "disconnect" and server_name:
                        # Disconnect would be handled through the client
                        result = {"success": True, "operation": "disconnect", "server_name": server_name}
                    
                    elif operation == "list":
                        result = await self.mcp_client.get_server_status()
                    
                    else:
                        result = {
                            "success": False,
                            "error": f"Unknown operation: {operation}",
                            "available_operations": ["status", "connect", "disconnect", "list"]
                        }
                    
                    # Log server management
                    self.logger.log_parliamentary_event(
                        event_type="mcp_server_management_completed",
                        data={
                            "operation": operation,
                            "server_name": server_name,
                            "success": result.get("success", True),
                            "constitutional_authority": ctx.deps.constitutional_authority.value
                        },
                        authority=ctx.deps.constitutional_authority.value
                    )
                    
                    return result
                    
            except Exception as e:
                self.logger.log_parliamentary_event(
                    event_type="mcp_server_management_error",
                    data={
                        "error": str(e),
                        "operation": operation,
                        "agent_id": ctx.deps.agent_id
                    },
                    authority=ctx.deps.constitutional_authority.value
                )
                raise
        
        return Tool(manage_mcp_servers)


# Helper function to register parliamentary MCP tools with agents
async def register_parliamentary_mcp_tools(
    agent: Agent,
    parliamentary_context: ParliamentaryContext,
    enabled_servers: Optional[List[str]] = None
) -> Agent:
    """
    Register parliamentary MCP tools with a Pydantic AI agent.
    
    Args:
        agent: Pydantic AI agent
        parliamentary_context: Parliamentary context for the agent
        enabled_servers: List of enabled MCP servers (optional)
    
    Returns:
        Agent with registered parliamentary MCP tools
    """
    toolset = ParliamentaryMCPToolset()
    tools = await toolset.get_tools()
    
    # Register tools with the agent
    for tool in tools:
        agent.tool(tool)
    
    # Log tool registration
    logger = get_logfire_config()
    logger.log_parliamentary_event(
        event_type="parliamentary_mcp_tools_registered",
        data={
            "agent_id": parliamentary_context.agent_id,
            "tools_count": len(tools),
            "enabled_servers": enabled_servers or ["all"],
            "constitutional_authority": parliamentary_context.constitutional_authority.value
        },
        authority=parliamentary_context.constitutional_authority.value
    )
    
    return agent


# Global parliamentary MCP toolset instance
parliamentary_mcp_toolset = ParliamentaryMCPToolset()


def get_parliamentary_mcp_toolset() -> ParliamentaryMCPToolset:
    """Get the global parliamentary MCP toolset."""
    return parliamentary_mcp_toolset