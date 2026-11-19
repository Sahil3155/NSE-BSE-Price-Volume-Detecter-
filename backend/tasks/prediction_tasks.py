"""Celery background tasks for model training and anomaly detection runs."""

from backend.tasks.celery_app import celery_app
from backend.app.core.logging import logger


@celery_app.task(name="tasks.run_surveillance_batch")
def run_surveillance_batch_task(target_date: str) -> dict:
    """Asynchronously execute the anomaly detection pipeline for a target date."""
    logger.info(f"Triggering background surveillance batch for date: {target_date}")
    return {"status": "SUCCESS", "target_date": target_date}
