"""FastAPI route dependencies."""

from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db


def get_db_session() -> Generator[Session, None, None]:
    """Dependency for providing request database session."""
    yield from get_db()


DatabaseDep = Depends(get_db_session)
