"""Hybrid market surveillance anomaly detector."""

from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from backend.app.core.logging import logger
from backend.ml.isolation_forest.predict import predict_isolation_forest
from backend.ml.lstm_autoencoder.predict import predict_lstm_reconstruction_errors
from backend.ml.hybrid_detector.scoring import (
    evaluate_microstructure_rules,
    compute_hybrid_anomaly_score,
    categorize_risk_level,
)


def normalize_lstm_errors(errors: np.ndarray, threshold: float) -> np.ndarray:
    """Normalize raw reconstruction errors to [0, 1] relative to threshold."""
    if len(errors) == 0:
        return np.array([])
    denom = max(1e-6, threshold * 2.0)
    return np.clip(errors / denom, 0.0, 1.0)


class HybridSurveillanceDetector:
    """Orchestrates multi-model anomaly scoring and alert explanation generation."""

    def __init__(self, iforest_artifacts: Optional[dict] = None, lstm_artifacts: Optional[dict] = None):
        self.iforest_artifacts = iforest_artifacts
        self.lstm_artifacts = lstm_artifacts

    def detect_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Run complete surveillance inference across given market records."""
        logger.info(f"Running hybrid anomaly detection across {len(df)} records...")
        res_df = df.copy().reset_index(drop=True)

        # 1. Isolation Forest scoring
        if_scores = predict_isolation_forest(res_df, self.iforest_artifacts)

        # 2. LSTM Autoencoder scoring
        lstm_errors, lstm_meta, threshold = predict_lstm_reconstruction_errors(
            res_df, self.lstm_artifacts
        )
        lstm_norm = normalize_lstm_errors(lstm_errors, threshold)
        lstm_map = {meta: float(score) for meta, score in zip(lstm_meta, lstm_norm)}

        return self._aggregate_results(res_df, if_scores, lstm_map, threshold)

    def _aggregate_results(
        self,
        df: pd.DataFrame,
        if_scores: np.ndarray,
        lstm_map: Dict[tuple, float],
        threshold: float,
    ) -> List[Dict[str, Any]]:
        """Synthesize model scores, rule flags, and explanations."""
        results = []
        for idx, row in df.iterrows():
            sym = str(row["symbol"])
            dt = str(row["trading_date"])
            if_val = float(if_scores[idx])
            lstm_val = float(lstm_map.get((sym, dt), if_val * 0.5))

            rule_val, reasons = evaluate_microstructure_rules(row.to_dict())
            if if_val > 0.75:
                reasons.append(f"Isolation Forest flagged rare multidimensional feature outlier ({if_val:.2f}).")
            if lstm_val > 0.70:
                reasons.append(f"LSTM Autoencoder detected sequence reconstruction deviation ({lstm_val:.2f}).")

            final_score = compute_hybrid_anomaly_score(if_val, lstm_val, rule_val)
            results.append({
                "symbol": sym,
                "exchange": str(row.get("exchange", "NSE")),
                "trading_date": dt,
                "anomaly_score": final_score,
                "risk_level": categorize_risk_level(final_score),
                "reasons": reasons,
                "model_breakdown": {
                    "isolation_forest_score": round(if_val, 4),
                    "lstm_reconstruction_score": round(lstm_val, 4),
                    "rule_score": round(rule_val, 4),
                },
            })
        return sorted(results, key=lambda x: x["anomaly_score"], reverse=True)
