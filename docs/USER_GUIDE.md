# User Guide — Surveillance Operations

This guide walks through common surveillance workflows in the application.

---

## 1. Navigating the Surveillance Dashboard
- Navigate to `http://localhost:5173`.
- The **Dashboard** displays macro statistics:
  - Total small-cap stocks monitored.
  - Active high-risk and medium-risk alerts.
  - Anomaly velocity chart across historical dates.
  - Top flagged equities ranked by peak anomaly score.

---

## 2. Inspecting Individual Stocks (Stock Explorer)
- Click **Stock Explorer** in the sidebar.
- Click any stock ticker pill (e.g., `PUMPDUMP_SUSPECT` or `SMALLCAP_NORM1`) or search by name.
- View the interactive **Price & Volume Trajectory** chart:
  - Blue line: Daily closing price in INR (₹).
  - Cyan bars: Daily trading volume.
  - Review consecutive upper circuit limit counters and price percentage changes.

---

## 3. Running Surveillance Scans (AI Detection Center)
- Click **AI Detection Center**.
- Select the Exchange (`NSE` or `BSE`), target stock symbol (or leave blank to scan all loaded equities), and choose the model (`HYBRID`, `ISOLATION_FOREST`, or `LSTM`).
- Click **Run Surveillance**:
  - The tri-modal model evaluates all observations.
  - Results are displayed with risk badges (`HIGH`, `MEDIUM`, `LOW`) and plain-language evidence breakdowns explaining why each stock was flagged.

---

## 4. Auditing & Triaging Alerts (Alert Management)
- Click **Alert Management**.
- Filter alerts by Risk Level (`HIGH`, `MEDIUM`) or Review Status (`PENDING_REVIEW`, `INVESTIGATING`, `CONFIRMED_ANOMALY`, `DISMISSED`).
- Click **Review** on any alert to open the audit dialog, update the status, and document investigator notes.

---

## 5. Ingesting New Datasets (Data Management)
- Click **Data Management**.
- Select the source exchange (`NSE` or `BSE`).
- Upload a historical Bhavcopy CSV file or ZIP archive.
- The pipeline validates OHLC consistency, calculates 16 microstructure features, suppresses duplicates, and saves the data to the database.
