"""Unified model artifact loader."""

from pathlib import Path
from typing import Dict, Any, Optional
from backend.app.core.config import settings
from backend.ml.isolation_forest.predict import load_isolation_forest_artifacts
from backend.ml.lstm_autoencoder.predict import load_lstm_artifacts


class ModelRegistryLoader:
    """Manages loading and caching of surveillance models."""

    def __init__(self, models_dir: Optional[Path] = None):
        self.models_dir = models_dir or Path(settings.TRAINED_MODELS_DIR)
        self._iforest_cache: Optional[Dict[str, Any]] = None
        self._lstm_cache: Optional[Dict[str, Any]] = None

    def get_isolation_forest(self) -> Dict[str, Any]:
        """Retrieve cached Isolation Forest artifacts."""
        if self._iforest_cache is None:
            path = self.models_dir / "isolation_forest" / "isolation_forest.joblib"
            self._iforest_cache = load_isolation_forest_artifacts(path)
        return self._iforest_cache

    def get_lstm_autoencoder(self) -> Dict[str, Any]:
        """Retrieve cached LSTM Autoencoder artifacts."""
        if self._lstm_cache is None:
            path = self.models_dir / "lstm_autoencoder" / "lstm_autoencoder.pt"
            self._lstm_cache = load_lstm_artifacts(path)
        return self._lstm_cache
