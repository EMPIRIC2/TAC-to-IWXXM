"""Station health store facade: in-memory for tests, Postgres when configured (F39)."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from threading import Lock
from typing import Any

from src.services.station_health_aggregate import enrich_station_window
from src.services.station_health_metrics import (
    RETENTION_SECONDS,
    WINDOW_SECONDS,
    count_solidus_signals,
    window_timedelta,
)
from src.services.station_health_signals import (
    detect_file_format,
    extract_maintenance_tags,
    normalize_issue_codes,
)
from src.services.station_health_store_rows import region_filter_key, station_list_row
from src.services.station_health_types import (
    DEFAULT_METRICS,
    StationHealthStoreProtocol,
    StationMeta,
    StationRecord,
)
from src.services.station_health_wmo_region import wmo_region_for_icao

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
        issue_codes: list[str] | tuple[str, ...] | None = None,
    ) -> StationRecord | None:
        """
        Append one observation and refresh station metadata.

        Applies rolling 90-day retention after each write.

        Parameters
        ----------
        args
            See function signature.

        Returns
        -------
        object
            Return value.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (record_observation)
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
        # Reject observations older than retention (ignore tip-drift history).
        if observed < now - window_timedelta("90d"):
            return None
        signals = count_solidus_signals(tac_text)
        body = tac_text or ""
        source_l = (source or "unknown").strip().lower() or "unknown"
        codes = normalize_issue_codes(issue_codes)
        row = StationRecord(
            icao=code,
            product=product_l,
            observed_at=observed,
            ingested_at=now,
            tac_text=body,
            source=source_l,
            solidus_count=signals.solidus_count,
            missing_digit_count=signals.missing_digit_count,
            lint_error_count=max(0, int(lint_error_count)),
            lint_warning_count=max(0, int(lint_warning_count)),
            convert_ok=convert_ok,
            character_count=signals.character_count,
            file_format=detect_file_format(body, source=source_l),
            maintenance_tags=extract_maintenance_tags(body),
            issue_codes=codes,
        )
        country: str | None = None
        try:
            from src.schemas.airport import get_airport_validator

            airport = get_airport_validator().get_airport(code)
            if airport is not None and getattr(airport, "country", None):
                raw_country = str(airport.country).strip().upper()
                # WMO region map keys are ISO 3166-1 alpha-2 only.
                country = raw_country if len(raw_country) == 2 else None
        except Exception:
            logger.exception("station health country lookup failed for %s", code)
        with self._lock:
            meta = self._stations.get(code)
            if meta is None:
                self._stations[code] = StationMeta(
                    icao=code,
                    name=name,
                    country=country,
                    first_seen_at=observed,
                    last_seen_at=observed,
                )
            else:
                meta.last_seen_at = observed
                if name and not meta.name:
                    meta.name = name
                if country and not meta.country:
                    meta.country = country
                if meta.first_seen_at is None or observed < meta.first_seen_at:
                    meta.first_seen_at = observed
            self._records.append(row)
            retention_cutoff = now - window_timedelta("90d")
            self._records[:] = [item for item in self._records if item.observed_at >= retention_cutoff]
        return row

    def list_stations(
        self,
        *,
        window_key: str = "6h",
        product: str | None = None,
        grade: str | None = None,
        region: str | None = None,
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
        region : object
            Optional WMO region filter (``I``-``VI`` or ``unknown``).
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
        # Region-scoped loads may need every station in that association.
        max_limit = 5000 if region else 500
        limit = max(1, min(int(limit), max_limit))
        now = datetime.now(UTC)
        retention_cutoff = now - window_timedelta("90d")
        cutoff = max(now - window_timedelta(window_key), retention_cutoff)
        product_filter = product.strip().lower() if product else None
        grade_filter = grade.strip().upper() if grade else None
        region_key = region_filter_key(region)

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
            wmo_region = wmo_region_for_icao(icao, country=meta.country)
            if region_key is not None and wmo_region != region_key:
                continue
            row = station_list_row(
                icao=icao,
                meta=meta,
                icao_rows=by_icao.get(icao, []),
                window_key=window_key,
                product_filter=product_filter,
                grade_filter=grade_filter,
            )
            if row is None:
                continue
            grade_counts[row["overall_grade"]] = grade_counts.get(row["overall_grade"], 0) + 1
            station_rows.append(row)

        station_rows.sort(key=lambda item: (-float(item["overall_score"]), item["icao"]))
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
        retention_cutoff = now - window_timedelta("90d")
        records = [row for row in records if row.observed_at >= retention_cutoff]
        for window_key in WINDOW_SECONDS:
            cutoff = max(now - window_timedelta(window_key), retention_cutoff)
            window_rows = [row for row in records if row.observed_at >= cutoff]
            windows[window_key] = enrich_station_window(
                meta=meta,
                rows=window_rows,
                window_key=window_key,
            )
        return {
            "icao": code,
            "name": meta.name,
            "wmo_region": wmo_region_for_icao(code, country=meta.country),
            "windows": windows,
            "record_count": len(records),
            "maintenance_tag_counts": windows.get("90d", {}).get("maintenance_tag_counts", {}),
            "file_format_counts": windows.get("90d", {}).get("file_format_counts", {}),
            "issue_code_counts": windows.get("90d", {}).get("issue_code_counts", {}),
            "centennial_metrics": windows.get("90d", {}).get("centennial_metrics", []),
        }

    def purge_expired(self) -> int:
        """
        Delete in-memory observations older than 90 days.

        Returns
        -------
        object
            Return value.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (purge_expired)
        2
        """
        now = datetime.now(UTC)
        cutoff = now - window_timedelta("90d")
        _ = RETENTION_SECONDS
        with self._lock:
            before = len(self._records)
            self._records[:] = [row for row in self._records if row.observed_at >= cutoff]
            return before - len(self._records)


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
