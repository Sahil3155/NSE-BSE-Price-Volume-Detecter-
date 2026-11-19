"""Service managing surveillance alerts review and lifecycle."""

import json
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.app.models.stock import Stock, Exchange
from backend.app.models.alert import DetectionAlert
from backend.app.schemas.alert import AlertResponse, AlertStatusUpdate


def get_alerts(
    db: Session,
    risk_level: Optional[str] = None,
    status: Optional[str] = None,
    symbol: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[AlertResponse]:
    """Retrieve filtered surveillance alerts."""
    query = (
        select(DetectionAlert, Stock.symbol, Exchange.code.label("exchange"))
        .join(Stock, DetectionAlert.stock_id == Stock.id)
        .join(Exchange, Stock.exchange_id == Exchange.id)
    )
    if risk_level:
        query = query.where(DetectionAlert.risk_level == risk_level.upper())
    if status:
        query = query.where(DetectionAlert.status == status.upper())
    if symbol:
        query = query.where(Stock.symbol == symbol.upper())

    query = query.order_by(DetectionAlert.detection_date.desc(), DetectionAlert.anomaly_score.desc())
    query = query.limit(limit).offset(offset)

    rows = db.execute(query).all()
    results = []
    for alert, sym, ex in rows:
        try:
            reasons = json.loads(alert.reasons_json)
        except Exception:
            reasons = []

        results.append(
            AlertResponse(
                id=alert.id,
                stock_symbol=sym,
                exchange=ex,
                detection_date=alert.detection_date,
                anomaly_score=alert.anomaly_score,
                risk_level=alert.risk_level,
                reasons=reasons,
                status=alert.status,
                investigator_notes=alert.investigator_notes,
                created_at=alert.created_at.isoformat() if alert.created_at else None,
            )
        )
    return results


def get_alert_by_id(db: Session, alert_id: int) -> Optional[AlertResponse]:
    """Fetch individual alert by primary key."""
    query = (
        select(DetectionAlert, Stock.symbol, Exchange.code.label("exchange"))
        .join(Stock, DetectionAlert.stock_id == Stock.id)
        .join(Exchange, Stock.exchange_id == Exchange.id)
        .where(DetectionAlert.id == alert_id)
    )
    row = db.execute(query).first()
    if not row:
        return None

    alert, sym, ex = row
    reasons = json.loads(alert.reasons_json) if alert.reasons_json else []
    return AlertResponse(
        id=alert.id,
        stock_symbol=sym,
        exchange=ex,
        detection_date=alert.detection_date,
        anomaly_score=alert.anomaly_score,
        risk_level=alert.risk_level,
        reasons=reasons,
        status=alert.status,
        investigator_notes=alert.investigator_notes,
        created_at=alert.created_at.isoformat() if alert.created_at else None,
    )


def update_alert_status(
    db: Session,
    alert_id: int,
    update_data: AlertStatusUpdate,
) -> Optional[AlertResponse]:
    """Update investigation status and reviewer notes on an alert."""
    alert = db.scalars(select(DetectionAlert).where(DetectionAlert.id == alert_id)).first()
    if not alert:
        return None

    alert.status = update_data.status.upper()
    if update_data.investigator_notes is not None:
        alert.investigator_notes = update_data.investigator_notes

    db.commit()
    db.refresh(alert)
    return get_alert_by_id(db, alert_id)
