"""Persist and read live-map evaluation snapshots (FR-045 / D-027).

In-memory default for unit tests; optional DO Postgres via DATABASE_URL.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import UTC, datetime
from typing import Any, cast

logger = logging.getLogger(__name__)

_EMPTY_PRODUCTS = (
    "metar",
    "speci",
    "taf",
    "airmet",
    "sigmet",
    "vaa",
    "tca",
    "vona",
)


def empty_snapshot(*, computed_at: datetime | None = None) -> dict[str, Any]:
    """Return a zeroed FR-045 snapshot body.

    Parameters
    ----------
    computed_at :
        Snapshot time; defaults to UTC now.

    Returns
    -------
    dict[str, Any]
        Contract-shaped payload including ``computed_at`` ISO string.
    """
    stamp = computed_at or datetime.now(tz=UTC)
    return {
        "computed_at": stamp.astimezone(UTC).isoformat().replace("+00:00", "Z"),
        "window_hours": 24,
        "products": list(_EMPTY_PRODUCTS),
        "partial_decode_count": 0,
        "lint_count": 0,
        "top_lint_codes": [],
        "convert_failure_count": 0,
        "iwxxm_validation": {"pass": 0, "fail": 0, "skip": 0},
        "failure_locations": [],
    }


class LiveMapEvalStore:
    """Latest-snapshot store (memory or Postgres JSON row)."""

    def __init__(self) -> None:
        self._latest: dict[str, Any] | None = None
        self._use_db = False
        self._engine: Any = None

    def enable_memory_only(self) -> None:
        """Force in-memory mode (tests)."""
        self._use_db = False
        self._engine = None

    def configure_from_env(self) -> None:
        """Try DATABASE_URL / LIVE_MAP_CACHE_URL for Postgres writes."""
        try:
            from sqlalchemy import create_engine

            from src.services.station_health_postgres_url import sync_database_url

            raw = (os.getenv("DATABASE_URL") or os.getenv("LIVE_MAP_CACHE_URL") or "").strip()
            sync = sync_database_url(raw or None)
            if not sync:
                self._use_db = False
                return
            self._engine = create_engine(sync, pool_pre_ping=True)
            self._use_db = True
        except Exception:  # pragma: no cover - defensive
            logger.exception("live_map_eval: Postgres unavailable; using memory")
            self._use_db = False
            self._engine = None

    def write_snapshot(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Replace the latest snapshot and optionally persist.

        Parameters
        ----------
        payload :
            Full response body including ``computed_at``.

        Returns
        -------
        dict[str, Any]
            Stored payload.
        """
        self._latest = dict(payload)
        if self._use_db and self._engine is not None:
            self._write_db(payload)
        return dict(self._latest)

    def read_latest(self) -> dict[str, Any]:
        """Return the latest snapshot (zeros if never written).

        Returns
        -------
        dict[str, Any]
            Snapshot body.
        """
        if self._use_db and self._engine is not None:
            loaded = self._read_db()
            if loaded is not None:
                self._latest = loaded
        if self._latest is None:
            return empty_snapshot()
        return dict(self._latest)

    def _write_db(self, payload: dict[str, Any]) -> None:
        from sqlalchemy import text

        raw = payload.get("computed_at")
        stamp = datetime.fromisoformat(raw.replace("Z", "+00:00")) if isinstance(raw, str) else datetime.now(tz=UTC)
        with self._engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO live_map_eval_snapshots "
                    "(computed_at, window_hours, payload) "
                    "VALUES (:computed_at, :window_hours, CAST(:payload AS json))"
                ),
                {
                    "computed_at": stamp,
                    "window_hours": int(payload.get("window_hours") or 24),
                    "payload": json.dumps(payload),
                },
            )

    def _read_db(self) -> dict[str, Any] | None:
        from sqlalchemy import text

        try:
            with self._engine.connect() as conn:
                row = conn.execute(
                    text("SELECT payload FROM live_map_eval_snapshots ORDER BY computed_at DESC LIMIT 1")
                ).fetchone()
        except Exception:  # pragma: no cover - missing table
            logger.exception("live_map_eval: read failed")
            return None
        if row is None:
            return None
        payload = row[0]
        if isinstance(payload, dict):
            return cast(dict[str, Any], payload)
        if isinstance(payload, str):
            parsed: object = json.loads(payload)
            if isinstance(parsed, dict):
                return cast(dict[str, Any], parsed)
            return None
        return None


_store: LiveMapEvalStore | None = None


def get_live_map_eval_store() -> LiveMapEvalStore:
    """Process singleton store."""
    global _store
    if _store is None:
        _store = LiveMapEvalStore()
        _store.configure_from_env()
    return _store


def set_live_map_eval_store(store: LiveMapEvalStore | None) -> None:
    """Replace store (tests)."""
    global _store
    _store = store
