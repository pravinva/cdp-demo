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
    # If not provided, will use ~/.databrickscfg automatically
    DATABRICKS_HOST: Optional[str] = None
    DATABRICKS_TOKEN: Optional[str] = None
    DATABRICKS_CATALOG: str = "cdp_platform"
    DATABRICKS_SCHEMA: str = "core"
    SQL_WAREHOUSE_ID: Optional[str] = None  # SQL warehouse ID for table operations
    
    # Security
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Agent Configuration
    # Model name for Databricks Foundation Model API
    # Examples:
    #   - "databricks-meta-llama-3-1-70b-instruct" (Llama 3.1 70B)
    #   - "databricks-meta-llama-3-3-70b-instruct" (Llama 3.3 70B)
    #   - "databricks-mixtral-8x7b-instruct" (Mixtral 8x7B)
    #   - Or any custom serving endpoint name
    AGENT_MODEL: str = "databricks-meta-llama-3-1-70b-instruct"
    AGENT_MAX_ITERATIONS: int = 10
    AGENT_TEMPERATURE: float = 0.7
    
    # Email Provider (SendGrid)
    SENDGRID_API_KEY: Optional[str] = None
    SENDGRID_FROM_EMAIL: str = "noreply@cdp-platform.com"
    
    # Email Testing Alternatives
    EMAIL_TEST_MODE: str = "console"  # Options: "console", "mailtrap", "mailhog", "sendgrid", "ses"
    MAILTRAP_API_TOKEN: Optional[str] = None  # For Mailtrap testing
    MAILHOG_HOST: str = "localhost"  # For MailHog local testing
    MAILHOG_PORT: int = 1025  # MailHog SMTP port
    
    # SMS Provider (Twilio)
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_FROM_NUMBER: Optional[str] = None
    
    # SMS Testing Alternatives
    SMS_TEST_MODE: str = "console"  # Options: "console", "twilio_test", "twilio", "mocksms"
    TWILIO_TEST_ACCOUNT_SID: Optional[str] = None  # Twilio test credentials
    TWILIO_TEST_AUTH_TOKEN: Optional[str] = None
    
    # Push Notification (Firebase)
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None
    
    # Redis (for feature caching)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # MLflow
    # If not provided, will use Databricks workspace MLflow
    MLFLOW_TRACKING_URI: Optional[str] = None
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
    
    # Workflow Scheduling
    # Cron expression for workflow schedules (Quartz format)
    # Default: once per day at midnight UTC ("0 0 0 * * ?")
    # Examples:
    #   - "0 0 0 * * ?" - Once per day at midnight UTC
    #   - "0 */5 * * * ?" - Every 5 minutes
    #   - "0 0 */4 * * ?" - Every 4 hours
    #   - "0 0 0 * * MON" - Every Monday at midnight
    WORKFLOW_SCHEDULE_CRON: str = "0 0 0 * * ?"  # Once per day at midnight UTC
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

