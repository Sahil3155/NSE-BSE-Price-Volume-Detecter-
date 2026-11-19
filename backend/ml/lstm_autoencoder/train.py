"""Training routines for the LSTM Autoencoder."""

from pathlib import Path
from typing import List, Tuple, Optional
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from backend.app.core.logging import logger
from backend.app.core.config import settings
from backend.data_pipeline.preprocessing.normalization import TimeSeriesNormalizer
from backend.ml.lstm_autoencoder.architecture import LSTMAutoencoder
from backend.ml.lstm_autoencoder.dataset import extract_sliding_sequences, TimeSeriesSequenceDataset


def execute_training_epochs(
    model: LSTMAutoencoder,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    epochs: int = 10,
) -> List[float]:
    """Execute forward and backward passes across epochs."""
    epoch_losses = []
    model.train()
    for ep in range(epochs):
        total_loss = 0.0
        for batch in loader:
            optimizer.zero_grad()
            recon = model(batch)
            loss = criterion(recon, batch)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        epoch_losses.append(total_loss / max(1, len(loader)))
    return epoch_losses


def save_lstm_artifacts(
    model: LSTMAutoencoder,
    normalizer: TimeSeriesNormalizer,
    feature_names: List[str],
    threshold: float,
    output_dir: Path,
) -> Path:
    """Save PyTorch weights and scaling parameters."""
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "lstm_autoencoder.pt"
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "input_dim": model.input_dim,
            "seq_len": model.seq_len,
            "normalizer": normalizer,
            "feature_names": feature_names,
            "calibrated_threshold": threshold,
        },
        out_path,
    )
    logger.info(f"LSTM Autoencoder saved to: {out_path}")
    return out_path


def train_lstm_autoencoder(
    train_df: pd.DataFrame,
    feature_names: List[str],
    seq_len: int = 10,
    epochs: int = 10,
    output_dir: Optional[Path] = None,
) -> Tuple[LSTMAutoencoder, float]:
    """Train sequence LSTM Autoencoder on chronological market data."""
    normalizer = TimeSeriesNormalizer(method="robust")
    scaled_df, _ = normalizer.fit_transform(train_df, feature_names)

    sequences, _ = extract_sliding_sequences(scaled_df, feature_names, seq_len)
    if len(sequences) == 0:
        raise ValueError("Insufficient sequence history to train LSTM Autoencoder.")

    dataset = TimeSeriesSequenceDataset(sequences)
    loader = DataLoader(dataset, batch_size=32, shuffle=True)

    model = LSTMAutoencoder(input_dim=len(feature_names), seq_len=seq_len)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.MSELoss()

    execute_training_epochs(model, loader, optimizer, criterion, epochs=epochs)

    # Calibrate threshold as 95th percentile of training reconstruction errors
    model.eval()
    with torch.no_grad():
        all_tensors = torch.from_numpy(sequences).float()
        recon = model(all_tensors)
        errors = torch.mean((recon - all_tensors) ** 2, dim=[1, 2]).numpy()
        threshold = float(np.percentile(errors, 95))

    dest = output_dir or (Path(settings.TRAINED_MODELS_DIR) / "lstm_autoencoder")
    save_lstm_artifacts(model, normalizer, feature_names, threshold, dest)
    return model, threshold
