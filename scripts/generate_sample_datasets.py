"""Generate realistic, clearly labeled synthetic market datasets for pipeline testing."""

from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import pandas as pd


def generate_synthetic_series(num_days: int = 60) -> pd.DataFrame:
    """Generate multi-day OHLCV series for normal and manipulated small-cap stocks."""
    np.random.seed(42)
    base_date = datetime(2024, 1, 1)
    dates = [(base_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(num_days)]

    records = []
    # 1. Normal stock 1
    p = 100.0
    for d in dates:
        ret = np.random.normal(0.001, 0.015)
        p = max(5.0, p * (1 + ret))
        vol = int(np.random.normal(50000, 10000))
        records.append({
            "trading_date": d, "exchange": "NSE", "symbol": "SMALLCAP_NORM1",
            "open": round(p * 0.995, 2), "high": round(p * 1.015, 2),
            "low": round(p * 0.985, 2), "close": round(p, 2),
            "volume": max(1000, vol), "dataset_source": "SYNTHETIC_BENCHMARK"
        })

    # 2. Manipulated Pump-and-Dump stock
    p = 50.0
    base_vol = 20000
    for idx, d in enumerate(dates):
        if idx < 30:  # Baseline normal period
            ret = np.random.normal(0.0005, 0.01)
            p = max(5.0, p * (1 + ret))
            vol = int(np.random.normal(base_vol, 3000))
            o = round(p * 0.99, 2)
            h = round(p * 1.01, 2)
            l = round(p * 0.99, 2)
            c = round(p, 2)
        elif 30 <= idx < 45:  # Accumulation & Pump phase: volume spike + consecutive upper circuit
            ret = 0.05  # 5% upper circuit lock
            p = round(p * (1 + ret), 2)
            vol = int(base_vol * np.random.uniform(4.5, 7.5))
            o = p
            h = p  # Locked at high
            l = round(p * 0.995, 2)
            c = p
        else:  # Distribution & Dump phase
            ret = -0.05  # 5% lower circuit drop
            p = round(p * (1 + ret), 2)
            vol = int(base_vol * np.random.uniform(2.0, 4.0))
            o = p
            h = round(p * 1.005, 2)
            l = p
            c = p

        records.append({
            "trading_date": d, "exchange": "NSE", "symbol": "PUMPDUMP_SUSPECT",
            "open": o, "high": h, "low": l, "close": c,
            "volume": max(1000, vol), "dataset_source": "SYNTHETIC_BENCHMARK"
        })

    return pd.DataFrame(records)


def main():
    """Output synthetic benchmark datasets to disk."""
    out_dir = Path("./datasets/sample")
    out_dir.mkdir(parents=True, exist_ok=True)

    df_series = generate_synthetic_series(num_days=60)
    series_path = out_dir / "synthetic_pump_dump_series.csv"
    df_series.to_csv(series_path, index=False)
    print(f"Generated synthetic time series at: {series_path}")

    # Generate single-day NSE Bhavcopy sample
    latest_day = df_series["trading_date"].max()
    day_df = df_series[df_series["trading_date"] == latest_day].copy()
    bhavcopy_df = pd.DataFrame({
        "SYMBOL": day_df["symbol"],
        "SERIES": "EQ",
        "OPEN": day_df["open"],
        "HIGH": day_df["high"],
        "LOW": day_df["low"],
        "CLOSE": day_df["close"],
        "LAST": day_df["close"],
        "PREVCLOSE": day_df["open"],
        "TOTTRDQTY": day_df["volume"],
        "TOTTRDVAL": day_df["volume"] * day_df["close"],
        "TIMESTAMP": day_df["trading_date"],
        "TOTALTRADES": 500,
        "ISIN": "INE000000000",
    })
    bhav_path = out_dir / "sample_nse_bhavcopy.csv"
    bhavcopy_df.to_csv(bhav_path, index=False)
    print(f"Generated sample NSE Bhavcopy at: {bhav_path}")

    # Generate sample SEBI weak labels
    sebi_dir = Path("./datasets/sebi_orders")
    sebi_dir.mkdir(parents=True, exist_ok=True)
    sebi_df = pd.DataFrame([{
        "order_id": "SEBI/WTM/2024/001",
        "order_date": "2024-03-01",
        "stock_symbol": "PUMPDUMP_SUSPECT",
        "exchange": "NSE",
        "allegation_type": "Social Media Coordinated Pump-and-Dump",
        "investigation_start_date": "2024-01-31",
        "investigation_end_date": "2024-02-15",
        "source_url": "https://www.sebi.gov.in/enforcement/orders/sample",
        "notes": "Synthetic benchmark order for evaluation testing."
    }])
    sebi_path = sebi_dir / "sample_sebi_weak_labels.csv"
    sebi_df.to_csv(sebi_path, index=False)
    print(f"Generated sample SEBI orders at: {sebi_path}")


if __name__ == "__main__":
    main()
