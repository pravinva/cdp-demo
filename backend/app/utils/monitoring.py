"""
Utility functions for monitoring and logging
"""

import logging
import json
from typing import Dict, Any
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time


def setup_logging():
    """Setup structured logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting API metrics"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log metrics
        logging.info(
            json.dumps({
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": process_time
            })
        )
        
        return response

