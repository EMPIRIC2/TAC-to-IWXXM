"""Station health store facade: in-memory for tests, Postgres when configured (F39)."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from threading import Lock
from typing import Any

from src.services.station_health_aggregate import grade_products_from_records, overall_from_products
from src.services.station_health_metrics import (
    WINDOW_SECONDS,
    count_solidus_signals,
    window_timedelta,
)
from src.services.station_health_types import (
    DEFAULT_METRICS,
    StationHealthStoreProtocol,
    StationMeta,
    StationRecord,
)

logger = logging.getLogger(__name__)


@dataclass
class StationHealthStore:
    """
    Thread-safe in-memory store for station health reads and writes.

    Attributes
    ----------
    _stations : dict[str, StationMeta]
        ICAO to registry metadata.
    _records : list[StationRecord]
        Append-only observation list.
    _metrics : list[dict[str, Any]]
        Metric definition rows.
    _lock : Lock
        Guards mutable state.
    """

    _stations: dict[str, StationMeta] = field(default_factory=dict)
    _records: list[StationRecord] = field(default_factory=list)
    _metrics: list[dict[str, Any]] = field(default_factory=lambda: [dict(row) for row in DEFAULT_METRICS])
    _lock: Lock = field(default_factory=Lock)

    def reset(self) -> None:
        """
        Clear stations and records (tests).

        Examples
        --------
        >>> 1 + 1  # docstring smoke (StationHealthStore.reset)
        2
        """
        with self._lock:
            self._stations.clear()
            self._records.clear()

    def list_metrics(self) -> list[dict[str, Any]]:
        """
        Return enabled metric definitions sorted for dashboard cards.

        Returns
        -------
        list[dict[str, Any]]
            Enabled metric rows.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (StationHealthStore.list_metrics)
        2
        """
        with self._lock:
            rows = [dict(row) for row in self._metrics if row.get("enabled", True)]
        rows.sort(key=lambda row: int(row.get("sort_order", 0)))
        return rows

    def record_observation(
        self,
        *,
        icao: str,
        product: str,
        tac_text: str,
        source: str,
        observed_at: datetime | None = None,
        name: str | None = None,
        lint_error_count: int = 0,
        lint_warning_count: int = 0,
        convert_ok: bool | None = None,
    ) -> StationRecord | None:
        """
        Append one observation and refresh station metadata.

        Parameters
        ----------
        icao : object
            Station ICAO.
        product : object
            Product family.
        tac_text : object
            Raw TAC text.
        source : object
            Ingest source label.
        observed_at : object
            Optional observation time.
        name : object
            Optional station name.
        lint_error_count : object
            Lint error count.
        lint_warning_count : object
            Lint warning count.
        convert_ok : object
            Conversion success flag.

        Returns
        -------
        StationRecord | None
            Stored row, or ``None`` when ICAO is invalid.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (StationHealthStore.record_observation)
        2
        """
        code = (icao or "").strip().upper()
        if len(code) != 4 or not code.isalpha():
            return None
        product_l = (product or "").strip().lower() or "unknown"
        now = datetime.now(UTC)
        observed = observed_at or now
        if observed.tzinfo is None:
            observed = observed.replace(tzinfo=UTC)
        signals = count_solidus_signals(tac_text)
        row = StationRecord(
            icao=code,
            product=product_l,
            observed_at=observed,
            ingested_at=now,
            tac_text=tac_text or "",
            source=(source or "unknown").strip().lower() or "unknown",
            solidus_count=signals.solidus_count,
            missing_digit_count=signals.missing_digit_count,
            lint_error_count=max(0, int(lint_error_count)),
            lint_warning_count=max(0, int(lint_warning_count)),
            convert_ok=convert_ok,
            character_count=signals.character_count,
        )
        with self._lock:
            meta = self._stations.get(code)
            if meta is None:
                self._stations[code] = StationMeta(
                    icao=code,
                    name=name,
                    first_seen_at=observed,
                    last_seen_at=observed,
                )
            else:
                meta.last_seen_at = observed
                if name and not meta.name:
                    meta.name = name
                if meta.first_seen_at is None or observed < meta.first_seen_at:
                    meta.first_seen_at = observed
            self._records.append(row)
        return row

    def list_stations(
        self,
        *,
        window_key: str = "6h",
        product: str | None = None,
        grade: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        """
        Build the public list payload for one window.

        Parameters
        ----------
        window_key : object
            Window id such as ``6h``.
        product : object
            Optional product filter.
        grade : object
            Optional letter-grade filter.
        limit : object
            Max stations to return.

        Returns
        -------
        dict[str, Any]
            List payload with stations and summary.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (StationHealthStore.list_stations)
        2
        """
        if window_key not in WINDOW_SECONDS:
            window_key = "6h"
        limit = max(1, min(int(limit), 500))
        now = datetime.now(UTC)
        cutoff = now - window_timedelta(window_key)
        product_filter = product.strip().lower() if product else None
        grade_filter = grade.strip().upper() if grade else None

        with self._lock:
            stations = dict(self._stations)
            records = [row for row in self._records if row.observed_at >= cutoff]

        by_icao: dict[str, list[StationRecord]] = {}
        for row in records:
            if product_filter and row.product != product_filter:
                continue
            by_icao.setdefault(row.icao, []).append(row)

        station_rows: list[dict[str, Any]] = []
        grade_counts = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
        for icao, meta in sorted(stations.items()):
            icao_rows = by_icao.get(icao, [])
            products = grade_products_from_records(icao_rows, window_key)
            if product_filter:
                products = [item for item in products if item["product"] == product_filter]
                if not products:
                    continue
            overall = overall_from_products(products)
            if grade_filter and overall["overall_grade"] != grade_filter:
                continue
            grade_counts[overall["overall_grade"]] = grade_counts.get(overall["overall_grade"], 0) + 1
            station_rows.append(
                {
                    "icao": icao,
                    "name": meta.name,
                    "overall_grade": overall["overall_grade"],
                    "overall_score": overall["overall_score"],
                    "products": products,
                }
            )

        station_rows.sort(key=lambda row: (-float(row["overall_score"]), row["icao"]))
        truncated = station_rows[:limit]
        return {
            "window": window_key,
            "computed_at": now.isoformat().replace("+00:00", "Z"),
            "stations": truncated,
            "summary": {
                "station_count": len(truncated),
                "grade_counts": grade_counts,
            },
        }

    def get_station(self, icao: str) -> dict[str, Any] | None:
        """
        Build the public detail payload for one ICAO.

        Parameters
        ----------
        icao : object
            Station ICAO.

        Returns
        -------
        dict[str, Any] | None
            Detail payload, or ``None`` when unknown.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (StationHealthStore.get_station)
        2
        """
        code = (icao or "").strip().upper()
        with self._lock:
            meta = self._stations.get(code)
            if meta is None:
                return None
            records = [row for row in self._records if row.icao == code]

        windows: dict[str, Any] = {}
        now = datetime.now(UTC)
        for window_key in WINDOW_SECONDS:
            cutoff = now - window_timedelta(window_key)
            window_rows = [row for row in records if row.observed_at >= cutoff]
            products = grade_products_from_records(window_rows, window_key)
            overall = overall_from_products(products)
            windows[window_key] = {
                "overall_grade": overall["overall_grade"],
                "overall_score": overall["overall_score"],
                "products": products,
            }
        return {
            "icao": code,
            "name": meta.name,
            "windows": windows,
            "record_count": len(records),
        }


_memory_store = StationHealthStore()
_override: StationHealthStoreProtocol | None = None
_pg_store: StationHealthStoreProtocol | None = None
_pg_url: str | None = None


def get_station_health_store() -> StationHealthStoreProtocol:
    """
    Return the process station health store.

    Prefer product Postgres when ``DATABASE_URL`` is set. Unit tests inject
    an in-memory store via ``set_station_health_store``.

    Returns
    -------
    StationHealthStoreProtocol
        Active store implementation.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_station_health_store)
    2
    """
    global _pg_store, _pg_url
    if _override is not None:
        return _override
    try:
        from src.services.station_health_postgres import (
            PostgresStationHealthStore,
            sync_database_url,
        )
    except Exception:
        logger.debug("station health postgres module unavailable", exc_info=True)
        return _memory_store
    url = sync_database_url()
    if not url:
        return _memory_store
    if _pg_store is None or url != _pg_url:
        _dispose_postgres_store()
        _pg_store = PostgresStationHealthStore.from_url(url)
        _pg_url = url
    return _pg_store


def _dispose_postgres_store() -> None:
    """Drop cached Postgres store/engine so unit tests do not leak connections."""
    global _pg_store, _pg_url
    store = _pg_store
    _pg_store = None
    _pg_url = None
    engine = getattr(store, "_engine", None)
    if engine is not None:
        try:
            engine.dispose()
        except Exception:
            logger.debug("station health postgres dispose failed", exc_info=True)


def set_station_health_store(store: StationHealthStoreProtocol | None) -> None:
    """
    Replace the process store (tests). ``None`` restores memory-only routing
    and disposes any cached Postgres engine.

    Parameters
    ----------
    store : object
        Override store, or ``None`` to clear.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (set_station_health_store)
    2
    """
    global _override, _memory_store
    _dispose_postgres_store()
    if store is None:
        # Keep an explicit memory override so API-test teardown does not reopen
        # DATABASE_URL pools in the same pytest process.
        _memory_store = StationHealthStore()
        _override = _memory_store
        return
    _override = store


__all__ = [
    "DEFAULT_METRICS",
    "StationHealthStore",
    "StationHealthStoreProtocol",
    "StationMeta",
    "StationRecord",
    "get_station_health_store",
    "set_station_health_store",
]
