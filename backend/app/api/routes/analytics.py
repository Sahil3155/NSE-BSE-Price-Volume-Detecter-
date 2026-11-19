"""FastAPI routes for surveillance analytics, trends, and model benchmarks."""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.api.dependencies import get_db_session
from backend.app.services.analytics_service import (
    get_surveillance_overview,
    get_anomaly_trends,
    get_model_comparison_benchmark,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=Dict[str, Any])
async def get_dashboard_overview(
    db: Session = Depends(get_db_session),
) -> Dict[str, Any]:
    """Retrieve high-level surveillance statistics for dashboard widgets."""
    return get_surveillance_overview(db)


@router.get("/anomaly-trends", response_model=List[Dict[str, Any]])
async def get_detection_trends(
    days: int = Query(30, ge=7, le=180),
    db: Session = Depends(get_db_session),
) -> List[Dict[str, Any]]:
    """Retrieve daily time-series anomaly counts for surveillance charts."""
    return get_anomaly_trends(db, days=days)


@router.get("/model-comparison", response_model=List[Dict[str, Any]])
async def get_model_benchmarks() -> List[Dict[str, Any]]:
    """Retrieve comparative evaluation metrics across all four surveillance approaches."""
    return get_model_comparison_benchmark()
