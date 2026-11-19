"""Data validation module for incoming market and exchange records."""

from typing import List, Tuple, Dict, Any
import pandas as pd
from backend.app.core.logging import logger

CANONICAL_COLUMNS: List[str] = [
    "trading_date",
    "exchange",
    "symbol",
    "open",
    "high",
    "low",
    "close",
    "volume",
]


def check_required_columns(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Validate presence of all required canonical columns."""
    missing = [col for col in CANONICAL_COLUMNS if col not in df.columns]
    if missing:
        logger.error(f"Missing required columns in dataset: {missing}")
        return False, missing
    return True, []


def validate_ohlc_consistency(df: pd.DataFrame) -> pd.Series:
    """Identify rows violating standard OHLC price bounds."""
    invalid_bounds = (
        (df["high"] < df["low"])
        | (df["high"] < df["open"])
        | (df["high"] < df["close"])
        | (df["low"] > df["open"])
        | (df["low"] > df["close"])
        | (df["open"] <= 0)
        | (df["close"] <= 0)
        | (df["volume"] < 0)
    )
    return invalid_bounds


def validate_market_dataframe(df: pd.DataFrame) -> Tuple[bool, Dict[str, Any]]:
    """Execute complete validation suite on a market dataframe."""
    is_valid_cols, missing = check_required_columns(df)
    if not is_valid_cols:
        return False, {"error": "Missing columns", "details": missing}

    if df.empty:
        return False, {"error": "Empty dataframe", "details": 0}

    invalid_mask = validate_ohlc_consistency(df)
    invalid_count = int(invalid_mask.sum())
    report = {
        "total_rows": len(df),
        "valid_rows": len(df) - invalid_count,
        "invalid_ohlc_rows": invalid_count,
    }
    return True, report
