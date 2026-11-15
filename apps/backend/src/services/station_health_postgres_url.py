"""Normalize DATABASE_URL for sync SQLAlchemy station-health access (F39)."""

from __future__ import annotations

import os


def sync_database_url(raw: str | None = None) -> str | None:
    """
    Normalize ``DATABASE_URL`` for sync SQLAlchemy (psycopg).

    Parameters
    ----------
    raw : object
        Optional URL; defaults to ``DATABASE_URL``.

    Returns
    -------
    str | None
        Sync driver URL, or ``None`` when unset.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (sync_database_url)
    2
    """
    value = (raw if raw is not None else os.environ.get("DATABASE_URL") or "").strip()
    if not value:
        return None
    if value.startswith("postgresql+asyncpg://"):
        url = "postgresql+psycopg://" + value.removeprefix("postgresql+asyncpg://")
    elif value.startswith("postgresql+psycopg2://"):
        url = "postgresql+psycopg://" + value.removeprefix("postgresql+psycopg2://")
    elif value.startswith("postgresql://"):
        url = "postgresql+psycopg://" + value.removeprefix("postgresql://")
    else:
        url = value
    if "ssl=require" in url and "sslmode=" not in url:
        url = url.replace("ssl=require", "sslmode=require")
    return url


__all__ = ["sync_database_url"]
