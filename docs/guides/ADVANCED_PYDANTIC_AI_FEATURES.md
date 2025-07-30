# Westminster Parliamentary AI - Advanced Pydantic AI Features Guide

This comprehensive guide covers the implementation of advanced Pydantic AI features in the Westminster Parliamentary AI System, including thinking patterns, direct responses, retry logic, and multimodal input handling.

## Overview

The Westminster Parliamentary AI System now implements the complete suite of advanced Pydantic AI features:

- **🧠 Thinking Patterns**: Structured reasoning for complex constitutional analysis
- **⚡ Direct Responses**: Fast, low-overhead responses for simple parliamentary queries
- **🔄 Retry Logic**: Robust error handling with constitutional oversight
- **📁 Input Handling**: Multimodal content processing with parliamentary validation

## Architecture Components

### 1. Thinking Patterns (`triad/agents/thinking_patterns.py`)

#### Structured Constitutional Reasoning
```python
from triad.agents.thinking_patterns import create_constitutional_thinking_agent, ThinkingComplexity

# Create thinking agent for complex constitutional analysis
constitutional_agent = create_constitutional_thinking_agent(ThinkingComplexity.COMPLEX)

# Analyze complex constitutional issue with structured thinking
result = await constitutional_agent.think_through_constitutional_issue(
    issue_description="Government implementing digital surveillance without parliamentary approval",
    constitutional_context={
        "constitutional_provision": "Charter Section 8 - Unreasonable search and seizure",
        "parliamentary_context": "No legislative authorization provided",
        "precedent": "R. v. Spencer (2014) - Digital privacy expectations"
    }
)

print(f"Thinking Steps: {len(result['thinking_process']['steps'])}")
print(f"Constitutional Compliance: {result['constitutional_compliance']}")
print(f"Reasoning Quality: {result['reasoning_quality']['overall_quality']:.2f}")
```

#### Role-Specific Thinking Configurations
```python
# Different thinking patterns by constitutional role
from triad.agents.thinking_patterns import ParliamentaryThinkingAgent, ThinkingConfiguration

# Evaluator: Deep constitutional reasoning
evaluator_config = ThinkingConfiguration(
    complexity=ThinkingComplexity.COMPLEX,
    reasoning_style=ReasoningStyle.CONSTITUTIONAL,
    reasoning_effort="high",
    thinking_token_budget=2500,
    step_by_step=True
)

# Overwatch: Crisis management reasoning
overwatch_config = ThinkingConfiguration(
    complexity=ThinkingComplexity.CRITICAL,
    reasoning_style=ReasoningStyle.CRISIS,
    reasoning_effort="high",
    thinking_token_budget=3000
)
```

### 2. Direct Responses (`triad/agents/direct_responses.py`)

#### Fast Parliamentary Queries
```python
from triad.agents.direct_responses import (
    quick_constitutional_check,
    parliamentary_procedure_query,
    urgent_parliamentary_lookup
)

# Quick constitutional compliance check
constitutional_result = await quick_constitutional_check(
    "Can the government implement emergency surveillance without parliamentary approval?",
    constitutional_authority=ParliamentaryAuthority.JUDICIAL
)

print(f"Constitutional Compliant: {constitutional_result.constitutional_compliant}")
print(f"Response: {constitutional_result.response}")
print(f"Execution Time: {constitutional_result.execution_time_seconds:.3f}s")

# Parliamentary procedure query
procedure_result = await parliamentary_procedure_query(
    "What is the correct procedure for introducing a private member's bill?",
    context={"session_type": "regular", "bill_type": "private_member"}
)

# Urgent lookup with fastest model selection
urgent_result = await urgent_parliamentary_lookup(
    "Current status of Bill C-2024-001?"
)
```

#### Model Selection by Priority
```python
from triad.agents.direct_responses import DirectResponseRequest, ResponsePriority

# System automatically selects fastest models for urgent requests
urgent_request = DirectResponseRequest(
    query="Constitutional crisis - need immediate guidance",
    response_type=DirectResponseType.CONSTITUTIONAL_CHECK,
    priority=ResponsePriority.URGENT,  # Uses fastest available model
    max_tokens=200,
    temperature=0.0
)

# Balanced speed/quality for normal requests
normal_request = DirectResponseRequest(
    query="Analyze policy implications of proposed legislation",
    response_type=DirectResponseType.SIMPLE_ANALYSIS,
    priority=ResponsePriority.NORMAL,  # Uses best available model
    max_tokens=500,
    temperature=0.1
)
```

### 3. Retry Patterns (`triad/agents/retry_patterns.py`)

#### Constitutional-Aware Retry Logic
```python
from triad.agents.retry_patterns import (
    parliamentary_retry,
    RetryCategory,
    RetryPriority,
    get_parliamentary_retry_manager
)

# Decorator-based retry for parliamentary operations
@parliamentary_retry(
    category=RetryCategory.CONSTITUTIONAL_ANALYSIS,
    priority=RetryPriority.HIGH,
    constitutional_authority=ParliamentaryAuthority.JUDICIAL
)
async def analyze_constitutional_compliance(bill_text: str) -> str:
    """Constitutional analysis with automatic retry on failure."""
    # Analysis logic here - automatically retried on network/model errors
    return "Constitutional analysis complete"

# Manual retry with full control
retry_manager = get_parliamentary_retry_manager()

result = await retry_manager.retry_with_parliamentary_oversight(
    operation=complex_constitutional_analysis,
    category=RetryCategory.CRISIS_MANAGEMENT,
    priority=RetryPriority.CRITICAL,  # Aggressive retries for crises
    constitutional_authority=ParliamentaryAuthority.CROWN,
    bill_data=bill_data
)

if result.success:
    print(f"Analysis completed after {result.total_attempts} attempts")
else:
    print(f"Analysis failed: {result.final_exception}")
```

#### Priority-Based Retry Configuration
```python
# Different retry behaviors by priority and category
from triad.agents.retry_patterns import RetryConfiguration

# Crisis management: Aggressive retries with fast initial retry
crisis_config = RetryConfiguration(
    category=RetryCategory.CRISIS_MANAGEMENT,
    priority=RetryPriority.CRITICAL,
    max_attempts=7,           # More attempts for critical operations
    base_wait_seconds=0.5,    # Faster initial retry
    max_wait_seconds=60.0,    # But don't wait too long
    exponential_multiplier=1.5, # Gentler backoff
    constitutional_validation=True
)

# Routine queries: Conservative retries
routine_config = RetryConfiguration(
    category=RetryCategory.ROUTINE_QUERY,
    priority=RetryPriority.LOW,
    max_attempts=3,
    base_wait_seconds=1.0,
    max_wait_seconds=30.0,
    constitutional_validation=False  # Less overhead for routine tasks
)
```

### 4. Input Handling (`triad/agents/input_handling.py`)

#### Multimodal Parliamentary Content
```python
from triad.agents.input_handling import (
    ParliamentaryInput,
    InputType,
    ParliamentaryContentType,
    analyze_bill_text,
    analyze_parliamentary_document,
    analyze_debate_audio
)

# Analyze bill text
bill_analysis = await analyze_bill_text(
    bill_text="An Act to establish digital privacy protections...",
    bill_title="Digital Privacy Protection Act",
    constitutional_authority=ParliamentaryAuthority.LEGISLATIVE
)

# Analyze parliamentary document (PDF, DOCX, etc.)
document_analysis = await analyze_parliamentary_document(
    document_path=Path("committee_report.pdf"),
    content_type=ParliamentaryContentType.COMMITTEE_REPORT,
    constitutional_authority=ParliamentaryAuthority.LEGISLATIVE
)

# Analyze parliamentary debate audio
debate_analysis = await analyze_debate_audio(
    audio_url="https://parliament.ca/debates/audio/session_123.mp3",
    debate_title="Question Period - Digital Privacy Act",
    constitutional_authority=ParliamentaryAuthority.SPEAKER
)
```

#### Security Classification and Validation
```python
from triad.agents.input_handling import SecurityClassification, ParliamentaryInputHandler

handler = ParliamentaryInputHandler()

# Input with security classification
classified_input = ParliamentaryInput(
    content="Confidential government policy document...",
    input_type=InputType.TEXT,
    content_type=ParliamentaryContentType.GOVERNMENT_DOCUMENT,
    security_classification=SecurityClassification.CONFIDENTIAL,
    constitutional_authority=ParliamentaryAuthority.EXECUTIVE
)

# Validate security clearance and constitutional compliance
validation_result = await handler.validate_parliamentary_input(
    classified_input,
    constitutional_authority=ParliamentaryAuthority.CROWN  # Has sufficient clearance
)

print(f"Security Cleared: {validation_result.security_cleared}")
print(f"Constitutional Compliant: {validation_result.constitutional_compliance}")
```

## Integration Examples

### 1. Complete Constitutional Analysis Pipeline

```python
from triad.agents.thinking_patterns import create_constitutional_thinking_agent
from triad.agents.retry_patterns import parliamentary_retry
from triad.agents.input_handling import analyze_bill_text
from triad.agents.direct_responses import quick_constitutional_check

@parliamentary_retry(
    category=RetryCategory.CONSTITUTIONAL_ANALYSIS,
    priority=RetryPriority.HIGH
)
async def comprehensive_constitutional_analysis(bill_text: str, bill_title: str):
    """Complete constitutional analysis with all advanced features."""
    
    # Step 1: Quick constitutional check for immediate feedback
    quick_check = await quick_constitutional_check(
        f"Is the {bill_title} constitutionally compliant at first glance?",
        constitutional_authority=ParliamentaryAuthority.JUDICIAL
    )
    
    # Step 2: Detailed input validation and analysis
    detailed_analysis = await analyze_bill_text(
        bill_text=bill_text,
        bill_title=bill_title,
        constitutional_authority=ParliamentaryAuthority.LEGISLATIVE
    )
    
    # Step 3: Deep thinking analysis for complex issues
    if not quick_check.constitutional_compliant:
        thinking_agent = create_constitutional_thinking_agent(ThinkingComplexity.COMPLEX)
        
        deep_analysis = await thinking_agent.think_through_constitutional_issue(
            issue_description=f"Constitutional concerns with {bill_title}",
            constitutional_context={
                "bill_text": bill_text,
                "quick_check_result": quick_check.response,
                "detailed_analysis": detailed_analysis['analysis_result']
            }
        )
        
        return {
            "quick_check": quick_check,
            "detailed_analysis": detailed_analysis,
            "deep_thinking": deep_analysis,
            "final_recommendation": deep_analysis['conclusion'],
            "constitutional_compliant": deep_analysis['constitutional_compliance']
        }
    
    return {
        "quick_check": quick_check, 
        "detailed_analysis": detailed_analysis,
        "constitutional_compliant": True
    }

# Execute with automatic retry on failures
result = await comprehensive_constitutional_analysis(
    bill_text="Sample bill text...",
    bill_title="Digital Rights Protection Act"
)
```

### 2. Multi-Priority Parliamentary Session

```python
async def handle_parliamentary_session():
    """Handle different priority parliamentary tasks appropriately."""
    
    # Critical: Constitutional crisis - use thinking + aggressive retries
    crisis_agent = create_crisis_thinking_agent()
    
    @parliamentary_retry(
        category=RetryCategory.CRISIS_MANAGEMENT,
        priority=RetryPriority.CRITICAL
    )
    async def handle_crisis():
        return await crisis_agent.think_through_constitutional_issue(
            issue_description="Government lost confidence vote but refused to resign",
            constitutional_context={"severity": "constitutional_crisis"}
        )
    
    # High Priority: Important bill analysis - use structured thinking
    constitutional_agent = create_constitutional_thinking_agent(ThinkingComplexity.COMPLEX)
    
    # Normal Priority: Parliamentary procedures - use direct responses  
    procedure_response = await parliamentary_procedure_query(
        "What is the deadline for committee report submission?",
        context={"bill_id": "C-2024-001", "committee": "Justice"}
    )
    
    # Low Priority: Status updates - use fastest direct responses
    status_update = await urgent_parliamentary_lookup(
        "Current status of all active bills?"
    )
    
    return {
        "crisis_handled": await handle_crisis(),
        "procedure_guidance": procedure_response,
        "status_update": status_update
    }
```

### 3. Multimodal Parliamentary Analysis

```python
async def comprehensive_multimodal_analysis():
    """Analyze different types of parliamentary content."""
    
    handler = get_parliamentary_input_handler()
    
    # Text analysis with thinking
    bill_input = ParliamentaryInput(
        content="An Act respecting artificial intelligence governance...",
        input_type=InputType.TEXT,
        content_type=ParliamentaryContentType.BILL_TEXT,
        title="AI Governance Act",
        security_classification=SecurityClassification.PROTECTED_A
    )
    
    # Document analysis with retry
    @parliamentary_retry(RetryCategory.PARLIAMENTARY_PROCEDURE, RetryPriority.NORMAL)
    async def analyze_committee_report():
        return await handler.analyze_parliamentary_content(
            input_data=ParliamentaryInput(
                content=Path("committee_report.pdf").read_bytes(),
                input_type=InputType.DOCUMENT,
                content_type=ParliamentaryContentType.COMMITTEE_REPORT,
                title="AI Governance Committee Report"
            ),
            analysis_instructions="Summarize key findings and recommendations",
            constitutional_authority=ParliamentaryAuthority.LEGISLATIVE
        )
    
    # Audio analysis with validation
    debate_audio = ParliamentaryInput(
        content="https://parliament.ca/debates/ai_governance_debate.mp3",
        input_type=InputType.AUDIO,
        content_type=ParliamentaryContentType.PARLIAMENTARY_DEBATE,
        title="AI Governance Debate - Question Period"
    )
    
    # Execute all analyses
    bill_analysis = await handler.analyze_parliamentary_content(
        bill_input,
        "Analyze constitutional implications and policy effectiveness",
        ParliamentaryAuthority.LEGISLATIVE
    )
    
    committee_analysis = await analyze_committee_report()
    
    debate_analysis = await handler.analyze_parliamentary_content(
        debate_audio,
        "Transcribe and analyze key arguments and procedural compliance",
        ParliamentaryAuthority.SPEAKER
    )
    
    return {
        "bill_analysis": bill_analysis,
        "committee_analysis": committee_analysis, 
        "debate_analysis": debate_analysis
    }
```

## Performance Optimization

### Model Selection Strategy

The system automatically selects optimal models based on:

1. **Task Priority**: 
   - URGENT → Fastest models (Groq, GPT-3.5-turbo, Claude Haiku)
   - HIGH → Balanced models (GPT-4o-mini, Claude Sonnet)
   - NORMAL → Best models (GPT-4o, Claude Sonnet, Gemini Pro)

2. **Task Complexity**:
   - Simple queries → Direct responses with fast models
   - Complex analysis → Thinking patterns with reasoning models
   - Multimodal content → Multimodal-capable models

3. **Constitutional Authority**:
   - Crown authority → Most powerful models for crisis management
   - Judicial authority → Most accurate models for constitutional analysis
   - Legislative/Executive → Balanced models for general work

### Caching and Efficiency

```python
# Direct responses include intelligent caching
from triad.agents.direct_responses import ParliamentaryDirectResponder

responder = ParliamentaryDirectResponder()

# Identical requests within 5 minutes use cached results
result1 = await responder.direct_response(request)  # Executes model call
result2 = await responder.direct_response(request)  # Uses cache

# Retry patterns include exponential backoff to avoid overwhelming services
# Input validation prevents unnecessary processing of invalid content
```

## Monitoring and Analytics

### Comprehensive Statistics

```python
# Thinking pattern quality assessment
thinking_agent = create_constitutional_thinking_agent()
result = await thinking_agent.think_through_constitutional_issue(...)

print(f"Reasoning Quality: {result['reasoning_quality']['overall_quality']:.2f}")
print(f"Constitutional Depth: {result['reasoning_quality']['constitutional_depth']:.2f}")
print(f"Improvement Suggestions: {result['reasoning_quality']['improvement_suggestions']}")

# Retry statistics monitoring
retry_manager = get_parliamentary_retry_manager()
stats = retry_manager.get_retry_statistics()

print(f"Success Rate: {stats['successful_operations'] / stats['total_operations']:.2%}")
print(f"Average Attempts: {stats['average_attempts']:.1f}")
print(f"Average Time: {stats['average_time_seconds']:.2f}s")

# Direct response performance
print(f"Response Time: {direct_result.execution_time_seconds:.3f}s")
print(f"Confidence Score: {direct_result.confidence_score:.2f}")
print(f"Model Used: {direct_result.model_used}")
```

### Constitutional Compliance Tracking

```python
# All features include constitutional compliance tracking
constitutional_metrics = {
    "thinking_analysis": result['constitutional_compliance'],
    "direct_responses": direct_result.constitutional_compliant,
    "retry_operations": retry_result.constitutional_compliance,
    "input_validation": validation_result.constitutional_compliance
}

# Comprehensive constitutional dashboard data
compliance_rate = sum(constitutional_metrics.values()) / len(constitutional_metrics)
print(f"Overall Constitutional Compliance: {compliance_rate:.1%}")
```

## Best Practices

### 1. Feature Selection Guidelines

- **Use Thinking Patterns** for:
  - Complex constitutional analysis
  - Multi-step reasoning requirements
  - Crisis management scenarios
  - High-stakes decisions requiring transparent reasoning

- **Use Direct Responses** for:
  - Simple factual queries
  - Status checks and lookups
  - Time-sensitive information requests
  - High-volume, low-complexity tasks

- **Use Retry Logic** for:
  - Network-dependent operations
  - Critical constitutional processes
  - External service integrations
  - Operations requiring high reliability

- **Use Input Handling** for:
  - Multimodal parliamentary content
  - Security-classified documents
  - Large document processing
  - Content validation requirements

### 2. Constitutional Compliance

- Always validate input security classifications
- Include constitutional context in analysis requests
- Use appropriate constitutional authority for operations
- Maintain audit trails for all constitutional decisions
- Implement proper separation of powers in tool usage

### 3. Performance Optimization

- Match task complexity to feature sophistication
- Use direct responses for simple, frequent queries
- Implement proper caching strategies
- Monitor and optimize retry configurations
- Balance thoroughness with response time requirements

The Westminster Parliamentary AI System now provides the most comprehensive implementation of Pydantic AI features while maintaining constitutional principles, democratic accountability, and Westminster parliamentary traditions. These advanced features enable sophisticated AI-assisted governance with proper oversight, validation, and reliability.