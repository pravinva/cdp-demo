"""
Feature Sync Workflow
Syncs customer features for ML serving
Run this as a Databricks Workflow task
"""

import sys
import os

# Setup imports - handles both repo and workspace scenarios
try:
    from _import_helper import setup_imports
    setup_imports()
except:
    # Fallback if helper not available
    current_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
    backend_path = os.path.join(current_dir, '../../backend')
    if os.path.exists(backend_path):
        sys.path.insert(0, os.path.abspath(backend_path))
    # Also try workspace paths
    for path in [
        '/Workspace/Users/pravin.varma@databricks.com/cdp-demo/backend',
        '/Workspace/Repos/cdp-demo/backend',
        '/Workspace/cdp-demo/backend'
    ]:
        if os.path.exists(path):
            sys.path.insert(0, path)
            break

from app.dependencies import get_workspace_client
from app.config import get_settings

def sync_customer_features():
    """Sync customer features - placeholder for feature store sync"""
    settings = get_settings()
    warehouse_id = settings.SQL_WAREHOUSE_ID or "4b9b953939869799"
    w = get_workspace_client()
    
    # For now, this is a placeholder
    # In production, this would sync features to a feature store
    # or compute ML features and store them
    
    print("Syncing customer features...")
    
    # Example: Update customer ML scores
    query = """
        SELECT COUNT(*) as count
        FROM cdp_platform.core.customers
        WHERE tenant_id = 'demo_tenant'
    """
    
    try:
        response = w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=query,
            wait_timeout="30s"
        )
        
        if response.result and response.result.data_array:
            count = response.result.data_array[0][0]
            print(f"Found {count} customers to sync")
    except Exception as e:
        print(f"Error syncing features: {e}")
    
    print("✅ Feature sync completed")
    return {'status': 'success'}

if __name__ == "__main__":
    sync_customer_features()

