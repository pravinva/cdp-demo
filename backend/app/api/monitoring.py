"""
Monitoring API endpoints
System tables queries and health checks
"""

from fastapi import APIRouter, Depends, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..dependencies import get_tenant_context, get_workspace_client
from ..services.system_tables import SystemTablesService
from ..services.alerting import AlertingService
from ..config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/health")
async def get_system_health():
    """Get overall system health from System Tables"""
    system_tables = SystemTablesService()
    alerting = AlertingService()
    
    health_summary = system_tables.get_health_summary()
    alerts = alerting.check_all_alerts()
    
    return {
        "status": "healthy" if alerts["total_alerts"] == 0 else "degraded",
        "health_summary": health_summary,
        "alerts": alerts
    }


@router.get("/workflows")
async def get_workflow_runs(
    workflow_name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(100, ge=1, le=1000),
    tenant_id: str = Depends(get_tenant_context)
):
    """Get workflow runs from System Tables"""
    system_tables = SystemTablesService()
    
    start_time = datetime.now() - timedelta(hours=hours)
    
    runs = system_tables.get_workflow_runs(
        workflow_name=workflow_name,
        start_time=start_time,
        status=status,
        limit=limit
    )
    
    return {
        "workflow_runs": runs,
        "count": len(runs),
        "time_range_hours": hours
    }


@router.get("/workflows/failed")
async def get_failed_workflows(
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(50, ge=1, le=500),
    tenant_id: str = Depends(get_tenant_context)
):
    """Get failed workflow runs"""
    system_tables = SystemTablesService()
    
    failed = system_tables.get_failed_workflows(hours=hours, limit=limit)
    
    return {
        "failed_workflows": failed,
        "count": len(failed),
        "time_range_hours": hours
    }


@router.get("/queries")
async def get_query_history(
    status: Optional[str] = Query(None),
    user_email: Optional[str] = Query(None),
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(100, ge=1, le=1000),
    tenant_id: str = Depends(get_tenant_context)
):
    """Get query history from System Tables"""
    system_tables = SystemTablesService()
    
    start_time = datetime.now() - timedelta(hours=hours)
    
    queries = system_tables.get_query_history(
        start_time=start_time,
        status=status,
        user_email=user_email,
        limit=limit
    )
    
    return {
        "queries": queries,
        "count": len(queries),
        "time_range_hours": hours
    }


@router.get("/queries/failed")
async def get_failed_queries(
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(50, ge=1, le=500),
    tenant_id: str = Depends(get_tenant_context)
):
    """Get failed queries"""
    system_tables = SystemTablesService()
    
    failed = system_tables.get_failed_queries(hours=hours, limit=limit)
    
    return {
        "failed_queries": failed,
        "count": len(failed),
        "time_range_hours": hours
    }


@router.get("/warehouse/metrics")
async def get_warehouse_metrics(
    warehouse_id: Optional[str] = Query(None),
    hours: int = Query(24, ge=1, le=168),
    tenant_id: str = Depends(get_tenant_context)
):
    """Get SQL warehouse metrics"""
    system_tables = SystemTablesService()
    
    metrics = system_tables.get_warehouse_metrics(
        warehouse_id=warehouse_id,
        hours=hours
    )
    
    return {
        "warehouse_metrics": metrics,
        "time_range_hours": hours
    }


@router.get("/audit")
async def get_audit_logs(
    action_name: Optional[str] = Query(None),
    user_email: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(100, ge=1, le=1000),
    tenant_id: str = Depends(get_tenant_context)
):
    """Get audit logs from System Tables"""
    system_tables = SystemTablesService()
    
    logs = system_tables.get_audit_logs(
        action_name=action_name,
        user_email=user_email,
        status=status,
        hours=hours,
        limit=limit
    )
    
    return {
        "audit_logs": logs,
        "count": len(logs),
        "time_range_hours": hours
    }


@router.get("/alerts")
async def get_alerts(
    tenant_id: str = Depends(get_tenant_context)
):
    """Get current alerts from monitoring"""
    alerting = AlertingService()
    
    alerts = alerting.check_all_alerts()
    
    return alerts


@router.get("/alerts/workflows")
async def get_workflow_alerts(
    hours: int = Query(1, ge=1, le=24),
    tenant_id: str = Depends(get_tenant_context)
):
    """Get workflow-specific alerts"""
    alerting = AlertingService()
    
    alerts = alerting.check_workflow_alerts(hours=hours)
    
    return {
        "alerts": alerts,
        "count": len(alerts),
        "time_range_hours": hours
    }


@router.get("/alerts/security")
async def get_security_alerts(
    hours: int = Query(1, ge=1, le=24),
    tenant_id: str = Depends(get_tenant_context)
):
    """Get security alerts (failed logins, etc.)"""
    alerting = AlertingService()
    
    alerts = alerting.check_security_alerts(hours=hours)
    
    return {
        "alerts": alerts,
        "count": len(alerts),
        "time_range_hours": hours
    }

