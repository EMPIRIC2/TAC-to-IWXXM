"""Authentication package initialization.

Provides FastAPI router via `auth.api.router` and DB init helpers.
"""

from .api import router  # re-export for easy inclusion
from .database import init_db

__all__ = ["router", "init_db"]
