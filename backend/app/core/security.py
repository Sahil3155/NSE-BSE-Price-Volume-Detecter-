"""Security utilities including filename sanitization and file upload validation."""

import os
import re
from pathlib import Path
from typing import Set

ALLOWED_EXTENSIONS: Set[str] = {".csv", ".zip", ".xlsx"}
MAX_FILE_SIZE_BYTES: int = 100 * 1024 * 1024  # 100 MB


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal attacks."""
    clean_name = os.path.basename(filename)
    clean_name = re.sub(r"[^\w\-.]", "_", clean_name)
    return clean_name


def validate_file_extension(filename: str) -> bool:
    """Check if the uploaded file has an approved extension."""
    suffix = Path(filename).suffix.lower()
    return suffix in ALLOWED_EXTENSIONS


def validate_file_size(size_bytes: int) -> bool:
    """Validate that the file size is within limits."""
    return 0 < size_bytes <= MAX_FILE_SIZE_BYTES
