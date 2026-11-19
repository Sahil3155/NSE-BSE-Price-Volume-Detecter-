"""SQLAlchemy models for historical market data, features, and ingestion audit."""

from typing import Optional
from sqlalchemy import (
    String,
    Float,
    BigInteger,
    Boolean,
    Date,
    ForeignKey,
    UniqueConstraint,
    Index,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.base import Base


class HistoricalMarketData(Base):
    """Daily OHLCV trading observations per stock."""

    __tablename__ = "historical_market_data"
    __table_args__ = (
        UniqueConstraint("stock_id", "trading_date", name="uq_stock_trading_date"),
        Index("idx_market_stock_date", "stock_id", "trading_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False)
    trading_date: Mapped[str] = mapped_column(String(10), index=True, nullable=False)
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[int] = mapped_column(BigInteger, nullable=False)
    turnover: Mapped[Optional[float]] = mapped_column(Float, default=0.0, nullable=True)
    upper_circuit_limit: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lower_circuit_limit: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_circuit_hit: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    stock: Mapped["Stock"] = relationship("Stock", back_populates="market_data")


class EngineeredFeature(Base):
    """Microstructure, volatility, and interaction features."""

    __tablename__ = "engineered_features"
    __table_args__ = (
        UniqueConstraint("stock_id", "trading_date", name="uq_feature_stock_date"),
        Index("idx_feature_stock_date", "stock_id", "trading_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False)
    trading_date: Mapped[str] = mapped_column(String(10), index=True, nullable=False)
    daily_return: Mapped[float] = mapped_column(Float, default=0.0)
    log_return: Mapped[float] = mapped_column(Float, default=0.0)
    rolling_return_5d: Mapped[float] = mapped_column(Float, default=0.0)
    rolling_return_10d: Mapped[float] = mapped_column(Float, default=0.0)
    rolling_return_20d: Mapped[float] = mapped_column(Float, default=0.0)
    price_z_score: Mapped[float] = mapped_column(Float, default=0.0)
    volume_ratio_20d: Mapped[float] = mapped_column(Float, default=1.0)
    abnormal_volume_pct: Mapped[float] = mapped_column(Float, default=0.0)
    volume_z_score: Mapped[float] = mapped_column(Float, default=0.0)
    volume_acceleration: Mapped[float] = mapped_column(Float, default=0.0)
    price_volatility_20d: Mapped[float] = mapped_column(Float, default=0.0)
    volume_volatility_20d: Mapped[float] = mapped_column(Float, default=0.0)
    return_volume_interaction: Mapped[float] = mapped_column(Float, default=0.0)
    price_volume_corr_20d: Mapped[float] = mapped_column(Float, default=0.0)
    price_volume_divergence: Mapped[float] = mapped_column(Float, default=0.0)
    consecutive_upper_circuits: Mapped[int] = mapped_column(BigInteger, default=0)


class DatasetImportHistory(Base):
    """Audit log of dataset ingestions."""

    __tablename__ = "dataset_import_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    exchange: Mapped[str] = mapped_column(String(10), nullable=False)
    file_format: Mapped[str] = mapped_column(String(10), nullable=False)
    record_count: Mapped[int] = mapped_column(BigInteger, default=0)
    success_count: Mapped[int] = mapped_column(BigInteger, default=0)
    error_count: Mapped[int] = mapped_column(BigInteger, default=0)
    status: Mapped[str] = mapped_column(String(50), default="COMPLETED")
    import_duration_sec: Mapped[float] = mapped_column(Float, default=0.0)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
