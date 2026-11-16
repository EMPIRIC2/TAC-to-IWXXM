"""Lazy ``src.api`` surface for conversion routes (breaks import cycles)."""

from __future__ import annotations


class _ApiSurface:
    """Resolve attributes from ``src.api`` only after the app module finished loading.

    Patches applied on this proxy (or on ``src.api``) share the same bindings so
    unit tests can monkeypatch either surface without shadowing the other.
    """

    __slots__ = ()

    def __getattr__(self, name: str) -> object:
        from src import api as _api

        return getattr(_api, name)

    def __setattr__(self, name: str, value: object) -> None:
        from src import api as _api

        setattr(_api, name, value)

    def __delattr__(self, name: str) -> None:
        from src import api as _api

        delattr(_api, name)


api_surface = _ApiSurface()

# Eager symbols safe to import without loading ``src.api`` (Depends defaults).
from src.api_wire import parse_files  # noqa: E402

__all__ = ["api_surface", "parse_files"]
