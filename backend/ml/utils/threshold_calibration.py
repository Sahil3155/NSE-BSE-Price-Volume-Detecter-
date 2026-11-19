"""Threshold calibration tools for unsupervised anomaly scoring."""

from typing import Dict, Any
import numpy as np


def calibrate_percentile_threshold(
    scores: np.ndarray,
    target_percentile: float = 95.0,
) -> float:
    """Derive anomaly cutoff threshold at specific historical score percentile."""
    if len(scores) == 0:
        return 0.5
    cutoff = float(np.percentile(scores, target_percentile))
    return round(cutoff, 4)


def tune_classification_threshold(
    y_true: np.ndarray,
    scores: np.ndarray,
    beta: float = 1.0,
) -> Dict[str, Any]:
    """Find threshold that maximizes F-beta score on validation weak labels."""
    best_thresh = 0.5
    best_f = 0.0

    for t in np.linspace(0.1, 0.9, 17):
        y_pred = (scores >= t).astype(int)
        tp = np.sum((y_true == 1) & (y_pred == 1))
        fp = np.sum((y_true == 0) & (y_pred == 1))
        fn = np.sum((y_true == 1) & (y_pred == 0))

        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f_beta = (
            (1 + beta**2) * (prec * rec) / ((beta**2 * prec) + rec)
            if (prec + rec) > 0
            else 0.0
        )
        if f_beta > best_f:
            best_f = f_beta
            best_thresh = t

    return {"optimal_threshold": round(best_thresh, 4), "max_f_score": round(best_f, 4)}
