"""BSE historical Bhavcopy ingestion adapter."""

import io
import re
import zipfile
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
from backend.app.core.logging import logger
from backend.data_pipeline.preprocessing.cleaning import clean_market_dataframe

BSE_COLUMN_MAP: Dict[str, str] = {
    "SC_CODE": "symbol",
    "SC_NAME": "security_name",
    "OPEN": "open",
    "HIGH": "high",
    "LOW": "low",
    "CLOSE": "close",
    "NO_OF_SHRS": "volume",
    "NET_TURNOV": "turnover",
}


def extract_date_from_bse_filename(filename: str) -> Optional[str]:
    """Attempt extracting date (DDMMYY) from typical BSE Bhavcopy filenames."""
    match = re.search(r"(\d{2})(\d{2})(\d{2})", filename)
    if match:
        day, month, year = match.groups()
        return f"20{year}-{month}-{day}"
    return None


def parse_bse_dataframe(raw_df: pd.DataFrame, default_date: Optional[str] = None) -> pd.DataFrame:
    """Map raw BSE columns to canonical surveillance schema."""
    df = raw_df.rename(columns=BSE_COLUMN_MAP)
    df["exchange"] = "BSE"

    if "trading_date" not in df.columns:
        if default_date:
            df["trading_date"] = default_date
        else:
            raise ValueError("BSE Bhavcopy lacks trading_date and default_date was not provided.")

    if "turnover" not in df.columns:
        df["turnover"] = 0.0

    return clean_market_dataframe(df)


def load_bse_csv(file_path: Path) -> pd.DataFrame:
    """Load and parse a BSE Bhavcopy CSV file."""
    logger.info(f"Loading BSE file: {file_path}")
    raw_df = pd.read_csv(file_path)
    file_date = extract_date_from_bse_filename(file_path.name)
    return parse_bse_dataframe(raw_df, default_date=file_date)


def load_bse_zip(zip_path: Path) -> pd.DataFrame:
    """Extract and parse all BSE Bhavcopy CSVs in a ZIP archive."""
    records = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        for name in zf.namelist():
            if name.endswith(".csv") and not name.startswith("__"):
                with zf.open(name) as f:
                    raw_df = pd.read_csv(io.BytesIO(f.read()))
                    file_date = extract_date_from_bse_filename(name)
                    parsed = parse_bse_dataframe(raw_df, default_date=file_date)
                    records.append(parsed)
    if not records:
        return pd.DataFrame()
    return pd.concat(records, ignore_index=True).drop_duplicates()
