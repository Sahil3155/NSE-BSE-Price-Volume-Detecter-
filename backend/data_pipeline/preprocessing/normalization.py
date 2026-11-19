"""Feature normalization and scaling utilities preserving time-series integrity."""

from typing import Tuple, List, Optional
import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler, StandardScaler


class TimeSeriesNormalizer:
    """Scaler wrapper ensuring fit only occurs on chronological training sets."""

    def __init__(self, method: str = "robust"):
        self.method = method
        self.scaler = RobustScaler() if method == "robust" else StandardScaler()
        self.feature_names: List[str] = []
        self.is_fitted: bool = False

    def fit(self, df: pd.DataFrame, feature_columns: List[str]) -> "TimeSeriesNormalizer":
        """Fit scaler parameters exclusively on training features."""
        self.feature_names = feature_columns
        data = df[feature_columns].replace([np.inf, -np.inf], np.nan).fillna(0)
        self.scaler.fit(data)
        self.is_fitted = True
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform target dataframe features using fitted parameters."""
        if not self.is_fitted:
            raise RuntimeError("Normalizer must be fitted on training data before transform.")
        scaled_df = df.copy()
        data = scaled_df[self.feature_names].replace([np.inf, -np.inf], np.nan).fillna(0)
        transformed = self.scaler.transform(data)
        for idx, col in enumerate(self.feature_names):
            scaled_df[col] = transformed[:, idx]
        return scaled_df

    def fit_transform(
        self, df: pd.DataFrame, feature_columns: List[str]
    ) -> Tuple[pd.DataFrame, "TimeSeriesNormalizer"]:
        """Fit on training data and return scaled dataframe with normalizer."""
        self.fit(df, feature_columns)
        return self.transform(df), self
