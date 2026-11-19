"""Service handling stock catalog and historical time-series queries."""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.app.models.stock import Stock, Exchange
from backend.app.models.historical_data import HistoricalMarketData, EngineeredFeature
from backend.app.schemas.stock import StockResponse, StockHistoryResponse, MarketDataPoint


def get_all_stocks(
    db: Session,
    exchange_code: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[StockResponse]:
    """Retrieve list of registered stocks filtered by exchange."""
    query = select(Stock, Exchange.code.label("exchange_code")).join(Exchange)
    if exchange_code:
        query = query.where(Exchange.code == exchange_code.upper())
    query = query.limit(limit).offset(offset)

    results = db.execute(query).all()
    out = []
    for stock, code in results:
        resp = StockResponse(
            id=stock.id,
            exchange_id=stock.exchange_id,
            exchange_code=code,
            symbol=stock.symbol,
            name=stock.name,
            isin=stock.isin,
            sector=stock.sector,
            market_cap_category=stock.market_cap_category,
            is_active=stock.is_active,
        )
        out.append(resp)
    return out


def get_stock_by_symbol(db: Session, symbol: str) -> Optional[Stock]:
    """Fetch individual stock record by ticker symbol."""
    stmt = select(Stock).where(Stock.symbol == symbol.upper())
    return db.scalars(stmt).first()


def get_stock_history(
    db: Session,
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Optional[StockHistoryResponse]:
    """Fetch chronological OHLCV and feature history for given stock symbol."""
    stock = get_stock_by_symbol(db, symbol)
    if not stock:
        return None

    query = (
        select(HistoricalMarketData, EngineeredFeature)
        .outerjoin(
            EngineeredFeature,
            (EngineeredFeature.stock_id == HistoricalMarketData.stock_id)
            & (EngineeredFeature.trading_date == HistoricalMarketData.trading_date),
        )
        .where(HistoricalMarketData.stock_id == stock.id)
    )
    if start_date:
        query = query.where(HistoricalMarketData.trading_date >= start_date)
    if end_date:
        query = query.where(HistoricalMarketData.trading_date <= end_date)
    query = query.order_by(HistoricalMarketData.trading_date.asc())

    rows = db.execute(query).all()
    points = []
    for h, f in rows:
        points.append(
            MarketDataPoint(
                trading_date=h.trading_date,
                open=h.open,
                high=h.high,
                low=h.low,
                close=h.close,
                volume=h.volume,
                turnover=h.turnover or 0.0,
                daily_return=f.daily_return if f else 0.0,
                consecutive_upper_circuits=f.consecutive_upper_circuits if f else 0,
            )
        )

    return StockHistoryResponse(
        symbol=stock.symbol,
        exchange=stock.exchange.code if stock.exchange else "NSE",
        total_records=len(points),
        history=points,
    )
