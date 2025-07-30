"""
Retry Patterns for Westminster Parliamentary AI System

Implements robust retry logic for AI agents with exponential backoff,
constitutional compliance validation, and parliamentary system reliability.
"""

import asyncio
from typing import Dict, List, Optional, Any, Callable, Type, Union
from datetime import datetime, timezone, timedelta
from enum import Enum
import time
import logging
from dataclasses import dataclass, field
import logfire
from pydantic import BaseModel, Field
from tenacity import (
    AsyncRetrying,
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    wait_retry_after,
    before_sleep_log,
    after_log,
    RetryError
)
from pydantic_ai.exceptions import ModelRetry, UsageLimitExceeded
from httpx import HTTPStatusError, ConnectError, TimeoutException

from triad.tools.parliamentary_toolsets import ParliamentaryAuthority
from triad.core.logging import get_logfire_config


class RetryCategory(Enum):
    """Categories of retry scenarios for parliamentary operations."""
    CONSTITUTIONAL_ANALYSIS = "constitutional_analysis"
    PARLIAMENTARY_PROCEDURE = "parliamentary_procedure"
    CRISIS_MANAGEMENT = "crisis_management"
    ROUTINE_QUERY = "routine_query"
    AGENT_COORDINATION = "agent_coordination"
    EXTERNAL_INTEGRATION = "external_integration"


class RetryPriority(Enum):
    """Priority levels affecting retry behavior."""
    CRITICAL = "critical"      # Constitutional crises - aggressive retries
    HIGH = "high"             # Important parliamentary procedures
    NORMAL = "normal"         # Standard operations
    LOW = "low"              # Background tasks


class FailureType(Enum):
    """Types of failures that can occur in parliamentary AI operations."""
    NETWORK_ERROR = "network_error"
    RATE_LIMIT = "rate_limit"
    MODEL_ERROR = "model_error"
    TIMEOUT = "timeout"
    AUTHENTICATION = "authentication"
    VALIDATION_ERROR = "validation_error"
    CONSTITUTIONAL_VIOLATION = "constitutional_violation"
    RESOURCE_EXHAUSTION = "resource_exhaustion"


@dataclass
class RetryConfiguration:
    """Configuration for retry behavior based on operation context."""
    category: RetryCategory
    priority: RetryPriority
    max_attempts: int = 3
    base_wait_seconds: float = 1.0
    max_wait_seconds: float = 60.0
    exponential_multiplier: float = 2.0
    jitter: bool = True
    retry_on_exceptions: List[Type[Exception]] = field(default_factory=lambda: [
        HTTPStatusError, ConnectError, TimeoutException, ModelRetry
    ])
    stop_on_exceptions: List[Type[Exception]] = field(default_factory=lambda: [
        UsageLimitExceeded
    ])
    constitutional_validation: bool = True
    log_attempts: bool = True


class RetryAttempt(BaseModel):
    """Record of a retry attempt."""
    attempt_number: int
    exception_type: str
    exception_message: str
    wait_time_seconds: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    constitutional_authority: Optional[str] = None


class RetryResult(BaseModel):
    """Result of retry operation with parliamentary context."""
    success: bool
    final_result: Any = None
    total_attempts: int
    total_time_seconds: float
    retry_attempts: List[RetryAttempt] = Field(default_factory=list)
    final_exception: Optional[str] = None
    constitutional_compliance: bool = True
    operation_category: RetryCategory
    priority: RetryPriority
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ParliamentaryRetryManager:
    """
    Retry manager for Westminster Parliamentary AI operations.
    
    Provides constitutional-aware retry logic with appropriate backoff strategies,
    logging, and parliamentary accountability for all retry operations.
    """
    
    def __init__(self):
        self.logger = get_logfire_config()
        self.retry_stats: Dict[str, List[RetryResult]] = {}
        
    def get_retry_configuration(
        self, 
        category: RetryCategory, 
        priority: RetryPriority
    ) -> RetryConfiguration:
        """Get retry configuration based on operation category and priority."""
        
        # Base configurations by category
        category_configs = {
            RetryCategory.CONSTITUTIONAL_ANALYSIS: RetryConfiguration(
                category=category,
                priority=priority,
                max_attempts=5,  # Important constitutional work
                base_wait_seconds=2.0,
                max_wait_seconds=120.0,
                constitutional_validation=True,
                log_attempts=True
            ),
            
            RetryCategory.PARLIAMENTARY_PROCEDURE: RetryConfiguration(
                category=category,
                priority=priority,
                max_attempts=4,
                base_wait_seconds=1.5,
                max_wait_seconds=90.0,
                constitutional_validation=True,
                log_attempts=True
            ),
            
            RetryCategory.CRISIS_MANAGEMENT: RetryConfiguration(
                category=category,
                priority=priority,
                max_attempts=7,  # Critical for crisis response
                base_wait_seconds=0.5,  # Faster initial retry
                max_wait_seconds=60.0,  # But don't wait too long
                exponential_multiplier=1.5,  # Gentler backoff
                constitutional_validation=True,
                log_attempts=True
            ),
            
            RetryCategory.ROUTINE_QUERY: RetryConfiguration(
                category=category,
                priority=priority,
                max_attempts=3,
                base_wait_seconds=1.0,
                max_wait_seconds=30.0,
                constitutional_validation=False,  # Less critical
                log_attempts=False
            ),
            
            RetryCategory.AGENT_COORDINATION: RetryConfiguration(
                category=category,
                priority=priority,
                max_attempts=4,
                base_wait_seconds=2.0,
                max_wait_seconds=100.0,
                constitutional_validation=True,
                log_attempts=True
            ),
            
            RetryCategory.EXTERNAL_INTEGRATION: RetryConfiguration(
                category=category,
                priority=priority,
                max_attempts=6,  # External systems can be unreliable
                base_wait_seconds=3.0,
                max_wait_seconds=180.0,
                exponential_multiplier=2.5,
                constitutional_validation=False,
                log_attempts=True
            )
        }
        
        config = category_configs.get(category, RetryConfiguration(category, priority))
        
        # Adjust based on priority
        if priority == RetryPriority.CRITICAL:
            config.max_attempts = min(config.max_attempts + 3, 10)
            config.base_wait_seconds = config.base_wait_seconds * 0.5
            config.constitutional_validation = True
            config.log_attempts = True
        
        elif priority == RetryPriority.HIGH:
            config.max_attempts = min(config.max_attempts + 1, 7)
            config.constitutional_validation = True
        
        elif priority == RetryPriority.LOW:
            config.max_attempts = max(config.max_attempts - 1, 2)
            config.max_wait_seconds = config.max_wait_seconds * 0.5
            config.log_attempts = False
        
        return config
    
    async def retry_with_parliamentary_oversight(
        self,
        operation: Callable,
        category: RetryCategory,
        priority: RetryPriority,
        constitutional_authority: Optional[ParliamentaryAuthority] = None,
        operation_context: Optional[Dict[str, Any]] = None,
        **operation_kwargs
    ) -> RetryResult:
        """
        Execute operation with retry logic and parliamentary oversight.
        
        Args:
            operation: Async operation to retry
            category: Category of parliamentary operation
            priority: Priority level for retry behavior
            constitutional_authority: Constitutional authority performing operation
            operation_context: Additional context for logging and validation
            **operation_kwargs: Arguments to pass to the operation
            
        Returns:
            RetryResult with operation outcome and retry metadata
        """
        
        config = self.get_retry_configuration(category, priority)
        start_time = datetime.now(timezone.utc)
        retry_attempts = []
        
        # Configure retry strategy
        retry_strategy = AsyncRetrying(
            retry=retry_if_exception_type(tuple(config.retry_on_exceptions)),
            stop=stop_after_attempt(config.max_attempts),
            wait=wait_exponential(
                multiplier=config.base_wait_seconds,
                max=config.max_wait_seconds,
                exp_base=config.exponential_multiplier
            ),
            reraise=True
        )
        
        # Add logging if configured
        if config.log_attempts:
            retry_strategy = retry_strategy.copy(
                before_sleep=before_sleep_log(
                    logging.getLogger(__name__), 
                    logging.WARNING
                ),
                after=after_log(
                    logging.getLogger(__name__), 
                    logging.INFO
                )
            )
        
        operation_id = f"{category.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            with self.logger.parliamentary_session_span(
                f"retry-operation-{category.value}",
                [constitutional_authority.value if constitutional_authority else "system"]
            ) as span:
                
                span.set_attribute("retry.category", category.value)
                span.set_attribute("retry.priority", priority.value)
                span.set_attribute("retry.max_attempts", config.max_attempts)
                
                # Custom retry logic with parliamentary tracking
                last_exception = None
                attempt_number = 0
                
                async for attempt in retry_strategy:
                    with attempt:
                        try:
                            attempt_number += 1
                            
                            # Log attempt start
                            if config.log_attempts:
                                self.logger.log_parliamentary_event(
                                    event_type="retry_attempt_started",
                                    data={
                                        "operation_id": operation_id,
                                        "attempt_number": attempt_number,
                                        "category": category.value,
                                        "priority": priority.value
                                    },
                                    authority=constitutional_authority.value if constitutional_authority else "system"
                                )
                            
                            # Execute operation
                            result = await operation(**operation_kwargs)
                            
                            # Validate constitutional compliance if required
                            if config.constitutional_validation and constitutional_authority:
                                compliance_valid = await self._validate_constitutional_compliance(
                                    result, constitutional_authority, operation_context
                                )
                                
                                if not compliance_valid:
                                    raise ValueError("Constitutional compliance validation failed")
                            
                            # Success - create result
                            total_time = (datetime.now(timezone.utc) - start_time).total_seconds()
                            
                            retry_result = RetryResult(
                                success=True,
                                final_result=result,
                                total_attempts=attempt_number,
                                total_time_seconds=total_time,
                                retry_attempts=retry_attempts,
                                constitutional_compliance=True,
                                operation_category=category,
                                priority=priority
                            )
                            
                            # Log successful completion
                            self.logger.log_parliamentary_event(
                                event_type="retry_operation_succeeded",
                                data={
                                    "operation_id": operation_id,
                                    "total_attempts": attempt_number,
                                    "total_time": total_time,
                                    "category": category.value,
                                    "priority": priority.value
                                },
                                authority=constitutional_authority.value if constitutional_authority else "system"
                            )
                            
                            span.set_attribute("retry.success", True)
                            span.set_attribute("retry.total_attempts", attempt_number)
                            span.set_attribute("retry.total_time", total_time)
                            
                            # Store stats
                            self._record_retry_stats(operation_id, retry_result)
                            
                            return retry_result
                            
                        except Exception as e:
                            last_exception = e
                            
                            # Check if this is a stop condition
                            if any(isinstance(e, exc_type) for exc_type in config.stop_on_exceptions):
                                self.logger.log_parliamentary_event(
                                    event_type="retry_operation_stopped",
                                    data={
                                        "operation_id": operation_id,
                                        "stop_exception": str(type(e).__name__),
                                        "attempt_number": attempt_number
                                    },
                                    authority=constitutional_authority.value if constitutional_authority else "system"
                                )
                                raise
                            
                            # Record retry attempt
                            wait_time = retry_strategy.statistics.get('delay_since_first_attempt', 0)
                            
                            retry_attempt = RetryAttempt(
                                attempt_number=attempt_number,
                                exception_type=type(e).__name__,
                                exception_message=str(e),
                                wait_time_seconds=wait_time,
                                constitutional_authority=constitutional_authority.value if constitutional_authority else None
                            )
                            
                            retry_attempts.append(retry_attempt)
                            
                            # Log retry attempt
                            if config.log_attempts:
                                self.logger.log_parliamentary_event(
                                    event_type="retry_attempt_failed",
                                    data={
                                        "operation_id": operation_id,
                                        "attempt_number": attempt_number,
                                        "exception_type": type(e).__name__,
                                        "exception_message": str(e)[:200],
                                        "wait_time": wait_time
                                    },
                                    authority=constitutional_authority.value if constitutional_authority else "system"
                                )
                            
                            # Re-raise to trigger retry logic
                            raise
        
        except RetryError as e:
            # All retries exhausted
            total_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            retry_result = RetryResult(
                success=False,
                total_attempts=attempt_number,
                total_time_seconds=total_time,
                retry_attempts=retry_attempts,
                final_exception=str(last_exception) if last_exception else str(e),
                constitutional_compliance=False,
                operation_category=category,
                priority=priority
            )
            
            # Log final failure
            self.logger.log_parliamentary_event(
                event_type="retry_operation_failed",
                data={
                    "operation_id": operation_id,
                    "total_attempts": attempt_number,
                    "total_time": total_time,
                    "final_exception": str(last_exception) if last_exception else str(e),
                    "category": category.value,
                    "priority": priority.value
                },
                authority=constitutional_authority.value if constitutional_authority else "system"
            )
            
            span.set_attribute("retry.success", False)
            span.set_attribute("retry.total_attempts", attempt_number)
            span.set_attribute("retry.final_exception", str(last_exception) if last_exception else str(e))
            
            # Store stats
            self._record_retry_stats(operation_id, retry_result)
            
            return retry_result
    
    def retry_sync_with_parliamentary_oversight(
        self,
        operation: Callable,
        category: RetryCategory,
        priority: RetryPriority,
        constitutional_authority: Optional[ParliamentaryAuthority] = None,
        operation_context: Optional[Dict[str, Any]] = None,
        **operation_kwargs
    ) -> RetryResult:
        """
        Synchronous version of retry with parliamentary oversight.
        
        Args:
            operation: Synchronous operation to retry
            category: Category of parliamentary operation
            priority: Priority level for retry behavior
            constitutional_authority: Constitutional authority performing operation
            operation_context: Additional context for logging and validation
            **operation_kwargs: Arguments to pass to the operation
            
        Returns:
            RetryResult with operation outcome and retry metadata
        """
        
        config = self.get_retry_configuration(category, priority)
        start_time = datetime.now(timezone.utc)
        retry_attempts = []
        
        # Configure synchronous retry strategy
        retry_strategy = Retrying(
            retry=retry_if_exception_type(tuple(config.retry_on_exceptions)),
            stop=stop_after_attempt(config.max_attempts),
            wait=wait_exponential(
                multiplier=config.base_wait_seconds,
                max=config.max_wait_seconds,
                exp_base=config.exponential_multiplier
            ),
            reraise=True
        )
        
        operation_id = f"{category.value}_sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            last_exception = None
            attempt_number = 0
            
            for attempt in retry_strategy:
                with attempt:
                    try:
                        attempt_number += 1
                        
                        # Execute operation
                        result = operation(**operation_kwargs)
                        
                        # Success
                        total_time = (datetime.now(timezone.utc) - start_time).total_seconds()
                        
                        retry_result = RetryResult(
                            success=True,
                            final_result=result,
                            total_attempts=attempt_number,
                            total_time_seconds=total_time,
                            retry_attempts=retry_attempts,
                            constitutional_compliance=True,
                            operation_category=category,
                            priority=priority
                        )
                        
                        return retry_result
                        
                    except Exception as e:
                        last_exception = e
                        
                        # Check stop conditions
                        if any(isinstance(e, exc_type) for exc_type in config.stop_on_exceptions):
                            raise
                        
                        # Record retry attempt
                        retry_attempt = RetryAttempt(
                            attempt_number=attempt_number,
                            exception_type=type(e).__name__,
                            exception_message=str(e),
                            wait_time_seconds=0,  # Calculated by tenacity
                            constitutional_authority=constitutional_authority.value if constitutional_authority else None
                        )
                        
                        retry_attempts.append(retry_attempt)
                        
                        # Re-raise to trigger retry
                        raise
        
        except RetryError as e:
            # All retries exhausted
            total_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            retry_result = RetryResult(
                success=False,
                total_attempts=attempt_number,
                total_time_seconds=total_time,
                retry_attempts=retry_attempts,
                final_exception=str(last_exception) if last_exception else str(e),
                constitutional_compliance=False,
                operation_category=category,
                priority=priority
            )
            
            return retry_result
    
    async def _validate_constitutional_compliance(
        self,
        result: Any,
        constitutional_authority: ParliamentaryAuthority,
        operation_context: Optional[Dict[str, Any]]
    ) -> bool:
        """Validate constitutional compliance of operation result."""
        
        try:
            # Basic constitutional compliance checks
            result_str = str(result).lower()
            
            # Check for constitutional violations in the result
            violation_indicators = [
                "unconstitutional", "violation", "breach", "illegal",
                "arbitrary", "discriminatory", "ultra vires"
            ]
            
            if any(indicator in result_str for indicator in violation_indicators):
                self.logger.log_constitutional_event(
                    event="constitutional_compliance_violation_detected",
                    authority=constitutional_authority.value,
                    details={
                        "result_snippet": result_str[:200],
                        "operation_context": operation_context
                    }
                )
                return False
            
            # Additional context-specific validations would go here
            # For now, simple heuristic validation
            
            return True
            
        except Exception as e:
            self.logger.log_constitutional_event(
                event="constitutional_compliance_validation_error",
                authority=constitutional_authority.value,
                details={"error": str(e)}
            )
            # Default to non-compliant on validation error
            return False
    
    def _record_retry_stats(self, operation_id: str, result: RetryResult):
        """Record retry statistics for monitoring and analysis."""
        
        category_key = result.operation_category.value
        
        if category_key not in self.retry_stats:
            self.retry_stats[category_key] = []
        
        self.retry_stats[category_key].append(result)
        
        # Keep only recent stats (last 1000 operations per category)
        if len(self.retry_stats[category_key]) > 1000:
            self.retry_stats[category_key] = self.retry_stats[category_key][-1000:]
    
    def get_retry_statistics(self) -> Dict[str, Any]:
        """Get comprehensive retry statistics for monitoring."""
        
        stats = {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "average_attempts": 0.0,
            "average_time_seconds": 0.0,
            "categories": {},
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        all_results = []
        for category_results in self.retry_stats.values():
            all_results.extend(category_results)
        
        if not all_results:
            return stats
        
        stats["total_operations"] = len(all_results)
        stats["successful_operations"] = sum(1 for r in all_results if r.success)
        stats["failed_operations"] = stats["total_operations"] - stats["successful_operations"]
        stats["average_attempts"] = sum(r.total_attempts for r in all_results) / len(all_results)
        stats["average_time_seconds"] = sum(r.total_time_seconds for r in all_results) / len(all_results)
        
        # Category-specific stats
        for category, results in self.retry_stats.items():
            if results:
                category_stats = {
                    "total_operations": len(results),
                    "success_rate": sum(1 for r in results if r.success) / len(results),
                    "average_attempts": sum(r.total_attempts for r in results) / len(results),
                    "average_time_seconds": sum(r.total_time_seconds for r in results) / len(results),
                    "recent_failures": [
                        {
                            "exception": r.final_exception,
                            "attempts": r.total_attempts,
                            "timestamp": r.timestamp.isoformat()
                        }
                        for r in results[-10:] if not r.success
                    ]
                }
                stats["categories"][category] = category_stats
        
        return stats


# Decorator for parliamentary operations with retry support

def parliamentary_retry(
    category: RetryCategory,
    priority: RetryPriority = RetryPriority.NORMAL,
    constitutional_authority: Optional[ParliamentaryAuthority] = None
):
    """
    Decorator to add retry logic to parliamentary operations.
    
    Args:
        category: Category of parliamentary operation
        priority: Priority level for retry behavior
        constitutional_authority: Constitutional authority performing operation
    """
    
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            retry_manager = get_parliamentary_retry_manager()
            
            result = await retry_manager.retry_with_parliamentary_oversight(
                operation=func,
                category=category,
                priority=priority,
                constitutional_authority=constitutional_authority,
                *args,
                **kwargs
            )
            
            if result.success:
                return result.final_result
            else:
                raise Exception(f"Operation failed after {result.total_attempts} attempts: {result.final_exception}")
        
        def sync_wrapper(*args, **kwargs):
            retry_manager = get_parliamentary_retry_manager()
            
            result = retry_manager.retry_sync_with_parliamentary_oversight(
                operation=func,
                category=category,
                priority=priority,
                constitutional_authority=constitutional_authority,
                *args,
                **kwargs
            )
            
            if result.success:
                return result.final_result
            else:
                raise Exception(f"Operation failed after {result.total_attempts} attempts: {result.final_exception}")
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Global retry manager
parliamentary_retry_manager = ParliamentaryRetryManager()


def get_parliamentary_retry_manager() -> ParliamentaryRetryManager:
    """Get the global parliamentary retry manager."""
    return parliamentary_retry_manager


# Example usage functions

@parliamentary_retry(
    category=RetryCategory.CONSTITUTIONAL_ANALYSIS,
    priority=RetryPriority.HIGH,
    constitutional_authority=ParliamentaryAuthority.JUDICIAL
)
async def example_constitutional_analysis(bill_text: str) -> str:
    """Example constitutional analysis with retry support."""
    
    # Simulate potential failures
    import random
    if random.random() < 0.3:  # 30% chance of failure
        raise HTTPStatusError("Service temporarily unavailable", request=None, response=None)
    
    return f"Constitutional analysis complete for bill: {bill_text[:50]}..."


@parliamentary_retry(
    category=RetryCategory.CRISIS_MANAGEMENT,
    priority=RetryPriority.CRITICAL,
    constitutional_authority=ParliamentaryAuthority.CROWN
)
async def example_crisis_response(crisis_description: str) -> Dict[str, Any]:
    """Example crisis response with retry support."""
    
    # Simulate potential network issues
    import random
    if random.random() < 0.4:  # 40% chance of failure
        raise ConnectError("Network connection failed")
    
    return {
        "crisis_assessment": f"Crisis analyzed: {crisis_description}",
        "immediate_actions": ["Notify stakeholders", "Activate emergency protocols"],
        "constitutional_compliance": True
    }


async def example_retry_operations():
    """Example of using retry patterns for parliamentary operations."""
    
    retry_manager = get_parliamentary_retry_manager()
    
    # Test constitutional analysis with retries
    try:
        result = await example_constitutional_analysis("Sample bill text for constitutional review")
        print(f"Constitutional analysis succeeded: {result}")
    except Exception as e:
        print(f"Constitutional analysis failed: {e}")
    
    # Test crisis management with retries
    try:
        crisis_result = await example_crisis_response("Government confidence vote failure")
        print(f"Crisis response succeeded: {crisis_result}")
    except Exception as e:
        print(f"Crisis response failed: {e}")
    
    # Get retry statistics
    stats = retry_manager.get_retry_statistics()
    print(f"\nRetry Statistics:")
    print(f"Total Operations: {stats['total_operations']}")
    print(f"Success Rate: {stats['successful_operations'] / max(stats['total_operations'], 1):.2%}")
    print(f"Average Attempts: {stats['average_attempts']:.1f}")
    print(f"Average Time: {stats['average_time_seconds']:.2f}s")
    
    return stats


if __name__ == "__main__":
    asyncio.run(example_retry_operations())