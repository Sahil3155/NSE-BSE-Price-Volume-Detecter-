"""Script to initialize database tables and seed baseline records."""

import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from backend.app.core.logging import logger
from backend.app.database.init_db import init_database_tables
from backend.app.database.connection import test_connection


def main():
    """Execute database setup and table verification."""
    logger.info("Verifying database connectivity...")
    if not test_connection():
        logger.error("Failed to connect to the configured database.")
        sys.exit(1)

    logger.info("Creating database tables if not existing...")
    init_database_tables()
    logger.info("Database setup completed successfully.")


if __name__ == "__main__":
    main()
