"""SEBI enforcement orders loader for weak-label evaluation benchmarking."""

from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
from backend.app.core.logging import logger

SEBI_REQUIRED_COLUMNS: List[str] = [
    "order_id",
    "order_date",
    "stock_symbol",
    "exchange",
    "allegation_type",
    "investigation_start_date",
    "investigation_end_date",
]


def validate_sebi_dataframe(df: pd.DataFrame) -> bool:
    """Check required columns for SEBI enforcement weak labels."""
    missing = [c for c in SEBI_REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        logger.warning(f"SEBI orders dataset missing columns: {missing}")
        return False
    return True


def load_sebi_orders(file_path: Path) -> pd.DataFrame:
    """Load and validate SEBI enforcement dataset."""
    logger.info(f"Loading SEBI orders from: {file_path}")
    df = pd.read_csv(file_path)
    if not validate_sebi_dataframe(df):
        raise ValueError(f"Invalid schema in SEBI orders file: {file_path}")

    cleaned = df.copy()
    cleaned["stock_symbol"] = cleaned["stock_symbol"].astype(str).str.strip().str.upper()
    cleaned["order_date"] = pd.to_datetime(cleaned["order_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    cleaned["investigation_start_date"] = pd.to_datetime(
        cleaned["investigation_start_date"], errors="coerce"
    ).dt.strftime("%Y-%m-%d")
    cleaned["investigation_end_date"] = pd.to_datetime(
        cleaned["investigation_end_date"], errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    return cleaned.dropna(subset=["stock_symbol", "investigation_start_date", "investigation_end_date"])
