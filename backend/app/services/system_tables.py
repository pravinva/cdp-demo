"""
Databricks System Tables Integration
Query system tables for monitoring and observability
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from ..dependencies import get_workspace_client
from ..config import get_settings

settings = get_settings()


class SystemTablesService:
    """Service for querying Databricks System Tables"""
    
    def __init__(self):
        self.w = get_workspace_client()
        self.warehouse_id = settings.SQL_WAREHOUSE_ID or "4b9b953939869799"
    
    def get_workflow_runs(
        self,
        workflow_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get workflow/job runs from system.compute.workflow_runs
        """
        where_clauses = []
        
        if workflow_name:
            where_clauses.append(f"workflow_name = '{workflow_name}'")
        if start_time:
            where_clauses.append(f"start_time >= timestamp('{start_time.isoformat()}')")
        if end_time:
            where_clauses.append(f"end_time <= timestamp('{end_time.isoformat()}')")
        if status:
            where_clauses.append(f"status = '{status}'")
        
        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        query = f"""
            SELECT 
                workflow_id,
                workflow_name,
                run_id,
                start_time,
                end_time,
                status,
                duration_ms,
                error_message
            FROM system.compute.workflow_runs
            WHERE {where_clause}
            ORDER BY start_time DESC
            LIMIT {limit}
        """
        
        runs = []
        try:
            response = self.w.statement_execution.execute_statement(
                warehouse_id=self.warehouse_id,
                statement=query,
                wait_timeout=30
            )
            
            if response.result and response.result.data_array:
                columns = [col.name for col in response.manifest.schema.columns] if response.manifest and response.manifest.schema else []
                for row in response.result.data_array:
                    run_dict = {columns[i]: row[i] for i in range(len(columns))}
                    runs.append(run_dict)
        except Exception as e:
            print(f"Error querying workflow runs: {e}")
        
        return runs
    
    def get_failed_workflows(
        self,
        hours: int = 24,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get failed workflow runs in last N hours"""
        start_time = datetime.now() - timedelta(hours=hours)
        
        return self.get_workflow_runs(
            start_time=start_time,
            status="FAILED",
            limit=limit
        )
    
    def get_query_history(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        status: Optional[str] = None,
        user_email: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get query history from system.compute.query_history
        """
        where_clauses = []
        
        if start_time:
            where_clauses.append(f"start_time >= timestamp('{start_time.isoformat()}')")
        if end_time:
            where_clauses.append(f"end_time <= timestamp('{end_time.isoformat()}')")
        if status:
            where_clauses.append(f"status = '{status}'")
        if user_email:
            where_clauses.append(f"user_email = '{user_email}'")
        
        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        query = f"""
            SELECT 
                query_id,
                query_text,
                user_email,
                start_time,
                end_time,
                duration_ms,
                status,
                error_message,
                rows_produced
            FROM system.compute.query_history
            WHERE {where_clause}
            ORDER BY start_time DESC
            LIMIT {limit}
        """
        
        queries = []
        try:
            response = self.w.statement_execution.execute_statement(
                warehouse_id=self.warehouse_id,
                statement=query,
                wait_timeout=30
            )
            
            if response.result and response.result.data_array:
                columns = [col.name for col in response.manifest.schema.columns] if response.manifest and response.manifest.schema else []
                for row in response.result.data_array:
                    query_dict = {columns[i]: row[i] for i in range(len(columns))}
                    queries.append(query_dict)
        except Exception as e:
            print(f"Error querying query history: {e}")
        
        return queries
    
    def get_failed_queries(
        self,
        hours: int = 24,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get failed queries in last N hours"""
        start_time = datetime.now() - timedelta(hours=hours)
        
        return self.get_query_history(
            start_time=start_time,
            status="FAILED",
            limit=limit
        )
    
    def get_warehouse_metrics(
        self,
        warehouse_id: Optional[str] = None,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get SQL warehouse metrics from system.compute.warehouse_events
        """
        start_time = datetime.now() - timedelta(hours=hours)
        
        where_clause = f"timestamp >= timestamp('{start_time.isoformat()}')"
        if warehouse_id:
            where_clause += f" AND warehouse_id = '{warehouse_id}'"
        
        query = f"""
            SELECT 
                warehouse_id,
                COUNT(*) as event_count,
                SUM(CASE WHEN event_type = 'start' THEN 1 ELSE 0 END) as starts,
                SUM(CASE WHEN event_type = 'stop' THEN 1 ELSE 0 END) as stops,
                SUM(CASE WHEN event_type = 'fail' THEN 1 ELSE 0 END) as failures
            FROM system.compute.warehouse_events
            WHERE {where_clause}
            GROUP BY warehouse_id
        """
        
        metrics = {}
        try:
            response = self.w.statement_execution.execute_statement(
                warehouse_id=self.warehouse_id,
                statement=query,
                wait_timeout=30
            )
            
            if response.result and response.result.data_array:
                columns = [col.name for col in response.manifest.schema.columns] if response.manifest and response.manifest.schema else []
                for row in response.result.data_array:
                    row_dict = {columns[i]: row[i] for i in range(len(columns))}
                    metrics[row_dict.get('warehouse_id', 'unknown')] = row_dict
        except Exception as e:
            print(f"Error querying warehouse metrics: {e}")
        
        return metrics
    
    def get_audit_logs(
        self,
        action_name: Optional[str] = None,
        user_email: Optional[str] = None,
        status: Optional[str] = None,
        hours: int = 24,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get audit logs from system.access.audit
        """
        start_time = datetime.now() - timedelta(hours=hours)
        
        where_clauses = [f"timestamp >= timestamp('{start_time.isoformat()}')"]
        
        if action_name:
            where_clauses.append(f"action_name = '{action_name}'")
        if user_email:
            where_clauses.append(f"user_email = '{user_email}'")
        if status:
            where_clauses.append(f"status = '{status}'")
        
        where_clause = " AND ".join(where_clauses)
        
        query = f"""
            SELECT 
                timestamp,
                user_email,
                action_name,
                request_id,
                status,
                service_name,
                method_name,
                request_params
            FROM system.access.audit
            WHERE {where_clause}
            ORDER BY timestamp DESC
            LIMIT {limit}
        """
        
        logs = []
        try:
            response = self.w.statement_execution.execute_statement(
                warehouse_id=self.warehouse_id,
                statement=query,
                wait_timeout=30
            )
            
            if response.result and response.result.data_array:
                columns = [col.name for col in response.manifest.schema.columns] if response.manifest and response.manifest.schema else []
                for row in response.result.data_array:
                    log_dict = {columns[i]: row[i] for i in range(len(columns))}
                    logs.append(log_dict)
        except Exception as e:
            print(f"Error querying audit logs: {e}")
        
        return logs
    
    def get_failed_logins(
        self,
        hours: int = 24,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get failed login attempts"""
        return self.get_audit_logs(
            action_name="login",
            status="FAILED",
            hours=hours,
            limit=limit
        )
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary from system tables"""
        now = datetime.now()
        last_24h = now - timedelta(hours=24)
        
        failed_workflows = self.get_failed_workflows(hours=24)
        failed_queries = self.get_failed_queries(hours=24)
        failed_logins = self.get_failed_logins(hours=24)
        warehouse_metrics = self.get_warehouse_metrics(hours=24)
        
        return {
            "timestamp": now.isoformat(),
            "last_24_hours": {
                "failed_workflows": len(failed_workflows),
                "failed_queries": len(failed_queries),
                "failed_logins": len(failed_logins),
                "warehouse_events": warehouse_metrics
            },
            "recent_failures": {
                "workflows": failed_workflows[:5],
                "queries": failed_queries[:5],
                "logins": failed_logins[:5]
            }
        }

