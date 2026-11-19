"""Evaluation metrics for time-series anomaly detection."""

from typing import Dict, Any
import numpy as np
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    precision_recall_curve,
    auc,
    confusion_matrix,
)


def compute_surveillance_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    scores: np.ndarray,
) -> Dict[str, Any]:
    """Calculate comprehensive surveillance evaluation metrics."""
    # Ensure at least one positive class in y_true for AUC
    has_positives = np.sum(y_true) > 0 and np.sum(y_true) < len(y_true)

    roc_auc = float(roc_auc_score(y_true, scores)) if has_positives else 0.0
    if has_positives:
        prec_arr, rec_arr, _ = precision_recall_curve(y_true, scores)
        pr_auc = float(auc(rec_arr, prec_arr))
    else:
        pr_auc = 0.0

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0

    return {
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "false_positive_rate": round(fpr, 4),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
    }
