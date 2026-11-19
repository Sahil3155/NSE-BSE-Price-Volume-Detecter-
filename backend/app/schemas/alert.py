"""Pydantic schemas for surveillance alerts and status reviews."""

from typing import Optional, List, Dict
from pydantic import BaseModel, ConfigDict


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    stock_symbol: str
    exchange: str
    detection_date: str
    anomaly_score: float
    risk_level: str
    reasons: List[str]
    status: str
    investigator_notes: Optional[str] = None
    created_at: Optional[str] = None


class AlertStatusUpdate(BaseModel):
    status: str  # PENDING_REVIEW, INVESTIGATING, DISMISSED, CONFIRMED_ANOMALY
    investigator_notes: Optional[str] = None
