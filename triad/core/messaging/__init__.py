"""
Message History and Communication

Message history management and inter-agent communication
following Pydantic AI standards with governance oversight.
"""

from .message_history import (
    MessageRole,
    StoredMessage,
    ConversationSession,
    MessageHistoryManager,
    get_message_history_manager
)

__all__ = [
    "MessageRole",
    "StoredMessage", 
    "ConversationSession",
    "MessageHistoryManager",
    "get_message_history_manager"
]