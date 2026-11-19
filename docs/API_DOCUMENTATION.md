# API Documentation — Surveillance Endpoints

Base URL: `http://localhost:8000/api/v1`

---

## 1. Health
### `GET /health`
Returns system status, active database connectivity, and environment mode.
- **Response 200:**
  ```json
  {
    "status": "healthy",
    "app_name": "NSE/BSE Pump-and-Dump Early Detector",
    "environment": "development",
    "database_connected": true,
    "timestamp": "2024-03-01T12:00:00Z",
    "version": "1.0.0"
  }
  ```

---

## 2. Stocks
### `GET /stocks`
Query catalog of listed equities.
- **Query Parameters:** `exchange` (NSE, BSE), `limit` (default 50), `offset` (default 0).
- **Response 200:** Array of `StockResponse`.

### `GET /stocks/{symbol}`
Fetch stock metadata for a specific ticker symbol.

### `GET /stocks/{symbol}/history`
Fetch chronological OHLCV series, returns, and circuit runs.
- **Query Parameters:** `start_date` (YYYY-MM-DD), `end_date` (YYYY-MM-DD).

---

## 3. Market Data
### `POST /market-data/upload`
Upload raw Bhavcopy CSV or ZIP file for ingestion and feature generation.
- **Form Data:** `file` (multipart), `exchange` ("NSE" or "BSE").
- **Response 200:** `MarketDataUploadResponse`.

### `GET /market-data/status`
Statistical summary of loaded market data, total equities, and date coverage.

---

## 4. Detection
### `POST /detection/run`
Trigger surveillance anomaly scoring.
- **Request Body:**
  ```json
  {
    "exchange": "NSE",
    "symbol": "PUMPDUMP_SUSPECT",
    "model_name": "HYBRID"
  }
  ```
- **Response 200:** `DetectionRunResponse` with ranked anomalies and evidence breakdown.

---

## 5. Alerts
### `GET /alerts`
Query surveillance alerts.
- **Query Parameters:** `risk_level` (HIGH, MEDIUM, LOW), `status` (PENDING_REVIEW, INVESTIGATING, etc.), `symbol`.

### `PATCH /alerts/{alert_id}/status`
Update investigation review status and desk notes.
- **Request Body:**
  ```json
  {
    "status": "INVESTIGATING",
    "investigator_notes": "Under review by surveillance desk."
  }
  ```

---

## 6. Analytics
- `GET /analytics/overview`: Macro statistics for surveillance dashboard.
- `GET /analytics/anomaly-trends`: Daily time-series anomaly counts.
- `GET /analytics/model-comparison`: Comparative benchmark metrics across all four models.

---

## 7. Model Management
- `POST /models/train`: Dispatches background retraining job.
- `GET /models`: Lists registered model artifacts and status.
- `GET /models/performance`: Benchmark metrics evaluated on weak labels.
