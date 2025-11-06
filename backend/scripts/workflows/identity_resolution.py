"""
Identity Resolution Workflow
Processes clickstream events and creates match groups
Run this as a Databricks Workflow task
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from app.services.identity_resolution_service import IdentityResolutionService
from app.config import get_settings

def run_identity_resolution():
    """Run identity resolution for all tenants"""
    settings = get_settings()
    
    # For now, process demo_tenant
    # In production, you'd query for all active tenants
    tenants = ['demo_tenant']
    
    total_processed = 0
    total_match_groups = 0
    
    for tenant_id in tenants:
        try:
            print(f"Running identity resolution for tenant: {tenant_id}")
            service = IdentityResolutionService(tenant_id)
            result = service.run_identity_resolution(batch_size=10000)
            
            processed = result.get('processed', 0)
            match_groups = result.get('match_groups_created', 0)
            
            print(f"Tenant {tenant_id}:")
            print(f"  - Events processed: {processed}")
            print(f"  - Match groups created: {match_groups}")
            
            total_processed += processed
            total_match_groups += match_groups
        
        except Exception as e:
            print(f"Error processing tenant {tenant_id}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n✅ Identity resolution completed")
    print(f"Total events processed: {total_processed}")
    print(f"Total match groups created: {total_match_groups}")
    
    return {
        'processed': total_processed,
        'match_groups_created': total_match_groups
    }

if __name__ == "__main__":
    run_identity_resolution()

