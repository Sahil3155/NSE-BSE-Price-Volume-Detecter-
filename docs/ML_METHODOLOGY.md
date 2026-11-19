# Machine Learning Methodology

## 1. Feature Engineering (Price & Volume Exclusively)
The feature pipeline calculates 16 microstructure metrics with strict anti-lookahead rules:
- **Price Trajectory:** Daily percentage return, Log return, 5-day, 10-day, and 20-day cumulative rolling returns, Price Z-score ($Z = \frac{Close_t - \mu_{20}}{\sigma_{20}}$).
- **Volume Surges:** 5-day, 10-day, and 20-day rolling average volumes, Volume Ratio ($\frac{Volume_t}{MA_{20}}$), Abnormal Volume Percentage, Volume Z-score, Volume Acceleration ($\Delta^2 Volume$).
- **Interaction & Volatility:** 20-day annualized volatility ($\sigma_{log} \times \sqrt{252}$), Volume coefficient of variation ($\frac{\sigma_{vol}}{\mu_{vol}}$), Return-Volume interaction ($Return_t \times \ln(Volume_t + 1)$), 20-day rolling Price-Volume correlation, Price-Volume Divergence indicator.
- **Circuit Clustering:** Consecutive upper circuit limit runs where $Close \approx High$ and $DailyReturn \ge 4.8\%$.

## 2. Models
### A. Isolation Forest
- **Paradigm:** Unsupervised non-parametric isolation of multivariate outliers.
- **Hypothesis:** Small-cap pump-and-dump anomalies are rare and exhibit extreme values in multidimensional price-volume space, requiring fewer tree splits to isolate.
- **Hyperparameters:** `n_estimators=150`, `contamination=0.05`, `max_samples=0.8`.

### B. PyTorch LSTM Autoencoder
- **Architecture:** 1-layer LSTM Encoder (hidden dim 32) compressing 10-day lookback sequences, connected to an LSTM Decoder that reconstructs the sequence.
- **Hypothesis:** An autoencoder trained on normal market behaviour fails to reconstruct sudden coordinated volume surges and circuit clusters, producing elevated sequence reconstruction errors (MSE).
- **Calibration:** Threshold calibrated as the 95th percentile of reconstruction loss on normal chronological training periods.

### C. Deterministic Rule Engine
- Evaluates domain-specific surveillance rules:
  1. Volume Ratio $\ge 4.0\times$ baseline.
  2. Daily price gain $\ge +10\%$.
  3. Consecutive upper circuits $\ge 3$.
  4. Volume Z-score $\ge 3.0\sigma$.

### D. Hybrid Risk Scoring
$$\text{Score} = (0.40 \times S_{\text{IF}} + 0.35 \times S_{\text{LSTM}} + 0.25 \times S_{\text{Rules}}) \times 100$$
- **High Risk:** $\text{Score} \ge 75$
- **Medium Risk:** $50 \le \text{Score} < 75$
- **Low Risk:** $\text{Score} < 50$

## 3. Evaluation & Weak Labels
SEBI enforcement orders are treated as weak ground-truth labels. Metrics reported include Precision, Recall, F1-score, ROC-AUC, PR-AUC, and False Positive Rate (FPR), strictly separated chronologically to prevent time-series leakage.
