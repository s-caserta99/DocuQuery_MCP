from pathlib import Path

from mcp_pdf.config.settings import settings


def ensure_directory_exists(path: str) -> None:
    """Ensures the directory at the given path exists."""
    Path(path).mkdir(parents=True, exist_ok=True)


def ensure_required_directories() -> None:
    """Create all required project folders if they don't exist."""
    dirs = [
        settings.documents_path,
        settings.vector_store_path,
        "./notes",
        "./images",
    ]
    for d in dirs:
        ensure_directory_exists(d)
    