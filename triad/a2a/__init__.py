"""
Agent-to-Agent (A2A) Communication System

Implements structured agent-to-agent communication following
Westminster constitutional principles with parliamentary oversight.
"""

from .broker import A2ABroker
from .client import A2AClient
from .models import TaskRequest, TaskResponse, AgentMessage
from .storage import A2AStorage

__all__ = [
    "A2ABroker",
    "A2AClient", 
    "TaskRequest",
    "TaskResponse",
    "AgentMessage",
    "A2AStorage",
]