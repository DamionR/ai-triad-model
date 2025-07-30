"""
AI Triad Model - Multi-Agent Framework

A structured multi-agent AI framework with built-in oversight,
systematic coordination, and transparent decision-making processes.

⚡ Four specialized agents working together for reliable AI coordination ⚡
"""

__version__ = "2.0.0"
__author__ = "AI Triad Model Team"
__email__ = "contact@ai-triad-model.org"

# Initialize Logfire for observability before importing components
from .core.logging.logfire_config import initialize_logfire
_logfire_initialized = initialize_logfire()

from .core.framework import TriadFramework
from .core.dependencies import TriadDeps
from .agents.roles.planner import PlannerAgent
from .agents.roles.executor import ExecutorAgent
from .agents.roles.evaluator import EvaluatorAgent
from .agents.roles.overwatch import OverwatchAgent
from .core.procedures import SystemProcedures
from .core.crisis import SystemCrisisManager
from .core.oversight import SystemOversight

__all__ = [
    "__version__",
    "TriadFramework",
    "TriadDeps", 
    "PlannerAgent",
    "ExecutorAgent",
    "EvaluatorAgent",
    "OverwatchAgent",
    "SystemProcedures",
    "SystemCrisisManager",
    "SystemOversight",
]