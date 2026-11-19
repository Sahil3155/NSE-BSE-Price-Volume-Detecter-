"""End-to-end data pipeline orchestrator."""

from pathlib import Path
from typing import Tuple, Optional
import pandas as pd
from backend.app.core.logging import logger
from backend.data_pipeline.ingestion.nse_loader import load_nse_csv, load_nse_zip
from backend.data_pipeline.ingestion.bse_loader import load_bse_csv, load_bse_zip
from backend.data_pipeline.preprocessing.validation import validate_market_dataframe
from backend.data_pipeline.feature_engineering.feature_builder import build_surveillance_features


def load_dataset_file(file_path: Path, exchange: str = "NSE") -> pd.DataFrame:
    """Ingest raw dataset file based on exchange and extension."""
    suffix = file_path.suffix.lower()
    if exchange.upper() == "NSE":
        return load_nse_zip(file_path) if suffix == ".zip" else load_nse_csv(file_path)
    if exchange.upper() == "BSE":
        return load_bse_zip(file_path) if suffix == ".zip" else load_bse_csv(file_path)
    raise ValueError(f"Unsupported exchange or file type: {exchange}, {suffix}")


def run_ingestion_and_feature_pipeline(
    file_path: Path,
    exchange: str = "NSE",
    output_path: Optional[Path] = None,
) -> Tuple[pd.DataFrame, dict]:
    """Execute end-to-end ingestion, validation, and feature generation."""
    logger.info(f"Running pipeline for {file_path} on {exchange}")
    raw_df = load_dataset_file(file_path, exchange)

    is_valid, report = validate_market_dataframe(raw_df)
    if not is_valid:
        raise ValueError(f"Market dataframe validation failed: {report}")

    featured_df, feature_cols = build_surveillance_features(raw_df)
    report["feature_count"] = len(feature_cols)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        featured_df.to_parquet(output_path, index=False)
        logger.info(f"Saved processed dataset to: {output_path}")

    return featured_df, report
