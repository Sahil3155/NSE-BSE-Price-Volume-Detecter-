"""Isolation Forest wrapper for multidimensional price-volume anomaly detection."""

from typing import Optional, Dict, Any
import numpy as np
from sklearn.ensemble import IsolationForest


class IsolationForestSurveillanceModel:
    """Configurable Isolation Forest model for market surveillance."""

    def __init__(
        self,
        n_estimators: int = 150,
        contamination: float = 0.05,
        max_samples: float = 0.8,
        random_state: int = 42,
    ):
        self.n_estimators = n_estimators
        self.contamination = contamination
        self.max_samples = max_samples
        self.random_state = random_state
        self.model = IsolationForest(
            n_estimators=self.n_estimators,
            contamination=self.contamination,
            max_samples=self.max_samples,
            random_state=self.random_state,
            n_jobs=-1,
        )
        self.is_fitted: bool = False

    def fit(self, X: np.ndarray) -> "IsolationForestSurveillanceModel":
        """Fit the isolation forest on training feature array."""
        self.model.fit(X)
        self.is_fitted = True
        return self

    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """Calculate normalized anomaly scores in range [0, 1].

        Lower raw decision_function means more anomalous; we invert and min-max scale.
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before scoring.")
        raw_scores = self.model.decision_function(X)
        # Invert: higher score = higher anomaly
        inverted = -raw_scores
        # Normalize dynamically
        min_val, max_val = inverted.min(), inverted.max()
        if max_val == min_val:
            return np.zeros_like(inverted)
        return (inverted - min_val) / (max_val - min_val)
