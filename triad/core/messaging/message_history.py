"""
Message History Management for Triad Model

Handles message history storage and retrieval for agents following
Pydantic AI's message history format with constitutional oversight.
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from enum import Enum
import json
import logfire
from pydantic import BaseModel, Field
from pydantic_ai.messages import (
    ModelMessage,
    UserPromptPart,
    SystemPromptPart,
    ToolCallPart,
    ToolReturnPart,
    RetryPromptPart
)


class MessageRole(str, Enum):
    """Message roles in conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class StoredMessage(BaseModel):
    """Stored message with metadata."""
    message_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    agent_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    message: ModelMessage
    constitutional_validated: bool = True
    parliamentary_context: Optional[Dict[str, Any]] = None
    
    class Config:
        arbitrary_types_allowed = True


class ConversationSession(BaseModel):
    """Conversation session with parliamentary context."""
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    agent_name: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    messages: List[StoredMessage] = Field(default_factory=list)
    parliamentary_session_id: Optional[str] = None
    constitutional_authority: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    active: bool = True


class MessageHistoryManager:
    """
    Manages message history for agents with constitutional oversight.
    
    Provides storage, retrieval, and parliamentary accountability
    for agent conversations following Pydantic AI patterns.
    """
    
    def __init__(self, logfire_logger: Optional[logfire] = None):
        self.logger = logfire_logger or logfire
        self.sessions: Dict[str, ConversationSession] = {}
        self.message_store: Dict[str, List[StoredMessage]] = {}
        
    async def create_session(
        self,
        agent_name: str,
        constitutional_authority: str,
        parliamentary_session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new conversation session."""
        session = ConversationSession(
            agent_name=agent_name,
            constitutional_authority=constitutional_authority,
            parliamentary_session_id=parliamentary_session_id,
            metadata=metadata or {}
        )
        
        self.sessions[session.session_id] = session
        self.message_store[session.session_id] = []
        
        await self.logger.info(
            "Message history session created",
            session_id=session.session_id,
            agent_name=agent_name,
            constitutional_authority=constitutional_authority
        )
        
        return session.session_id
    
    async def add_message(
        self,
        session_id: str,
        message: ModelMessage,
        parliamentary_context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a message to the session history."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        
        stored_message = StoredMessage(
            session_id=session_id,
            agent_name=session.agent_name,
            message=message,
            parliamentary_context=parliamentary_context
        )
        
        session.messages.append(stored_message)
        session.last_activity = datetime.now(timezone.utc)
        
        if session_id not in self.message_store:
            self.message_store[session_id] = []
        self.message_store[session_id].append(stored_message)
        
        # Log for parliamentary accountability
        await self.logger.info(
            "Message added to history",
            session_id=session_id,
            message_type=type(message).__name__,
            agent_name=session.agent_name,
            constitutional_authority=session.constitutional_authority
        )
    
    async def get_messages(
        self,
        session_id: str,
        limit: Optional[int] = None,
        message_types: Optional[List[type[ModelMessage]]] = None
    ) -> List[ModelMessage]:
        """Get messages from session history."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        messages = self.message_store.get(session_id, [])
        
        # Filter by message types if specified
        if message_types:
            messages = [
                msg for msg in messages 
                if type(msg.message) in message_types
            ]
        
        # Apply limit if specified
        if limit:
            messages = messages[-limit:]
        
        # Return just the ModelMessage objects for Pydantic AI
        return [msg.message for msg in messages]
    
    async def get_conversation_history(
        self,
        session_id: str,
        include_system: bool = True,
        include_tools: bool = True
    ) -> List[ModelMessage]:
        """
        Get full conversation history formatted for Pydantic AI.
        
        Returns messages in the format expected by Pydantic AI's
        message_history parameter.
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        messages = []
        stored_messages = self.message_store.get(session_id, [])
        
        for stored_msg in stored_messages:
            msg = stored_msg.message
            
            # Filter based on parameters
            if isinstance(msg, SystemPromptPart) and not include_system:
                continue
            if isinstance(msg, (ToolCallPart, ToolReturnPart)) and not include_tools:
                continue
                
            messages.append(msg)
        
        return messages
    
    async def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of a conversation session."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        messages = self.message_store.get(session_id, [])
        
        # Count message types
        message_counts = {}
        for msg in messages:
            msg_type = type(msg.message).__name__
            message_counts[msg_type] = message_counts.get(msg_type, 0) + 1
        
        return {
            "session_id": session_id,
            "agent_name": session.agent_name,
            "constitutional_authority": session.constitutional_authority,
            "started_at": session.started_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "total_messages": len(messages),
            "message_types": message_counts,
            "parliamentary_session_id": session.parliamentary_session_id,
            "active": session.active,
            "duration_seconds": (session.last_activity - session.started_at).total_seconds()
        }
    
    async def end_session(self, session_id: str) -> None:
        """End a conversation session."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        session.active = False
        
        await self.logger.info(
            "Message history session ended",
            session_id=session_id,
            agent_name=session.agent_name,
            total_messages=len(session.messages),
            duration_seconds=(session.last_activity - session.started_at).total_seconds()
        )
    
    async def get_agent_sessions(
        self,
        agent_name: str,
        active_only: bool = False
    ) -> List[str]:
        """Get all sessions for a specific agent."""
        sessions = []
        for session_id, session in self.sessions.items():
            if session.agent_name == agent_name:
                if not active_only or session.active:
                    sessions.append(session_id)
        return sessions
    
    async def clear_old_sessions(self, days: int = 30) -> int:
        """Clear sessions older than specified days."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        cleared = 0
        
        for session_id in list(self.sessions.keys()):
            session = self.sessions[session_id]
            if session.last_activity < cutoff_date:
                del self.sessions[session_id]
                if session_id in self.message_store:
                    del self.message_store[session_id]
                cleared += 1
        
        await self.logger.info(
            "Cleared old message history sessions",
            cleared_count=cleared,
            days_threshold=days
        )
        
        return cleared
    
    def export_session(self, session_id: str) -> Dict[str, Any]:
        """Export session data for parliamentary records."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        messages = self.message_store.get(session_id, [])
        
        # Convert messages to exportable format
        exported_messages = []
        for msg in messages:
            exported_msg = {
                "message_id": msg.message_id,
                "timestamp": msg.timestamp.isoformat(),
                "type": type(msg.message).__name__,
                "constitutional_validated": msg.constitutional_validated
            }
            
            # Add message-specific data
            if isinstance(msg.message, UserPromptPart):
                exported_msg["content"] = msg.message.content
            elif isinstance(msg.message, ModelResponse):
                exported_msg["content"] = msg.message.content
                exported_msg["timestamp"] = msg.message.timestamp.isoformat() if msg.message.timestamp else None
            elif isinstance(msg.message, ToolCallPart):
                exported_msg["tool_name"] = msg.message.tool_name
                exported_msg["args"] = msg.message.args.model_dump() if hasattr(msg.message.args, 'model_dump') else {}
            elif isinstance(msg.message, ToolReturnPart):
                exported_msg["tool_name"] = msg.message.tool_name
                exported_msg["content"] = msg.message.content
                
            exported_messages.append(exported_msg)
        
        return {
            "session": {
                "session_id": session.session_id,
                "agent_name": session.agent_name,
                "constitutional_authority": session.constitutional_authority,
                "started_at": session.started_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "parliamentary_session_id": session.parliamentary_session_id,
                "active": session.active,
                "metadata": session.metadata
            },
            "messages": exported_messages,
            "summary": {
                "total_messages": len(exported_messages),
                "duration_seconds": (session.last_activity - session.started_at).total_seconds()
            }
        }


# Global message history manager instance
message_history_manager = MessageHistoryManager()


async def get_message_history_manager() -> MessageHistoryManager:
    """Get the global message history manager."""
    return message_history_manager