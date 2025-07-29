"""
AI Triad Constitutional Parliamentary System

A complete Westminster parliamentary AI system with constitutional governance,
democratic accountability, and transparent decision-making processes.

🇨🇦 Based on the Canadian Westminster Parliamentary System 🇨🇦
"""

__version__ = "2.0.0"
__author__ = "AI Triad Constitutional Team"
__email__ = "contact@ai-triad-constitutional.org"

from .core.constitutional import ConstitutionalFramework
from .core.dependencies import TriadDeps
from .agents.planner import PlannerAgent
from .agents.executor import ExecutorAgent
from .agents.evaluator import EvaluatorAgent
from .agents.overwatch import OverwatchAgent
from .parliamentary.procedures import ParliamentaryProcedure
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
    "ParliamentaryProcedure",
    "ConstitutionalCrisisManager",
    "CrownPrerogative",
]