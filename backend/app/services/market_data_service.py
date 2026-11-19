"""Service for market data ingestion, persistence, and status queries."""

import time
from typing import Dict, Any, Optional, List
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from backend.app.core.logging import logger
from backend.app.models.stock import Stock, Exchange
from backend.app.models.historical_data import (
    HistoricalMarketData,
    EngineeredFeature,
    DatasetImportHistory,
)
from backend.app.schemas.market_data import MarketDataStatusResponse


def get_or_create_exchange(db: Session, code: str) -> Exchange:
    """Ensure exchange record exists and return instance."""
    stmt = select(Exchange).where(Exchange.code == code.upper())
    exchange = db.scalars(stmt).first()
    if not exchange:
        exchange = Exchange(
            code=code.upper(),
            name="National Stock Exchange" if code.upper() == "NSE" else "Bombay Stock Exchange",
            country="India",
        )
        db.add(exchange)
        db.flush()
    return exchange


def get_or_create_stock(db: Session, exchange_id: int, symbol: str) -> Stock:
    """Ensure stock entity exists and return instance."""
    stmt = select(Stock).where(
        (Stock.exchange_id == exchange_id) & (Stock.symbol == symbol.upper())
    )
    stock = db.scalars(stmt).first()
    if not stock:
        stock = Stock(exchange_id=exchange_id, symbol=symbol.upper(), name=symbol.upper())
        db.add(stock)
        db.flush()
    return stock


def persist_market_and_features(
    db: Session,
    featured_df: pd.DataFrame,
    filename: str,
    exchange_code: str = "NSE",
) -> Dict[str, Any]:
    """Persist market records and precomputed features idempotently."""
    start_time = time.time()
    exchange = get_or_create_exchange(db, exchange_code)
    inserted_count = 0

    for _, row in featured_df.iterrows():
        stock = get_or_create_stock(db, exchange.id, str(row["symbol"]))
        dt = str(row["trading_date"])

        # Check existing market record
        existing = db.scalars(
            select(HistoricalMarketData).where(
                (HistoricalMarketData.stock_id == stock.id)
                & (HistoricalMarketData.trading_date == dt)
            )
        ).first()

        if not existing:
            m_rec = HistoricalMarketData(
                stock_id=stock.id,
                trading_date=dt,
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                volume=int(row["volume"]),
                turnover=float(row.get("turnover", 0.0) or 0.0),
                is_circuit_hit=bool(row.get("is_upper_circuit", False)),
            )
            db.add(m_rec)
            inserted_count += 1

        # Check existing features record
        feat_existing = db.scalars(
            select(EngineeredFeature).where(
                (EngineeredFeature.stock_id == stock.id)
                & (EngineeredFeature.trading_date == dt)
            )
        ).first()

        if not feat_existing:
            f_rec = EngineeredFeature(
                stock_id=stock.id,
                trading_date=dt,
                daily_return=float(row.get("daily_return", 0.0)),
                log_return=float(row.get("log_return", 0.0)),
                rolling_return_5d=float(row.get("rolling_return_5d", 0.0)),
                rolling_return_10d=float(row.get("rolling_return_10d", 0.0)),
                rolling_return_20d=float(row.get("rolling_return_20d", 0.0)),
                price_z_score=float(row.get("price_z_score", 0.0)),
                volume_ratio_20d=float(row.get("volume_ratio_20d", 1.0)),
                abnormal_volume_pct=float(row.get("abnormal_volume_pct", 0.0)),
                volume_z_score=float(row.get("volume_z_score", 0.0)),
                volume_acceleration=float(row.get("volume_acceleration", 0.0)),
                price_volatility_20d=float(row.get("price_volatility_20d", 0.0)),
                volume_volatility_20d=float(row.get("volume_volatility_20d", 0.0)),
                return_volume_interaction=float(row.get("return_volume_interaction", 0.0)),
                price_volume_corr_20d=float(row.get("price_volume_corr_20d", 0.0)),
                price_volume_divergence=float(row.get("price_volume_divergence", 0.0)),
                consecutive_upper_circuits=int(row.get("consecutive_upper_circuits", 0)),
            )
            db.add(f_rec)

    # Log audit
    audit = DatasetImportHistory(
        filename=filename,
        exchange=exchange_code,
        file_format=filename.split(".")[-1] if "." in filename else "csv",
        record_count=len(featured_df),
        success_count=inserted_count,
        error_count=0,
        status="COMPLETED",
        import_duration_sec=round(time.time() - start_time, 3),
    )
    db.add(audit)
    db.commit()

    return {
        "status": "COMPLETED",
        "total_rows": len(featured_df),
        "inserted_records": inserted_count,
        "duration_sec": audit.import_duration_sec,
    }


def get_market_data_summary(db: Session) -> MarketDataStatusResponse:
    """Fetch counts and date coverage of ingested data."""
    total_stocks = db.scalar(select(func.count(Stock.id))) or 0
    total_m_records = db.scalar(select(func.count(HistoricalMarketData.id))) or 0
    total_f_records = db.scalar(select(func.count(EngineeredFeature.id))) or 0

    dates_stmt = select(
        func.min(HistoricalMarketData.trading_date),
        func.max(HistoricalMarketData.trading_date),
    )
    earliest, latest = db.execute(dates_stmt).first() or (None, None)
    exchanges = db.scalars(select(Exchange.code)).all()

    return MarketDataStatusResponse(
        total_stocks=total_stocks,
        total_market_records=total_m_records,
        total_featured_records=total_f_records,
        latest_trading_date=latest,
        earliest_trading_date=earliest,
        exchanges=list(exchanges),
    )
