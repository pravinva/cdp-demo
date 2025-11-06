"""
Journey Orchestrator Workflow
Processes customer journey states and advances customers through journeys
Run this as a Databricks Workflow task
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from app.services.journey_orchestrator_service import JourneyOrchestratorService
from app.config import get_settings

def process_all_tenants():
    """Process journey states for all tenants"""
    settings = get_settings()
    
    # For now, process demo_tenant
    # In production, you'd query for all active tenants
    tenants = ['demo_tenant']
    
    total_stats = {
        'agent_actions': 0,
        'waits_checked': 0,
        'branches_evaluated': 0,
        'completed': 0,
        'errors': 0
    }
    
    for tenant_id in tenants:
        try:
            print(f"Processing journeys for tenant: {tenant_id}")
            orchestrator = JourneyOrchestratorService(tenant_id)
            stats = orchestrator.process_journey_states()
            
            print(f"Tenant {tenant_id} stats:")
            print(f"  - Agent actions: {stats['agent_actions']}")
            print(f"  - Waits checked: {stats['waits_checked']}")
            print(f"  - Branches evaluated: {stats['branches_evaluated']}")
            print(f"  - Completed: {stats['completed']}")
            print(f"  - Errors: {stats['errors']}")
            
            # Aggregate stats
            for key in total_stats:
                total_stats[key] += stats[key]
        
        except Exception as e:
            print(f"Error processing tenant {tenant_id}: {e}")
            import traceback
            traceback.print_exc()
            total_stats['errors'] += 1
    
    print(f"\n✅ Journey orchestrator completed")
    print(f"Total stats: {total_stats}")
    return total_stats

if __name__ == "__main__":
    process_all_tenants()

