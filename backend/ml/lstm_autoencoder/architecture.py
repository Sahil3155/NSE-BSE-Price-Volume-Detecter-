"""PyTorch LSTM Autoencoder architecture for time-series anomaly detection."""

import torch
import torch.nn as nn


class LSTMEncoder(nn.Module):
    """Sequence encoder compressing time-series window into latent representation."""

    def __init__(self, input_dim: int, hidden_dim: int = 32, num_layers: int = 1):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Encode input sequence into final hidden state."""
        _, (hn, _) = self.lstm(x)
        return hn[-1]


class LSTMDecoder(nn.Module):
    """Sequence decoder reconstructing original time-series from latent vector."""

    def __init__(self, seq_len: int, hidden_dim: int = 32, output_dim: int = 16, num_layers: int = 1):
        super().__init__()
        self.seq_len = seq_len
        self.lstm = nn.LSTM(
            input_size=hidden_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
        )
        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        """Reconstruct sequence by repeating latent vector across sequence length."""
        repeated = z.unsqueeze(1).repeat(1, self.seq_len, 1)
        out, _ = self.lstm(repeated)
        return self.fc(out)


class LSTMAutoencoder(nn.Module):
    """End-to-end LSTM Autoencoder model."""

    def __init__(
        self,
        input_dim: int,
        seq_len: int = 10,
        hidden_dim: int = 32,
        num_layers: int = 1,
    ):
        super().__init__()
        self.input_dim = input_dim
        self.seq_len = seq_len
        self.encoder = LSTMEncoder(input_dim, hidden_dim, num_layers)
        self.decoder = LSTMDecoder(seq_len, hidden_dim, input_dim, num_layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Reconstruct input tensor through latent bottleneck."""
        z = self.encoder(x)
        return self.decoder(z)
