"""FastAPI routes for surveillance alerts and investigation workflows."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.api.dependencies import get_db_session
from backend.app.schemas.alert import AlertResponse, AlertStatusUpdate
from backend.app.services.alert_service import get_alerts, get_alert_by_id, update_alert_status

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=List[AlertResponse])
async def list_alerts(
    risk_level: Optional[str] = Query(None, description="HIGH, MEDIUM, or LOW"),
    alert_status: Optional[str] = Query(None, alias="status", description="PENDING_REVIEW, INVESTIGATING, DISMISSED, CONFIRMED_ANOMALY"),
    symbol: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db_session),
) -> List[AlertResponse]:
    """Query surveillance alerts with risk and review status filtering."""
    return get_alerts(
        db,
        risk_level=risk_level,
        status=alert_status,
        symbol=symbol,
        limit=limit,
        offset=offset,
    )


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert_details(
    alert_id: int,
    db: Session = Depends(get_db_session),
) -> AlertResponse:
    """Retrieve details and evidence explanation for an individual alert."""
    alert = get_alert_by_id(db, alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert #{alert_id} not found.",
        )
    return alert


@router.patch("/{alert_id}/status", response_model=AlertResponse)
async def update_alert_investigation_status(
    alert_id: int,
    update_data: AlertStatusUpdate,
    db: Session = Depends(get_db_session),
) -> AlertResponse:
    """Update surveillance investigation status and reviewer notes on an alert."""
    updated = update_alert_status(db, alert_id, update_data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert #{alert_id} not found.",
        )
    return updated
