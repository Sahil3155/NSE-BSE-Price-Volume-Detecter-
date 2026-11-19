"""Script to train and persist all surveillance machine-learning models."""

import sys
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

import pandas as pd
from backend.app.core.logging import logger
from backend.data_pipeline.feature_engineering.feature_builder import (
    build_surveillance_features,
    CORE_ML_FEATURE_COLUMNS,
)
from backend.ml.isolation_forest.train import train_isolation_forest
from backend.ml.lstm_autoencoder.train import train_lstm_autoencoder


def main():
    """Execute chronological model training workflow."""
    dataset_path = Path("datasets/sample/synthetic_pump_dump_series.csv")
    if not dataset_path.exists():
        logger.error(f"Dataset not found at: {dataset_path}")
        sys.exit(1)

    logger.info(f"Loading dataset from: {dataset_path}")
    raw_df = pd.read_csv(dataset_path)
    featured_df, feature_cols = build_surveillance_features(raw_df)

    # Chronological training split (first 40 days)
    unique_dates = sorted(featured_df["trading_date"].unique())
    split_date = unique_dates[min(40, len(unique_dates) - 1)]
    train_df = featured_df[featured_df["trading_date"] <= split_date]
    logger.info(f"Chronological split at {split_date}: {len(train_df)} train rows.")

    # 1. Train Isolation Forest
    train_isolation_forest(train_df, feature_cols)

    # 2. Train LSTM Autoencoder
    train_lstm_autoencoder(train_df, feature_cols, seq_len=10, epochs=10)

    logger.info("All surveillance models trained and artifacts saved successfully.")


if __name__ == "__main__":
    main()
