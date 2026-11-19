"""Script to ingest market dataset file into the surveillance database."""

import sys
import argparse
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

import pandas as pd
from backend.app.core.logging import logger
from backend.app.database.connection import SessionLocal
from backend.app.services.market_data_service import persist_market_and_features
from backend.data_pipeline.feature_engineering.feature_builder import build_surveillance_features


def parse_arguments():
    """Parse command line input arguments."""
    parser = argparse.ArgumentParser(description="Ingest historical market CSV into database.")
    parser.add_argument(
        "--file",
        type=str,
        default="datasets/sample/synthetic_pump_dump_series.csv",
        help="Path to CSV dataset file.",
    )
    parser.add_argument("--exchange", type=str, default="NSE", help="Exchange code (NSE, BSE).")
    return parser.parse_args()


def main():
    """Execute dataset ingestion into database."""
    args = parse_arguments()
    target_path = Path(args.file)
    if not target_path.exists():
        logger.error(f"Target file does not exist: {target_path}")
        sys.exit(1)

    logger.info(f"Ingesting {target_path} into database for {args.exchange}...")
    df = pd.read_csv(target_path)
    featured_df, _ = build_surveillance_features(df)

    db = SessionLocal()
    try:
        res = persist_market_and_features(
            db, featured_df, filename=target_path.name, exchange_code=args.exchange
        )
        logger.info(f"Ingestion finished successfully: {res}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
