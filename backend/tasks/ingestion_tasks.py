"""Celery background tasks for dataset ingestion and preprocessing."""

from backend.tasks.celery_app import celery_app
from backend.app.core.logging import logger


@celery_app.task(name="tasks.ingest_dataset_file")
def ingest_dataset_file_task(file_path: str, exchange: str) -> dict:
    """Asynchronously process an uploaded market dataset file."""
    logger.info(f"Starting background ingestion for {file_path} ({exchange})")
    # Will hook into data pipeline
    return {"status": "SUCCESS", "file_path": file_path, "exchange": exchange}
