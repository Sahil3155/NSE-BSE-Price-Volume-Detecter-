"""Application configuration module using Pydantic Settings."""

from pathlib import Path
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global configuration settings for the surveillance system."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # General
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    APP_NAME: str = "NSE/BSE Pump-and-Dump Early Detector"
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = "default_development_secret_key_2026"
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    # Database Settings
    DATABASE_URL: str = (
        "postgresql://surveillance_user:surveillance_pass@localhost:5432/market_surveillance_db"
    )
    USE_SQLITE_FALLBACK: bool = True
    SQLITE_DB_PATH: str = "./market_surveillance.db"

    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Paths
    DATASET_DIR: str = "./datasets"
    TRAINED_MODELS_DIR: str = "./trained_models"
    MLRUNS_DIR: str = "./mlruns"

    # Anomaly Detection & Scoring Thresholds
    CONTAMINATION_RATE: float = 0.05
    LOOKBACK_WINDOW: int = 20
    Z_SCORE_VOLUME_THRESHOLD: float = 3.0
    PRICE_CHANGE_ALERT_THRESHOLD: float = 10.0
    VOLUME_SPIKE_RATIO_THRESHOLD: float = 4.0
    CONSECUTIVE_CIRCUITS_ALERT: int = 3
    HYBRID_HIGH_RISK_THRESHOLD: float = 75.0
    HYBRID_MEDIUM_RISK_THRESHOLD: float = 50.0

    @property
    def dataset_path(self) -> Path:
        """Return resolved path to the dataset directory."""
        return Path(self.DATASET_DIR).resolve()

    @property
    def models_path(self) -> Path:
        """Return resolved path to the trained models directory."""
        return Path(self.TRAINED_MODELS_DIR).resolve()


settings = Settings()
