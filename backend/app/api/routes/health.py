"""Health check route module."""

from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import APIRouter, status
from backend.app.core.config import settings
from backend.app.database.connection import test_connection

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", status_code=status.HTTP_200_OK, response_model=Dict[str, Any])
async def check_system_health() -> Dict[str, Any]:
    """Check application, database connectivity, and environment status."""
    db_healthy = test_connection()
    return {
        "status": "healthy" if db_healthy else "degraded",
        "app_name": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "database_connected": db_healthy,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
    }
