"""FastAPI routes for stock catalog and historical time-series."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.api.dependencies import get_db_session
from backend.app.schemas.stock import StockResponse, StockHistoryResponse
from backend.app.services.stock_service import get_all_stocks, get_stock_by_symbol, get_stock_history

router = APIRouter(prefix="/stocks", tags=["Stocks"])


@router.get("", response_model=List[StockResponse])
async def list_stocks(
    exchange: Optional[str] = Query(None, description="Filter by exchange code (e.g. NSE, BSE)"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db_session),
) -> List[StockResponse]:
    """Retrieve catalog of listed equities."""
    return get_all_stocks(db, exchange_code=exchange, limit=limit, offset=offset)


@router.get("/{symbol}", response_model=StockResponse)
async def get_stock_details(
    symbol: str,
    db: Session = Depends(get_db_session),
) -> StockResponse:
    """Retrieve details for a specific stock ticker."""
    stock = get_stock_by_symbol(db, symbol)
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock '{symbol}' not found.",
        )
    return StockResponse(
        id=stock.id,
        exchange_id=stock.exchange_id,
        exchange_code=stock.exchange.code if stock.exchange else "NSE",
        symbol=stock.symbol,
        name=stock.name,
        isin=stock.isin,
        sector=stock.sector,
        market_cap_category=stock.market_cap_category,
        is_active=stock.is_active,
    )


@router.get("/{symbol}/history", response_model=StockHistoryResponse)
async def get_stock_historical_data(
    symbol: str,
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
    db: Session = Depends(get_db_session),
) -> StockHistoryResponse:
    """Retrieve chronological OHLCV and feature history for a stock."""
    history = get_stock_history(db, symbol, start_date=start_date, end_date=end_date)
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Historical data for stock '{symbol}' not found.",
        )
    return history
