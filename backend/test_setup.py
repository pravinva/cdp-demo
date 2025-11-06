#!/usr/bin/env python3
"""
Simple test script to verify API setup
Tests imports and basic functionality without starting the server
"""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing CDP Platform API Setup...")
print("=" * 50)

# Test 1: Configuration
print("\n1. Testing configuration...")
try:
    from app.config import get_settings
    settings = get_settings()
    print(f"   ✓ Config loaded - APP_NAME: {settings.APP_NAME}")
except Exception as e:
    print(f"   ✗ Config error: {e}")
    sys.exit(1)

# Test 2: Models
print("\n2. Testing models...")
try:
    from app.models.customer import Customer
    from app.models.campaign import Campaign
    from app.models.journey import JourneyDefinition
    print("   ✓ Models imported successfully")
except Exception as e:
    print(f"   ✗ Models error: {e}")
    sys.exit(1)

# Test 3: API Routes
print("\n3. Testing API routes...")
try:
    from app.api import journeys, customers, campaigns, agents, analytics, identity
    print(f"   ✓ Journeys router: {journeys.router}")
    print(f"   ✓ Customers router: {customers.router}")
    print(f"   ✓ Campaigns router: {campaigns.router}")
    print(f"   ✓ Agents router: {agents.router}")
    print(f"   ✓ Analytics router: {analytics.router}")
    print(f"   ✓ Identity router: {identity.router}")
except Exception as e:
    print(f"   ✗ API routes error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Main App
print("\n4. Testing FastAPI app...")
try:
    from app.main import app
    print(f"   ✓ FastAPI app created: {app.title}")
    print(f"   ✓ App version: {app.version}")
    
    # Check routes
    routes = [route.path for route in app.routes]
    print(f"   ✓ Total routes registered: {len(routes)}")
    print(f"   ✓ Sample routes:")
    for route in routes[:10]:
        print(f"      - {route}")
except Exception as e:
    print(f"   ✗ FastAPI app error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Services (might fail without Databricks connection, that's OK)
print("\n5. Testing services...")
try:
    from app.services.journey_orchestrator_service import JourneyOrchestratorService
    from app.services.agent_service import AgentService
    print("   ✓ Services imported successfully")
    print("   ⚠ Note: Services require Databricks connection to fully test")
except Exception as e:
    print(f"   ⚠ Services import warning: {e}")
    print("   (This is expected if Databricks SDK is not configured)")

print("\n" + "=" * 50)
print("✓ Basic API setup validation complete!")
print("\nTo start the server:")
print("  1. Install dependencies: pip3 install -r requirements.txt")
print("  2. Configure Databricks: Ensure ~/.databrickscfg is set up")
print("  3. Start server: uvicorn app.main:app --reload")
print("\nThe API will be available at: http://localhost:8000")
print("API docs at: http://localhost:8000/api/docs")

