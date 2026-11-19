"""Pydantic schemas for stocks and exchanges."""

from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class ExchangeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    country: str


class StockBase(BaseModel):
    symbol: str
    name: Optional[str] = ""
    isin: Optional[str] = None
    sector: Optional[str] = None
    market_cap_category: str = "SmallCap"
    is_active: bool = True


class StockResponse(StockBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    exchange_id: int
    exchange_code: Optional[str] = None


class MarketDataPoint(BaseModel):
    trading_date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    turnover: Optional[float] = 0.0
    daily_return: Optional[float] = 0.0
    consecutive_upper_circuits: Optional[int] = 0


class StockHistoryResponse(BaseModel):
    symbol: str
    exchange: str
    total_records: int
    history: List[MarketDataPoint]
