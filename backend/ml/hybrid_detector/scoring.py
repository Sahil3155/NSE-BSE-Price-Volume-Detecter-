"""Hybrid scoring engine combining model scores and deterministic microstructure rules."""

from typing import Dict, Any, List, Tuple
from backend.app.core.config import settings


def evaluate_microstructure_rules(row: Dict[str, Any]) -> Tuple[float, List[str]]:
    """Evaluate deterministic rules and formulate plain-language evidence explanations."""
    rule_score = 0.0
    reasons = []

    # 1. Volume surge rule
    vol_ratio = row.get("volume_ratio_20d", 1.0)
    if vol_ratio >= settings.VOLUME_SPIKE_RATIO_THRESHOLD:
        rule_score += 0.35
        reasons.append(f"Trading volume is {vol_ratio:.1f}x its 20-day moving average.")

    # 2. Daily price jump rule
    daily_ret = row.get("daily_return", 0.0)
    if daily_ret >= settings.PRICE_CHANGE_ALERT_THRESHOLD:
        rule_score += 0.25
        reasons.append(f"Abnormal single-day price gain of +{daily_ret:.1f}%.")

    # 3. Consecutive upper circuits
    circuits = int(row.get("consecutive_upper_circuits", 0))
    if circuits >= settings.CONSECUTIVE_CIRCUITS_ALERT:
        rule_score += 0.25
        reasons.append(f"Security hit {circuits} consecutive upper-circuit limits.")

    # 4. Statistical volume outlier
    z_vol = row.get("volume_z_score", 0.0)
    if z_vol >= settings.Z_SCORE_VOLUME_THRESHOLD:
        rule_score += 0.15
        reasons.append(f"Volume Z-score ({z_vol:.2f}) exceeded statistical threshold.")

    return min(1.0, rule_score), reasons


def compute_hybrid_anomaly_score(
    iforest_score: float,
    lstm_score: float,
    rule_score: float,
    weight_iforest: float = 0.40,
    weight_lstm: float = 0.35,
    weight_rules: float = 0.25,
) -> float:
    """Calculate weighted composite anomaly score on scale [0, 100]."""
    composite = (
        (iforest_score * weight_iforest)
        + (lstm_score * weight_lstm)
        + (rule_score * weight_rules)
    )
    return round(float(composite * 100.0), 2)


def categorize_risk_level(score: float) -> str:
    """Classify anomaly risk level based on configured thresholds."""
    if score >= settings.HYBRID_HIGH_RISK_THRESHOLD:
        return "HIGH"
    if score >= settings.HYBRID_MEDIUM_RISK_THRESHOLD:
        return "MEDIUM"
    return "LOW"
