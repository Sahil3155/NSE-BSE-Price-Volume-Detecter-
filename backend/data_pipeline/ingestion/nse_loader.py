"""NSE historical Bhavcopy ingestion adapter supporting legacy, full, and UDiFF formats."""

import io
import zipfile
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
from backend.app.core.logging import logger
from backend.data_pipeline.preprocessing.cleaning import clean_market_dataframe

LEGACY_NSE_COLUMN_MAP: Dict[str, str] = {
    "SYMBOL": "symbol",
    "TIMESTAMP": "trading_date",
    "OPEN": "open",
    "HIGH": "high",
    "LOW": "low",
    "CLOSE": "close",
    "TOTTRDQTY": "volume",
    "TOTTRDVAL": "turnover",
}

FULL_BHAVDATA_NSE_COLUMN_MAP: Dict[str, str] = {
    "SYMBOL": "symbol",
    "DATE1": "trading_date",
    "OPEN_PRICE": "open",
    "HIGH_PRICE": "high",
    "LOW_PRICE": "low",
    "CLOSE_PRICE": "close",
    "TTL_TRD_QNTY": "volume",
    "TURNOVER_LACS": "turnover",
}

UDIFF_NSE_COLUMN_MAP: Dict[str, str] = {
    "TckrSymb": "symbol",
    "TradDt": "trading_date",
    "OpnPric": "open",
    "HghPric": "high",
    "LwPric": "low",
    "ClsPric": "close",
    "TtlTradgVol": "volume",
    "TtlTrfVal": "turnover",
}


def identify_nse_document_type(content: str, filename: str) -> str:
    """Identify the document type from initial file lines and filename."""
    lower_content = content.lower()
    lower_filename = filename.lower()
    if "52_week_high" in lower_content or "52_wk_high" in lower_filename:
        return "NSE_52_WEEK_HIGH_LOW"
    if "mto_" in lower_filename or "delivery position" in lower_content:
        return "NSE_DELIVERY_REPORT"
    if "ind_close" in lower_filename or "indices" in lower_content:
        return "NSE_INDEX_REPORT"
    return "NSE_MARKET_DATA"


def find_header_row_index(lines: List[str]) -> int:
    """Find the row index containing OHLC column headers."""
    for idx, line in enumerate(lines[:10]):
        clean = line.replace('"', '').replace("'", '').upper()
        tokens = [t.strip() for t in clean.split(',')]
        if "SYMBOL" in tokens or "TCKRSYMB" in tokens:
            return idx
    return 0


def detect_nse_column_mapping(columns: List[str]) -> Optional[Dict[str, str]]:
    """Determine applicable column mapping from sanitized file header."""
    col_set = {c.strip() for c in columns}
    if "SYMBOL" in col_set and "CLOSE" in col_set:
        return LEGACY_NSE_COLUMN_MAP
    if "SYMBOL" in col_set and "CLOSE_PRICE" in col_set:
        return FULL_BHAVDATA_NSE_COLUMN_MAP
    if "TckrSymb" in col_set and "ClsPric" in col_set:
        return UDIFF_NSE_COLUMN_MAP
    return None


def parse_nse_dataframe(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Map raw NSE columns to canonical surveillance schema."""
    cleaned_cols = [str(c).strip() for c in raw_df.columns]
    raw_df.columns = cleaned_cols
    mapping = detect_nse_column_mapping(cleaned_cols)
    if not mapping:
        raise ValueError(
            "Unrecognized NSE Bhavcopy schema. Expected daily OHLCV columns (Open, High, Low, Close, Volume)."
        )

    df = raw_df.rename(columns=mapping)
    df["exchange"] = "NSE"
    if "turnover" not in df.columns:
        df["turnover"] = 0.0

    if "SERIES" in raw_df.columns:
        df = df[raw_df["SERIES"].isin(["EQ", "BE", "BZ", "SM"])]
    elif "SctySrs" in raw_df.columns:
        df = df[raw_df["SctySrs"].isin(["EQ", "BE", "BZ", "SM"])]

    return clean_market_dataframe(df)


def load_nse_csv(file_path: Path) -> pd.DataFrame:
    """Load and parse an NSE Bhavcopy CSV file with preamble detection."""
    logger.info(f"Loading NSE file: {file_path}")
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        sample_lines = [f.readline() for _ in range(10)]

    doc_type = identify_nse_document_type("".join(sample_lines), file_path.name)
    if doc_type == "NSE_52_WEEK_HIGH_LOW":
        raise ValueError(
            f"The uploaded file '{file_path.name}' is an NSE 52-Week High/Low Report. "
            "It provides annual 52-week price extremes rather than daily OHLCV trading records "
            "(Open, High, Low, Close, Volume) required for time-series anomaly detection. "
            "Please upload the official daily NSE Bhavcopy (e.g. 'sec_bhavdata_full_*.csv' or 'cm*bhav.csv')."
        )

    skip = find_header_row_index(sample_lines)
    raw_df = pd.read_csv(file_path, skiprows=skip)
    return parse_nse_dataframe(raw_df)


def load_nse_zip(zip_path: Path) -> pd.DataFrame:
    """Extract and parse all NSE Bhavcopy CSVs within a ZIP archive."""
    records = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        for name in zf.namelist():
            if name.endswith(".csv") and not name.startswith("__"):
                with zf.open(name) as f:
                    content_bytes = f.read()
                    sample_str = content_bytes[:2048].decode("utf-8", errors="ignore")
                    doc_type = identify_nse_document_type(sample_str, name)
                    if doc_type != "NSE_MARKET_DATA":
                        continue
                    lines = sample_str.splitlines(keepends=True)
                    skip = find_header_row_index(lines)
                    raw_df = pd.read_csv(io.BytesIO(content_bytes), skiprows=skip)
                    parsed = parse_nse_dataframe(raw_df)
                    records.append(parsed)
    if not records:
        return pd.DataFrame()
    return pd.concat(records, ignore_index=True).drop_duplicates()
