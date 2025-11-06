"""
Dependency injection for FastAPI
Handles authentication, database connections, etc.
"""

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from databricks.sdk import WorkspaceClient
from pyspark.sql import SparkSession
import mlflow
from typing import Optional
from .config import get_settings
from .auth import get_current_user, get_tenant_from_user, get_user_id_from_context

settings = get_settings()
security = HTTPBearer()

# Databricks Client (singleton)
_workspace_client = None
_spark_session = None

def get_workspace_client() -> WorkspaceClient:
    """Get Databricks workspace client
    Will automatically use ~/.databrickscfg if host/token not provided
    """
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

def get_spark_session() -> SparkSession:
    """Get or create Spark session
    Uses Databricks SQL warehouse connection from ~/.databrickscfg
    """
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

def get_tenant_context(
    x_tenant_id: Optional[str] = Header(None),
    user: Optional[dict] = Depends(get_current_user)
) -> str:
    """
    Extract tenant ID from authenticated user or header (for backward compatibility)
    Prefers JWT token tenant_id, falls back to header if provided
    """
    # First try to get from authenticated user
    tenant_id = user.get("tenant_id") if user else None
    
    # Fallback to header for backward compatibility (deprecated)
    if not tenant_id and x_tenant_id:
        if settings.ENVIRONMENT == "development":
            return x_tenant_id
        else:
            # In production, require JWT token
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="X-Tenant-ID header is deprecated. Use JWT token authentication."
            )
    
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant ID not found in authentication token"
        )
    
    return tenant_id

def setup_mlflow():
    """Configure MLflow tracking
    Uses Databricks MLflow if no explicit URI provided
    """
    if settings.MLFLOW_TRACKING_URI:
        mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
    else:
        # Use Databricks workspace MLflow (automatically configured)
        # MLflow will use ~/.databrickscfg
        pass
    
    mlflow.set_experiment(settings.MLFLOW_EXPERIMENT_NAME)

