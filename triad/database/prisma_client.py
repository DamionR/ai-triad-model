"""
Prisma Database Client for Triad Model

Database client using Prisma with compliance oversight
and organizational accountability.
"""

from typing import Dict, Any, List, Optional, AsyncContextManager
import asyncio
from datetime import datetime, timezone, timedelta
import logfire
from prisma import Prisma
from prisma.models import (
    Agent, Task, Workflow, MessageSession, AgentMessage,
    ParliamentarySession, ParliamentaryAction, QuestionPeriod,
    Motion, Vote, ConstitutionalReview, ValidationReport,
    AuditLog, SystemMetric, CrisisEvent
)


class TriadPrismaClient:
    """
    Prisma client for Triad Model with constitutional oversight.
    
    Provides database operations with parliamentary accountability
    and constitutional compliance tracking.
    """
    
    def __init__(self, logfire_logger: Optional[logfire] = None):
        self.logger = logfire_logger or logfire
        self.client = Prisma()
        self.connected = False
        
    async def connect(self) -> None:
        """Connect to the database with constitutional logging."""
        try:
            await self.client.connect()
            self.connected = True
            
            self.logger.info(
                "Database connected",
                client="prisma",
                constitutional_oversight=True
            )
            
        except Exception as e:
            self.logger.error(
                "Database connection failed",
                error=str(e),
                constitutional_accountability=True
            )
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from the database."""
        try:
            await self.client.disconnect()
            self.connected = False
            
            self.logger.info("Database disconnected")
            
        except Exception as e:
            self.logger.error(
                "Database disconnection failed",
                error=str(e)
            )
    
    def get_context(self) -> AsyncContextManager[Prisma]:
        """Get database context manager."""
        return self.client
    
    # Agent Operations
    async def create_agent(
        self,
        name: str,
        constitutional_authority: str,
        model: str = "claude-3-5-sonnet-20241022"
    ) -> Agent:
        """Create a new agent with constitutional registration."""
        try:
            agent = await self.client.agent.create(
                data={
                    "name": name,
                    "constitutionalAuthority": constitutional_authority,
                    "model": model
                }
            )
            
            self.logger.info(
                "Agent created",
                agent_name=name,
                constitutional_authority=constitutional_authority,
                parliamentary_accountability=True
            )
            
            return agent
            
        except Exception as e:
            self.logger.error(
                "Agent creation failed",
                agent_name=name,
                error=str(e)
            )
            raise
    
    async def get_agent_by_name(self, name: str) -> Optional[Agent]:
        """Get agent by name."""
        return await self.client.agent.find_unique(
            where={"name": name}
        )
    
    async def list_active_agents(self) -> List[Agent]:
        """List all active agents."""
        return await self.client.agent.find_many(
            where={"active": True}
        )
    
    # Task Operations
    async def create_task(
        self,
        task_type: str,
        description: str,
        requesting_agent_id: str,
        assigned_agent_id: str,
        priority: str = "medium",
        parameters: Optional[Dict[str, Any]] = None
    ) -> Task:
        """Create a new task with constitutional oversight."""
        try:
            task = await self.client.task.create(
                data={
                    "type": task_type,
                    "description": description,
                    "requestingAgentId": requesting_agent_id,
                    "assignedAgentId": assigned_agent_id,
                    "priority": priority,
                    "parameters": parameters or {}
                }
            )
            
            self.logger.info(
                "Task created",
                task_id=task.id,
                task_type=task_type,
                requesting_agent=requesting_agent_id,
                assigned_agent=assigned_agent_id,
                constitutional_oversight=True
            )
            
            return task
            
        except Exception as e:
            self.logger.error(
                "Task creation failed",
                error=str(e),
                constitutional_accountability=True
            )
            raise
    
    async def update_task_status(
        self,
        task_id: str,
        status: str,
        result: Optional[Dict[str, Any]] = None
    ) -> Task:
        """Update task status with parliamentary accountability."""
        update_data = {"status": status}
        
        if result:
            update_data["result"] = result
            
        if status == "completed":
            update_data["completedAt"] = datetime.now(timezone.utc)
        
        task = await self.client.task.update(
            where={"id": task_id},
            data=update_data
        )
        
        self.logger.info(
            "Task status updated",
            task_id=task_id,
            status=status,
            parliamentary_accountability=True
        )
        
        return task
    
    async def get_tasks_by_agent(
        self,
        agent_id: str,
        status: Optional[str] = None
    ) -> List[Task]:
        """Get tasks assigned to an agent."""
        where_clause = {"assignedAgentId": agent_id}
        if status:
            where_clause["status"] = status
            
        return await self.client.task.find_many(
            where=where_clause,
            order={"createdAt": "desc"}
        )
    
    # Message History Operations
    async def create_message_session(
        self,
        session_id: str,
        agent_id: str,
        constitutional_authority: str,
        parliamentary_session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MessageSession:
        """Create a new message session."""
        try:
            session = await self.client.messagesession.create(
                data={
                    "sessionId": session_id,
                    "agentId": agent_id,
                    "constitutionalAuthority": constitutional_authority,
                    "parliamentarySessionId": parliamentary_session_id,
                    "metadata": metadata or {}
                }
            )
            
            self.logger.info(
                "Message session created",
                session_id=session_id,
                agent_id=agent_id,
                constitutional_authority=constitutional_authority
            )
            
            return session
            
        except Exception as e:
            self.logger.error(
                "Message session creation failed",
                session_id=session_id,
                error=str(e)
            )
            raise
    
    async def add_message(
        self,
        session_id: str,
        agent_id: str,
        message_type: str,
        content: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_args: Optional[Dict[str, Any]] = None,
        parliamentary_context: Optional[Dict[str, Any]] = None
    ) -> AgentMessage:
        """Add a message to the session."""
        try:
            message = await self.client.agentmessage.create(
                data={
                    "sessionId": session_id,
                    "agentId": agent_id,
                    "messageType": message_type,
                    "content": content,
                    "toolName": tool_name,
                    "toolArgs": tool_args,
                    "parliamentaryContext": parliamentary_context
                }
            )
            
            # Update session last activity
            await self.client.messagesession.update(
                where={"sessionId": session_id},
                data={"lastActivity": datetime.now(timezone.utc)}
            )
            
            return message
            
        except Exception as e:
            self.logger.error(
                "Message creation failed",
                session_id=session_id,
                error=str(e)
            )
            raise
    
    async def get_session_messages(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[AgentMessage]:
        """Get messages from a session."""
        query_params = {
            "where": {"sessionId": session_id},
            "order": {"timestamp": "asc"}
        }
        
        if limit:
            query_params["take"] = limit
        
        return await self.client.agentmessage.find_many(**query_params)
    
    # Parliamentary Operations
    async def create_parliamentary_session(
        self,
        session_type: str,
        constitutional_authority: str,
        agenda: Optional[List[str]] = None,
        participants: Optional[List[str]] = None
    ) -> ParliamentarySession:
        """Create a new parliamentary session."""
        try:
            session = await self.client.parliamentarysession.create(
                data={
                    "sessionType": session_type,
                    "constitutionalAuthority": constitutional_authority,
                    "agenda": agenda or [],
                    "participants": participants or []
                }
            )
            
            self.logger.info(
                "Parliamentary session created",
                session_id=session.id,
                session_type=session_type,
                constitutional_authority=constitutional_authority,
                parliamentary_accountability=True
            )
            
            return session
            
        except Exception as e:
            self.logger.error(
                "Parliamentary session creation failed",
                error=str(e)
            )
            raise
    
    async def record_parliamentary_action(
        self,
        session_id: str,
        agent_id: str,
        action_type: str,
        content: str,
        constitutional_basis: Optional[str] = None
    ) -> ParliamentaryAction:
        """Record a parliamentary action."""
        try:
            action = await self.client.parliamentaryaction.create(
                data={
                    "sessionId": session_id,
                    "agentId": agent_id,
                    "actionType": action_type,
                    "content": content,
                    "constitutionalBasis": constitutional_basis
                }
            )
            
            self.logger.info(
                "Parliamentary action recorded",
                action_id=action.id,
                session_id=session_id,
                action_type=action_type,
                agent_id=agent_id,
                parliamentary_accountability=True
            )
            
            return action
            
        except Exception as e:
            self.logger.error(
                "Parliamentary action recording failed",
                error=str(e)
            )
            raise
    
    # Audit Operations
    async def log_audit_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None,
        workflow_id: Optional[str] = None
    ) -> AuditLog:
        """Log an audit event for constitutional accountability."""
        try:
            audit_log = await self.client.auditlog.create(
                data={
                    "eventType": event_type,
                    "eventData": event_data,
                    "agentId": agent_id,
                    "taskId": task_id,
                    "workflowId": workflow_id
                }
            )
            
            return audit_log
            
        except Exception as e:
            self.logger.error(
                "Audit logging failed",
                event_type=event_type,
                error=str(e)
            )
            raise
    
    async def get_audit_trail(
        self,
        agent_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """Get audit trail for parliamentary oversight."""
        where_clause = {}
        if agent_id:
            where_clause["agentId"] = agent_id
        if event_type:
            where_clause["eventType"] = event_type
        
        return await self.client.auditlog.find_many(
            where=where_clause,
            order={"timestamp": "desc"},
            take=limit
        )
    
    # System Health Operations
    async def record_system_metric(
        self,
        metric_type: str,
        metric_name: str,
        value: float,
        unit: str,
        agent_name: Optional[str] = None,
        component_name: Optional[str] = None
    ) -> SystemMetric:
        """Record a system metric."""
        try:
            metric = await self.client.systemmetric.create(
                data={
                    "metricType": metric_type,
                    "metricName": metric_name,
                    "value": value,
                    "unit": unit,
                    "agentName": agent_name,
                    "componentName": component_name
                }
            )
            
            return metric
            
        except Exception as e:
            self.logger.error(
                "System metric recording failed",
                error=str(e)
            )
            raise
    
    async def get_system_metrics(
        self,
        metric_type: Optional[str] = None,
        agent_name: Optional[str] = None,
        hours: int = 24
    ) -> List[SystemMetric]:
        """Get system metrics for monitoring."""
        where_clause = {}
        if metric_type:
            where_clause["metricType"] = metric_type
        if agent_name:
            where_clause["agentName"] = agent_name
        
        # Add time filter
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        where_clause["timestamp"] = {"gte": cutoff_time}
        
        return await self.client.systemmetric.find_many(
            where=where_clause,
            order={"timestamp": "desc"}
        )
    
    # Constitutional Review Operations
    async def create_constitutional_review(
        self,
        review_type: str,
        target_id: str,
        target_type: str,
        constitutional_compliant: bool,
        violations: List[str],
        recommendations: List[str],
        reviewing_agent: str,
        constitutional_authority: str
    ) -> ConstitutionalReview:
        """Create a constitutional compliance review."""
        try:
            review = await self.client.constitutionalreview.create(
                data={
                    "reviewType": review_type,
                    "targetId": target_id,
                    "targetType": target_type,
                    "constitutionalCompliant": constitutional_compliant,
                    "violations": violations,
                    "recommendations": recommendations,
                    "reviewingAgent": reviewing_agent,
                    "constitutionalAuthority": constitutional_authority
                }
            )
            
            self.logger.info(
                "Constitutional review created",
                review_id=review.id,
                target_type=target_type,
                target_id=target_id,
                constitutional_compliant=constitutional_compliant,
                violations_count=len(violations)
            )
            
            return review
            
        except Exception as e:
            self.logger.error(
                "Constitutional review creation failed",
                error=str(e)
            )
            raise
    
    # Health Check
    async def health_check(self) -> Dict[str, Any]:
        """Perform database health check."""
        try:
            # Test basic connectivity
            agent_count = await self.client.agent.count()
            task_count = await self.client.task.count()
            
            return {
                "status": "healthy",
                "connected": self.connected,
                "agent_count": agent_count,
                "task_count": task_count,
                "constitutional_oversight": True,
                "parliamentary_accountability": True
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e),
                "constitutional_oversight": False
            }


# Global Prisma client instance
prisma_client = TriadPrismaClient()


async def get_prisma_client() -> TriadPrismaClient:
    """Get the global Prisma client."""
    return prisma_client