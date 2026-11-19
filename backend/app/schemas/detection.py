"""Pydantic schemas for anomaly detection runs and results."""

from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class DetectionRunRequest(BaseModel):
    exchange: Optional[str] = Field("NSE", description="Target exchange")
    symbol: Optional[str] = Field(None, description="Specific stock symbol or None for all")
    start_date: Optional[str] = Field(None, description="Start date YYYY-MM-DD")
    end_date: Optional[str] = Field(None, description="End date YYYY-MM-DD")
    model_name: Optional[str] = Field("HYBRID", description="ISOLATION_FOREST, LSTM, or HYBRID")


class ModelContribution(BaseModel):
    isolation_forest_score: float
    lstm_reconstruction_score: float
    rule_score: float


class DetectionResultItem(BaseModel):
    id: Optional[int] = None
    symbol: str
    exchange: str
    trading_date: str
    anomaly_score: float
    risk_level: str
    reasons: List[str]
    model_breakdown: ModelContribution


class DetectionRunResponse(BaseModel):
    status: str
    records_analyzed: int
    anomalies_detected: int
    high_risk_count: int
    medium_risk_count: int
    results: List[DetectionResultItem]
