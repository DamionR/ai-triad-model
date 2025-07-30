"""
Logfire Configuration for Triad Model

Provides comprehensive Logfire setup with spans, traces, auto-instrumentation,
and manual tracing for the Westminster Parliamentary AI System.
"""

import os
import warnings
from typing import Optional, Dict, Any, Callable
from contextlib import asynccontextmanager, contextmanager
import logfire


class TriadLogfireConfig:
    """
    Robust Logfire configuration for Triad Model.
    
    Handles authentication, token validation, and provides
    fallback mechanisms with constitutional oversight.
    """
    
    def __init__(self):
        self.configured = False
        self.token = None
        self.fallback_mode = False
        
    def configure(self, token: Optional[str] = None, project_name: str = "triadmodel") -> bool:
        """
        Configure Logfire with robust error handling.
        
        Args:
            token: Logfire write token (optional, will use env var)
            project_name: Logfire project name
            
        Returns:
            bool: True if successfully configured, False if using fallback
        """
        
        # Get token from parameter or environment
        self.token = token or os.getenv("LOGFIRE_TOKEN")
        
        if not self.token or self.token == "disabled":
            print("ℹ️  Logfire disabled or no token provided - using fallback logging")
            self._setup_fallback_logging()
            return False
            
        try:
            # Configure Logfire with comprehensive instrumentation
            logfire.configure(
                token=self.token,
                console=True,
                inspect_arguments=True,  # Enable automatic argument inspection
                # service_name="triad-model",
                # service_version="2.0.0"
            )
            
            # Enable auto-instrumentation for key integrations
            self._setup_auto_instrumentation()
            
            # Test with a proper span
            with logfire.span("triad-model-initialization"):
                logfire.info(
                    "🏛️ Triad Model Logfire initialized successfully",
                    system="triad-model",
                    component="logfire-config",
                    constitutional_authority="system",
                    version="2.0.0"
                )
            
            self.configured = True
            print("✅ Logfire configured successfully with full instrumentation")
            return True
            
        except Exception as e:
            print(f"⚠️  Logfire configuration failed: {e}")
            
            # Try alternative configuration without project_name
            try:
                os.environ["LOGFIRE_TOKEN"] = self.token
                logfire.configure()
                logfire.info("Triad Model fallback configuration test")
                
                self.configured = True
                print("✅ Logfire configured with fallback method")
                return True
                
            except Exception as e2:
                print(f"   Fallback configuration also failed: {e2}")
                print("   Using console logging only...")
                self._setup_fallback_logging()
                return False
    
    def _setup_auto_instrumentation(self):
        """Set up auto-instrumentation for various integrations."""
        try:
            # Instrument FastAPI
            logfire.instrument_fastapi()
            
            # Instrument HTTP clients
            logfire.instrument_httpx()
            logfire.instrument_requests()
            
            # Instrument databases
            logfire.instrument_sqlite3()
            logfire.instrument_sqlalchemy()
            
            # Instrument Pydantic AI (if available)
            try:
                logfire.instrument_pydantic_ai()
            except:
                pass
            
            # Instrument system metrics
            logfire.instrument_system_metrics()
            
            print("✅ Auto-instrumentation enabled")
            
        except Exception as e:
            print(f"⚠️  Some auto-instrumentation failed: {e}")
    
    def _setup_fallback_logging(self):
        """Set up fallback logging when Logfire is unavailable."""
        self.fallback_mode = True
        
        # Suppress Logfire warnings in fallback mode
        warnings.filterwarnings("ignore", module="logfire")
        
        # Configure basic console logging
        try:
            logfire.configure(console=True)
        except:
            pass
    
    def log_parliamentary_event(self, event_type: str, data: dict, authority: str = "system"):
        """
        Log parliamentary events with constitutional oversight using spans.
        
        Args:
            event_type: Type of parliamentary event
            data: Event details
            authority: Constitutional authority (legislative, executive, judicial, crown)
        """
        try:
            if self.configured:
                with logfire.span(
                    f"parliamentary-event-{event_type}",
                    parliamentary_event=event_type,
                    constitutional_authority=authority,
                    system="triad-model",
                    component="parliamentary"
                ) as span:
                    span.set_attribute("event.type", event_type)
                    span.set_attribute("event.authority", authority)
                    span.set_attribute("event.data", str(data))
                    
                    logfire.info(
                        f"🏛️ Parliamentary Event: {event_type}",
                        event_type=event_type,
                        event_data=data,
                        constitutional_authority=authority,
                        system="triad-model",
                        component="parliamentary"
                    )
            else:
                # Fallback to simple print
                print(f"🏛️ Parliamentary Event [{authority}]: {event_type} - {data}")
        except Exception as e:
            print(f"Logging error: {e}")
    
    def log_agent_activity(self, agent_name: str, activity: str, data: dict):
        """
        Log agent activities with constitutional tracking using spans.
        
        Args:
            agent_name: Name of the agent
            activity: Activity description
            data: Activity details
        """
        try:
            if self.configured:
                with logfire.span(
                    f"agent-activity-{agent_name}-{activity}",
                    agent_name=agent_name,
                    activity=activity,
                    system="triad-model",
                    component="agents"
                ) as span:
                    span.set_attribute("agent.name", agent_name)
                    span.set_attribute("agent.activity", activity)
                    span.set_attribute("agent.data", str(data))
                    
                    logfire.info(
                        f"🤖 Agent Activity: {agent_name} - {activity}",
                        agent=agent_name,
                        activity=activity,
                        data=data,
                        system="triad-model",
                        component="agents"
                    )
            else:
                print(f"🤖 Agent [{agent_name}]: {activity} - {data}")
        except Exception as e:
            print(f"Logging error: {e}")
    
    def log_constitutional_event(self, event: str, authority: str, details: dict):
        """
        Log constitutional events with high priority using spans.
        
        Args:
            event: Constitutional event description
            authority: Constitutional authority involved
            details: Event details
        """
        try:
            if self.configured:
                with logfire.span(
                    f"constitutional-event-{event}",
                    constitutional_event=event,
                    constitutional_authority=authority,
                    system="triad-model",
                    component="constitutional",
                    priority="high"
                ) as span:
                    span.set_attribute("constitutional.event", event)
                    span.set_attribute("constitutional.authority", authority)
                    span.set_attribute("constitutional.details", str(details))
                    span.set_level("warn")  # High priority for constitutional events
                    
                    logfire.warning(  # Use warning level for constitutional events
                        f"⚖️ Constitutional Event: {event}",
                        event=event,
                        constitutional_authority=authority,
                        details=details,
                        system="triad-model",
                        component="constitutional",
                        priority="high"
                    )
            else:
                print(f"⚖️ CONSTITUTIONAL [{authority}]: {event} - {details}")
        except Exception as e:
            print(f"Constitutional logging error: {e}")
    
    @contextmanager
    def parliamentary_session_span(self, session_type: str, participants: list):
        """
        Create a span for a parliamentary session.
        
        Args:
            session_type: Type of parliamentary session
            participants: List of participating agents
        """
        if self.configured:
            with logfire.span(
                f"parliamentary-session-{session_type}",
                session_type=session_type,
                participants=participants,
                system="triad-model",
                component="parliamentary"
            ) as span:
                span.set_attribute("session.type", session_type)
                span.set_attribute("session.participants", str(participants))
                yield span
        else:
            class DummySpan:
                def set_attribute(self, key, value): pass
                def record_exception(self, exception): pass
            yield DummySpan()
    
    @asynccontextmanager
    async def agent_task_span(self, agent_name: str, task_type: str, task_data: dict):
        """
        Create an async span for agent task execution.
        
        Args:
            agent_name: Name of the executing agent
            task_type: Type of task being executed
            task_data: Task parameters and data
        """
        if self.configured:
            with logfire.span(
                f"agent-task-{agent_name}-{task_type}",
                agent_name=agent_name,
                task_type=task_type,
                system="triad-model",
                component="agents"
            ) as span:
                span.set_attribute("task.agent", agent_name)
                span.set_attribute("task.type", task_type)
                span.set_attribute("task.data", str(task_data))
                
                try:
                    yield span
                except Exception as e:
                    span.record_exception(e)
                    logfire.exception(
                        f"❌ Agent task failed: {agent_name} - {task_type}",
                        agent=agent_name,
                        task_type=task_type,
                        error=str(e)
                    )
                    raise
        else:
            class DummySpan:
                def set_attribute(self, key, value): pass
                def record_exception(self, exception): pass
            yield DummySpan()
    
    def log_metric(self, metric_name: str, value: float, unit: str = "", **attributes):
        """
        Log a metric with Logfire.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement
            **attributes: Additional attributes
        """
        try:
            if self.configured:
                # Combine attributes safely
                metric_attrs = {
                    "metric_name": metric_name,
                    "metric_value": value,
                    "metric_unit": unit,
                    "system": "triad-model",
                    "triad_component": "metrics",  # Avoid conflict with 'component'
                    **attributes
                }
                
                logfire.info(
                    f"📊 Metric: {metric_name} = {value} {unit}",
                    **metric_attrs
                )
            else:
                print(f"📊 Metric: {metric_name} = {value} {unit}")
        except Exception as e:
            print(f"Metric logging error: {e}")
    
    def instrument_function(self, func: Callable) -> Callable:
        """
        Decorator to instrument a function with automatic tracing.
        
        Args:
            func: Function to instrument
            
        Returns:
            Instrumented function
        """
        if self.configured:
            return logfire.instrument(func)
        else:
            return func


# Global Logfire configuration instance
triad_logfire = TriadLogfireConfig()


def initialize_logfire() -> bool:
    """
    Initialize Logfire for the Triad Model system.
    
    Returns:
        bool: True if Logfire configured successfully, False if using fallback
    """
    return triad_logfire.configure()


def get_logfire_config() -> TriadLogfireConfig:
    """Get the global Logfire configuration instance."""
    return triad_logfire