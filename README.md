# NSE/BSE Small-Cap Pump-and-Dump Early Detector (Price + Volume Only)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com)
[![React 18](https://img.shields.io/badge/React-18.3+-61dafb.svg)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-5.4+-646CFF.svg)](https://vitejs.dev/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)

A research-grade AI/ML financial market surveillance system designed to detect abnormal price-volume manipulation signatures in small-cap and micro-cap securities listed on the National Stock Exchange of India (NSE) and the Bombay Stock Exchange (BSE).

---

## 1. Problem Statement & Motivation

Small-cap and micro-cap stocks on Indian exchanges (NSE/BSE) frequently fall victim to social-media-orchestrated pump-and-dump manipulation schemes. Perpetrators quietly accumulate illiquid shares, coordinate promotional campaigns across social media channels (e.g., Telegram, WhatsApp, YouTube), engineer artificial volume spikes and consecutive upper-circuit limits, and subsequently offload their positions onto retail investors during the liquidity crest.

Public enforcement orders issued by the Securities and Exchange Board of India (SEBI) in 2023–2024 highlight that existing surveillance algorithms are tuned for large-cap/index-level movements or crypto markets, leaving small-cap market microstructure unmodeled.

**Our Objective:** Provide an explainable, time-series anomaly-detection engine operating exclusively on **price and volume data**, identifying suspicious patterns prior to or during the early accumulation/pump phase to support regulatory surveillance and investor protection.

---

## 2. Technology Stack

- **Backend:** Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, Uvicorn
- **Data Engineering:** Pandas, NumPy, SciPy
- **Machine Learning & Deep Learning:** Scikit-learn (Isolation Forest), PyTorch (LSTM Autoencoder), Joblib
- **Database & Queue:** PostgreSQL (with optional TimescaleDB extension, SQLite fallback for local test), Redis, Celery
- **Frontend:** React 18, Vite, TypeScript, Tailwind CSS, Recharts, Lucide Icons, React Router DOM, Axios
- **Experiment Tracking:** MLflow
- **Deployment:** Docker, Docker Compose, Nginx

---

## 3. Project Architecture

```
NSE-BSE-Price-Volume-Detecter-/
├── backend/
│   ├── app/                    # FastAPI routes, models, schemas, and services
│   ├── data_pipeline/          # Ingestion, cleaning, and microstructure feature engineering
│   ├── ml/                     # Isolation Forest, PyTorch LSTM Autoencoder, Hybrid Engine
│   ├── tasks/                  # Celery background workers
│   └── tests/                  # Unit and integration test suites
├── frontend/                   # Modern React + Vite + TypeScript surveillance UI
├── datasets/                   # Raw, processed, and sample benchmark datasets
├── trained_models/             # Persisted models and scaler checkpoints
├── docs/                       # Architecture, ML methodology, and API specifications
├── scripts/                    # CLI scripts for database setup, ingestion, training, detection
└── docker-compose.yml          # Containerized multi-service deployment
```

---

## 4. Key Capabilities & Detection Pipeline

1. **Exchange-Aware Ingestion:** Ingests official NSE Bhavcopy CSVs, BSE Bhavcopy CSVs, and ZIP archives with duplicate suppression and validation.
2. **Microstructure Feature Engineering:**
   - Multi-period rolling returns (5d, 10d, 20d) and Log Returns
   - Volume spikes (relative to 20-day moving average) and Volume Z-scores
   - Price-Volume Correlation & Divergence metrics
   - Consecutive Upper/Lower Circuit limit clustering detection
   - Return-Volume interaction & volatility acceleration
3. **Tri-Modal Anomaly Detection:**
   - **Isolation Forest:** High-dimensional unsupervised anomaly isolation
   - **LSTM Autoencoder (PyTorch):** Deep sequence reconstruction error on lookback windows
   - **Deterministic Rule Engine:** Explicit threshold triggers (e.g., circuit runs, 4x volume surge)
4. **Explainable Hybrid Risk Scoring:**
   - Unified 0–100 risk score (Low, Medium, High)
   - Transparent feature breakdown explaining exactly *why* a security was flagged.
   - Zero subjective accusations: flags evidence-based surveillance anomalies.

---

## 5. Local Setup & Execution (Without Docker)

### Prerequisites
- Python 3.11+
- Node.js 18+ (Node 20+ recommended)
- Git

### Backend Setup
```bash
# Clone the repository
git clone https://github.com/sahil/NSE-BSE-Price-Volume-Detecter-.git
cd NSE-BSE-Price-Volume-Detecter-

# Install Python requirements
pip install -r backend/requirements.txt

# Configure environment variables
cp .env.example .env

# Initialize database schema
python scripts/setup_database.py

# Start the FastAPI server
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation will be live at: `http://localhost:8000/api/v1/docs`

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Access the surveillance dashboard at: `http://localhost:5173`

---

## 6. Docker Deployment

To launch all services (PostgreSQL, Redis, Celery Worker, FastAPI backend, and Nginx React frontend):

```bash
docker compose up --build
```

---

## 7. Research Methodology & Weak Labels

SEBI enforcement orders are treated strictly as **weak labels** to benchmark recall and lead time. Time-series cross-validation adheres to strict **chronological splits** to prevent look-ahead bias and feature leakage.
