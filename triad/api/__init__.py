"""
Triad Model API

FastAPI endpoints for Westminster Parliamentary AI System
with constitutional oversight and democratic accountability.
"""

from .main import app
from .routes import agents, health, parliamentary

__all__ = [
    "app",
    "agents", 
    "health",
    "parliamentary"
]