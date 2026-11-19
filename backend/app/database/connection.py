"""Database engine and session management with PostgreSQL and SQLite fallback."""

from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from backend.app.core.config import settings
from backend.app.core.logging import logger


def create_db_engine() -> Engine:
    """Create database engine with fallback handling."""
    if settings.DATABASE_URL.startswith("sqlite"):
        logger.info(f"Using SQLite database: {settings.DATABASE_URL}")
        return create_engine(
            settings.DATABASE_URL,
            connect_args={"check_same_thread": False},
        )

    try:
        pg_engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 2},
        )
        with pg_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Connected successfully to PostgreSQL.")
        return pg_engine
    except Exception as exc:
        if settings.USE_SQLITE_FALLBACK:
            logger.warning(
                f"PostgreSQL connection unavailable: {exc}. Using SQLite fallback."
            )
            sqlite_url = f"sqlite:///{settings.SQLITE_DB_PATH}"
            return create_engine(
                sqlite_url,
                connect_args={"check_same_thread": False},
            )
        raise exc


engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Provide a transactional database session scope."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection() -> bool:
    """Verify active database connectivity."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.error(f"Database connection check failed: {exc}")
        return False
