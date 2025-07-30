"""
A2A Storage Implementation

Storage layer for A2A communication with constitutional record keeping
and parliamentary accountability.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete
import json

from .models import TaskRequest, TaskResponse, AgentMessage, ConversationContext, BroadcastMessage


class A2AStorage:
    """
    Storage layer for A2A communication system.
    
    Maintains constitutional records and parliamentary accountability
    for all agent-to-agent communications.
    """
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def store_task_request(self, request: TaskRequest) -> None:
        """Store task request with constitutional oversight."""
        request_data = {
            "request_id": request.request_id,
            "requesting_agent": request.requesting_agent,
            "target_agent": request.target_agent,
            "task_type": request.task_type,
            "task_description": request.task_description,
            "task_parameters": json.dumps(request.task_parameters),
            "context_id": request.context_id,
            "constitutional_authority_required": request.constitutional_authority_required,
            "parliamentary_oversight": request.parliamentary_oversight,
            "crown_notification": request.crown_notification,
            "priority": request.priority.value,
            "deadline": request.deadline,
            "created_at": request.created_at,
            "parliamentary_session_id": request.parliamentary_session_id,
            "status": "pending"
        }
        
        await self.db_session.execute(
            """
            INSERT INTO a2a_task_requests (
                request_id, requesting_agent, target_agent, task_type,
                task_description, task_parameters, context_id,
                constitutional_authority_required, parliamentary_oversight,
                crown_notification, priority, deadline, created_at,
                parliamentary_session_id, status
            ) VALUES (
                :request_id, :requesting_agent, :target_agent, :task_type,
                :task_description, :task_parameters, :context_id,
                :constitutional_authority_required, :parliamentary_oversight,
                :crown_notification, :priority, :deadline, :created_at,
                :parliamentary_session_id, :status
            )
            """,
            request_data
        )
        await self.db_session.commit()
    
    async def get_task_request(self, request_id: str) -> Optional[TaskRequest]:
        """Retrieve task request by ID."""
        result = await self.db_session.execute(
            "SELECT * FROM a2a_task_requests WHERE request_id = :request_id",
            {"request_id": request_id}
        )
        row = result.fetchone()
        
        if not row:
            return None
        
        # Convert back to TaskRequest object
        task_parameters = json.loads(row.task_parameters) if row.task_parameters else {}
        
        return TaskRequest(
            request_id=row.request_id,
            requesting_agent=row.requesting_agent,
            target_agent=row.target_agent,
            task_type=row.task_type,
            task_description=row.task_description,
            task_parameters=task_parameters,
            context_id=row.context_id,
            constitutional_authority_required=row.constitutional_authority_required,
            parliamentary_oversight=row.parliamentary_oversight,
            crown_notification=row.crown_notification,
            priority=row.priority,
            deadline=row.deadline,
            created_at=row.created_at,
            parliamentary_session_id=row.parliamentary_session_id
        )
    
    async def store_task_response(self, response: TaskResponse) -> None:
        """Store task response with constitutional compliance tracking."""
        response_data = {
            "response_id": response.response_id,
            "request_id": response.request_id,
            "responding_agent": response.responding_agent,
            "status": response.status,
            "result": json.dumps(response.result) if response.result else None,
            "error_message": response.error_message,
            "execution_time_seconds": response.execution_time_seconds,
            "resources_used": json.dumps(response.resources_used),
            "constitutional_compliance": response.constitutional_compliance,
            "validation_required": response.validation_required,
            "ministerial_responsibility_accepted": response.ministerial_responsibility_accepted,
            "accuracy_score": response.accuracy_score,
            "confidence_level": response.confidence_level,
            "completed_at": response.completed_at
        }
        
        await self.db_session.execute(
            """
            INSERT INTO a2a_task_responses (
                response_id, request_id, responding_agent, status,
                result, error_message, execution_time_seconds,
                resources_used, constitutional_compliance,
                validation_required, ministerial_responsibility_accepted,
                accuracy_score, confidence_level, completed_at
            ) VALUES (
                :response_id, :request_id, :responding_agent, :status,
                :result, :error_message, :execution_time_seconds,
                :resources_used, :constitutional_compliance,
                :validation_required, :ministerial_responsibility_accepted,
                :accuracy_score, :confidence_level, :completed_at
            )
            """,
            response_data
        )
        
        # Update request status
        await self.db_session.execute(
            "UPDATE a2a_task_requests SET status = 'completed' WHERE request_id = :request_id",
            {"request_id": response.request_id}
        )
        
        await self.db_session.commit()
    
    async def store_agent_message(self, message: AgentMessage) -> None:
        """Store agent message with parliamentary record."""
        message_data = {
            "message_id": message.message_id,
            "message_type": message.message_type.value,
            "sender_agent": message.sender_agent,
            "recipient_agent": message.recipient_agent,
            "subject": message.subject,
            "content": message.content,
            "structured_data": json.dumps(message.structured_data),
            "constitutional_authority": message.constitutional_authority,
            "parliamentary_procedure": message.parliamentary_procedure,
            "requires_response": message.requires_response,
            "response_deadline": message.response_deadline,
            "priority": message.priority.value,
            "broadcast": message.broadcast,
            "crown_copy": message.crown_copy,
            "status": message.status.value,
            "delivered_at": message.delivered_at,
            "acknowledged_at": message.acknowledged_at,
            "created_at": message.created_at,
            "expires_at": message.expires_at
        }
        
        await self.db_session.execute(
            """
            INSERT INTO a2a_messages (
                message_id, message_type, sender_agent, recipient_agent,
                subject, content, structured_data, constitutional_authority,
                parliamentary_procedure, requires_response, response_deadline,
                priority, broadcast, crown_copy, status, delivered_at,
                acknowledged_at, created_at, expires_at
            ) VALUES (
                :message_id, :message_type, :sender_agent, :recipient_agent,
                :subject, :content, :structured_data, :constitutional_authority,
                :parliamentary_procedure, :requires_response, :response_deadline,
                :priority, :broadcast, :crown_copy, :status, :delivered_at,
                :acknowledged_at, :created_at, :expires_at
            )
            """,
            message_data
        )
        await self.db_session.commit()
    
    async def store_conversation_context(self, context: ConversationContext) -> None:
        """Store conversation context for parliamentary record."""
        context_data = {
            "context_id": context.context_id,
            "conversation_type": context.conversation_type,
            "participants": json.dumps(context.participants),
            "initiated_by": context.initiated_by,
            "status": context.status,
            "current_topic": context.current_topic,
            "constitutional_oversight": context.constitutional_oversight,
            "parliamentary_record": context.parliamentary_record,
            "crown_monitoring": context.crown_monitoring,
            "message_count": context.message_count,
            "last_activity": context.last_activity,
            "created_at": context.created_at,
            "parliamentary_session_id": context.parliamentary_session_id
        }
        
        # Use upsert (INSERT ... ON CONFLICT DO UPDATE)
        await self.db_session.execute(
            """
            INSERT INTO a2a_conversations (
                context_id, conversation_type, participants, initiated_by,
                status, current_topic, constitutional_oversight,
                parliamentary_record, crown_monitoring, message_count,
                last_activity, created_at, parliamentary_session_id
            ) VALUES (
                :context_id, :conversation_type, :participants, :initiated_by,
                :status, :current_topic, :constitutional_oversight,
                :parliamentary_record, :crown_monitoring, :message_count,
                :last_activity, :created_at, :parliamentary_session_id
            ) ON CONFLICT (context_id) DO UPDATE SET
                status = EXCLUDED.status,
                current_topic = EXCLUDED.current_topic,
                message_count = EXCLUDED.message_count,
                last_activity = EXCLUDED.last_activity
            """,
            context_data
        )
        await self.db_session.commit()
    
    async def store_broadcast(self, broadcast: BroadcastMessage) -> None:
        """Store broadcast message record."""
        broadcast_data = {
            "broadcast_id": broadcast.broadcast_id,
            "message_type": broadcast.message_type.value,
            "sender_agent": broadcast.sender_agent,
            "subject": broadcast.subject,
            "content": broadcast.content,
            "target_agents": json.dumps(broadcast.target_agents) if broadcast.target_agents else None,
            "constitutional_authorities": json.dumps(broadcast.constitutional_authorities) if broadcast.constitutional_authorities else None,
            "priority": broadcast.priority.value,
            "immediate_action_required": broadcast.immediate_action_required,
            "parliamentary_notification": broadcast.parliamentary_notification,
            "acknowledgment_required": broadcast.acknowledgment_required,
            "response_required": broadcast.response_required,
            "response_deadline": broadcast.response_deadline,
            "delivered_to": json.dumps(broadcast.delivered_to),
            "acknowledged_by": json.dumps(broadcast.acknowledged_by),
            "created_at": broadcast.created_at,
            "expires_at": broadcast.expires_at
        }
        
        await self.db_session.execute(
            """
            INSERT INTO a2a_broadcasts (
                broadcast_id, message_type, sender_agent, subject, content,
                target_agents, constitutional_authorities, priority,
                immediate_action_required, parliamentary_notification,
                acknowledgment_required, response_required, response_deadline,
                delivered_to, acknowledged_by, created_at, expires_at
            ) VALUES (
                :broadcast_id, :message_type, :sender_agent, :subject, :content,
                :target_agents, :constitutional_authorities, :priority,
                :immediate_action_required, :parliamentary_notification,
                :acknowledgment_required, :response_required, :response_deadline,
                :delivered_to, :acknowledged_by, :created_at, :expires_at
            )
            """,
            broadcast_data
        )
        await self.db_session.commit()
    
    async def store_queued_message(self, message_id: str, message: Dict[str, Any]) -> None:
        """Store message in agent queue."""
        queue_data = {
            "message_id": message_id,
            "agent_name": message.get("target_agent", "unknown"),
            "message_data": json.dumps(message),
            "queued_at": datetime.now(timezone.utc),
            "status": "queued",
            "priority": message.get("priority", "routine")
        }
        
        await self.db_session.execute(
            """
            INSERT INTO a2a_message_queue (
                message_id, agent_name, message_data, queued_at, status, priority
            ) VALUES (
                :message_id, :agent_name, :message_data, :queued_at, :status, :priority
            )
            """,
            queue_data
        )
        await self.db_session.commit()
    
    async def get_queued_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve queued message by ID."""
        result = await self.db_session.execute(
            "SELECT * FROM a2a_message_queue WHERE message_id = :message_id",
            {"message_id": message_id}
        )
        row = result.fetchone()
        
        if not row:
            return None
        
        message_data = json.loads(row.message_data)
        return {
            "message_id": row.message_id,
            "agent_name": row.agent_name,
            "message_data": message_data,
            "queued_at": row.queued_at,
            "status": row.status,
            "priority": row.priority
        }
    
    async def update_message_status(self, message_id: str, status: str) -> None:
        """Update message status in queue."""
        await self.db_session.execute(
            "UPDATE a2a_message_queue SET status = :status WHERE message_id = :message_id",
            {"status": status, "message_id": message_id}
        )
        await self.db_session.commit()
    
    async def store_parliamentary_record(self, entry: Dict[str, Any]) -> None:
        """Store entry in parliamentary record (Hansard)."""
        record_data = {
            "record_id": f"hansard_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{entry.get('event_type', 'unknown')}",
            "timestamp": entry["timestamp"],
            "event_type": entry["event_type"],
            "data": json.dumps(entry["data"]),
            "recorded_by": entry["recorded_by"],
            "constitutional_oversight": entry.get("constitutional_oversight", True),
            "parliamentary_session_id": entry.get("parliamentary_session_id")
        }
        
        await self.db_session.execute(
            """
            INSERT INTO a2a_parliamentary_records (
                record_id, timestamp, event_type, data, recorded_by,
                constitutional_oversight, parliamentary_session_id
            ) VALUES (
                :record_id, :timestamp, :event_type, :data, :recorded_by,
                :constitutional_oversight, :parliamentary_session_id
            )
            """,
            record_data
        )
        await self.db_session.commit()
    
    async def store_cache_config(self, config: Dict[str, Any]) -> None:
        """Store cache coordination configuration."""
        config_data = {
            "config_id": f"cache_config_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            "configuration": json.dumps(config),
            "created_at": datetime.now(timezone.utc),
            "active": True
        }
        
        # Deactivate previous configs
        await self.db_session.execute(
            "UPDATE a2a_cache_configs SET active = false WHERE active = true"
        )
        
        # Insert new config
        await self.db_session.execute(
            """
            INSERT INTO a2a_cache_configs (
                config_id, configuration, created_at, active
            ) VALUES (
                :config_id, :configuration, :created_at, :active
            )
            """,
            config_data
        )
        await self.db_session.commit()
    
    async def get_agent_messages(
        self,
        agent_name: str,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get messages for specific agent."""
        query = """
            SELECT * FROM a2a_message_queue 
            WHERE agent_name = :agent_name
        """
        params = {"agent_name": agent_name}
        
        if status:
            query += " AND status = :status"
            params["status"] = status
        
        query += " ORDER BY queued_at DESC LIMIT :limit"
        params["limit"] = limit
        
        result = await self.db_session.execute(query, params)
        rows = result.fetchall()
        
        messages = []
        for row in rows:
            message_data = json.loads(row.message_data)
            messages.append({
                "message_id": row.message_id,
                "message_data": message_data,
                "queued_at": row.queued_at,
                "status": row.status,
                "priority": row.priority
            })
        
        return messages
    
    async def get_conversation_history(
        self,
        context_id: str
    ) -> List[Dict[str, Any]]:
        """Get conversation message history."""
        result = await self.db_session.execute(
            """
            SELECT m.*, r.context_id FROM a2a_messages m
            LEFT JOIN a2a_task_requests r ON m.message_id = r.context_id
            WHERE r.context_id = :context_id OR m.message_id IN (
                SELECT message_id FROM a2a_messages 
                WHERE structured_data::text LIKE '%' || :context_id || '%'
            )
            ORDER BY m.created_at ASC
            """,
            {"context_id": context_id}
        )
        
        messages = []
        for row in result.fetchall():
            structured_data = json.loads(row.structured_data) if row.structured_data else {}
            messages.append({
                "message_id": row.message_id,
                "message_type": row.message_type,
                "sender_agent": row.sender_agent,
                "subject": row.subject,
                "content": row.content,
                "structured_data": structured_data,
                "created_at": row.created_at
            })
        
        return messages
    
    async def get_constitutional_records(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get constitutional records for oversight."""
        query = "SELECT * FROM a2a_parliamentary_records WHERE 1=1"
        params = {}
        
        if start_date:
            query += " AND timestamp >= :start_date"
            params["start_date"] = start_date.isoformat()
        
        if end_date:
            query += " AND timestamp <= :end_date"
            params["end_date"] = end_date.isoformat()
        
        if event_type:
            query += " AND event_type = :event_type"
            params["event_type"] = event_type
        
        query += " ORDER BY timestamp DESC LIMIT 1000"
        
        result = await self.db_session.execute(query, params)
        
        records = []
        for row in result.fetchall():
            data = json.loads(row.data) if row.data else {}
            records.append({
                "record_id": row.record_id,
                "timestamp": row.timestamp,
                "event_type": row.event_type,
                "data": data,
                "recorded_by": row.recorded_by,
                "constitutional_oversight": row.constitutional_oversight
            })
        
        return records
    
    async def cleanup_expired_messages(self) -> int:
        """Clean up expired messages and return count."""
        current_time = datetime.now(timezone.utc)
        
        # Delete expired messages
        result = await self.db_session.execute(
            "DELETE FROM a2a_messages WHERE expires_at IS NOT NULL AND expires_at < :current_time",
            {"current_time": current_time}
        )
        
        # Delete old queue entries
        cutoff_time = current_time - timedelta(days=7)
        await self.db_session.execute(
            "DELETE FROM a2a_message_queue WHERE queued_at < :cutoff_time AND status = 'processed'",
            {"cutoff_time": cutoff_time}
        )
        
        await self.db_session.commit()
        
        return result.rowcount
    
    async def get_communication_statistics(self) -> Dict[str, Any]:
        """Get A2A communication statistics."""
        # Task request statistics
        task_stats = await self.db_session.execute(
            """
            SELECT 
                COUNT(*) as total_requests,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_requests,
                COUNT(CASE WHEN constitutional_authority_required THEN 1 END) as constitutional_requests,
                AVG(CASE WHEN status = 'completed' THEN 
                    EXTRACT(EPOCH FROM (SELECT completed_at FROM a2a_task_responses WHERE request_id = a2a_task_requests.request_id)) - 
                    EXTRACT(EPOCH FROM created_at) 
                END) as avg_completion_time_seconds
            FROM a2a_task_requests
            WHERE created_at > NOW() - INTERVAL '24 hours'
            """
        )
        task_row = task_stats.fetchone()
        
        # Message statistics
        message_stats = await self.db_session.execute(
            """
            SELECT 
                COUNT(*) as total_messages,
                COUNT(CASE WHEN broadcast THEN 1 END) as broadcast_messages,
                COUNT(CASE WHEN crown_copy THEN 1 END) as crown_notifications,
                COUNT(CASE WHEN constitutional_authority = 'crown' THEN 1 END) as crown_messages
            FROM a2a_messages
            WHERE created_at > NOW() - INTERVAL '24 hours'
            """
        )
        message_row = message_stats.fetchone()
        
        return {
            "task_requests": {
                "total": task_row.total_requests or 0,
                "completed": task_row.completed_requests or 0,
                "constitutional": task_row.constitutional_requests or 0,
                "completion_rate": (task_row.completed_requests or 0) / max(task_row.total_requests or 1, 1),
                "avg_completion_time_seconds": task_row.avg_completion_time_seconds or 0
            },
            "messages": {
                "total": message_row.total_messages or 0,
                "broadcasts": message_row.broadcast_messages or 0,
                "crown_notifications": message_row.crown_notifications or 0,
                "crown_messages": message_row.crown_messages or 0
            },
            "constitutional_compliance": {
                "parliamentary_oversight_rate": 1.0,  # All A2A is under oversight
                "constitutional_review_rate": (task_row.constitutional_requests or 0) / max(task_row.total_requests or 1, 1)
            }
        }