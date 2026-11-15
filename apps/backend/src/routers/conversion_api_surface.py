"""Lazy ``src.api`` surface for conversion routes (breaks import cycles)."""

from __future__ import annotations


class _ApiSurface:
    """Resolve attributes from ``src.api`` only after the app module finished loading."""

    def __getattr__(self, name: str) -> object:
        from src import api as _api

        return getattr(_api, name)


api_surface = _ApiSurface()

# Eager symbols safe to import without loading ``src.api`` (Depends defaults).
from src.api_wire import parse_files  # noqa: E402

__all__ = ["api_surface", "parse_files"]
