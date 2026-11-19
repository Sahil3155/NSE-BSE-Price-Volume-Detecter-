"""Service executing surveillance inference and saving alert predictions."""

import json
from typing import List, Dict, Any, Optional
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from backend.app.core.logging import logger
from backend.app.models.stock import Stock, Exchange
from backend.app.models.historical_data import HistoricalMarketData, EngineeredFeature
from backend.app.models.anomaly import AnomalyPrediction
from backend.app.models.alert import DetectionAlert
from backend.app.schemas.detection import DetectionRunRequest, DetectionRunResponse, DetectionResultItem, ModelContribution
from backend.ml.utils.model_loader import ModelRegistryLoader
from backend.ml.hybrid_detector.detector import HybridSurveillanceDetector


def load_dataframe_from_db(
    db: Session,
    exchange_code: Optional[str] = None,
    symbol: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Extract joined market and feature dataframe from database."""
    query = (
        select(
            Stock.symbol,
            Exchange.code.label("exchange"),
            HistoricalMarketData.trading_date,
            HistoricalMarketData.open,
            HistoricalMarketData.high,
            HistoricalMarketData.low,
            HistoricalMarketData.close,
            HistoricalMarketData.volume,
            HistoricalMarketData.turnover,
            EngineeredFeature.daily_return,
            EngineeredFeature.log_return,
            EngineeredFeature.rolling_return_5d,
            EngineeredFeature.rolling_return_10d,
            EngineeredFeature.rolling_return_20d,
            EngineeredFeature.price_z_score,
            EngineeredFeature.volume_ratio_20d,
            EngineeredFeature.abnormal_volume_pct,
            EngineeredFeature.volume_z_score,
            EngineeredFeature.volume_acceleration,
            EngineeredFeature.price_volatility_20d,
            EngineeredFeature.volume_volatility_20d,
            EngineeredFeature.return_volume_interaction,
            EngineeredFeature.price_volume_corr_20d,
            EngineeredFeature.price_volume_divergence,
            EngineeredFeature.consecutive_upper_circuits,
        )
        .join(Stock, HistoricalMarketData.stock_id == Stock.id)
        .join(Exchange, Stock.exchange_id == Exchange.id)
        .join(
            EngineeredFeature,
            (EngineeredFeature.stock_id == Stock.id)
            & (EngineeredFeature.trading_date == HistoricalMarketData.trading_date),
        )
    )
    if exchange_code:
        query = query.where(Exchange.code == exchange_code.upper())
    if symbol:
        query = query.where(Stock.symbol == symbol.upper())
    if start_date:
        query = query.where(HistoricalMarketData.trading_date >= start_date)
    if end_date:
        query = query.where(HistoricalMarketData.trading_date <= end_date)
    query = query.order_by(Stock.symbol, HistoricalMarketData.trading_date.asc())

    rows = db.execute(query).mappings().all()
    return pd.DataFrame(rows)


def persist_detection_results(db: Session, detections: List[Dict[str, Any]]) -> None:
    """Store predictions and generate alerts for suspicious records."""
    for det in detections:
        stock = db.scalars(select(Stock).where(Stock.symbol == det["symbol"])).first()
        if not stock:
            continue

        existing_pred = db.scalars(
            select(AnomalyPrediction).where(
                (AnomalyPrediction.stock_id == stock.id)
                & (AnomalyPrediction.trading_date == det["trading_date"])
            )
        ).first()

        breakdown = det["model_breakdown"]
        if not existing_pred:
            pred = AnomalyPrediction(
                stock_id=stock.id,
                trading_date=det["trading_date"],
                isolation_forest_score=breakdown["isolation_forest_score"],
                lstm_reconstruction_error=breakdown["lstm_reconstruction_score"],
                rule_score=breakdown["rule_score"],
                hybrid_score=det["anomaly_score"],
                risk_level=det["risk_level"],
            )
            db.add(pred)
            db.flush()
        else:
            pred = existing_pred

        # Create alert if Medium or High risk
        if det["risk_level"] in ["MEDIUM", "HIGH"]:
            alert_exists = db.scalars(
                select(DetectionAlert).where(
                    (DetectionAlert.stock_id == stock.id)
                    & (DetectionAlert.detection_date == det["trading_date"])
                )
            ).first()
            if not alert_exists:
                alert = DetectionAlert(
                    prediction_id=pred.id,
                    stock_id=stock.id,
                    detection_date=det["trading_date"],
                    anomaly_score=det["anomaly_score"],
                    risk_level=det["risk_level"],
                    reasons_json=json.dumps(det["reasons"]),
                    status="PENDING_REVIEW",
                )
                db.add(alert)
    db.commit()


def run_surveillance_detection(
    db: Session,
    request: DetectionRunRequest,
) -> DetectionRunResponse:
    """Execute complete surveillance detection pipeline on database data."""
    df = load_dataframe_from_db(
        db,
        exchange_code=request.exchange,
        symbol=request.symbol,
        start_date=request.start_date,
        end_date=request.end_date,
    )
    if df.empty:
        return DetectionRunResponse(
            status="NO_DATA",
            records_analyzed=0,
            anomalies_detected=0,
            high_risk_count=0,
            medium_risk_count=0,
            results=[],
        )

    loader = ModelRegistryLoader()
    detector = HybridSurveillanceDetector(
        loader.get_isolation_forest(),
        loader.get_lstm_autoencoder(),
    )
    detections = detector.detect_anomalies(df)
    persist_detection_results(db, detections)

    high_risk = sum(1 for d in detections if d["risk_level"] == "HIGH")
    med_risk = sum(1 for d in detections if d["risk_level"] == "MEDIUM")

    items = [
        DetectionResultItem(
            symbol=d["symbol"],
            exchange=d["exchange"],
            trading_date=d["trading_date"],
            anomaly_score=d["anomaly_score"],
            risk_level=d["risk_level"],
            reasons=d["reasons"],
            model_breakdown=ModelContribution(**d["model_breakdown"]),
        )
        for d in detections
    ]
    return DetectionRunResponse(
        status="SUCCESS",
        records_analyzed=len(df),
        anomalies_detected=high_risk + med_risk,
        high_risk_count=high_risk,
        medium_risk_count=med_risk,
        results=items,
    )
