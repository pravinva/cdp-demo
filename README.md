# Databricks Customer Intelligence Platform (CDP)

A native Databricks Customer Intelligence Platform with identity resolution, relationship intelligence, agentic AI activation, and multi-channel orchestration.

## Features

- **Native to Lakehouse** - All data in Unity Catalog, zero data movement
- **Agentic AI** - Autonomous agents that analyze each customer and execute personalized campaigns
- **Journey Orchestration** - Multi-step customer journeys with state machine orchestration
- **Identity Resolution** - Match groups that unify anonymous and known customer touchpoints
- **Relationship Intelligence** - Graph-based household/network understanding with visual graph viewer
- **Multi-Channel Activation** - Email, SMS, Push, Ads, Real-time web
- **SQL Execution API** - Backend uses Databricks SQL Execution API for local development without Databricks Connect
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
- Databricks SQL Warehouse (for SQL Execution API)
- Databricks CLI configured (`~/.databrickscfg`) OR environment variables
- Python 3.10+
- Node.js 18+ (for frontend)

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
   export SQL_WAREHOUSE_ID=your-warehouse-id  # Optional, defaults to hardcoded ID
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

5. **Populate Identity Graph:**
```bash
# Option A: Run SQL script directly in Databricks SQL Editor
cat backend/scripts/populate_identity_graph.sql

# Option B: Run via Python script
python backend/scripts/populate_identity_graph.py
```

6. **Start backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

7. **Start frontend:**
```bash
cd frontend
npm install
npm run dev
```

8. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Project Structure

```
databricks-cdp-platform/
├── backend/          # FastAPI backend
├── frontend/         # React frontend
├── infrastructure/   # Databricks workflows and apps
├── docs/            # Documentation
└── scripts/         # Utility scripts
```

## Key Components

### Identity Resolution
- **Match Groups**: Unify anonymous and known customer touchpoints across devices and channels
- **Identity Graph**: Visual representation of customer relationships and households
- **Household Detection**: Automatically identify family members sharing devices/IPs

### Agentic AI
- **Marketing Agent**: Analyzes customer context and makes personalized campaign decisions
- **Agent Tools**: Unity Catalog functions that provide customer context and enable actions
- **Decision Tracking**: Full audit trail of agent decisions with reasoning

### Journey Orchestration
- **State Machine**: Multi-step customer journeys with conditional branching
- **Journey Analytics**: Track customer progression through journey stages
- **Event-Driven**: Journeys triggered by customer events and behaviors

## Documentation

See `docs/` directory for detailed documentation on:
- **Databricks Apps Architecture** (`docs/DATABRICKS_APPS.md`) - How APIs are exposed
- **Deployment Guide** (`docs/DEPLOYMENT.md`) - How to deploy to Databricks
- **Testing Guide** (`docs/TESTING.md`) - Testing strategies and examples
- **Quick Start** (`QUICKSTART.md`) - Step-by-step setup guide
- **Status** (`STATUS.md`) - Current implementation status

## Recent Updates

- ✅ **Identity Graph Viewer**: Interactive visualization of customer relationships
- ✅ **SQL Execution API**: Backend migrated to use SQL Execution API for better local development
- ✅ **Agent Insights Dashboard**: View agent decisions, metrics, and performance
- ✅ **Identity Graph Data Population**: SQL scripts for populating match groups and graph edges
- ✅ **Frontend Pages**: Complete UI for Customers, Campaigns, Journeys, Agents, Analytics, and Identity Graph

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

