"""Volume-derived feature engineering calculations."""

import numpy as np
import pandas as pd


def compute_rolling_average_volumes(df: pd.DataFrame) -> pd.DataFrame:
    """Compute rolling volume averages across 5, 10, and 20 day windows."""
    res = df.copy()
    grouped = res.groupby("symbol")["volume"]

    for window in [5, 10, 20]:
        res[f"volume_ma_{window}d"] = grouped.transform(
            lambda s: s.rolling(window, min_periods=2).mean()
        ).fillna(res["volume"])
    return res


def compute_volume_spike_features(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate volume ratio and abnormal volume percentage."""
    res = df.copy()
    if "volume_ma_20d" not in res.columns:
        res = compute_rolling_average_volumes(res)

    safe_ma = res["volume_ma_20d"].replace(0, np.nan)
    res["volume_ratio_20d"] = (res["volume"] / safe_ma).fillna(1.0)

    # Abnormal volume percentage is excess volume over the 20d baseline
    res["abnormal_volume_pct"] = ((res["volume"] - safe_ma) / safe_ma * 100.0).fillna(0.0)
    return res


def compute_volume_z_score_and_acceleration(
    df: pd.DataFrame, window: int = 20
) -> pd.DataFrame:
    """Calculate rolling volume Z-score and volume acceleration."""
    res = df.copy()
    grouped = res.groupby("symbol")["volume"]

    rolling_mean = grouped.transform(lambda s: s.rolling(window, min_periods=3).mean())
    rolling_std = grouped.transform(lambda s: s.rolling(window, min_periods=3).std())

    res["volume_z_score"] = (res["volume"] - rolling_mean) / rolling_std.replace(0, np.nan)
    res["volume_z_score"] = res["volume_z_score"].fillna(0.0)

    # Volume acceleration: delta of daily volume change
    vol_change = grouped.diff().fillna(0.0)
    res["volume_acceleration"] = vol_change.groupby(res["symbol"]).diff().fillna(0.0)
    return res
