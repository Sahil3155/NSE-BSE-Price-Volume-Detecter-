"""Centralized structured logging configuration."""

import logging
import sys
from typing import Optional


def get_log_format() -> str:
    """Return standard log format string."""
    return "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"


def setup_logger(
    name: str = "surveillance",
    level: Optional[int] = None,
) -> logging.Logger:
    """Configure and return a structured logger instance."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    log_level = level if level is not None else logging.INFO
    logger.setLevel(log_level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    formatter = logging.Formatter(get_log_format(), datefmt="%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    return logger


logger = setup_logger()
