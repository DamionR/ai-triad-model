"""
API Routes for Triad Parliamentary System

FastAPI route modules with constitutional oversight
and Westminster parliamentary accountability.
"""

from . import agents
from . import health  
from . import parliamentary

__all__ = [
    "agents",
    "health", 
    "parliamentary"
]