"""
AI Triad Constitutional Parliamentary System

A complete Westminster parliamentary AI system with constitutional governance,
democratic accountability, and transparent decision-making processes.

🇨🇦 Based on the Canadian Westminster Parliamentary System 🇨🇦
"""

__version__ = "2.0.0"
__author__ = "AI Triad Constitutional Team"
__email__ = "contact@ai-triad-constitutional.org"

# Initialize Logfire for observability before importing components
from .core.logging.logfire_config import initialize_logfire
_logfire_initialized = initialize_logfire()

from .core.constitutional import ConstitutionalFramework
from .core.dependencies import TriadDeps
from .agents.roles.planner import PlannerAgent
from .agents.roles.executor import ExecutorAgent
from .agents.roles.evaluator import EvaluatorAgent
from .agents.roles.overwatch import OverwatchAgent
from .parliamentary.procedures import ParliamentaryProcedures
from .parliamentary.crisis import ConstitutionalCrisisManager
from .parliamentary.crown import CrownPrerogative

__all__ = [
    "__version__",
    "ConstitutionalFramework",
    "TriadDeps", 
    "PlannerAgent",
    "ExecutorAgent",
    "EvaluatorAgent",
    "OverwatchAgent",
    "ParliamentaryProcedures",
    "ConstitutionalCrisisManager",
    "CrownPrerogative",
]