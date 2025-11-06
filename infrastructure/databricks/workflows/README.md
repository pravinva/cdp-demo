# Databricks Workflows Deployment Guide

This directory contains Databricks Workflow definitions for background processing.

## Workflows

### 1. Journey Orchestrator (`journey_orchestrator.yml`)
- **Schedule**: Every 5 minutes
- **Purpose**: Process active customer journey states and advance customers through journeys
- **Script**: `backend/scripts/workflows/journey_orchestrator.py`

### 2. Identity Resolution (`identity_resolution.yml`)
- **Schedule**: Every 4 hours
- **Purpose**: Process unmatched clickstream events and create match groups
- **Script**: `backend/scripts/workflows/identity_resolution.py`

### 3. Scheduled Deliveries (`scheduled_deliveries.yml`)
- **Schedule**: Every 5 minutes
- **Purpose**: Process scheduled message deliveries and send them
- **Script**: `backend/scripts/workflows/scheduled_deliveries.py`

### 4. Feature Sync (`feature_sync.yml`)
- **Schedule**: Every 15 minutes
- **Purpose**: Sync customer features for ML serving
- **Script**: `backend/scripts/workflows/feature_sync.py`

## Deployment Options

### Option 1: Deploy via Databricks CLI (Recommended)

```bash
# Deploy all workflows
databricks workflows deploy --workflows-dir infrastructure/databricks/workflows

# Or deploy individually
databricks workflows deploy infrastructure/databricks/workflows/journey_orchestrator.yml
```

### Option 2: Deploy via Databricks UI

1. Go to Databricks Workspace → Workflows
2. Click "Create" → "Workflow"
3. Import YAML file or create manually
4. Upload Python scripts to workspace
5. Configure schedule and notifications

### Option 3: Use Notebook Tasks (Easier for Development)

Convert Python scripts to Databricks notebooks and use notebook tasks:

```yaml
tasks:
  - task_key: process_journey_states
    notebook_task:
      notebook_path: /Workspace/Repos/cdp-demo/backend/scripts/workflows/journey_orchestrator
    max_retries: 2
    timeout_seconds: 3600
```

## Prerequisites

1. **Python Scripts**: Ensure workflow scripts are accessible in Databricks workspace
2. **Dependencies**: Backend dependencies must be installed in cluster/notebook environment
3. **Permissions**: Workflow service principal needs access to Unity Catalog tables
4. **Configuration**: `~/.databrickscfg` or environment variables configured

## Testing Workflows Locally

You can test workflow scripts locally before deploying:

```bash
cd backend/scripts/workflows
python journey_orchestrator.py
python identity_resolution.py
python scheduled_deliveries.py
python feature_sync.py
```

## Monitoring

- Workflow runs appear in Databricks Workflows UI
- Check logs in workflow run details
- Set up alerts for workflow failures (configured in YAML)

## Configuration

Workflows use:
- `~/.databrickscfg` for authentication (default)
- `SQL_WAREHOUSE_ID` from environment or config
- `cdp_platform.core` schema for all tables

