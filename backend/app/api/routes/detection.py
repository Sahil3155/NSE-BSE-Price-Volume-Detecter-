"""FastAPI routes for triggering anomaly detection and viewing results."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.app.api.dependencies import get_db_session
from backend.app.models.anomaly import AnomalyPrediction
from backend.app.models.stock import Stock, Exchange
from backend.app.schemas.detection import (
    DetectionRunRequest,
    DetectionRunResponse,
    DetectionResultItem,
    ModelContribution,
)
from backend.app.services.detection_service import run_surveillance_detection

router = APIRouter(prefix="/detection", tags=["Detection"])


@router.post("/run", response_model=DetectionRunResponse)
async def trigger_detection(
    request: DetectionRunRequest,
    db: Session = Depends(get_db_session),
) -> DetectionRunResponse:
    """Run anomaly detection models on demand across market data."""
    try:
        return run_surveillance_detection(db, request)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Detection execution failed: {str(exc)}",
        )


@router.get("/results", response_model=List[DetectionResultItem])
async def get_detection_results(
    risk_level: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db_session),
) -> List[DetectionResultItem]:
    """Retrieve historical anomaly inference results."""
    stmt = (
        select(AnomalyPrediction, Stock.symbol, Exchange.code.label("exchange"))
        .join(Stock, AnomalyPrediction.stock_id == Stock.id)
        .join(Exchange, Stock.exchange_id == Exchange.id)
    )
    if risk_level:
        stmt = stmt.where(AnomalyPrediction.risk_level == risk_level.upper())
    stmt = stmt.order_by(AnomalyPrediction.trading_date.desc(), AnomalyPrediction.hybrid_score.desc())
    stmt = stmt.limit(limit).offset(offset)

    rows = db.execute(stmt).all()
    return [
        DetectionResultItem(
            id=pred.id,
            symbol=sym,
            exchange=ex,
            trading_date=pred.trading_date,
            anomaly_score=pred.hybrid_score,
            risk_level=pred.risk_level,
            reasons=[f"Anomaly score {pred.hybrid_score:.1f}/100 categorized as {pred.risk_level}."],
            model_breakdown=ModelContribution(
                isolation_forest_score=pred.isolation_forest_score,
                lstm_reconstruction_score=pred.lstm_reconstruction_error,
                rule_score=pred.rule_score,
            ),
        )
        for pred, sym, ex in rows
    ]


@router.get("/{prediction_id}", response_model=DetectionResultItem)
async def get_detection_by_id(
    prediction_id: int,
    db: Session = Depends(get_db_session),
) -> DetectionResultItem:
    """Retrieve an individual prediction by primary key."""
    stmt = (
        select(AnomalyPrediction, Stock.symbol, Exchange.code.label("exchange"))
        .join(Stock, AnomalyPrediction.stock_id == Stock.id)
        .join(Exchange, Stock.exchange_id == Exchange.id)
        .where(AnomalyPrediction.id == prediction_id)
    )
    row = db.execute(stmt).first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction #{prediction_id} not found.",
        )
    pred, sym, ex = row
    return DetectionResultItem(
        id=pred.id,
        symbol=sym,
        exchange=ex,
        trading_date=pred.trading_date,
        anomaly_score=pred.hybrid_score,
        risk_level=pred.risk_level,
        reasons=[f"Risk score: {pred.hybrid_score:.1f}/100"],
        model_breakdown=ModelContribution(
            isolation_forest_score=pred.isolation_forest_score,
            lstm_reconstruction_score=pred.lstm_reconstruction_error,
            rule_score=pred.rule_score,
        ),
    )
