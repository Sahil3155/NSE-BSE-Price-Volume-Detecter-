"""SQLAlchemy model for actionable surveillance alerts."""

from typing import Optional
from sqlalchemy import String, Float, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database.base import Base


class DetectionAlert(Base):
    """Actionable surveillance alert records."""

    __tablename__ = "detection_alerts"
    __table_args__ = (
        Index("idx_alert_risk_date", "risk_level", "detection_date"),
        Index("idx_alert_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    prediction_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("anomaly_predictions.id", ondelete="SET NULL"), nullable=True
    )
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False)
    detection_date: Mapped[str] = mapped_column(String(10), index=True, nullable=False)
    anomaly_score: Mapped[float] = mapped_column(Float, index=True, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    reasons_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    status: Mapped[str] = mapped_column(String(50), default="PENDING_REVIEW", nullable=False)
    investigator_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
