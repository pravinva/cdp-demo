"""
Workflow Entry Points
These functions are called by Databricks Workflows
"""

# Journey Orchestrator entry point
def process_journey_states():
    """Entry point for journey orchestrator workflow"""
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))
    from scripts.workflows.journey_orchestrator import process_all_tenants
    return process_all_tenants()

# Identity Resolution entry point
def run_identity_resolution():
    """Entry point for identity resolution workflow"""
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))
    from scripts.workflows.identity_resolution import run_identity_resolution
    return run_identity_resolution()

# Scheduled Deliveries entry point
def process_scheduled_deliveries():
    """Entry point for scheduled deliveries workflow"""
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))
    from scripts.workflows.scheduled_deliveries import process_scheduled_deliveries
    return process_scheduled_deliveries()

# Feature Sync entry point
def sync_customer_features():
    """Entry point for feature sync workflow"""
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))
    from scripts.workflows.feature_sync import sync_customer_features
    return sync_customer_features()

