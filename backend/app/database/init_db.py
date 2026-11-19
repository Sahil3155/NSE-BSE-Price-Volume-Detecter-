"""Database initialization and table creation helper."""

from backend.app.database.base import Base
from backend.app.database.connection import engine
from backend.app.core.logging import logger


def init_database_tables() -> None:
    """Create all registered database tables if they do not exist."""
    try:
        # Import models so they are registered with metadata
        import backend.app.models.stock
        import backend.app.models.historical_data
        import backend.app.models.anomaly
        import backend.app.models.alert
        import backend.app.models.model_registry

        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")
    except Exception as exc:
        logger.error(f"Error initializing database tables: {exc}")
        raise exc
