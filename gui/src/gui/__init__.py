"""GUI package init (src layout)."""
from .app import app  # re-export for uvicorn entry
__all__ = ["app"]
