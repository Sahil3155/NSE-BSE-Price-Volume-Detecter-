"""SQLAlchemy models for machine learning model versioning and training run audit."""

from typing import Optional
from sqlalchemy import String, Float, Boolean, ForeignKey, BigInteger, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database.base import Base


class ModelRegistry(Base):
    """Registered and versioned machine learning models."""

    __tablename__ = "model_registry"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_type: Mapped[str] = mapped_column(String(50), nullable=False)
    version: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    artifact_path: Mapped[str] = mapped_column(String(500), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    parameters_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)


class ModelTrainingRun(Base):
    """Audit log of historical model training sessions and evaluation metrics."""

    __tablename__ = "model_training_runs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    model_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("model_registry.id", ondelete="SET NULL"), nullable=True
    )
    training_date_start: Mapped[str] = mapped_column(String(10), nullable=False)
    training_date_end: Mapped[str] = mapped_column(String(10), nullable=False)
    num_samples: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    precision: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    recall: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    f1_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    roc_auc: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
