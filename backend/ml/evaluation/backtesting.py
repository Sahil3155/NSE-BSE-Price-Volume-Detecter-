"""Historical backtesting framework using SEBI enforcement weak labels."""

from typing import List, Dict, Any, Tuple
import pandas as pd
import numpy as np


def map_sebi_weak_labels_to_market_data(
    market_df: pd.DataFrame,
    sebi_df: pd.DataFrame,
) -> pd.Series:
    """Label market trading dates as suspicious (1) if within SEBI investigation window."""
    labels = pd.Series(0, index=market_df.index)
    for _, order in sebi_df.iterrows():
        sym = order["stock_symbol"]
        start_dt = order["investigation_start_date"]
        end_dt = order["investigation_end_date"]

        mask = (
            (market_df["symbol"] == sym)
            & (market_df["trading_date"] >= start_dt)
            & (market_df["trading_date"] <= end_dt)
        )
        labels[mask] = 1
    return labels


def calculate_detection_lead_time(
    detections: List[Dict[str, Any]],
    event_start_date: str,
    target_symbol: str,
) -> int:
    """Compute surveillance lead time in days prior to event or peak."""
    symbol_dets = [
        d for d in detections
        if d["symbol"] == target_symbol and d["risk_level"] in ["MEDIUM", "HIGH"]
    ]
    if not symbol_dets:
        return 0

    earliest_alert_date = min(d["trading_date"] for d in symbol_dets)
    lead_days = (
        pd.to_datetime(event_start_date) - pd.to_datetime(earliest_alert_date)
    ).days
    return max(0, lead_days)
