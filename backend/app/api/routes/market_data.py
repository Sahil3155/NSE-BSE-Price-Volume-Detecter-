"""FastAPI routes for market data file uploads and status monitoring."""

import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.app.api.dependencies import get_db_session
from backend.app.core.security import sanitize_filename, validate_file_extension
from backend.app.core.config import settings
from backend.app.schemas.market_data import (
    MarketDataUploadResponse,
    MarketDataStatusResponse,
    MarketDataRecordResponse,
)
from backend.app.services.market_data_service import (
    persist_market_and_features,
    get_market_data_summary,
)
from backend.data_pipeline.pipeline import run_ingestion_and_feature_pipeline
from backend.app.models.historical_data import HistoricalMarketData
from backend.app.models.stock import Stock

router = APIRouter(prefix="/market-data", tags=["Market Data"])


@router.post("/upload", response_model=MarketDataUploadResponse)
async def upload_market_dataset(
    file: UploadFile = File(...),
    exchange: str = Form("NSE"),
    db: Session = Depends(get_db_session),
) -> MarketDataUploadResponse:
    """Upload and ingest raw NSE/BSE Bhavcopy CSV or ZIP dataset."""
    clean_name = sanitize_filename(file.filename or "dataset.csv")
    if not validate_file_extension(clean_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload a CSV or ZIP file.",
        )

    upload_dir = Path(settings.DATASET_DIR) / "raw"
    upload_dir.mkdir(parents=True, exist_ok=True)
    temp_path = upload_dir / clean_name

    with temp_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        featured_df, report = run_ingestion_and_feature_pipeline(temp_path, exchange=exchange)
        persist_report = persist_market_and_features(
            db, featured_df, filename=clean_name, exchange_code=exchange
        )
        return MarketDataUploadResponse(
            status="SUCCESS",
            filename=clean_name,
            exchange=exchange,
            total_records=report["total_rows"],
            valid_records=report["valid_rows"],
            invalid_records=report["invalid_ohlc_rows"],
            message=f"Ingested {persist_report['inserted_records']} records successfully.",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to process dataset file: {str(exc)}",
        )


@router.get("", response_model=List[MarketDataRecordResponse])
async def list_market_data(
    symbol: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db_session),
) -> List[MarketDataRecordResponse]:
    """Query paginated historical market records."""
    stmt = (
        select(HistoricalMarketData, Stock.symbol)
        .join(Stock, HistoricalMarketData.stock_id == Stock.id)
    )
    if symbol:
        stmt = stmt.where(Stock.symbol == symbol.upper())
    stmt = stmt.order_by(HistoricalMarketData.trading_date.desc()).limit(limit).offset(offset)

    rows = db.execute(stmt).all()
    return [
        MarketDataRecordResponse(
            id=rec.id,
            stock_id=rec.stock_id,
            symbol=sym,
            trading_date=rec.trading_date,
            open=rec.open,
            high=rec.high,
            low=rec.low,
            close=rec.close,
            volume=rec.volume,
            turnover=rec.turnover,
        )
        for rec, sym in rows
    ]


@router.get("/status", response_model=MarketDataStatusResponse)
async def check_market_data_status(
    db: Session = Depends(get_db_session),
) -> MarketDataStatusResponse:
    """Retrieve statistical summary and temporal coverage of market dataset."""
    return get_market_data_summary(db)
