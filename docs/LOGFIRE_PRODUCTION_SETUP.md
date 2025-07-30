# Logfire Production Setup Guide
## Westminster Parliamentary AI System Observability

This guide provides comprehensive instructions for setting up Logfire observability for the Triad Model production environment, including dashboards, alerts, telemetry, and monitoring for the Westminster Parliamentary AI System.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Dashboard Configuration](#dashboard-configuration)
3. [Alert Setup](#alert-setup)
4. [Telemetry Configuration](#telemetry-configuration)
5. [Agent Performance Monitoring](#agent-performance-monitoring)
6. [Constitutional Oversight Dashboards](#constitutional-oversight-dashboards)
7. [Parliamentary Session Tracking](#parliamentary-session-tracking)
8. [Database Monitoring with Prisma](#database-monitoring-with-prisma)
9. [Production Deployment](#production-deployment)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

### Environment Setup
```bash
# Install dependencies
pip install logfire>=4.0.0 prisma==0.13.1 pydantic-ai>=0.0.12

# Set environment variables
export LOGFIRE_TOKEN="pylf_v1_us_RBzlVBKMK2kWbCh8nYwT6qzq8cbpjqfSczvLZ5zq8wQq"
export DATABASE_URL="file:./data/triad_production.db"
export TRIAD_ENV="production"
```

### Logfire Account Configuration
1. Create a Logfire project named "triadmodel"
2. Generate write token: `pylf_v1_us_RBzlVBKMK2kWbCh8nYwT6qzq8cbpjqfSczvLZ5zq8wQq`
3. Generate read token: `pylf_v1_us_RCN2RNnwh1RZBS2tk94TLcxDD29ZF9cnNnqZZrWQv6QK`

## Dashboard Configuration

### 1. Constitutional Agents Dashboard

Create a dashboard to monitor the four constitutional agents:

```sql
-- Agent Activity Overview
SELECT 
    agent,
    activity,
    COUNT(*) as activity_count,
    AVG(duration) as avg_duration_ms
FROM logs 
WHERE system = 'triad-model' 
    AND component = 'agents'
    AND timestamp > NOW() - INTERVAL '1 hour'
GROUP BY agent, activity
ORDER BY activity_count DESC;

-- Constitutional Authority Distribution
SELECT 
    constitutional_authority,
    COUNT(*) as event_count,
    MAX(timestamp) as last_activity
FROM logs 
WHERE system = 'triad-model'
    AND constitutional_authority IS NOT NULL
GROUP BY constitutional_authority;
```

**Dashboard Widgets:**
- **Time Series Chart**: Agent activity over time
- **Bar Chart**: Tasks by constitutional authority
- **Table**: Recent agent activities with constitutional context
- **Pie Chart**: Activity distribution by agent type

### 2. Parliamentary Session Dashboard

Monitor parliamentary proceedings and democratic processes:

```sql
-- Active Parliamentary Sessions
SELECT 
    session_type,
    constitutional_authority,
    COUNT(*) as session_count,
    AVG(EXTRACT(EPOCH FROM (ended_at - started_at))) as avg_duration_seconds
FROM logs 
WHERE component = 'parliamentary'
    AND parliamentary_event IS NOT NULL
    AND timestamp > NOW() - INTERVAL '24 hours'
GROUP BY session_type, constitutional_authority;

-- Constitutional Events Timeline
SELECT 
    timestamp,
    constitutional_event,
    constitutional_authority,
    details
FROM logs 
WHERE component = 'constitutional'
    AND priority = 'high'
ORDER BY timestamp DESC
LIMIT 50;
```

**Dashboard Widgets:**
- **Timeline**: Constitutional events chronology
- **Gauge**: Active parliamentary sessions
- **Table**: Recent parliamentary actions
- **Heat Map**: Constitutional authority activity patterns

### 3. System Health Dashboard

Monitor overall system performance and constitutional compliance:

```sql
-- System Metrics Overview
SELECT 
    metric_name,
    metric_value,
    metric_unit,
    timestamp
FROM logs 
WHERE triad_component = 'metrics'
    AND timestamp > NOW() - INTERVAL '1 hour'
ORDER BY timestamp DESC;

-- Constitutional Compliance Rate
SELECT 
    constitutional_compliant,
    COUNT(*) as review_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM logs 
WHERE component = 'constitutional'
    AND constitutional_compliant IS NOT NULL
GROUP BY constitutional_compliant;
```

**Dashboard Widgets:**
- **Number Display**: Constitutional compliance rate
- **Line Chart**: System performance metrics
- **Status Indicator**: Database connection health
- **Table**: Recent constitutional reviews

## Alert Setup

### 1. Constitutional Violation Alerts

Create alerts for constitutional compliance issues:

```yaml
# Constitutional Violation Alert
name: "Constitutional Violation Detected"
condition: |
  SELECT COUNT(*) 
  FROM logs 
  WHERE component = 'constitutional' 
    AND constitutional_compliant = false
    AND timestamp > NOW() - INTERVAL '5 minutes'
threshold: 1
severity: "critical"
notification:
  webhook_url: "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
  message: "🚨 Constitutional violation detected in Triad Model system"
```

### 2. Agent Performance Alerts

Monitor agent responsiveness and task completion:

```yaml
# Agent Task Failure Alert
name: "Agent Task Failures"
condition: |
  SELECT COUNT(*) 
  FROM logs 
  WHERE component = 'agents' 
    AND level = 'error'
    AND timestamp > NOW() - INTERVAL '10 minutes'
threshold: 3
severity: "warning"
notification:
  webhook_url: "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
  message: "⚠️ Multiple agent task failures detected"
```

### 3. Parliamentary Session Alerts

Alert on parliamentary process anomalies:

```yaml
# Long Running Parliamentary Session
name: "Parliamentary Session Timeout"
condition: |
  SELECT COUNT(*) 
  FROM logs 
  WHERE component = 'parliamentary' 
    AND session_type IS NOT NULL
    AND timestamp < NOW() - INTERVAL '30 minutes'
    AND ended_at IS NULL
threshold: 1
severity: "warning"
notification:
  webhook_url: "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
  message: "⏰ Parliamentary session running longer than expected"
```

## Telemetry Configuration

### Auto-Instrumentation Setup

The system automatically instruments key components:

```python
# Already configured in triad/core/logfire_config.py
def _setup_auto_instrumentation(self):
    """Set up auto-instrumentation for various integrations."""
    try:
        # FastAPI endpoints and middleware
        logfire.instrument_fastapi()
        
        # HTTP client requests
        logfire.instrument_httpx()
        logfire.instrument_requests()
        
        # Database operations
        logfire.instrument_sqlite3()
        logfire.instrument_sqlalchemy()
        
        # Pydantic AI agent interactions
        logfire.instrument_pydantic_ai()
        
        # System resource monitoring
        logfire.instrument_system_metrics()
        
    except Exception as e:
        print(f"⚠️  Some auto-instrumentation failed: {e}")
```

### Custom Span Configuration

For parliamentary sessions and constitutional events:

```python
# Example usage in your agents
from triad.core.logfire_config import get_logfire_config

logger = get_logfire_config()

# Parliamentary session tracking
with logger.parliamentary_session_span("question_period", ["planner", "executor"]) as span:
    # Parliamentary proceedings here
    span.set_attribute("session.outcome", "motion_passed")

# Agent task execution
async with logger.agent_task_span("planner", "policy_analysis", task_data) as span:
    # Agent work here
    span.set_attribute("task.constitutional_basis", "legislative")
```

## Agent Performance Monitoring

### Key Metrics to Track

1. **Task Completion Rate**
   - Success/failure ratio by agent
   - Average task duration
   - Queue depth and backlog

2. **Constitutional Compliance**
   - Compliance review pass rate
   - Constitutional violation frequency
   - Authority escalation patterns

3. **Parliamentary Efficiency**
   - Session duration patterns
   - Motion pass/fail rates
   - Question period effectiveness

### Performance Queries

```sql
-- Agent Task Performance
SELECT 
    agent,
    COUNT(*) as total_tasks,
    SUM(CASE WHEN level = 'error' THEN 1 ELSE 0 END) as failed_tasks,
    ROUND(AVG(duration_ms), 2) as avg_duration_ms
FROM spans 
WHERE span_name LIKE 'agent-task-%'
    AND timestamp > NOW() - INTERVAL '1 day'
GROUP BY agent
ORDER BY total_tasks DESC;

-- Constitutional Authority Workload
SELECT 
    constitutional_authority,
    COUNT(*) as events,
    MAX(timestamp) as last_activity
FROM logs 
WHERE constitutional_authority IS NOT NULL
    AND timestamp > NOW() - INTERVAL '1 day'
GROUP BY constitutional_authority;
```

## Constitutional Oversight Dashboards

### Compliance Monitoring

Create specialized views for constitutional oversight:

```sql
-- Constitutional Review Summary
SELECT 
    review_type,
    target_type,
    constitutional_compliant,
    COUNT(*) as review_count,
    STRING_AGG(DISTINCT reviewing_agent, ', ') as reviewing_agents
FROM logs 
WHERE component = 'constitutional'
    AND review_type IS NOT NULL
GROUP BY review_type, target_type, constitutional_compliant
ORDER BY review_count DESC;

-- Violation Trends
SELECT 
    DATE_TRUNC('hour', timestamp) as hour,
    COUNT(*) as violation_count
FROM logs 
WHERE constitutional_compliant = false
    AND timestamp > NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour;
```

### Authority Separation Tracking

Monitor separation of powers:

```sql
-- Cross-Authority Interactions
SELECT 
    source_authority,
    target_authority,
    interaction_type,
    COUNT(*) as interaction_count
FROM logs 
WHERE source_authority != target_authority
    AND timestamp > NOW() - INTERVAL '1 day'
GROUP BY source_authority, target_authority, interaction_type;
```

## Parliamentary Session Tracking

### Session Analytics

```sql
-- Parliamentary Session Effectiveness
SELECT 
    session_type,
    AVG(EXTRACT(EPOCH FROM (session_end - session_start))) as avg_duration_seconds,
    COUNT(*) as total_sessions,
    SUM(CASE WHEN session_outcome = 'successful' THEN 1 ELSE 0 END) as successful_sessions
FROM parliamentary_sessions 
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY session_type;

-- Motion Success Rate
SELECT 
    motion_type,
    COUNT(*) as total_motions,
    SUM(CASE WHEN vote_result = 'passed' THEN 1 ELSE 0 END) as passed_motions,
    ROUND(SUM(CASE WHEN vote_result = 'passed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as pass_rate
FROM parliamentary_motions 
GROUP BY motion_type;
```

## Database Monitoring with Prisma

### Prisma Operation Tracking

The system automatically tracks database operations:

```python
# Database operation spans are automatically created
async def create_agent(self, name: str, constitutional_authority: str):
    # This operation is automatically instrumented
    agent = await self.client.agent.create(
        data={
            "name": name,
            "constitutionalAuthority": constitutional_authority
        }
    )
    
    # Custom logging with constitutional context
    self.logger.info(
        "Agent created",
        agent_name=name,
        constitutional_authority=constitutional_authority,
        parliamentary_accountability=True
    )
```

### Database Health Monitoring

```sql
-- Database Operation Performance
SELECT 
    operation_type,
    table_name,
    COUNT(*) as operation_count,
    AVG(duration_ms) as avg_duration_ms,
    MAX(duration_ms) as max_duration_ms
FROM database_operations 
WHERE timestamp > NOW() - INTERVAL '1 hour'
GROUP BY operation_type, table_name
ORDER BY avg_duration_ms DESC;

-- Connection Pool Health
SELECT 
    timestamp,
    active_connections,
    idle_connections,
    max_connections
FROM connection_pool_metrics 
WHERE timestamp > NOW() - INTERVAL '1 hour'
ORDER BY timestamp DESC;
```

## Production Deployment

### Environment Configuration

```bash
# Production environment variables
export TRIAD_ENV=production
export LOGFIRE_TOKEN=pylf_v1_us_RBzlVBKMK2kWbCh8nYwT6qzq8cbpjqfSczvLZ5zq8wQq
export DATABASE_URL=file:./data/triad_production.db
export JWT_SECRET=gsZWHujNKLBcvzKOXZ6pxxSc33Stw1CgX0EJIHqs-GVFyF3wFuj2Oi76PCsPEvQ1sJ-tsTHy9L6JuzbbDCzTvg

# Optional: Enhanced logging
export LOGFIRE_CONSOLE=true
export LOGFIRE_INSPECT_ARGUMENTS=true
```

### Docker Configuration

```dockerfile
# Add to your Dockerfile
ENV LOGFIRE_TOKEN=pylf_v1_us_RBzlVBKMK2kWbCh8nYwT6qzq8cbpjqfSczvLZ5zq8wQq
ENV TRIAD_ENV=production

# Install observability dependencies
RUN pip install logfire>=4.0.0
```

### Process Manager Configuration

```bash
# Using PM2 for process management
pm2 start triad_app.py --name "triad-model" --env production

# Environment file for PM2
# ecosystem.config.js
module.exports = {
  apps: [{
    name: 'triad-model',
    script: 'python',
    args: 'main.py',
    env: {
      TRIAD_ENV: 'production',
      LOGFIRE_TOKEN: 'pylf_v1_us_RBzlVBKMK2kWbCh8nYwT6qzq8cbpjqfSczvLZ5zq8wQq'
    }
  }]
};
```

## Troubleshooting

### Common Issues

1. **Logfire Connection Failures**
   ```bash
   # Check token validity
   curl -H "Authorization: Bearer pylf_v1_us_RBzlVBKMK2kWbCh8nYwT6qzq8cbpjqfSczvLZ5zq8wQq" \
        https://api.logfire.dev/health
   
   # Verify fallback logging
   python -c "from triad.core.logfire_config import initialize_logfire; print(initialize_logfire())"
   ```

2. **Missing Spans or Traces**
   ```python
   # Enable debug logging
   import logging
   logging.getLogger('logfire').setLevel(logging.DEBUG)
   ```

3. **Database Instrumentation Issues**
   ```python
   # Manually instrument if auto-instrumentation fails
   import logfire
   logfire.instrument_sqlite3()
   ```

### Health Check Endpoints

```python
# Add to your FastAPI app
@app.get("/health/logfire")
async def logfire_health():
    from triad.core.logfire_config import get_logfire_config
    config = get_logfire_config()
    return {
        "configured": config.configured,
        "fallback_mode": config.fallback_mode,
        "instrumentation": "enabled"
    }
```

### Performance Optimization

1. **Sampling Configuration**
   ```python
   # Reduce trace volume in high-traffic scenarios
   logfire.configure(
       sampling_rate=0.1  # Sample 10% of traces
   )
   ```

2. **Batch Export**
   ```python
   # Configure batch export for better performance
   logfire.configure(
       batch_export=True,
       max_batch_size=512
   )
   ```

## Integration with Westminster Parliamentary System

### Constitutional Compliance Dashboards

1. **Authority Separation Monitor**: Track interactions between legislative, executive, judicial, and crown authorities
2. **Democratic Process Tracker**: Monitor parliamentary sessions, votes, and question periods
3. **Constitutional Review Pipeline**: Track compliance reviews and violation remediation

### Parliamentary Accountability Features

1. **Hansard-style Logging**: Complete record of all parliamentary proceedings
2. **Question Period Analytics**: Track question-answer patterns and response times
3. **Motion Tracking**: Monitor proposal, debate, and voting patterns
4. **Constitutional Crisis Detection**: Automated alerts for potential constitutional violations

### Agent Constitutional Roles

- **Planner Agent**: Legislative authority monitoring and policy development tracking
- **Executor Agent**: Executive authority monitoring and implementation tracking  
- **Evaluator Agent**: Judicial authority monitoring and compliance review tracking
- **Overwatch Agent**: Crown authority monitoring and constitutional oversight tracking

This setup provides comprehensive observability for the Westminster Parliamentary AI System, ensuring constitutional compliance, democratic accountability, and system reliability in production environments.