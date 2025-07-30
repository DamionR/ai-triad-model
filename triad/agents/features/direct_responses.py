"""
Direct Response Patterns for Westminster Parliamentary AI System

Implements Pydantic AI direct model responses for simple parliamentary tasks,
quick constitutional checks, and low-level model interactions without agent overhead.
"""

import asyncio
from typing import Dict, List, Optional, Any, Union, AsyncGenerator
from datetime import datetime, timezone
from enum import Enum
import logfire
from pydantic import BaseModel, Field
from pydantic_ai.direct import (
    model_request, 
    model_request_sync, 
    model_request_stream,
    model_request_stream_sync
)
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest, 
    UserPromptPart,
    SystemPromptPart
)

from triad.models.model_config import get_model_config, ModelProvider
from triad.tools.parliamentary_toolsets import ParliamentaryAuthority
from triad.core.logging import get_logfire_config


class DirectResponseType(Enum):
    """Types of direct responses for parliamentary tasks."""
    CONSTITUTIONAL_CHECK = "constitutional_check"
    PROCEDURAL_QUERY = "procedural_query"
    QUICK_LOOKUP = "quick_lookup"
    SIMPLE_ANALYSIS = "simple_analysis"
    STATUS_CHECK = "status_check"
    VALIDATION = "validation"


class ResponsePriority(Enum):
    """Priority levels for direct responses."""
    URGENT = "urgent"          # Immediate constitutional questions
    HIGH = "high"             # Time-sensitive parliamentary procedures
    NORMAL = "normal"         # Standard queries
    LOW = "low"              # Non-critical information requests


class DirectResponseRequest(BaseModel):
    """Structured request for direct model responses."""
    query: str
    response_type: DirectResponseType
    priority: ResponsePriority = ResponsePriority.NORMAL
    constitutional_authority: Optional[ParliamentaryAuthority] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    max_tokens: int = 500
    temperature: float = 0.1
    stream: bool = False
    requesting_agent: Optional[str] = None


class DirectResponseResult(BaseModel):
    """Result from direct model response."""
    query: str
    response: str
    response_type: DirectResponseType
    model_used: str
    execution_time_seconds: float
    token_usage: Dict[str, int] = Field(default_factory=dict)
    constitutional_compliant: bool = True
    confidence_score: float = 0.8
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ParliamentaryDirectResponder:
    """
    Direct response handler for simple parliamentary queries.
    
    Provides fast, low-overhead responses for constitutional checks,
    procedural queries, and simple parliamentary information requests.
    """
    
    def __init__(self):
        self.logger = get_logfire_config()
        self.model_config = get_model_config()
        self.response_cache: Dict[str, DirectResponseResult] = {}
        
    def _get_preferred_model(self, priority: ResponsePriority) -> str:
        """Get preferred model based on response priority and task complexity."""
        
        enabled_providers = self.model_config.get_enabled_providers()
        
        if not enabled_providers:
            raise ValueError("No AI providers enabled for direct responses")
        
        # Model selection based on priority
        if priority == ResponsePriority.URGENT:
            # Use fastest models for urgent responses
            fast_models = ["groq", "openai", "anthropic"]
            for provider in fast_models:
                if provider in enabled_providers:
                    if provider == "groq":
                        return "groq:llama-3.1-8b-instant"
                    elif provider == "openai":
                        return "openai:gpt-3.5-turbo"
                    elif provider == "anthropic":
                        return "anthropic:claude-3-5-haiku-20241022"
        
        elif priority == ResponsePriority.HIGH:
            # Balance speed and quality
            if "openai" in enabled_providers:
                return "openai:gpt-4o-mini"
            elif "anthropic" in enabled_providers:
                return "anthropic:claude-3-5-haiku-20241022"
            elif "groq" in enabled_providers:
                return "groq:llama-3.1-70b-versatile"
        
        else:  # NORMAL or LOW priority
            # Use best available models
            if "anthropic" in enabled_providers:
                return "anthropic:claude-3-5-sonnet-20241022"
            elif "openai" in enabled_providers:
                return "openai:gpt-4o"
            elif "gemini" in enabled_providers:
                return "gemini:gemini-2.0-flash-exp"
        
        # Fallback to first available provider
        provider = enabled_providers[0]
        provider_config = self.model_config.providers[provider]
        if provider_config.models:
            return f"{provider}:{provider_config.models[0]}"
        
        return f"{provider}:default"
    
    def _create_parliamentary_system_message(
        self, 
        response_type: DirectResponseType,
        constitutional_authority: Optional[ParliamentaryAuthority] = None
    ) -> SystemPromptPart:
        """Create system message for parliamentary context."""
        
        base_context = """You are providing direct responses for the Westminster Parliamentary AI System. 
Provide concise, accurate information while maintaining constitutional accountability and Westminster principles."""
        
        if response_type == DirectResponseType.CONSTITUTIONAL_CHECK:
            context = base_context + """

CONSTITUTIONAL CHECK MODE:
- Provide clear Yes/No answers for constitutional compliance
- Reference specific constitutional provisions when relevant  
- Note any Charter rights implications
- Keep responses brief but constitutionally sound
- If uncertain, indicate need for detailed constitutional review"""
        
        elif response_type == DirectResponseType.PROCEDURAL_QUERY:
            context = base_context + """

PARLIAMENTARY PROCEDURE MODE:
- Reference specific parliamentary procedures and conventions
- Cite relevant Standing Orders when applicable
- Provide step-by-step guidance for procedural questions
- Maintain Westminster parliamentary traditions
- Note any Speaker rulings or precedents"""
        
        elif response_type == DirectResponseType.QUICK_LOOKUP:
            context = base_context + """

QUICK LOOKUP MODE:
- Provide factual information from parliamentary records
- Reference official sources when possible
- Keep responses concise and accurate
- Note if information requires verification
- Direct to appropriate authorities for detailed information"""
        
        elif response_type == DirectResponseType.SIMPLE_ANALYSIS:
            context = base_context + """

SIMPLE ANALYSIS MODE:
- Provide basic analysis without deep reasoning
- Focus on key points and immediate implications
- Note constitutional considerations if relevant
- Keep conclusions clear and actionable
- Indicate if complex analysis is needed"""
        
        elif response_type == DirectResponseType.STATUS_CHECK:
            context = base_context + """

STATUS CHECK MODE:
- Provide current status information
- Include relevant dates and stages
- Note next steps or upcoming deadlines
- Reference official sources
- Keep updates factual and current"""
        
        elif response_type == DirectResponseType.VALIDATION:
            context = base_context + """

VALIDATION MODE:
- Validate information against parliamentary standards
- Check for procedural compliance
- Verify constitutional requirements
- Provide clear validation results
- Note any discrepancies or concerns"""
        
        else:
            context = base_context
        
        if constitutional_authority:
            context += f"\n\nResponding from {constitutional_authority.value} constitutional authority perspective."
        
        return SystemPromptPart(content=context)
    
    async def direct_response(
        self, 
        request: DirectResponseRequest
    ) -> DirectResponseResult:
        """
        Execute direct model response for parliamentary query.
        
        Args:
            request: Structured direct response request
            
        Returns:
            Direct response result with constitutional metadata
        """
        
        # Check cache for identical requests (optional optimization)
        cache_key = f"{request.query}_{request.response_type.value}_{request.priority.value}"
        if cache_key in self.response_cache:
            cached_result = self.response_cache[cache_key]
            if (datetime.now(timezone.utc) - cached_result.timestamp).seconds < 300:  # 5 minute cache
                return cached_result
        
        start_time = datetime.now(timezone.utc)
        
        try:
            with self.logger.parliamentary_session_span(
                f"direct-response-{request.response_type.value}",
                [request.requesting_agent or "direct_responder"]
            ) as span:
                
                # Get appropriate model
                model_name = self._get_preferred_model(request.priority)
                
                # Create messages
                system_message = self._create_parliamentary_system_message(
                    request.response_type, 
                    request.constitutional_authority
                )
                
                user_message = UserPromptPart(content=request.query)
                
                # Add context if provided
                if request.context:
                    context_str = "\n".join([f"{k}: {v}" for k, v in request.context.items()])
                    user_message = UserPromptPart(
                        content=f"{request.query}\n\nContext:\n{context_str}"
                    )
                
                messages = [
                    ModelRequest.from_message(system_message),
                    ModelRequest.from_message(user_message)
                ]
                
                # Execute direct model request
                if request.stream:
                    # Streaming response
                    response_parts = []
                    async for chunk in model_request_stream(model_name, messages):
                        if hasattr(chunk, 'parts') and chunk.parts:
                            for part in chunk.parts:
                                if hasattr(part, 'content'):
                                    response_parts.append(part.content)
                    
                    response_text = ''.join(response_parts)
                else:
                    # Non-streaming response
                    response = await model_request(model_name, messages)
                    response_text = response.parts[0].content if response.parts else ""
                
                execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
                
                # Assess constitutional compliance (simple heuristic)
                constitutional_compliant = self._assess_constitutional_compliance(
                    request.query, response_text, request.response_type
                )
                
                # Calculate confidence score
                confidence_score = self._calculate_confidence_score(
                    response_text, request.response_type
                )
                
                # Create result
                result = DirectResponseResult(
                    query=request.query,
                    response=response_text,
                    response_type=request.response_type,
                    model_used=model_name,
                    execution_time_seconds=execution_time,
                    constitutional_compliant=constitutional_compliant,
                    confidence_score=confidence_score,
                    metadata={
                        "priority": request.priority.value,
                        "constitutional_authority": request.constitutional_authority.value if request.constitutional_authority else None,
                        "context_provided": bool(request.context),
                        "stream_response": request.stream,
                        "requesting_agent": request.requesting_agent
                    }
                )
                
                # Cache result
                self.response_cache[cache_key] = result
                
                # Log direct response
                self.logger.log_parliamentary_event(
                    event_type="direct_response_completed",
                    data={
                        "response_type": request.response_type.value,
                        "priority": request.priority.value,
                        "model_used": model_name,
                        "execution_time": execution_time,
                        "constitutional_compliant": constitutional_compliant,
                        "confidence_score": confidence_score
                    },
                    authority=request.constitutional_authority.value if request.constitutional_authority else "system"
                )
                
                span.set_attribute("direct_response.type", request.response_type.value)
                span.set_attribute("direct_response.priority", request.priority.value)
                span.set_attribute("direct_response.model", model_name)
                span.set_attribute("direct_response.execution_time", execution_time)
                span.set_attribute("direct_response.constitutional_compliant", constitutional_compliant)
                
                return result
                
        except Exception as e:
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            self.logger.log_parliamentary_event(
                event_type="direct_response_error",
                data={
                    "error": str(e),
                    "query": request.query,
                    "response_type": request.response_type.value,
                    "execution_time": execution_time
                },
                authority=request.constitutional_authority.value if request.constitutional_authority else "system"
            )
            
            raise
    
    def direct_response_sync(
        self, 
        request: DirectResponseRequest
    ) -> DirectResponseResult:
        """
        Synchronous version of direct response for blocking operations.
        
        Args:
            request: Structured direct response request
            
        Returns:
            Direct response result with constitutional metadata
        """
        
        start_time = datetime.now(timezone.utc)
        
        try:
            # Get appropriate model
            model_name = self._get_preferred_model(request.priority)
            
            # Create messages
            system_message = self._create_parliamentary_system_message(
                request.response_type, 
                request.constitutional_authority
            )
            
            user_message = UserPromptPart(content=request.query)
            
            messages = [
                ModelRequest.from_message(system_message),
                ModelRequest.from_message(user_message)
            ]
            
            # Execute synchronous direct model request
            response = model_request_sync(model_name, messages)
            response_text = response.parts[0].content if response.parts else ""
            
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            # Assess constitutional compliance
            constitutional_compliant = self._assess_constitutional_compliance(
                request.query, response_text, request.response_type
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                response_text, request.response_type
            )
            
            # Create result
            result = DirectResponseResult(
                query=request.query,
                response=response_text,
                response_type=request.response_type,
                model_used=model_name,
                execution_time_seconds=execution_time,
                constitutional_compliant=constitutional_compliant,
                confidence_score=confidence_score,
                metadata={
                    "priority": request.priority.value,
                    "synchronous": True,
                    "requesting_agent": request.requesting_agent
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.log_parliamentary_event(
                event_type="direct_response_sync_error",
                data={
                    "error": str(e),
                    "query": request.query,
                    "response_type": request.response_type.value
                },
                authority="system"
            )
            raise
    
    def _assess_constitutional_compliance(
        self, 
        query: str, 
        response: str, 
        response_type: DirectResponseType
    ) -> bool:
        """Simple assessment of constitutional compliance in response."""
        
        # Basic heuristics for constitutional compliance
        response_lower = response.lower()
        
        # Check for constitutional language
        constitutional_indicators = [
            "constitutional", "charter", "rights", "freedom", "due process",
            "rule of law", "separation of powers", "parliamentary", "democratic"
        ]
        
        # Check for problematic language
        problematic_indicators = [
            "unconstitutional", "violation", "breach", "illegal", "unlawful",
            "arbitrary", "discriminatory"
        ]
        
        constitutional_score = sum(1 for indicator in constitutional_indicators 
                                 if indicator in response_lower)
        
        problematic_score = sum(1 for indicator in problematic_indicators 
                              if indicator in response_lower)
        
        # Simple scoring: more constitutional language = better compliance
        # Unless there are explicit problems mentioned
        if problematic_score > constitutional_score:
            return False
        
        # For constitutional checks, look for explicit compliance language
        if response_type == DirectResponseType.CONSTITUTIONAL_CHECK:
            if any(phrase in response_lower for phrase in ["complies", "constitutional", "lawful"]):
                return True
            elif any(phrase in response_lower for phrase in ["violates", "unconstitutional", "unlawful"]):
                return False
        
        # Default to compliant unless clear problems identified
        return problematic_score == 0
    
    def _calculate_confidence_score(
        self, 
        response: str, 
        response_type: DirectResponseType
    ) -> float:
        """Calculate confidence score for the response."""
        
        response_lower = response.lower()
        confidence = 0.5  # Base confidence
        
        # Increase confidence for definitive language
        definitive_phrases = [
            "clearly", "definitely", "certainly", "established", "confirmed",
            "according to", "pursuant to", "as per", "specifically"
        ]
        
        confidence += min(0.3, sum(0.05 for phrase in definitive_phrases 
                                 if phrase in response_lower))
        
        # Decrease confidence for uncertain language
        uncertain_phrases = [
            "might", "could", "possibly", "unclear", "uncertain", "ambiguous",
            "depends", "varies", "potentially"
        ]
        
        confidence -= min(0.4, sum(0.08 for phrase in uncertain_phrases 
                                 if phrase in response_lower))
        
        # Adjust based on response type
        if response_type == DirectResponseType.CONSTITUTIONAL_CHECK:
            if any(word in response_lower for word in ["yes", "no", "compliant", "violation"]):
                confidence += 0.2  # Clear constitutional determination
        
        elif response_type == DirectResponseType.PROCEDURAL_QUERY:
            if "standing order" in response_lower or "procedure" in response_lower:
                confidence += 0.15  # Procedural specificity
        
        # Ensure confidence stays within bounds
        return max(0.1, min(1.0, confidence))


# Convenience functions for common parliamentary direct responses

async def quick_constitutional_check(
    question: str,
    constitutional_authority: Optional[ParliamentaryAuthority] = None,
    requesting_agent: Optional[str] = None
) -> DirectResponseResult:
    """Quick constitutional compliance check."""
    
    responder = ParliamentaryDirectResponder()
    
    request = DirectResponseRequest(
        query=question,
        response_type=DirectResponseType.CONSTITUTIONAL_CHECK,
        priority=ResponsePriority.HIGH,
        constitutional_authority=constitutional_authority,
        max_tokens=300,
        temperature=0.05,  # Very deterministic for constitutional checks
        requesting_agent=requesting_agent
    )
    
    return await responder.direct_response(request)


async def parliamentary_procedure_query(
    procedure_question: str,
    context: Optional[Dict[str, Any]] = None,
    requesting_agent: Optional[str] = None
) -> DirectResponseResult:
    """Query about parliamentary procedures."""
    
    responder = ParliamentaryDirectResponder()
    
    request = DirectResponseRequest(
        query=procedure_question,
        response_type=DirectResponseType.PROCEDURAL_QUERY,
        priority=ResponsePriority.NORMAL,
        constitutional_authority=ParliamentaryAuthority.SPEAKER,
        context=context or {},
        max_tokens=500,
        temperature=0.1,
        requesting_agent=requesting_agent
    )
    
    return await responder.direct_response(request)


async def urgent_parliamentary_lookup(
    lookup_query: str,
    requesting_agent: Optional[str] = None
) -> DirectResponseResult:
    """Urgent lookup for time-sensitive parliamentary information."""
    
    responder = ParliamentaryDirectResponder()
    
    request = DirectResponseRequest(
        query=lookup_query,
        response_type=DirectResponseType.QUICK_LOOKUP,
        priority=ResponsePriority.URGENT,
        max_tokens=200,
        temperature=0.0,  # Completely deterministic for lookups
        requesting_agent=requesting_agent
    )
    
    return await responder.direct_response(request)


def validate_parliamentary_action_sync(
    action_description: str,
    constitutional_authority: ParliamentaryAuthority,
    requesting_agent: Optional[str] = None
) -> DirectResponseResult:
    """Synchronous validation of parliamentary action."""
    
    responder = ParliamentaryDirectResponder()
    
    request = DirectResponseRequest(
        query=f"Validate this parliamentary action: {action_description}",
        response_type=DirectResponseType.VALIDATION,
        priority=ResponsePriority.HIGH,
        constitutional_authority=constitutional_authority,
        max_tokens=400,
        temperature=0.05,
        requesting_agent=requesting_agent
    )
    
    return responder.direct_response_sync(request)


# Example usage functions

async def example_direct_responses():
    """Example of using direct responses for parliamentary queries."""
    
    # Quick constitutional check
    constitutional_result = await quick_constitutional_check(
        "Can the government implement emergency surveillance without parliamentary approval?",
        constitutional_authority=ParliamentaryAuthority.JUDICIAL,
        requesting_agent="example_agent"
    )
    
    print(f"Constitutional Check:")
    print(f"Query: {constitutional_result.query}")
    print(f"Response: {constitutional_result.response}")
    print(f"Compliant: {constitutional_result.constitutional_compliant}")
    print(f"Confidence: {constitutional_result.confidence_score:.2f}")
    print(f"Execution Time: {constitutional_result.execution_time_seconds:.3f}s")
    
    # Parliamentary procedure query
    procedure_result = await parliamentary_procedure_query(
        "What is the correct procedure for introducing a private member's bill?",
        context={"session_type": "regular", "bill_type": "private_member"},
        requesting_agent="planner_agent"
    )
    
    print(f"\nProcedural Query:")
    print(f"Query: {procedure_result.query}")
    print(f"Response: {procedure_result.response[:200]}...")
    print(f"Confidence: {procedure_result.confidence_score:.2f}")
    
    # Urgent lookup
    urgent_result = await urgent_parliamentary_lookup(
        "Current status of Bill C-2024-001?",
        requesting_agent="status_checker"
    )
    
    print(f"\nUrgent Lookup:")
    print(f"Query: {urgent_result.query}")
    print(f"Response: {urgent_result.response}")
    print(f"Execution Time: {urgent_result.execution_time_seconds:.3f}s")
    
    # Synchronous validation
    validation_result = validate_parliamentary_action_sync(
        "Minister introducing bill without cabinet approval",
        constitutional_authority=ParliamentaryAuthority.EXECUTIVE,
        requesting_agent="validation_system"
    )
    
    print(f"\nSynchronous Validation:")
    print(f"Action: Minister introducing bill without cabinet approval")
    print(f"Valid: {validation_result.constitutional_compliant}")
    print(f"Response: {validation_result.response}")
    print(f"Confidence: {validation_result.confidence_score:.2f}")
    
    return {
        "constitutional_check": constitutional_result,
        "procedure_query": procedure_result,
        "urgent_lookup": urgent_result,
        "validation": validation_result
    }


# Global direct responder instance
parliamentary_direct_responder = ParliamentaryDirectResponder()


def get_parliamentary_direct_responder() -> ParliamentaryDirectResponder:
    """Get the global parliamentary direct responder."""
    return parliamentary_direct_responder


if __name__ == "__main__":
    asyncio.run(example_direct_responses())