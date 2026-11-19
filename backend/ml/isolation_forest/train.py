"""Training pipeline for Isolation Forest anomaly detection."""

from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import joblib
import pandas as pd
from backend.app.core.logging import logger
from backend.app.core.config import settings
from backend.data_pipeline.preprocessing.normalization import TimeSeriesNormalizer
from backend.ml.isolation_forest.model import IsolationForestSurveillanceModel


def save_isolation_forest_artifacts(
    model: IsolationForestSurveillanceModel,
    normalizer: TimeSeriesNormalizer,
    feature_names: List[str],
    output_dir: Path,
) -> Path:
    """Persist trained model, normalizer, and metadata to disk."""
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "model": model,
        "normalizer": normalizer,
        "feature_names": feature_names,
    }
    artifact_path = output_dir / "isolation_forest.joblib"
    joblib.dump(payload, artifact_path)
    logger.info(f"Isolation Forest artifacts saved to: {artifact_path}")
    return artifact_path


def train_isolation_forest(
    train_df: pd.DataFrame,
    feature_names: List[str],
    contamination: float = 0.05,
    output_dir: Optional[Path] = None,
) -> Tuple[IsolationForestSurveillanceModel, TimeSeriesNormalizer]:
    """Train and persist Isolation Forest model on chronological training data."""
    logger.info(f"Training Isolation Forest on {len(train_df)} observations...")
    normalizer = TimeSeriesNormalizer(method="robust")
    scaled_df, _ = normalizer.fit_transform(train_df, feature_names)

    X_train = scaled_df[feature_names].values
    model = IsolationForestSurveillanceModel(contamination=contamination)
    model.fit(X_train)

    dest_dir = output_dir or (Path(settings.TRAINED_MODELS_DIR) / "isolation_forest")
    save_isolation_forest_artifacts(model, normalizer, feature_names, dest_dir)
    return model, normalizer
