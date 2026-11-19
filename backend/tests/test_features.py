"""Unit and integration tests for feature engineering and data pipelines."""

from pathlib import Path
import pandas as pd
import numpy as np
from backend.data_pipeline.ingestion.nse_loader import load_nse_csv
from backend.data_pipeline.preprocessing.validation import validate_market_dataframe
from backend.data_pipeline.preprocessing.cleaning import clean_market_dataframe
from backend.data_pipeline.preprocessing.normalization import TimeSeriesNormalizer
from backend.data_pipeline.feature_engineering.feature_builder import (
    build_surveillance_features,
    CORE_ML_FEATURE_COLUMNS,
)


def test_nse_bhavcopy_loading():
    """Verify loading and schema mapping for NSE Bhavcopy."""
    bhav_path = Path("datasets/sample/sample_nse_bhavcopy.csv")
    assert bhav_path.exists()
    df = load_nse_csv(bhav_path)
    assert not df.empty
    assert "close" in df.columns
    assert "volume" in df.columns
    assert (df["exchange"] == "NSE").all()


def test_market_validation_and_cleaning():
    """Verify validation rejects corrupted OHLC and cleaning sanitizes data."""
    raw_records = pd.DataFrame([
        {"trading_date": "2024-01-01", "exchange": "NSE", "symbol": "TEST1", "open": 100, "high": 90, "low": 80, "close": 95, "volume": 1000},
        {"trading_date": "2024-01-01", "exchange": "NSE", "symbol": "TEST2", "open": 100, "high": 110, "low": 95, "close": 105, "volume": 5000},
    ])
    cleaned = clean_market_dataframe(raw_records)
    # TEST1 has high (90) < open (100), must be removed
    assert len(cleaned) == 1
    assert cleaned.iloc[0]["symbol"] == "TEST2"


def test_feature_engineering_pipeline():
    """Verify feature generation on multi-day synthetic series."""
    series_path = Path("datasets/sample/synthetic_pump_dump_series.csv")
    raw_df = pd.read_csv(series_path)
    featured_df, cols = build_surveillance_features(raw_df)

    assert not featured_df.empty
    for col in CORE_ML_FEATURE_COLUMNS:
        assert col in featured_df.columns
        assert not featured_df[col].isna().any(), f"NaN found in feature {col}"

    # Verify pump-dump suspect triggers high volume ratio during manipulation
    suspect = featured_df[featured_df["symbol"] == "PUMPDUMP_SUSPECT"]
    assert suspect["volume_ratio_20d"].max() > 3.0
    assert suspect["consecutive_upper_circuits"].max() >= 3


def test_timeseries_normalizer():
    """Verify time series scaling preserves chronological independence."""
    series_path = Path("datasets/sample/synthetic_pump_dump_series.csv")
    raw_df = pd.read_csv(series_path)
    featured_df, cols = build_surveillance_features(raw_df)

    # Chronological split
    train_df = featured_df.iloc[:60]
    test_df = featured_df.iloc[60:]

    normalizer = TimeSeriesNormalizer(method="robust")
    normalizer.fit(train_df, cols[:5])
    scaled_test = normalizer.transform(test_df)

    assert not scaled_test[cols[:5]].isna().any().any()
    assert len(scaled_test) == len(test_df)
