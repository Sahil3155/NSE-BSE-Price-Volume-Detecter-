"""Service providing aggregate market surveillance statistics and benchmark metrics."""

from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc, case
from backend.app.models.stock import Stock
from backend.app.models.historical_data import HistoricalMarketData
from backend.app.models.anomaly import AnomalyPrediction
from backend.app.models.alert import DetectionAlert
from backend.ml.evaluation.model_comparison import compare_all_models
from backend.ml.evaluation.backtesting import map_sebi_weak_labels_to_market_data


def get_surveillance_overview(db: Session) -> Dict[str, Any]:
    """Compile macro-level metrics for dashboard surveillance header."""
    total_stocks = db.scalar(select(func.count(Stock.id))) or 0
    total_anomalies = db.scalar(
        select(func.count(AnomalyPrediction.id)).where(AnomalyPrediction.risk_level.in_(["MEDIUM", "HIGH"]))
    ) or 0
    high_alerts = db.scalar(select(func.count(DetectionAlert.id)).where(DetectionAlert.risk_level == "HIGH")) or 0
    med_alerts = db.scalar(select(func.count(DetectionAlert.id)).where(DetectionAlert.risk_level == "MEDIUM")) or 0
    latest_date = db.scalar(select(func.max(HistoricalMarketData.trading_date)))

    top_stocks_stmt = (
        select(Stock.symbol, func.max(AnomalyPrediction.hybrid_score).label("max_score"))
        .join(Stock, AnomalyPrediction.stock_id == Stock.id)
        .group_by(Stock.symbol)
        .order_by(desc("max_score"))
        .limit(5)
    )
    top_stocks = [{"symbol": s, "score": round(score, 1)} for s, score in db.execute(top_stocks_stmt).all()]

    return {
        "total_stocks_monitored": total_stocks,
        "stocks_with_anomalies": total_anomalies,
        "high_risk_alerts": high_alerts,
        "medium_risk_alerts": med_alerts,
        "latest_detection_date": latest_date,
        "highest_anomaly_stocks": top_stocks,
    }


def get_anomaly_trends(db: Session, days: int = 30) -> List[Dict[str, Any]]:
    """Aggregate anomaly detections by trading date for trend charts."""
    stmt = (
        select(
            AnomalyPrediction.trading_date,
            func.count(AnomalyPrediction.id).label("total"),
            func.sum(case((AnomalyPrediction.risk_level == "HIGH", 1), else_=0)).label("high_risk"),
            func.sum(case((AnomalyPrediction.risk_level == "MEDIUM", 1), else_=0)).label("medium_risk"),
            func.avg(AnomalyPrediction.hybrid_score).label("avg_score"),
        )
        .group_by(AnomalyPrediction.trading_date)
        .order_by(AnomalyPrediction.trading_date.asc())
        .limit(days)
    )
    rows = db.execute(stmt).all()
    return [
        {
            "date": dt,
            "total_detections": int(tot),
            "high_risk": int(high or 0),
            "medium_risk": int(med or 0),
            "average_score": round(float(avg or 0.0), 2),
        }
        for dt, tot, high, med, avg in rows
    ]


def get_model_comparison_benchmark() -> List[Dict[str, Any]]:
    """Evaluate and compare models on the synthetic benchmark dataset."""
    series_path = Path("datasets/sample/synthetic_pump_dump_series.csv")
    sebi_path = Path("datasets/sebi_orders/sample_sebi_weak_labels.csv")
    if not series_path.exists() or not sebi_path.exists():
        return []

    market_df = pd.read_csv(series_path)
    sebi_df = pd.read_csv(sebi_path)
    y_true = map_sebi_weak_labels_to_market_data(market_df, sebi_df).values

    from backend.data_pipeline.feature_engineering.feature_builder import build_surveillance_features
    from backend.ml.utils.model_loader import ModelRegistryLoader
    from backend.ml.hybrid_detector.detector import HybridSurveillanceDetector

    featured_df, _ = build_surveillance_features(market_df)
    loader = ModelRegistryLoader()
    detector = HybridSurveillanceDetector(loader.get_isolation_forest(), loader.get_lstm_autoencoder())
    detections = detector.detect_anomalies(featured_df)

    if_scores = np.array([d["model_breakdown"]["isolation_forest_score"] for d in detections])
    lstm_scores = np.array([d["model_breakdown"]["lstm_reconstruction_score"] for d in detections])
    rule_scores = np.array([d["model_breakdown"]["rule_score"] for d in detections])
    hybrid_scores = np.array([d["anomaly_score"] for d in detections])

    return compare_all_models(y_true, rule_scores, if_scores, lstm_scores, hybrid_scores)
