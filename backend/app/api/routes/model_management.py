"""FastAPI routes for model registry inspection and training job initiation."""

from pathlib import Path
from typing import List, Dict, Any
from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.app.core.config import settings
from backend.app.api.dependencies import get_db_session
from backend.app.models.model_registry import ModelRegistry
from backend.app.services.analytics_service import get_model_comparison_benchmark

router = APIRouter(prefix="/models", tags=["Model Management"])


def run_training_job_async():
    """Background task function to retrain models without blocking HTTP."""
    from scripts.train_models import main as run_train
    run_train()


@router.post("/train", status_code=status.HTTP_202_ACCEPTED)
async def trigger_model_training(background_tasks: BackgroundTasks) -> Dict[str, str]:
    """Dispatch background training job for Isolation Forest and LSTM Autoencoder."""
    background_tasks.add_task(run_training_job_async)
    return {
        "status": "QUEUED",
        "message": "Model training job dispatched to background worker.",
    }


@router.get("", response_model=List[Dict[str, Any]])
async def list_registered_models() -> List[Dict[str, Any]]:
    """Enumerate deployed surveillance models and artifacts."""
    models_dir = Path(settings.TRAINED_MODELS_DIR)
    iforest_exists = (models_dir / "isolation_forest" / "isolation_forest.joblib").exists()
    lstm_exists = (models_dir / "lstm_autoencoder" / "lstm_autoencoder.pt").exists()

    return [
        {
            "name": "Isolation Forest Surveillance Model",
            "type": "ISOLATION_FOREST",
            "version": "1.0.0",
            "status": "READY" if iforest_exists else "UNTRAINED",
            "contamination": settings.CONTAMINATION_RATE,
        },
        {
            "name": "PyTorch LSTM Autoencoder",
            "type": "LSTM_AUTOENCODER",
            "version": "1.0.0",
            "status": "READY" if lstm_exists else "UNTRAINED",
            "lookback_window": settings.LOOKBACK_WINDOW,
        },
        {
            "name": "Hybrid Risk Scoring Engine",
            "type": "HYBRID",
            "version": "1.0.0",
            "status": "READY" if (iforest_exists and lstm_exists) else "DEGRADED",
            "weights": {"isolation_forest": 0.40, "lstm": 0.35, "rules": 0.25},
        },
    ]


@router.get("/performance", response_model=List[Dict[str, Any]])
async def get_models_performance() -> List[Dict[str, Any]]:
    """Retrieve benchmark performance metrics across models."""
    return get_model_comparison_benchmark()
