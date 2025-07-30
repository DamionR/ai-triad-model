"""
Thinking Patterns for Westminster Parliamentary AI System

Implements Pydantic AI thinking patterns for complex constitutional reasoning,
parliamentary analysis, and structured decision-making processes.
"""

import asyncio
from typing import Dict, List, Optional, Any, Union, Type
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass
import logfire
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models import ModelSettings
from pydantic_ai.models.openai import OpenAIModel, OpenAIModelSettings
from pydantic_ai.models.anthropic import AnthropicModel, AnthropicModelSettings
from pydantic_ai.models.groq import GroqModel, GroqModelSettings

from triad.models.model_config import ParliamentaryRole, get_model_config
from triad.agents.enhanced_agents import EnhancedParliamentaryDeps
from triad.tools.parliamentary_toolsets import ParliamentaryAuthority
from triad.core.logging import get_logfire_config


class ThinkingComplexity(Enum):
    """Complexity levels for thinking patterns."""
    SIMPLE = "simple"           # Basic parliamentary procedures
    MODERATE = "moderate"       # Standard constitutional analysis
    COMPLEX = "complex"         # Multi-faceted constitutional issues
    CRITICAL = "critical"       # Constitutional crises requiring deep reasoning


class ReasoningStyle(Enum):
    """Styles of reasoning for parliamentary thinking."""
    CONSTITUTIONAL = "constitutional"     # Constitutional law reasoning
    PROCEDURAL = "procedural"            # Parliamentary procedure reasoning
    POLICY = "policy"                    # Policy analysis reasoning
    CRISIS = "crisis"                    # Crisis management reasoning
    SYNTHESIS = "synthesis"              # Multi-perspective synthesis


@dataclass
class ThinkingConfiguration:
    """Configuration for thinking patterns based on task complexity."""
    complexity: ThinkingComplexity
    reasoning_style: ReasoningStyle
    thinking_enabled: bool = True
    reasoning_effort: str = "medium"     # low, medium, high for OpenAI
    reasoning_summary: str = "detailed"  # brief, detailed for OpenAI
    thinking_token_budget: int = 2000    # For Anthropic
    thinking_format: str = "parsed"      # raw, hidden, parsed for Groq
    step_by_step: bool = True
    show_reasoning: bool = True


class ParliamentaryThinkingAgent:
    """
    Parliamentary agent with enhanced thinking capabilities.
    
    Implements structured thinking patterns for constitutional analysis,
    parliamentary procedures, and complex decision-making processes.
    """
    
    def __init__(
        self,
        role: ParliamentaryRole,
        agent_id: Optional[str] = None,
        thinking_config: Optional[ThinkingConfiguration] = None
    ):
        self.role = role
        self.agent_id = agent_id or f"thinking_{role.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.logger = get_logfire_config()
        self.model_config = get_model_config()
        
        # Default thinking configuration based on role
        self.thinking_config = thinking_config or self._get_default_thinking_config(role)
        
        # Create thinking-enabled agent
        self.agent = self._create_thinking_agent()
        
        # Enhanced dependencies
        self.deps = EnhancedParliamentaryDeps(
            agent_id=self.agent_id,
            constitutional_authority=self._role_to_authority(role),
            parliamentary_role=role
        )
    
    def _role_to_authority(self, role: ParliamentaryRole) -> ParliamentaryAuthority:
        """Convert parliamentary role to constitutional authority."""
        authority_map = {
            ParliamentaryRole.PLANNER: ParliamentaryAuthority.LEGISLATIVE,
            ParliamentaryRole.EXECUTOR: ParliamentaryAuthority.EXECUTIVE,
            ParliamentaryRole.EVALUATOR: ParliamentaryAuthority.JUDICIAL,
            ParliamentaryRole.OVERWATCH: ParliamentaryAuthority.CROWN,
            ParliamentaryRole.SPEAKER: ParliamentaryAuthority.SPEAKER,
            ParliamentaryRole.CLERK: ParliamentaryAuthority.CLERK
        }
        return authority_map[role]
    
    def _get_default_thinking_config(self, role: ParliamentaryRole) -> ThinkingConfiguration:
        """Get default thinking configuration for parliamentary role."""
        
        role_configs = {
            ParliamentaryRole.PLANNER: ThinkingConfiguration(
                complexity=ThinkingComplexity.MODERATE,
                reasoning_style=ReasoningStyle.POLICY,
                reasoning_effort="medium",
                thinking_token_budget=1500,
                step_by_step=True
            ),
            ParliamentaryRole.EXECUTOR: ThinkingConfiguration(
                complexity=ThinkingComplexity.MODERATE,
                reasoning_style=ReasoningStyle.PROCEDURAL,
                reasoning_effort="medium",
                thinking_token_budget=1200,
                step_by_step=True
            ),
            ParliamentaryRole.EVALUATOR: ThinkingConfiguration(
                complexity=ThinkingComplexity.COMPLEX,
                reasoning_style=ReasoningStyle.CONSTITUTIONAL,
                reasoning_effort="high",
                reasoning_summary="detailed",
                thinking_token_budget=2500,
                step_by_step=True,
                show_reasoning=True
            ),
            ParliamentaryRole.OVERWATCH: ThinkingConfiguration(
                complexity=ThinkingComplexity.CRITICAL,
                reasoning_style=ReasoningStyle.CRISIS,
                reasoning_effort="high",
                reasoning_summary="detailed",
                thinking_token_budget=3000,
                step_by_step=True,
                show_reasoning=True
            ),
            ParliamentaryRole.SPEAKER: ThinkingConfiguration(
                complexity=ThinkingComplexity.SIMPLE,
                reasoning_style=ReasoningStyle.PROCEDURAL,
                reasoning_effort="low",
                thinking_token_budget=800,
                step_by_step=False
            ),
            ParliamentaryRole.CLERK: ThinkingConfiguration(
                complexity=ThinkingComplexity.SIMPLE,
                reasoning_style=ReasoningStyle.PROCEDURAL,
                reasoning_effort="low",
                thinking_token_budget=600,
                step_by_step=False
            )
        }
        
        return role_configs.get(role, ThinkingConfiguration(
            complexity=ThinkingComplexity.MODERATE,
            reasoning_style=ReasoningStyle.CONSTITUTIONAL
        ))
    
    def _create_thinking_agent(self) -> Agent:
        """Create agent with thinking capabilities configured."""
        
        # Get enabled providers
        enabled_providers = self.model_config.get_enabled_providers()
        
        if not enabled_providers:
            raise ValueError("No AI providers enabled for thinking agent")
        
        # Prefer providers with good thinking support
        thinking_priority = ["openai", "anthropic", "groq", "gemini"]
        selected_provider = None
        
        for provider in thinking_priority:
            if provider in enabled_providers:
                selected_provider = provider
                break
        
        if not selected_provider:
            selected_provider = enabled_providers[0]
        
        # Configure model with thinking settings
        if selected_provider == "openai":
            # OpenAI reasoning model configuration
            model_settings = OpenAIModelSettings(
                openai_reasoning_effort=self.thinking_config.reasoning_effort,
                openai_reasoning_summary=self.thinking_config.reasoning_summary
            )
            
            # Use reasoning model if available
            model_name = "o1-mini"  # Or other reasoning model
            fallback_model = self.model_config.create_fallback_model([selected_provider])
            
        elif selected_provider == "anthropic":
            # Anthropic thinking configuration
            model_settings = AnthropicModelSettings(
                thinking_budget=self.thinking_config.thinking_token_budget
            )
            fallback_model = self.model_config.create_fallback_model([selected_provider])
            
        elif selected_provider == "groq":
            # Groq thinking configuration
            model_settings = GroqModelSettings(
                groq_reasoning_format=self.thinking_config.thinking_format
            )
            fallback_model = self.model_config.create_fallback_model([selected_provider])
            
        else:
            # Fallback configuration
            model_settings = ModelSettings(
                temperature=0.1 if self.thinking_config.complexity == ThinkingComplexity.CRITICAL else 0.3,
                max_tokens=4096
            )
            fallback_model = self.model_config.create_fallback_model([selected_provider])
        
        # Create system prompt for thinking
        system_prompt = self._create_thinking_system_prompt()
        
        # Create agent with thinking configuration
        agent = Agent(
            model=fallback_model,
            system_prompt=system_prompt,
            model_settings=model_settings
        )
        
        return agent
    
    def _create_thinking_system_prompt(self) -> str:
        """Create system prompt that encourages structured thinking."""
        
        base_prompt = f"""You are the {self.role.value} agent in the Westminster Parliamentary AI System, 
serving as the {self._role_to_authority(self.role).value} constitutional authority.

THINKING INSTRUCTIONS:
When analyzing complex issues, use structured thinking to break down problems step-by-step:

1. CONSTITUTIONAL FRAMEWORK: Consider relevant constitutional principles and Westminster conventions
2. FACTUAL ANALYSIS: Examine the facts and evidence objectively
3. LEGAL/PROCEDURAL REVIEW: Apply relevant laws, precedents, and parliamentary procedures
4. STAKEHOLDER IMPACT: Consider effects on different parties and institutions
5. OPTIONS EVALUATION: Analyze different possible approaches and their consequences
6. RECOMMENDATION: Provide clear, actionable recommendations with constitutional basis

"""
        
        # Add role-specific thinking guidance
        if self.role == ParliamentaryRole.EVALUATOR:
            base_prompt += """
CONSTITUTIONAL REASONING FOCUS:
- Apply Charter of Rights and Freedoms analysis
- Consider constitutional precedents and case law
- Evaluate separation of powers implications
- Assess rule of law compliance
- Use strict constitutional interpretation methodology

When reasoning through constitutional issues:
<think>
1. Identify the constitutional question
2. Review relevant constitutional provisions
3. Apply constitutional interpretation principles
4. Consider precedent cases
5. Analyze constitutional compliance
6. Formulate constitutional conclusion
</think>
"""
        
        elif self.role == ParliamentaryRole.OVERWATCH:
            base_prompt += """
CRISIS REASONING FOCUS:
- Assess threats to constitutional order
- Consider Crown prerogative powers
- Evaluate need for emergency measures
- Balance democratic principles with stability
- Apply constitutional safeguards

When reasoning through crises:
<think>
1. Assess crisis severity and constitutional implications
2. Review available constitutional powers and remedies
3. Consider democratic accountability requirements
4. Evaluate proportionality of response
5. Plan constitutional restoration measures
6. Formulate crisis response strategy
</think>
"""
        
        elif self.role == ParliamentaryRole.PLANNER:
            base_prompt += """
POLICY REASONING FOCUS:
- Analyze policy effectiveness and feasibility
- Consider democratic representation and accountability
- Evaluate constitutional compliance of proposals
- Assess implementation requirements and challenges
- Balance competing interests and values

When reasoning through policy issues:
<think>
1. Define policy problem and objectives
2. Analyze stakeholder interests and impacts
3. Evaluate policy options and trade-offs
4. Assess constitutional and legal requirements
5. Consider implementation feasibility
6. Formulate policy recommendations
</think>
"""
        
        elif self.role == ParliamentaryRole.EXECUTOR:
            base_prompt += """
IMPLEMENTATION REASONING FOCUS:
- Assess practical implementation requirements
- Consider resource allocation and management
- Evaluate administrative feasibility
- Balance efficiency with accountability
- Ensure constitutional compliance in execution

When reasoning through implementation issues:
<think>
1. Analyze implementation requirements and constraints
2. Assess available resources and capabilities
3. Identify potential challenges and risks
4. Develop implementation strategy and timeline
5. Plan accountability and oversight mechanisms
6. Formulate implementation recommendations
</think>
"""
        
        base_prompt += f"""

REASONING COMPLEXITY: {self.thinking_config.complexity.value}
REASONING STYLE: {self.thinking_config.reasoning_style.value}

Always maintain:
- Constitutional accountability and transparency
- Westminster parliamentary principles
- Democratic values and rule of law
- Separation of powers respect
- Institutional integrity
"""
        
        return base_prompt
    
    async def think_through_constitutional_issue(
        self,
        issue_description: str,
        constitutional_context: Dict[str, Any],
        thinking_override: Optional[ThinkingConfiguration] = None
    ) -> Dict[str, Any]:
        """
        Use structured thinking to analyze complex constitutional issues.
        
        Args:
            issue_description: Description of the constitutional issue
            constitutional_context: Relevant constitutional context and background
            thinking_override: Optional override for thinking configuration
        
        Returns:
            Structured thinking results with reasoning and conclusions
        """
        
        # Use override config if provided
        config = thinking_override or self.thinking_config
        
        try:
            with self.logger.parliamentary_session_span(
                f"constitutional-thinking-{self.role.value}",
                [self.agent_id]
            ) as span:
                
                # Create structured thinking prompt
                thinking_prompt = self._create_constitutional_thinking_prompt(
                    issue_description, constitutional_context, config
                )
                
                # Execute with thinking enabled
                start_time = datetime.now(timezone.utc)
                
                result = await self.agent.run(
                    thinking_prompt,
                    deps=self.deps
                )
                
                execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
                
                # Extract thinking process if available
                thinking_process = self._extract_thinking_process(result)
                
                # Create structured response
                thinking_result = {
                    "issue": issue_description,
                    "constitutional_authority": self._role_to_authority(self.role).value,
                    "reasoning_style": config.reasoning_style.value,
                    "complexity": config.complexity.value,
                    "thinking_process": thinking_process,
                    "conclusion": str(result.data),
                    "constitutional_compliance": True,  # Would validate this
                    "reasoning_quality": self._assess_reasoning_quality(result, thinking_process),
                    "execution_time_seconds": execution_time,
                    "analyzed_by": self.agent_id,
                    "analysis_timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                # Log constitutional thinking
                self.logger.log_constitutional_event(
                    event="constitutional_thinking_completed",
                    authority=self._role_to_authority(self.role).value,
                    details={
                        "issue_type": "constitutional_analysis",
                        "reasoning_style": config.reasoning_style.value,
                        "complexity": config.complexity.value,
                        "execution_time": execution_time,
                        "thinking_steps": len(thinking_process.get("steps", []))
                    }
                )
                
                span.set_attribute("thinking.complexity", config.complexity.value)
                span.set_attribute("thinking.style", config.reasoning_style.value)
                span.set_attribute("thinking.execution_time", execution_time)
                span.set_attribute("thinking.steps_count", len(thinking_process.get("steps", [])))
                
                return thinking_result
                
        except Exception as e:
            self.logger.log_constitutional_event(
                event="constitutional_thinking_error",
                authority=self._role_to_authority(self.role).value,
                details={
                    "error": str(e),
                    "issue": issue_description
                }
            )
            raise
    
    def _create_constitutional_thinking_prompt(
        self,
        issue_description: str,
        constitutional_context: Dict[str, Any],
        config: ThinkingConfiguration
    ) -> str:
        """Create a prompt that encourages structured constitutional thinking."""
        
        prompt = f"""
CONSTITUTIONAL ANALYSIS REQUEST

Issue to Analyze: {issue_description}

Constitutional Context:
"""
        
        for key, value in constitutional_context.items():
            prompt += f"- {key}: {value}\n"
        
        prompt += f"""

THINKING REQUIREMENTS:
- Complexity Level: {config.complexity.value}
- Reasoning Style: {config.reasoning_style.value}
- Constitutional Authority: {self._role_to_authority(self.role).value}

"""
        
        if config.step_by_step:
            prompt += """
Please work through this constitutional issue step-by-step using structured thinking:

<think>
Step 1: Constitutional Framework Analysis
- What constitutional principles apply?
- Which provisions of the Constitution are relevant?
- What Westminster conventions are applicable?

Step 2: Legal and Precedent Review
- What legal precedents exist?
- How do existing court decisions apply?
- What parliamentary precedents are relevant?

Step 3: Stakeholder and Impact Analysis
- Who are the affected parties?
- What are the democratic implications?
- How does this affect institutional relationships?

Step 4: Options and Consequences Evaluation
- What are the possible approaches?
- What are the constitutional implications of each option?
- What are the risks and benefits?

Step 5: Constitutional Compliance Assessment
- Does each option comply with the Constitution?
- Are there any Charter rights implications?
- Does this maintain separation of powers?

Step 6: Recommendation Formulation
- What is the constitutionally sound approach?
- What safeguards are needed?
- How should this be implemented?
</think>

After your structured thinking, provide your constitutional analysis and recommendations.
"""
        
        else:
            prompt += """
Please analyze this constitutional issue using your expertise and provide:

1. Constitutional assessment
2. Legal and procedural implications
3. Recommendations for resolution
4. Any constitutional safeguards needed

Ensure your analysis maintains constitutional accountability and Westminster principles.
"""
        
        return prompt
    
    def _extract_thinking_process(self, result: Any) -> Dict[str, Any]:
        """Extract structured thinking process from agent result."""
        
        thinking_process = {
            "steps": [],
            "reasoning_chain": [],
            "constitutional_considerations": [],
            "precedents_considered": [],
            "conclusion_basis": ""
        }
        
        # Check if result has thinking parts (varies by model)
        if hasattr(result, 'thinking') and result.thinking:
            thinking_process["raw_thinking"] = str(result.thinking)
            
            # Parse thinking steps from the thinking content
            thinking_content = str(result.thinking)
            
            # Extract steps (this would be more sophisticated in practice)
            if "Step 1:" in thinking_content:
                steps = []
                for i in range(1, 7):  # Up to 6 steps
                    step_marker = f"Step {i}:"
                    if step_marker in thinking_content:
                        # Extract step content (simplified)
                        step_start = thinking_content.find(step_marker)
                        step_end = thinking_content.find(f"Step {i+1}:", step_start)
                        if step_end == -1:
                            step_end = len(thinking_content)
                        
                        step_content = thinking_content[step_start:step_end].strip()
                        steps.append({
                            "step_number": i,
                            "description": step_content[:100] + "..." if len(step_content) > 100 else step_content,
                            "full_content": step_content
                        })
                
                thinking_process["steps"] = steps
        
        # Extract constitutional considerations from the response
        response_text = str(result.data)
        
        if "constitutional" in response_text.lower():
            thinking_process["constitutional_considerations"].append("Constitutional analysis performed")
        
        if "precedent" in response_text.lower():
            thinking_process["precedents_considered"].append("Legal precedents considered")
        
        if "charter" in response_text.lower():
            thinking_process["constitutional_considerations"].append("Charter rights analyzed")
        
        return thinking_process
    
    def _assess_reasoning_quality(self, result: Any, thinking_process: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the quality of the reasoning process."""
        
        quality_assessment = {
            "completeness": 0.0,  # 0-1 scale
            "constitutional_depth": 0.0,
            "logical_consistency": 0.0,
            "precedent_usage": 0.0,
            "overall_quality": 0.0,
            "improvement_suggestions": []
        }
        
        # Assess completeness based on thinking steps
        steps_count = len(thinking_process.get("steps", []))
        if steps_count >= 5:
            quality_assessment["completeness"] = 1.0
        elif steps_count >= 3:
            quality_assessment["completeness"] = 0.7
        elif steps_count >= 1:
            quality_assessment["completeness"] = 0.4
        else:
            quality_assessment["completeness"] = 0.1
        
        # Assess constitutional depth
        constitutional_considerations = len(thinking_process.get("constitutional_considerations", []))
        if constitutional_considerations >= 3:
            quality_assessment["constitutional_depth"] = 1.0
        elif constitutional_considerations >= 2:
            quality_assessment["constitutional_depth"] = 0.7
        elif constitutional_considerations >= 1:
            quality_assessment["constitutional_depth"] = 0.4
        else:
            quality_assessment["constitutional_depth"] = 0.1
        
        # Assess precedent usage
        precedents = len(thinking_process.get("precedents_considered", []))
        if precedents >= 2:
            quality_assessment["precedent_usage"] = 1.0
        elif precedents >= 1:
            quality_assessment["precedent_usage"] = 0.6
        else:
            quality_assessment["precedent_usage"] = 0.2
        
        # Simple logical consistency check (would be more sophisticated)
        response_text = str(result.data).lower()
        if "therefore" in response_text or "because" in response_text or "consequently" in response_text:
            quality_assessment["logical_consistency"] = 0.8
        else:
            quality_assessment["logical_consistency"] = 0.5
        
        # Calculate overall quality
        quality_assessment["overall_quality"] = (
            quality_assessment["completeness"] * 0.3 +
            quality_assessment["constitutional_depth"] * 0.3 +
            quality_assessment["logical_consistency"] * 0.2 +
            quality_assessment["precedent_usage"] * 0.2
        )
        
        # Generate improvement suggestions
        if quality_assessment["completeness"] < 0.7:
            quality_assessment["improvement_suggestions"].append("Consider more comprehensive step-by-step analysis")
        
        if quality_assessment["constitutional_depth"] < 0.7:
            quality_assessment["improvement_suggestions"].append("Include more constitutional principles and considerations")
        
        if quality_assessment["precedent_usage"] < 0.6:
            quality_assessment["improvement_suggestions"].append("Reference more legal precedents and case law")
        
        return quality_assessment
    
    async def quick_constitutional_check(
        self,
        question: str,
        minimal_thinking: bool = True
    ) -> Dict[str, Any]:
        """
        Perform a quick constitutional check with minimal thinking overhead.
        
        Used for simple constitutional questions that don't require deep analysis.
        """
        
        # Override to simple thinking for quick checks
        quick_config = ThinkingConfiguration(
            complexity=ThinkingComplexity.SIMPLE,
            reasoning_style=ReasoningStyle.CONSTITUTIONAL,
            reasoning_effort="low",
            thinking_token_budget=500,
            step_by_step=False,
            show_reasoning=minimal_thinking
        )
        
        try:
            quick_prompt = f"""
QUICK CONSTITUTIONAL CHECK

Question: {question}

Provide a brief constitutional assessment focusing on:
1. Constitutional compliance (Yes/No with brief reason)
2. Relevant constitutional principle
3. Any immediate concerns

Keep response concise and focused.
"""
            
            result = await self.agent.run(quick_prompt, deps=self.deps)
            
            return {
                "question": question,
                "constitutional_compliance": "compliant" in str(result.data).lower(),
                "quick_assessment": str(result.data),
                "response_type": "quick_check",
                "analyzed_by": self.agent_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.log_constitutional_event(
                event="quick_constitutional_check_error",
                authority=self._role_to_authority(self.role).value,
                details={"error": str(e), "question": question}
            )
            raise


# Factory functions for creating thinking agents

def create_constitutional_thinking_agent(
    complexity: ThinkingComplexity = ThinkingComplexity.COMPLEX
) -> ParliamentaryThinkingAgent:
    """Create a thinking agent specialized for constitutional analysis."""
    
    config = ThinkingConfiguration(
        complexity=complexity,
        reasoning_style=ReasoningStyle.CONSTITUTIONAL,
        reasoning_effort="high",
        reasoning_summary="detailed",
        thinking_token_budget=2500,
        step_by_step=True,
        show_reasoning=True
    )
    
    return ParliamentaryThinkingAgent(
        role=ParliamentaryRole.EVALUATOR,
        thinking_config=config
    )


def create_crisis_thinking_agent() -> ParliamentaryThinkingAgent:
    """Create a thinking agent specialized for constitutional crisis management."""
    
    config = ThinkingConfiguration(
        complexity=ThinkingComplexity.CRITICAL,
        reasoning_style=ReasoningStyle.CRISIS,
        reasoning_effort="high",
        reasoning_summary="detailed",
        thinking_token_budget=3000,
        step_by_step=True,
        show_reasoning=True
    )
    
    return ParliamentaryThinkingAgent(
        role=ParliamentaryRole.OVERWATCH,
        thinking_config=config
    )


def create_policy_thinking_agent() -> ParliamentaryThinkingAgent:
    """Create a thinking agent specialized for policy analysis."""
    
    config = ThinkingConfiguration(
        complexity=ThinkingComplexity.MODERATE,
        reasoning_style=ReasoningStyle.POLICY,
        reasoning_effort="medium",
        thinking_token_budget=1800,
        step_by_step=True,
        show_reasoning=False  # Less verbose for policy work
    )
    
    return ParliamentaryThinkingAgent(
        role=ParliamentaryRole.PLANNER,
        thinking_config=config
    )


async def example_constitutional_thinking():
    """Example of using constitutional thinking for complex analysis."""
    
    # Create constitutional thinking agent
    constitutional_agent = create_constitutional_thinking_agent(ThinkingComplexity.COMPLEX)
    
    # Analyze complex constitutional issue
    issue = "Government implementing digital surveillance without parliamentary approval"
    context = {
        "constitutional_provision": "Charter Section 8 - Unreasonable search and seizure",
        "parliamentary_context": "No legislative authorization provided",
        "precedent": "R. v. Spencer (2014) - Digital privacy expectations",
        "government_justification": "National security emergency"
    }
    
    # Execute thinking analysis
    result = await constitutional_agent.think_through_constitutional_issue(
        issue_description=issue,
        constitutional_context=context
    )
    
    print(f"Constitutional Analysis Complete:")
    print(f"Issue: {result['issue']}")
    print(f"Authority: {result['constitutional_authority']}")
    print(f"Complexity: {result['complexity']}")
    print(f"Reasoning Quality: {result['reasoning_quality']['overall_quality']:.2f}")
    print(f"Thinking Steps: {len(result['thinking_process']['steps'])}")
    print(f"Conclusion: {result['conclusion'][:200]}...")
    
    return result


if __name__ == "__main__":
    asyncio.run(example_constitutional_thinking())