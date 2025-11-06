# Testing Guide

## Quick Test (Without Installing Dependencies)

Run the setup validation script:
```bash
cd backend
python3 test_setup.py
```

This will check:
- ✓ Configuration loading
- ✓ Model imports
- ✓ API route registration
- ✓ FastAPI app structure

## Full Local Testing

### 1. Install Dependencies

```bash
cd backend
pip3 install -r requirements.txt
```

**Note:** Some packages may require additional setup:
- `pyspark` - Requires Java/JDK
- `databricks-sdk` - Requires `~/.databrickscfg` configuration
- MLflow - Will use Databricks workspace MLflow

### 2. Configure Databricks Credentials

Ensure `~/.databrickscfg` is configured:
```bash
databricks configure --token
```

Or set environment variables:
```bash
export DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
export DATABRICKS_TOKEN=dapi...
```

### 3. Start the Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Test Endpoints

Once running, visit:
- **API Docs (Swagger)**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/health

### 5. Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# List customers (requires X-Tenant-ID header)
curl -H "X-Tenant-ID: demo_tenant" http://localhost:8000/api/customers

# List journeys
curl -H "X-Tenant-ID: demo_tenant" http://localhost:8000/api/journeys

# Dashboard analytics
curl -H "X-Tenant-ID: demo_tenant" http://localhost:8000/api/analytics/dashboard
```

## Expected Behavior

### Without Databricks Connection
- ✓ FastAPI app should start successfully
- ✓ API routes registered
- ✓ API docs accessible
- ⚠ Database queries will fail (requires Unity Catalog setup)
- ⚠ Agent service will fail (requires Databricks SDK connection)

### With Databricks Connection
- ✓ All endpoints functional
- ✓ Can query Unity Catalog tables
- ✓ Agent service can make decisions
- ✓ Journey orchestrator can process states

## Pre-requisites for Full Testing

1. **Unity Catalog Setup** (one-time):
   ```bash
   python scripts/setup_unity_catalog.py
   ```

2. **Create UC Functions** (one-time):
   - Run `scripts/create_uc_functions.sql` in Databricks SQL Editor

3. **Generate Demo Data** (optional):
   ```bash
   python scripts/seed_demo_data.py
   ```

## Troubleshooting

### Import Errors
If you see `No module named 'xxx'`:
- Install dependencies: `pip3 install -r requirements.txt`
- Check Python version: `python3 --version` (requires 3.10+)

### Databricks Connection Errors
- Verify `~/.databrickscfg` exists and is valid
- Check workspace URL format: `https://<workspace>.cloud.databricks.com`
- Verify token permissions (needs Unity Catalog access)

### Database Errors
- Run Unity Catalog setup script first
- Ensure tables exist: `SHOW TABLES IN cdp_platform.core;`
- Check permissions: Unity Catalog access required

## Next Steps After Testing

1. ✅ All API endpoints implemented
2. ⏭️ Frontend development
3. ⏭️ Deploy as Databricks App
4. ⏭️ Set up background workflows

