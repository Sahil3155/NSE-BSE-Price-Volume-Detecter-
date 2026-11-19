"""Dataset and sliding sequence builder for LSTM Autoencoder."""

from typing import List, Tuple
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset


def extract_sliding_sequences(
    df: pd.DataFrame,
    feature_cols: List[str],
    seq_len: int = 10,
) -> Tuple[np.ndarray, List[Tuple[str, str]]]:
    """Generate chronological sliding windows per symbol without cross-stock contamination."""
    sequences = []
    metadata = []  # List of (symbol, target_trading_date)

    for symbol, group in df.groupby("symbol"):
        sorted_group = group.sort_values("trading_date")
        values = sorted_group[feature_cols].values
        dates = sorted_group["trading_date"].tolist()

        if len(values) < seq_len:
            continue

        for i in range(len(values) - seq_len + 1):
            sequences.append(values[i : i + seq_len])
            metadata.append((symbol, dates[i + seq_len - 1]))

    if not sequences:
        return np.empty((0, seq_len, len(feature_cols))), []

    return np.array(sequences, dtype=np.float32), metadata


class TimeSeriesSequenceDataset(Dataset):
    """PyTorch Dataset wrapping sliding sequence matrices."""

    def __init__(self, sequences: np.ndarray):
        self.tensors = torch.from_numpy(sequences).float()

    def __len__(self) -> int:
        return len(self.tensors)

    def __getitem__(self, idx: int) -> torch.Tensor:
        return self.tensors[idx]
