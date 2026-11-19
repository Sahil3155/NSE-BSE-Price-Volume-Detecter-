"""Unit tests for ML models, hybrid scoring, and surveillance evaluation."""

from pathlib import Path
import numpy as np
import pandas as pd
from backend.data_pipeline.feature_engineering.feature_builder import build_surveillance_features
from backend.ml.utils.model_loader import ModelRegistryLoader
from backend.ml.hybrid_detector.detector import HybridSurveillanceDetector
from backend.ml.hybrid_detector.scoring import categorize_risk_level, compute_hybrid_anomaly_score
from backend.ml.evaluation.metrics import compute_surveillance_metrics
from backend.ml.evaluation.backtesting import map_sebi_weak_labels_to_market_data, calculate_detection_lead_time


def test_model_inference_and_hybrid_scoring():
    """Verify that trained models generate valid hybrid scores and explanations."""
    series_path = Path("datasets/sample/synthetic_pump_dump_series.csv")
    raw_df = pd.read_csv(series_path)
    featured_df, _ = build_surveillance_features(raw_df)

    loader = ModelRegistryLoader()
    detector = HybridSurveillanceDetector(
        loader.get_isolation_forest(),
        loader.get_lstm_autoencoder(),
    )
    alerts = detector.detect_anomalies(featured_df)

    assert len(alerts) == len(featured_df)
    top_alert = alerts[0]
    assert top_alert["symbol"] == "PUMPDUMP_SUSPECT"
    assert top_alert["risk_level"] in ["MEDIUM", "HIGH"]
    assert top_alert["anomaly_score"] >= 70.0
    assert len(top_alert["reasons"]) > 0


def test_scoring_weights_and_risk_bands():
    """Verify hybrid score bounds and risk classification thresholds."""
    assert categorize_risk_level(80.0) == "HIGH"
    assert categorize_risk_level(60.0) == "MEDIUM"
    assert categorize_risk_level(30.0) == "LOW"

    score = compute_hybrid_anomaly_score(1.0, 1.0, 1.0)
    assert score == 100.0
    zero_score = compute_hybrid_anomaly_score(0.0, 0.0, 0.0)
    assert zero_score == 0.0


def test_evaluation_metrics_and_backtesting():
    """Verify evaluation metric calculations with synthetic weak labels."""
    y_true = np.array([0, 0, 1, 1, 0, 1])
    y_pred = np.array([0, 0, 1, 0, 0, 1])
    scores = np.array([0.1, 0.2, 0.8, 0.4, 0.3, 0.9])

    metrics = compute_surveillance_metrics(y_true, y_pred, scores)
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == round(2 / 3, 4)
    assert metrics["f1_score"] > 0.0
    assert metrics["roc_auc"] > 0.5


def test_sebi_weak_label_mapping():
    """Verify mapping of SEBI enforcement orders to market dates."""
    market_df = pd.DataFrame([
        {"symbol": "TEST_SYM", "trading_date": "2024-01-10"},
        {"symbol": "TEST_SYM", "trading_date": "2024-02-05"},
    ])
    sebi_df = pd.DataFrame([{
        "stock_symbol": "TEST_SYM",
        "investigation_start_date": "2024-02-01",
        "investigation_end_date": "2024-02-28",
    }])
    labels = map_sebi_weak_labels_to_market_data(market_df, sebi_df)
    assert labels.tolist() == [0, 1]
