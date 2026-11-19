"""Model benchmarking and comparison suite."""

from typing import Dict, Any, List
import numpy as np
import pandas as pd
from backend.ml.evaluation.metrics import compute_surveillance_metrics


def evaluate_detection_model(
    model_name: str,
    y_true: np.ndarray,
    scores: np.ndarray,
    threshold: float = 0.5,
) -> Dict[str, Any]:
    """Compute benchmark performance for an individual detection model."""
    y_pred = (scores >= threshold).astype(int)
    metrics = compute_surveillance_metrics(y_true, y_pred, scores)
    return {
        "model_name": model_name,
        "threshold": threshold,
        **metrics,
    }


def compare_all_models(
    y_true: np.ndarray,
    rule_scores: np.ndarray,
    iforest_scores: np.ndarray,
    lstm_scores: np.ndarray,
    hybrid_scores: np.ndarray,
) -> List[Dict[str, Any]]:
    """Generate comparative evaluation table across all four surveillance methods."""
    results = [
        evaluate_detection_model("Rule-Based Detector", y_true, rule_scores, threshold=0.4),
        evaluate_detection_model("Isolation Forest", y_true, iforest_scores, threshold=0.6),
        evaluate_detection_model("LSTM Autoencoder", y_true, lstm_scores, threshold=0.5),
        evaluate_detection_model("Hybrid Surveillance Engine", y_true, hybrid_scores / 100.0, threshold=0.5),
    ]
    return results
