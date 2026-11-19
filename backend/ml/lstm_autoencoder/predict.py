"""Inference and reconstruction error evaluation for LSTM Autoencoder."""

from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List
import numpy as np
import pandas as pd
import torch
from backend.app.core.config import settings
from backend.ml.lstm_autoencoder.architecture import LSTMAutoencoder
from backend.ml.lstm_autoencoder.dataset import extract_sliding_sequences


def load_lstm_artifacts(artifact_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load persisted PyTorch LSTM Autoencoder artifacts."""
    target_path = artifact_path or (
        Path(settings.TRAINED_MODELS_DIR) / "lstm_autoencoder" / "lstm_autoencoder.pt"
    )
    if not target_path.exists():
        raise FileNotFoundError(f"LSTM Autoencoder artifact not found at: {target_path}")

    checkpoint = torch.load(target_path, map_location="cpu", weights_only=False)
    model = LSTMAutoencoder(
        input_dim=checkpoint["input_dim"],
        seq_len=checkpoint["seq_len"],
    )
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    checkpoint["model"] = model
    return checkpoint


def predict_lstm_reconstruction_errors(
    df: pd.DataFrame,
    artifacts: Optional[Dict[str, Any]] = None,
) -> Tuple[np.ndarray, List[Tuple[str, str]], float]:
    """Calculate reconstruction error per sliding window sequence."""
    loaded = artifacts or load_lstm_artifacts()
    model: LSTMAutoencoder = loaded["model"]
    normalizer = loaded["normalizer"]
    feature_names = loaded["feature_names"]
    threshold = loaded["calibrated_threshold"]

    scaled_df = normalizer.transform(df)
    sequences, meta = extract_sliding_sequences(scaled_df, feature_names, model.seq_len)

    if len(sequences) == 0:
        return np.array([]), [], threshold

    with torch.no_grad():
        tensors = torch.from_numpy(sequences).float()
        recon = model(tensors)
        # Sequence-level mean squared error
        errors = torch.mean((recon - tensors) ** 2, dim=[1, 2]).numpy()

    return errors, meta, threshold
