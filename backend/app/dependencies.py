"""
Dependency injection for FastAPI
Handles authentication, database connections, etc.
"""

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from .config import get_settings

# Optional Databricks imports for local development
try:
    from databricks.sdk import WorkspaceClient
    DATABRICKS_AVAILABLE = True
except ImportError:
    DATABRICKS_AVAILABLE = False
    WorkspaceClient = None

try:
    from pyspark.sql import SparkSession
    SPARK_AVAILABLE = True
except ImportError:
    SPARK_AVAILABLE = False
    SparkSession = None

try:
    import mlflow
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    mlflow = None

settings = get_settings()
security = HTTPBearer()

# Databricks Client (singleton)
_workspace_client = None
_spark_session = None

def get_workspace_client():
    """Get Databricks workspace client
    Will automatically use ~/.databrickscfg if host/token not provided
    """
    if not DATABRICKS_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Databricks SDK not available. Install with: pip install databricks-sdk"
        )
    
    global _workspace_client
    if _workspace_client is None:
        if settings.DATABRICKS_HOST and settings.DATABRICKS_TOKEN:
            # Use explicit credentials
            _workspace_client = WorkspaceClient(
                host=settings.DATABRICKS_HOST,
                token=settings.DATABRICKS_TOKEN
            )
        else:
            # Use ~/.databrickscfg automatically
            _workspace_client = WorkspaceClient()
    return _workspace_client

def get_spark_session():
    """Get or create Spark session
    Uses Databricks SQL warehouse connection from ~/.databrickscfg
    """
    if not SPARK_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="PySpark not available. Install with: pip install pyspark"
        )
    
    global _spark_session
    if _workspace_client is None:
        get_workspace_client()  # Initialize client to get config
    
    if _spark_session is None:
        builder = SparkSession.builder.appName("CDP Platform API")
        
        # If explicit credentials provided, use them
        if settings.DATABRICKS_HOST and settings.DATABRICKS_TOKEN:
            builder = builder \
                .config("spark.databricks.service.address", settings.DATABRICKS_HOST) \
                .config("spark.databricks.service.token", settings.DATABRICKS_TOKEN)
        # Otherwise, Spark will use ~/.databrickscfg automatically via databricks-connect or SQL warehouse
        
        _spark_session = builder.getOrCreate()
    return _spark_session

def get_tenant_context(x_tenant_id: Optional[str] = Header(None)) -> str:
    """
    Extract tenant ID from request headers
    In production, this would validate JWT and extract tenant from claims
    """
    if not x_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Tenant-ID header is required"
        )
    return x_tenant_id

async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Verify JWT token (simplified for demo)
    In production, use proper JWT validation with databricks-sdk or custom auth
    """
    token = credentials.credentials
    
    # TODO: Implement proper JWT validation
    # For now, accept any token in development
    if settings.ENVIRONMENT == "development":
        return {"user_id": "demo_user", "tenant_id": "demo_tenant"}
    
    # Production: validate token
    try:
        # Validate token and extract claims
        payload = verify_jwt_token(token)
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

def verify_jwt_token(token: str) -> dict:
    """Validate JWT token"""
    # Implement JWT validation logic
    pass

def setup_mlflow():
    """Configure MLflow tracking
    Uses Databricks MLflow if no explicit URI provided
    """
    if not MLFLOW_AVAILABLE:
        # MLflow not available, skip setup
        return
    
    if settings.MLFLOW_TRACKING_URI:
        mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
    else:
        # Use Databricks workspace MLflow (automatically configured)
        # MLflow will use ~/.databrickscfg
        pass
    
    try:
        mlflow.set_experiment(settings.MLFLOW_EXPERIMENT_NAME)
    except Exception:
        # Experiment creation may fail in local dev, that's okay
        pass

