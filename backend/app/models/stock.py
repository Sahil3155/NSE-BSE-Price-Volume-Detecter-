"""SQLAlchemy models for stock exchanges and equities."""

from typing import List, Optional
from sqlalchemy import String, Boolean, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.base import Base


class Exchange(Base):
    """Securities exchange entity (NSE, BSE)."""

    __tablename__ = "exchanges"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(10), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(50), default="India", nullable=False)

    stocks: Mapped[List["Stock"]] = relationship(back_populates="exchange", cascade="all, delete-orphan")


class Stock(Base):
    """Listed stock equity entity."""

    __tablename__ = "stocks"
    __table_args__ = (
        UniqueConstraint("exchange_id", "symbol", name="uq_exchange_symbol"),
        Index("idx_stock_symbol", "symbol"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    exchange_id: Mapped[int] = mapped_column(ForeignKey("exchanges.id"), nullable=False)
    symbol: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), default="", nullable=False)
    isin: Mapped[Optional[str]] = mapped_column(String(20), index=True, nullable=True)
    sector: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    market_cap_category: Mapped[str] = mapped_column(String(50), default="SmallCap", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    exchange: Mapped["Exchange"] = relationship(back_populates="stocks")
    market_data: Mapped[List["HistoricalMarketData"]] = relationship(
        "HistoricalMarketData", back_populates="stock", cascade="all, delete-orphan"
    )
