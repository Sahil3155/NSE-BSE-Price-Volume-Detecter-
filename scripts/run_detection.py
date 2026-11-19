"""Script to run hybrid surveillance detection across market records."""

import sys
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

import pandas as pd
from backend.app.core.logging import logger
from backend.data_pipeline.feature_engineering.feature_builder import build_surveillance_features
from backend.ml.utils.model_loader import ModelRegistryLoader
from backend.ml.hybrid_detector.detector import HybridSurveillanceDetector


def main():
    """Execute detection engine and output suspicious alerts."""
    dataset_path = Path("datasets/sample/synthetic_pump_dump_series.csv")
    if not dataset_path.exists():
        logger.error(f"Dataset not found at: {dataset_path}")
        sys.exit(1)

    raw_df = pd.read_csv(dataset_path)
    featured_df, _ = build_surveillance_features(raw_df)

    loader = ModelRegistryLoader()
    if_artifacts = loader.get_isolation_forest()
    lstm_artifacts = loader.get_lstm_autoencoder()

    detector = HybridSurveillanceDetector(if_artifacts, lstm_artifacts)
    alerts = detector.detect_anomalies(featured_df)

    print("\n" + "=" * 70)
    print("TOP SURVEILLANCE ALERTS (RANKED BY ANOMALY SCORE)")
    print("=" * 70)
    for alert in alerts[:5]:
        print(f"Stock: {alert['symbol']} | Date: {alert['trading_date']} | Risk: {alert['risk_level']} | Score: {alert['anomaly_score']}/100")
        for reason in alert["reasons"]:
            print(f"  - {reason}")
        print("-" * 70)


if __name__ == "__main__":
    main()
