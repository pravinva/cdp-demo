# Databricks Customer Intelligence Platform (CDP)

A native Databricks Customer Intelligence Platform with identity resolution, relationship intelligence, agentic AI activation, and multi-channel orchestration.

## Features

- **Native to Lakehouse** - All data in Unity Catalog, zero data movement
- **Agentic AI** - Autonomous agents that analyze each customer and execute personalized campaigns
- **Journey Orchestration** - Multi-step customer journeys with state machine orchestration
- **Relationship Intelligence** - Graph-based household/network understanding
- **Multi-Channel Activation** - Email, SMS, Push, Ads, Real-time web
- **Complete Governance** - Full audit trail, explainable AI, compliance-ready

## Architecture

```
Frontend (React + TypeScript)
    ↓
Backend API (FastAPI)
    ↓
Intelligence Layer (Databricks Agent Framework, MLflow)
    ↓
Data Layer (Unity Catalog + Delta Lake)
```

## Technology Stack

- **Backend:** FastAPI, Python 3.10+, PySpark, Databricks SDK
- **Frontend:** React 18+, TypeScript, Material-UI, Recharts
- **Data:** Delta Lake, Unity Catalog, Delta Live Tables
- **AI/ML:** Databricks Agent Framework, MLflow, Foundation Model APIs
- **Infrastructure:** Databricks Apps, Serverless Compute

## Quick Start

### Prerequisites

- Databricks workspace with Unity Catalog enabled
- Databricks CLI configured (`~/.databrickscfg`) OR environment variables
- Python 3.10+

### Setup

1. **Configure Databricks credentials:**

   **Option A: Use Databricks CLI (Recommended)**
   ```bash
   # Ensure ~/.databrickscfg is configured
   databricks configure --token
   # The app will automatically use these credentials
   ```

   **Option B: Use environment variables**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your Databricks credentials
   export DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
   export DATABRICKS_TOKEN=dapi...
   ```

2. **Setup Unity Catalog:**
```bash
cd backend
python scripts/setup_unity_catalog.py
```

3. **Create UC functions:**
```bash
# Run SQL file in Databricks SQL Editor
cat scripts/create_uc_functions.sql
```

4. **Generate demo data:**
```bash
python scripts/seed_demo_data.py
```

5. **Start backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

6. **Start frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
databricks-cdp-platform/
├── backend/          # FastAPI backend
├── frontend/         # React frontend
├── infrastructure/   # Databricks workflows and apps
├── docs/            # Documentation
└── scripts/         # Utility scripts
```

## Documentation

See `docs/` directory for detailed documentation on:
- **Databricks Apps Architecture** (`docs/DATABRICKS_APPS.md`) - How APIs are exposed
- **Deployment Guide** (`docs/DEPLOYMENT.md`) - How to deploy to Databricks
- API documentation
- User guides
- Identity resolution
- Journey orchestration

## Deployment as Databricks App

This platform is designed to run as a **Databricks App**, which provides:

- ✅ **Automatic HTTPS URL**: `https://<workspace>.cloud.databricks.com/apps/cdp-platform`
- ✅ **Workspace Authentication**: Built-in Databricks auth
- ✅ **Direct Unity Catalog Access**: No separate database connections
- ✅ **Auto-Scaling**: Handles traffic automatically
- ✅ **Background Jobs**: Scheduled workflows for journey orchestration

Deploy with:
```bash
databricks apps deploy --app-spec infrastructure/databricks/apps/cdp-platform-app.yml
```

See `docs/DATABRICKS_APPS.md` for complete architecture details.

## License

Enterprise Production-Ready

