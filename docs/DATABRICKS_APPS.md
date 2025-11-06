# Databricks Apps - API Exposure Architecture

## Overview

This CDP Platform is designed to run as a **Databricks App**, which provides a fully managed way to deploy and expose FastAPI applications directly within your Databricks workspace.

## How Databricks Apps Expose APIs

### 1. **Automatic HTTPS URL Generation**
When you deploy a Databricks App:
- Databricks automatically generates a secure HTTPS URL
- Format: `https://<workspace-name>.cloud.databricks.com/apps/<app-name>`
- No manual DNS configuration needed
- SSL/TLS certificates managed automatically

### 2. **Workspace Authentication Integration**
- APIs are automatically protected by Databricks workspace authentication
- Users authenticate using their Databricks credentials
- No separate OAuth/JWT setup required for workspace users
- Can integrate with Databricks Groups and Access Control Lists (ACLs)

### 3. **Direct Unity Catalog Access**
- Apps run with context of the deploying user/organization
- Direct access to Unity Catalog tables and schemas
- No need for separate database connection strings
- Automatic credential management via Databricks SDK

### 4. **Auto-Scaling**
- Apps automatically scale based on load
- Configured in `cdp-platform-app.yml`:
  ```yaml
  scale:
    min_replicas: 2
    max_replicas: 10
    target_cpu_utilization: 70
  ```

### 5. **Resource Access**
- Apps can access Unity Catalog catalogs, schemas, and tables
- Access to MLflow experiments and models
- Connection to Databricks SQL warehouses
- Integration with Databricks Workflows

## Deployment Process

### Step 1: Build Docker Image
```bash
cd backend
docker build -t cdp-platform:latest .
```

### Step 2: Deploy as Databricks App
```bash
# Using Databricks CLI
databricks apps deploy \
  --app-spec infrastructure/databricks/apps/cdp-platform-app.yml
```

### Step 3: Access Your API
Once deployed:
- Visit: `https://<workspace>.cloud.databricks.com/apps/cdp-platform`
- API Docs: `https://<workspace>.cloud.databricks.com/apps/cdp-platform/api/docs`
- ReDoc: `https://<workspace>.cloud.databricks.com/apps/cdp-platform/api/redoc`

## API Endpoints

All endpoints are prefixed with `/api`:

- **Health Check**: `GET /health`
- **Journeys**: `GET/POST/PATCH /api/journeys/*`
- **Customers**: `GET/POST/PATCH /api/customers/*` (coming soon)
- **Campaigns**: `GET/POST/PATCH /api/campaigns/*` (coming soon)
- **Agents**: `POST /api/agents/*` (coming soon)
- **Analytics**: `GET /api/analytics/*` (coming soon)
- **Identity**: `GET /api/identity/*` (coming soon)

## Authentication

### For Workspace Users
- Uses Databricks workspace authentication automatically
- No additional setup needed

### For External API Clients
- Current implementation uses `X-Tenant-ID` header for tenant context
- Can be extended with JWT tokens for external authentication
- OAuth2 integration available via FastAPI security

## Environment Variables

Databricks Apps support secrets management:
```yaml
env:
  DATABRICKS_HOST: ${secrets/cdp/databricks_host}
  DATABRICKS_TOKEN: ${secrets/cdp/databricks_token}
```

Secrets are stored in Databricks Secrets Scope and injected at runtime.

## Background Jobs

Journey Orchestrator runs as a scheduled workflow:
- **Schedule**: Every 5 minutes
- **Purpose**: Process active journey states and advance customers
- **Location**: `infrastructure/databricks/workflows/journey_orchestrator.yml`

## Local Development

For local development, run FastAPI directly:
```bash
cd backend
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
- Uses `~/.databrickscfg` for Databricks credentials
- Connects to your Databricks workspace
- Full API functionality available locally

## Production Considerations

1. **HTTPS Only**: Databricks Apps enforce HTTPS
2. **Load Balancing**: Automatic load balancing across replicas
3. **Health Checks**: Built-in health check endpoint at `/health`
4. **Monitoring**: Integration with Databricks System Tables
5. **Logging**: Structured logging to Databricks cluster logs
6. **Scaling**: Automatic scaling based on CPU utilization

## Advantages of Databricks Apps

✅ **Native Integration**: Built for Databricks ecosystem  
✅ **Zero Infrastructure**: No need to manage servers, load balancers, or SSL certificates  
✅ **Automatic Scaling**: Handles traffic spikes automatically  
✅ **Security**: Workspace authentication and secrets management built-in  
✅ **Cost Effective**: Pay only for compute resources used  
✅ **Unified Platform**: APIs, data, and ML all in one place  

## Next Steps

1. Deploy the app to your Databricks workspace
2. Access the API via the generated HTTPS URL
3. Integrate with your frontend application
4. Set up monitoring and alerts
5. Configure additional workflows as needed

For more information, see: [Databricks Apps Documentation](https://docs.databricks.com/dev-tools/apps/index.html)

