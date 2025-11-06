# Databricks CDP Platform - Deployment Guide

## Architecture Overview

This platform runs as a **Databricks App**, which provides:

- **Automatic HTTPS URL**: `https://<workspace>.cloud.databricks.com/apps/cdp-platform`
- **Workspace Authentication**: Built-in Databricks auth
- **Direct Unity Catalog Access**: No separate database connections needed
- **Auto-Scaling**: Handles traffic automatically
- **Background Jobs**: Scheduled workflows for journey orchestration

## Quick Deploy

### Prerequisites
- Databricks workspace with Unity Catalog enabled
- Databricks CLI configured (`~/.databrickscfg`)
- Docker installed (for building images)

### Steps

1. **Setup Unity Catalog** (one-time):
   ```bash
   cd backend
   python scripts/setup_unity_catalog.py
   ```

2. **Deploy Databricks App**:
   ```bash
   databricks apps deploy \
     --app-spec infrastructure/databricks/apps/cdp-platform-app.yml
   ```

3. **Access Your API**:
   - URL: `https://<workspace>.cloud.databricks.com/apps/cdp-platform`
   - Docs: `https://<workspace>.cloud.databricks.com/apps/cdp-platform/api/docs`

## Local Development

Run locally while developing:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Access at: `http://localhost:8000/api/docs`

## API Endpoints

- `GET /health` - Health check
- `GET /api/journeys` - List journeys
- `POST /api/journeys` - Create journey
- `POST /api/journeys/{id}/execute` - Execute journey
- `GET /api/journeys/{id}/progress` - Journey analytics

See `docs/DATABRICKS_APPS.md` for complete architecture details.

