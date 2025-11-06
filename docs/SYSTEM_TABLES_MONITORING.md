# Databricks System Tables Integration

## Overview

The platform integrates with Databricks System Tables for comprehensive monitoring and observability. System Tables provide access to operational data including workflow runs, query history, warehouse metrics, and audit logs.

## Available System Tables

### 1. `system.compute.workflow_runs`
- Workflow/job execution history
- Success/failure status
- Duration and error messages
- Used for: Monitoring background workflows

### 2. `system.compute.query_history`
- SQL query execution history
- Query performance metrics
- Failed queries and errors
- Used for: Performance monitoring, debugging

### 3. `system.compute.warehouse_events`
- SQL warehouse start/stop events
- Warehouse utilization
- Used for: Cost optimization, capacity planning

### 4. `system.access.audit`
- API access logs
- Authentication events
- Failed login attempts
- Used for: Security monitoring, compliance

## API Endpoints

### Health & Monitoring

**GET `/api/monitoring/health`**
- Overall system health summary
- Includes alerts and recent failures

**GET `/health/detailed`**
- Enhanced health check with System Tables data
- Returns system health and alerts

### Workflow Monitoring

**GET `/api/monitoring/workflows`**
- List workflow runs
- Filter by: workflow_name, status, time range
- Query params: `workflow_name`, `status`, `hours`, `limit`

**GET `/api/monitoring/workflows/failed`**
- Get failed workflow runs
- Query params: `hours`, `limit`

### Query Monitoring

**GET `/api/monitoring/queries`**
- Query execution history
- Filter by: status, user_email, time range
- Query params: `status`, `user_email`, `hours`, `limit`

**GET `/api/monitoring/queries/failed`**
- Get failed queries
- Query params: `hours`, `limit`

### Warehouse Metrics

**GET `/api/monitoring/warehouse/metrics`**
- SQL warehouse metrics
- Event counts (starts, stops, failures)
- Query params: `warehouse_id`, `hours`

### Audit Logs

**GET `/api/monitoring/audit`**
- Access audit logs
- Filter by: action_name, user_email, status
- Query params: `action_name`, `user_email`, `status`, `hours`, `limit`

### Alerts

**GET `/api/monitoring/alerts`**
- Get all current alerts
- Includes workflow, query, and security alerts

**GET `/api/monitoring/alerts/workflows`**
- Workflow-specific alerts
- Query params: `hours`

**GET `/api/monitoring/alerts/security`**
- Security alerts (failed logins, etc.)
- Query params: `hours`

## Alert Thresholds

Default thresholds (configurable):
- **Failed workflows per hour**: 5
- **Failed queries per hour**: 10
- **Failed logins per hour**: 20
- **Consecutive failures**: 3

## Usage Examples

### Check System Health
```bash
curl http://localhost:8000/api/monitoring/health \
  -H "X-Tenant-ID: demo_tenant"
```

### Get Failed Workflows
```bash
curl "http://localhost:8000/api/monitoring/workflows/failed?hours=24" \
  -H "X-Tenant-ID: demo_tenant"
```

### Get All Alerts
```bash
curl http://localhost:8000/api/monitoring/alerts \
  -H "X-Tenant-ID: demo_tenant"
```

### Monitor Specific Workflow
```bash
curl "http://localhost:8000/api/monitoring/workflows?workflow_name=journey_orchestrator&hours=24" \
  -H "X-Tenant-ID: demo_tenant"
```

## Alert Severity Levels

- **Critical**: Consecutive workflow failures, security breaches
- **High**: Multiple workflow failures, failed logins
- **Medium**: Query failures, performance issues

## Integration with Background Jobs

The alerting service can be integrated into background workflows:

```python
# In workflow script
from app.services.alerting import AlertingService

alerting = AlertingService()
alerts = alerting.check_all_alerts()

if alerts["total_alerts"] > 0:
    # Send notifications
    for alert in alerts["alerts"]:
        alerting.send_alert_notification(alert)
```

## Next Steps

1. **Set up alert notifications** (email, Slack, PagerDuty)
2. **Create monitoring dashboard** using System Tables data
3. **Configure alert thresholds** per environment
4. **Set up scheduled alert checks** in workflows

