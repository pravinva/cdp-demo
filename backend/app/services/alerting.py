"""
Error Alerting Service
Monitors system health and sends alerts for errors
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from ..services.system_tables import SystemTablesService
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class AlertingService:
    """Service for monitoring and alerting on errors"""
    
    def __init__(self):
        self.system_tables = SystemTablesService()
        self.alert_thresholds = {
            "failed_workflows_per_hour": 5,
            "failed_queries_per_hour": 10,
            "failed_logins_per_hour": 20,
            "consecutive_failures": 3
        }
    
    def check_workflow_alerts(self, hours: int = 1) -> List[Dict[str, Any]]:
        """Check for workflow failures and generate alerts"""
        alerts = []
        
        failed_workflows = self.system_tables.get_failed_workflows(hours=hours)
        
        if len(failed_workflows) >= self.alert_thresholds["failed_workflows_per_hour"]:
            alerts.append({
                "severity": "high",
                "type": "workflow_failures",
                "message": f"{len(failed_workflows)} workflow failures in last {hours} hour(s)",
                "count": len(failed_workflows),
                "workflows": failed_workflows[:10],
                "timestamp": datetime.now().isoformat()
            })
        
        # Check for consecutive failures
        workflow_failures_by_name = {}
        for workflow in failed_workflows:
            name = workflow.get('workflow_name', 'unknown')
            if name not in workflow_failures_by_name:
                workflow_failures_by_name[name] = []
            workflow_failures_by_name[name].append(workflow)
        
        for workflow_name, failures in workflow_failures_by_name.items():
            if len(failures) >= self.alert_thresholds["consecutive_failures"]:
                alerts.append({
                    "severity": "critical",
                    "type": "consecutive_workflow_failures",
                    "message": f"Workflow '{workflow_name}' has failed {len(failures)} times",
                    "workflow_name": workflow_name,
                    "failures": failures,
                    "timestamp": datetime.now().isoformat()
                })
        
        return alerts
    
    def check_query_alerts(self, hours: int = 1) -> List[Dict[str, Any]]:
        """Check for query failures and generate alerts"""
        alerts = []
        
        failed_queries = self.system_tables.get_failed_queries(hours=hours)
        
        if len(failed_queries) >= self.alert_thresholds["failed_queries_per_hour"]:
            alerts.append({
                "severity": "medium",
                "type": "query_failures",
                "message": f"{len(failed_queries)} query failures in last {hours} hour(s)",
                "count": len(failed_queries),
                "queries": failed_queries[:10],
                "timestamp": datetime.now().isoformat()
            })
        
        return alerts
    
    def check_security_alerts(self, hours: int = 1) -> List[Dict[str, Any]]:
        """Check for security issues (failed logins, etc.)"""
        alerts = []
        
        failed_logins = self.system_tables.get_failed_logins(hours=hours)
        
        if len(failed_logins) >= self.alert_thresholds["failed_logins_per_hour"]:
            alerts.append({
                "severity": "high",
                "type": "security_alert",
                "message": f"{len(failed_logins)} failed login attempts in last {hours} hour(s)",
                "count": len(failed_logins),
                "attempts": failed_logins[:10],
                "timestamp": datetime.now().isoformat()
            })
        
        return alerts
    
    def check_all_alerts(self) -> Dict[str, Any]:
        """Check all alert types and return summary"""
        workflow_alerts = self.check_workflow_alerts()
        query_alerts = self.check_query_alerts()
        security_alerts = self.check_security_alerts()
        
        all_alerts = workflow_alerts + query_alerts + security_alerts
        
        # Log alerts
        for alert in all_alerts:
            severity = alert.get("severity", "info")
            message = alert.get("message", "Unknown alert")
            
            if severity == "critical":
                logger.critical(f"ALERT: {message}", extra={"alert": alert})
            elif severity == "high":
                logger.error(f"ALERT: {message}", extra={"alert": alert})
            elif severity == "medium":
                logger.warning(f"ALERT: {message}", extra={"alert": alert})
            else:
                logger.info(f"ALERT: {message}", extra={"alert": alert})
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_alerts": len(all_alerts),
            "critical": len([a for a in all_alerts if a.get("severity") == "critical"]),
            "high": len([a for a in all_alerts if a.get("severity") == "high"]),
            "medium": len([a for a in all_alerts if a.get("severity") == "medium"]),
            "alerts": all_alerts
        }
    
    def send_alert_notification(self, alert: Dict[str, Any]):
        """Send alert notification (email, Slack, etc.)"""
        # TODO: Integrate with notification service
        # For now, just log
        logger.error(f"ALERT NOTIFICATION: {alert.get('message')}", extra={"alert": alert})
        
        # In production, send via:
        # - Email (SendGrid)
        # - Slack webhook
        # - PagerDuty
        # - Databricks Alerts API

