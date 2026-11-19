"""Pydantic schemas for market data ingestion and querying."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict


class MarketDataRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    stock_id: int
    symbol: Optional[str] = None
    exchange: Optional[str] = None
    trading_date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    turnover: Optional[float] = 0.0


class MarketDataUploadResponse(BaseModel):
    status: str
    filename: str
    exchange: str
    total_records: int
    valid_records: int
    invalid_records: int
    message: str


class MarketDataStatusResponse(BaseModel):
    total_stocks: int
    total_market_records: int
    total_featured_records: int
    latest_trading_date: Optional[str]
    earliest_trading_date: Optional[str]
    exchanges: List[str]
