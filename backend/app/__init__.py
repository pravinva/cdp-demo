"""
Configuration management for CDP Platform
Uses Pydantic settings for validation and environment variable management
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional, List
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Databricks CDP Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Databricks
    DATABRICKS_HOST: str
    DATABRICKS_TOKEN: str
    DATABRICKS_CATALOG: str = "cdp_platform"
    DATABRICKS_SCHEMA: str = "core"
    
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Agent Configuration
    AGENT_MODEL: str = "databricks-meta-llama-3-1-70b-instruct"
    AGENT_MAX_ITERATIONS: int = 10
    AGENT_TEMPERATURE: float = 0.7
    
    # Email Provider (SendGrid)
    SENDGRID_API_KEY: Optional[str] = None
    SENDGRID_FROM_EMAIL: str = "noreply@cdp-platform.com"
    
    # SMS Provider (Twilio)
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_FROM_NUMBER: Optional[str] = None
    
    # Push Notification (Firebase)
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None
    
    # Redis (for feature caching)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # MLflow
    MLFLOW_TRACKING_URI: str
    MLFLOW_EXPERIMENT_NAME: str = "/cdp-platform/agent-decisions"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Monitoring
    LOG_LEVEL: str = "INFO"
    ENABLE_METRICS: bool = True
    
    # Journey Orchestrator
    JOURNEY_CHECK_INTERVAL_SECONDS: int = 60  # How often to check for journeys to progress
    JOURNEY_MAX_WAIT_DAYS: int = 90  # Maximum wait time before auto-exit
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

