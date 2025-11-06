"""
Main FastAPI application
Entry point for CDP Platform API
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from contextlib import asynccontextmanager

from .config import get_settings
from .dependencies import setup_mlflow
from .utils.monitoring import setup_logging, MetricsMiddleware

settings = get_settings()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    setup_logging()
    setup_mlflow()
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Customer Data Platform with Agentic AI and Journey Orchestration",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
# app.add_middleware(MetricsMiddleware)  # Uncomment when monitoring utils are created

# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred"
        }
    )

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

# Include routers
from .api import journeys

app.include_router(
    journeys.router,
    prefix="/api/journeys",
    tags=["journeys"]
)

# TODO: Add other routers as they're implemented
# from .api import customers, campaigns, agents, analytics, identity
# 
# app.include_router(
#     customers.router,
#     prefix="/api/customers",
#     tags=["customers"]
# )
# app.include_router(
#     campaigns.router,
#     prefix="/api/campaigns",
#     tags=["campaigns"]
# )
# app.include_router(
#     agents.router,
#     prefix="/api/agents",
#     tags=["agents"]
# )
# app.include_router(
#     analytics.router,
#     prefix="/api/analytics",
#     tags=["analytics"]
# )
# app.include_router(
#     identity.router,
#     prefix="/api/identity",
#     tags=["identity"]
# )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/api/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

