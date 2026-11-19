# Installation Guide

## System Requirements
- OS: Windows 10/11, macOS, or Linux
- Python 3.11+
- Node.js 18+ (Node 20+ recommended)
- Optional: Docker & Docker Compose

---

## Local Installation (Windows / Native)

### 1. Python Environment Setup
```powershell
# Clone the repository
git clone https://github.com/sahil/NSE-BSE-Price-Volume-Detecter-.git
cd NSE-BSE-Price-Volume-Detecter-

# Install Python requirements
python -m pip install -r backend/requirements.txt
```

### 2. Configure Environment
```powershell
Copy-Item .env.example .env
```
Default `.env` is configured for rapid local testing using SQLite (`USE_SQLITE_FALLBACK=True`).

### 3. Setup Database & Ingest Sample Benchmark Data
```powershell
# Initialize all 10 relational tables
python scripts/setup_database.py

# Generate synthetic benchmark dataset
python scripts/generate_sample_datasets.py

# Ingest benchmark records
python scripts/import_dataset.py

# Train Isolation Forest & PyTorch LSTM Autoencoder
python scripts/train_models.py
```

### 4. Start Backend Server
```powershell
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
Swagger API UI will be available at: `http://localhost:8000/api/v1/docs`

### 5. Start Frontend Development Server
```powershell
cd frontend
npm install
npm run dev
```
Open your browser at `http://localhost:5173`.

---

## Containerized Deployment (Docker Compose)
```powershell
docker compose up --build
```
This automatically boots PostgreSQL, Redis, Celery Worker, FastAPI backend, and Nginx React frontend.
