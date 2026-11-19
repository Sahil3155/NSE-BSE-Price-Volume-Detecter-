"""SQLAlchemy models for anomaly predictions and SEBI enforcement weak labels."""

from typing import Optional
from sqlalchemy import String, Float, ForeignKey, UniqueConstraint, Index, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database.base import Base


class AnomalyPrediction(Base):
    """Multi-model anomaly inference outputs per security and date."""

    __tablename__ = "anomaly_predictions"
    __table_args__ = (
        UniqueConstraint("stock_id", "trading_date", name="uq_pred_stock_date"),
        Index("idx_pred_stock_date", "stock_id", "trading_date"),
        Index("idx_pred_risk_score", "risk_level", "hybrid_score"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False)
    trading_date: Mapped[str] = mapped_column(String(10), index=True, nullable=False)
    isolation_forest_score: Mapped[float] = mapped_column(Float, default=0.0)
    lstm_reconstruction_error: Mapped[float] = mapped_column(Float, default=0.0)
    rule_score: Mapped[float] = mapped_column(Float, default=0.0)
    hybrid_score: Mapped[float] = mapped_column(Float, index=True, default=0.0)
    risk_level: Mapped[str] = mapped_column(String(20), index=True, default="LOW")
    model_version: Mapped[str] = mapped_column(String(50), default="1.0.0")


class SEBIEnforcementCase(Base):
    """Historical SEBI enforcement orders used as weak labels."""

    __tablename__ = "sebi_enforcement_cases"
    __table_args__ = (
        UniqueConstraint("order_id", "stock_symbol", name="uq_order_symbol"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    order_date: Mapped[str] = mapped_column(String(10), nullable=False)
    stock_symbol: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    exchange: Mapped[str] = mapped_column(String(10), default="NSE", nullable=False)
    allegation_type: Mapped[str] = mapped_column(String(200), nullable=False)
    investigation_start_date: Mapped[str] = mapped_column(String(10), nullable=False)
    investigation_end_date: Mapped[str] = mapped_column(String(10), nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
