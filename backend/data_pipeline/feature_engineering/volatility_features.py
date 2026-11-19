"""Volatility and price-volume interaction feature calculations."""

import numpy as np
import pandas as pd


def compute_volatility_features(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """Calculate rolling annualized price volatility and volume volatility."""
    res = df.copy()
    grouped = res.groupby("symbol")

    # Annualized price volatility from daily log returns (252 trading days)
    if "log_return" in res.columns:
        res["price_volatility_20d"] = grouped["log_return"].transform(
            lambda s: s.rolling(window, min_periods=3).std() * np.sqrt(252)
        ).fillna(0.0)
    else:
        res["price_volatility_20d"] = 0.0

    # Rolling coefficient of variation of volume
    vol_mean = grouped["volume"].transform(lambda s: s.rolling(window, min_periods=3).mean())
    vol_std = grouped["volume"].transform(lambda s: s.rolling(window, min_periods=3).std())
    res["volume_volatility_20d"] = (vol_std / vol_mean.replace(0, np.nan)).fillna(0.0)
    return res


def compute_price_volume_interaction(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate price-volume correlation, divergence, and interaction term."""
    res = df.copy()

    # Return-Volume interaction: daily return scaled by log volume
    log_vol = np.log1p(res["volume"].clip(lower=0))
    res["return_volume_interaction"] = res["daily_return"] * log_vol

    # Rolling price-volume correlation
    def calc_corr(sub_df: pd.DataFrame) -> pd.Series:
        return sub_df["daily_return"].rolling(20, min_periods=5).corr(sub_df["volume"]).fillna(0.0)

    res["price_volume_corr_20d"] = (
        res.groupby("symbol", group_keys=False).apply(calc_corr)
        if "daily_return" in res.columns
        else 0.0
    )

    # Divergence indicator: high positive return with collapsing volume
    vol_ratio = res.get("volume_ratio_20d", 1.0)
    res["price_volume_divergence"] = (
        (res["daily_return"] > 5.0) & (vol_ratio < 0.5)
    ).astype(float)
    return res


def compute_circuit_limit_features(df: pd.DataFrame) -> pd.DataFrame:
    """Detect consecutive upper-circuit clustering."""
    res = df.copy()
    # Upper circuit: daily return >= 4.8% and close within 0.5% of day high
    high_close_spread = (res["high"] - res["close"]).abs() / res["close"].replace(0, np.nan)
    is_upper_circuit = (res["daily_return"] >= 4.8) & (high_close_spread <= 0.006)
    res["is_upper_circuit"] = is_upper_circuit.astype(int)

    def count_consecutive(series: pd.Series) -> pd.Series:
        is_circuit = series.astype(bool)
        runs = series.groupby((~is_circuit).cumsum()).cumsum()
        return runs

    res["consecutive_upper_circuits"] = (
        res.groupby("symbol")["is_upper_circuit"].transform(count_consecutive)
    )
    return res
