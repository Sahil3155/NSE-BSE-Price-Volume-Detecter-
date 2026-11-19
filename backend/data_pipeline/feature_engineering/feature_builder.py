"""Master feature builder coordinating all price, volume, and microstructure features."""

from typing import List, Tuple
import pandas as pd
from backend.app.core.logging import logger
from backend.data_pipeline.feature_engineering.price_features import (
    compute_daily_returns,
    compute_rolling_returns,
    compute_price_z_score,
)
from backend.data_pipeline.feature_engineering.volume_features import (
    compute_rolling_average_volumes,
    compute_volume_spike_features,
    compute_volume_z_score_and_acceleration,
)
from backend.data_pipeline.feature_engineering.volatility_features import (
    compute_volatility_features,
    compute_price_volume_interaction,
    compute_circuit_limit_features,
)

CORE_ML_FEATURE_COLUMNS: List[str] = [
    "daily_return",
    "log_return",
    "rolling_return_5d",
    "rolling_return_10d",
    "rolling_return_20d",
    "price_z_score",
    "volume_ratio_20d",
    "abnormal_volume_pct",
    "volume_z_score",
    "volume_acceleration",
    "price_volatility_20d",
    "volume_volatility_20d",
    "return_volume_interaction",
    "price_volume_corr_20d",
    "price_volume_divergence",
    "consecutive_upper_circuits",
]


def build_surveillance_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """Build all surveillance features for given market dataframe."""
    logger.info("Computing price, volume, and microstructure features...")
    res = df.sort_values(by=["symbol", "trading_date"]).reset_index(drop=True)

    # Price features
    res = compute_daily_returns(res)
    res = compute_rolling_returns(res)
    res = compute_price_z_score(res)

    # Volume features
    res = compute_rolling_average_volumes(res)
    res = compute_volume_spike_features(res)
    res = compute_volume_z_score_and_acceleration(res)

    # Volatility and interaction features
    res = compute_volatility_features(res)
    res = compute_price_volume_interaction(res)
    res = compute_circuit_limit_features(res)

    # Replace any remnant NaNs or infs safely
    for col in CORE_ML_FEATURE_COLUMNS:
        if col in res.columns:
            res[col] = res[col].fillna(0.0)

    logger.info(f"Engineered {len(CORE_ML_FEATURE_COLUMNS)} core features for {len(res)} rows.")
    return res, CORE_ML_FEATURE_COLUMNS
