"""Inference module for Isolation Forest model."""

from pathlib import Path
from typing import Optional, Dict, Any
import numpy as np
import pandas as pd
import joblib
from backend.app.core.config import settings


def load_isolation_forest_artifacts(artifact_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load Isolation Forest model and preprocessing artifacts."""
    target_path = artifact_path or (
        Path(settings.TRAINED_MODELS_DIR) / "isolation_forest" / "isolation_forest.joblib"
    )
    if not target_path.exists():
        raise FileNotFoundError(f"Isolation Forest model not found at: {target_path}")
    return joblib.load(target_path)


def predict_isolation_forest(
    df: pd.DataFrame,
    artifacts: Optional[Dict[str, Any]] = None,
) -> np.ndarray:
    """Generate normalized anomaly scores using Isolation Forest."""
    loaded = artifacts or load_isolation_forest_artifacts()
    model = loaded["model"]
    normalizer = loaded["normalizer"]
    feature_names = loaded["feature_names"]

    scaled_df = normalizer.transform(df)
    X = scaled_df[feature_names].values
    scores = model.score_samples(X)
    return scores
