"""Data cleaning routines for raw and normalized market feeds."""

from typing import Optional
import pandas as pd
from backend.app.core.logging import logger
from backend.data_pipeline.preprocessing.validation import validate_ohlc_consistency


def parse_trading_dates(series: pd.Series) -> pd.Series:
    """Robustly parse date series into normalized date objects."""
    parsed = pd.to_datetime(series, errors="coerce", dayfirst=True)
    return parsed.dt.strftime("%Y-%m-%d")


def standardize_symbols(series: pd.Series) -> pd.Series:
    """Standardize stock symbol strings."""
    return series.astype(str).str.strip().str.upper()


def clean_market_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean, deduplicate, and sanitize market dataframe."""
    cleaned = df.copy()
    cleaned["symbol"] = standardize_symbols(cleaned["symbol"])
    cleaned["trading_date"] = parse_trading_dates(cleaned["trading_date"])

    # Drop nulls in essential columns
    cleaned = cleaned.dropna(
        subset=["trading_date", "symbol", "open", "high", "low", "close", "volume"]
    )

    # Cast numeric columns safely
    numeric_cols = ["open", "high", "low", "close", "volume"]
    for col in numeric_cols:
        cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")

    cleaned = cleaned.dropna(subset=numeric_cols)

    # Remove invalid OHLC rows
    invalid_mask = validate_ohlc_consistency(cleaned)
    cleaned = cleaned[~invalid_mask]

    # Deduplicate by exchange, symbol, date
    cleaned = cleaned.drop_duplicates(
        subset=["exchange", "symbol", "trading_date"],
        keep="last",
    )
    return cleaned.sort_values(by=["symbol", "trading_date"]).reset_index(drop=True)
