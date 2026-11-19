"""Price-derived feature engineering calculations without look-ahead bias."""

import numpy as np
import pandas as pd


def compute_daily_returns(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate daily percentage return and log return per symbol."""
    res = df.copy()
    grouped = res.groupby("symbol")["close"]
    prev_close = grouped.shift(1)

    res["daily_return"] = ((res["close"] - prev_close) / prev_close.replace(0, np.nan)) * 100.0
    res["daily_return"] = res["daily_return"].fillna(0.0)

    # Log returns
    ratio = res["close"] / prev_close.replace(0, np.nan)
    res["log_return"] = np.log(ratio.where(ratio > 0, np.nan)).fillna(0.0)
    return res


def compute_rolling_returns(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate 5-day, 10-day, and 20-day cumulative rolling returns."""
    res = df.copy()
    grouped = res.groupby("symbol")["close"]

    for window in [5, 10, 20]:
        past_close = grouped.shift(window)
        col_name = f"rolling_return_{window}d"
        res[col_name] = ((res["close"] - past_close) / past_close.replace(0, np.nan)) * 100.0
        res[col_name] = res[col_name].fillna(0.0)
    return res


def compute_price_z_score(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """Calculate rolling price Z-score relative to rolling mean and std."""
    res = df.copy()
    grouped = res.groupby("symbol")["close"]

    rolling_mean = grouped.transform(lambda s: s.rolling(window, min_periods=3).mean())
    rolling_std = grouped.transform(lambda s: s.rolling(window, min_periods=3).std())

    # Avoid zero division
    res["price_z_score"] = (res["close"] - rolling_mean) / rolling_std.replace(0, np.nan)
    res["price_z_score"] = res["price_z_score"].fillna(0.0)
    return res
