# Project Overview — NSE/BSE Small-Cap Pump-and-Dump Early Detector

## Executive Summary
The **NSE/BSE Small-Cap Pump-and-Dump Early Detector** is an AI-powered surveillance system engineered to identify price and volume manipulation signatures in small-cap and micro-cap securities listed on the National Stock Exchange of India (NSE) and the Bombay Stock Exchange (BSE).

Unlike large-cap surveillance models and cryptocurrency fraud detection tools, this project specifically models the unique market microstructure of Indian equity markets — particularly **sudden volume surges, consecutive circuit-limit locks, low-float accumulation, and price-volume divergence** — strictly using historical **price and volume data without external sentiment or news indicators**.

---

## The Market Vulnerability: Small-Cap Pump-and-Dump in India
Small-cap and micro-cap stocks with thin trading floats and limited institutional ownership are disproportionately targeted by coordinated manipulation syndicates. A typical scheme follows three distinct stages:

1. **Quiet Accumulation:** Perpetrators quietly accumulate shares over days or weeks when trading volume is minimal, keeping prices relatively steady.
2. **Promotional Pump Phase:** Synergistic social-media campaigns (Telegram channels, WhatsApp groups, YouTube influencers) tout exponential upside. Coordinated buying creates artificial volume spikes (4x–10x normal volume) and triggers consecutive upper circuit limits (5%, 10%, or 20% price bands).
3. **Liquidity Distribution & Dump:** The perpetrators dump their accumulated holdings into the incoming retail buying frenzy, precipitating subsequent lower-circuit locks where trapped retail buyers cannot exit.

Enforcement orders issued by SEBI in 2023–2024 (e.g., in the matters of Sadhna Broadcast, Sharpline Broadcast, and various micro-cap Telegram pump groups) demonstrate an urgent surveillance need for early algorithmic flagging before the dump occurs.

---

## Core Detection Paradigm
To maintain objective scientific rigor, the application does not make definitive accusations of fraud; instead, it generates **quantified surveillance anomaly alerts** with **transparent evidence breakdowns**:
- **Isolation Forest:** High-dimensional unsupervised isolation of anomalous price-volume vectors.
- **PyTorch LSTM Autoencoder:** Deep sequence reconstruction error on 10-day sliding windows, identifying temporal trajectory deviations from baseline behaviour.
- **Deterministic Microstructure Rules:** Explicit checks for volume multiples, single-day percentage gains, and consecutive circuit hits.
- **Hybrid Risk Scoring (0–100):** Weighted combination (40% IF + 35% LSTM + 25% Rules) categorized into **Low**, **Medium**, and **High** risk bands.
