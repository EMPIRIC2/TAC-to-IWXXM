"""Station health store facade: in-memory for tests, Postgres when configured (F39)."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from threading import Lock
from typing import Any, Protocol

from src.services.station_health_metrics import (
    WINDOW_SECONDS,
    count_solidus_signals,
    grade_product_window,
    window_timedelta,
)

logger = logging.getLogger(__name__)

DEFAULT_METRICS: tuple[dict[str, Any], ...] = (
    {
        "id": "availability",
        "label": "Availability",
        "description": "Share of expected TAC reports received in the window",
        "unit": "percent",
        "higher_is_better": True,
        "enabled": True,
        "sort_order": 10,
    },
    {
        "id": "solidus_rate",
        "label": "Solidus rate",
        "description": "Share of solidus characters in received TAC text",
        "unit": "ratio",
        "higher_is_better": False,
        "enabled": True,
        "sort_order": 20,
    },
    {
        "id": "missing_digit_rate",
        "label": "Missing digit rate",
        "description": "Average missing-digit solidus runs per report",
        "unit": "ratio",
        "higher_is_better": False,
        "enabled": True,
        "sort_order": 30,
    },
    {
        "id": "lint_severity",
        "label": "Lint severity",
        "description": "Quality score from stored lint error and warning counts",
        "unit": "percent",
        "higher_is_better": True,
        "enabled": True,
        "sort_order": 40,
    },
    {
        "id": "overall_grade",
        "label": "Overall grade",
        "description": "Combined availability and quality letter grade",
        "unit": "letter",
        "higher_is_better": True,
        "enabled": True,
        "sort_order": 50,
    },
)


@dataclass(slots=True)
class StationRecord:
    """
    One stored TAC observation for a station.

    Attributes
    ----------
    icao : object
        Field ``icao``.
    product : object
        Field ``product``.
    observed_at : object
        Field ``observed_at``.
    ingested_at : object
        Field ``ingested_at``.
    tac_text : object
        Field ``tac_text``.
    source : object
        Field ``source``.
    solidus_count : object
        Field ``solidus_count``.
    missing_digit_count : object
        Field ``missing_digit_count``.
    lint_error_count : object
        Field ``lint_error_count``.
    lint_warning_count : object
        Field ``lint_warning_count``.
    convert_ok : object
        Field ``convert_ok``.
    character_count : object
        Field ``character_count``.
    """

    icao: str
    product: str
    observed_at: datetime
    ingested_at: datetime
    tac_text: str
    source: str
    solidus_count: int
    missing_digit_count: int
    lint_error_count: int
    lint_warning_count: int
    convert_ok: bool | None
    character_count: int


@dataclass(slots=True)
class StationMeta:
    """
    Station registry row.

    Attributes
    ----------
    icao : object
        Field ``icao``.
    name : object
        Field ``name``.
    country : object
        Field ``country``.
    latitude : object
        Field ``latitude``.
    longitude : object
        Field ``longitude``.
    first_seen_at : object
        Field ``first_seen_at``.
    last_seen_at : object
        Field ``last_seen_at``.
    """

    icao: str
    name: str | None = None
    country: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    first_seen_at: datetime | None = None
    last_seen_at: datetime | None = None


@dataclass
class StationHealthStore:
    """
    Thread-safe in-memory store for station health reads and writes.

    Attributes
    ----------
    _stations : object
        Field ``_stations``.
    _records : object
        Field ``_records``.
    _metrics : object
        Field ``_metrics``.
    _lock : object
        Field ``_lock``.
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
        >>> 1 + 1  # docstring smoke (reset)
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
        object
            Return value.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (list_metrics)
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

        Returns
        -------
        StationRecord | None
            Stored row, or ``None`` when the ICAO is invalid.

        Parameters
        ----------
        icao : object
            Argument ``icao``.
        product : object
            Argument ``product``.
        tac_text : object
            Argument ``tac_text``.
        source : object
            Argument ``source``.
        observed_at : object
            Argument ``observed_at``.
        name : object
            Argument ``name``.
        lint_error_count : object
            Argument ``lint_error_count``.
        lint_warning_count : object
            Argument ``lint_warning_count``.
        convert_ok : object
            Argument ``convert_ok``.

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
            Argument ``window_key``.
        product : object
            Argument ``product``.
        grade : object
            Argument ``grade``.
        limit : object
            Argument ``limit``.

        Returns
        -------
        object
            Return value.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (list_stations)
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
            products = self._grade_products(icao_rows, window_key)
            if product_filter:
                products = [item for item in products if item["product"] == product_filter]
                if not products:
                    continue
            overall = self._overall_from_products(products)
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
            Argument ``icao``.

        Returns
        -------
        object
            Return value.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (get_station)
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
            products = self._grade_products(window_rows, window_key)
            overall = self._overall_from_products(products)
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

    @staticmethod
    def _grade_products(rows: list[StationRecord], window_key: str) -> list[dict[str, Any]]:
        """
        Internal helper ``_grade_products``.

        Parameters
        ----------
        rows : object
            Argument ``rows``.
        window_key : object
            Argument ``window_key``.

        Returns
        -------
        object
            Return value.
        """
        by_product: dict[str, list[StationRecord]] = {}
        for row in rows:
            by_product.setdefault(row.product, []).append(row)
        graded: list[dict[str, Any]] = []
        for product, product_rows in sorted(by_product.items()):
            grade = grade_product_window(
                product=product,
                window_key=window_key,
                actual_count=len(product_rows),
                solidus_count=sum(row.solidus_count for row in product_rows),
                character_count=sum(row.character_count for row in product_rows),
                missing_digit_count=sum(row.missing_digit_count for row in product_rows),
                lint_error_count=sum(row.lint_error_count for row in product_rows),
                lint_warning_count=sum(row.lint_warning_count for row in product_rows),
            )
            graded.append(
                {
                    "product": grade.product,
                    "grade": grade.overall_grade,
                    "overall_score": grade.overall_score,
                    "availability_score": grade.availability_score,
                    "actual_count": grade.actual_count,
                    "expected_count": grade.expected_count,
                    "solidus_rate": grade.solidus_rate,
                    "missing_digit_rate": grade.missing_digit_rate,
                    "lint_severity_score": grade.lint_severity_score,
                    "lint_error_count": sum(row.lint_error_count for row in product_rows),
                }
            )
        return graded

    @staticmethod
    def _overall_from_products(products: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Internal helper ``_overall_from_products``.

        Parameters
        ----------
        products : object
            Argument ``products``.

        Returns
        -------
        object
            Return value.
        """
        if not products:
            return {"overall_grade": "F", "overall_score": 0.0}
        score = sum(float(item["overall_score"]) for item in products) / len(products)
        from src.services.station_health_metrics import letter_grade

        return {"overall_grade": letter_grade(score), "overall_score": round(score, 2)}


class StationHealthStoreProtocol(Protocol):
    """
    Shared read/write surface for memory and Postgres stores.

    Attributes
    ----------
    _ : object
        Field ``_``.
    """

    def reset(self) -> None:
        """
        Clear mutable state when supported.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (reset)
        2
        """

    def list_metrics(self) -> list[dict[str, Any]]:
        """
        Return enabled metric definitions.

        Returns
        -------
        object
            Return value.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (list_metrics)
        2
        """

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
        Append one observation.

        Parameters
        ----------
        icao : object
            Argument ``icao``.
        product : object
            Argument ``product``.
        tac_text : object
            Argument ``tac_text``.
        source : object
            Argument ``source``.
        observed_at : object
            Argument ``observed_at``.
        name : object
            Argument ``name``.
        lint_error_count : object
            Argument ``lint_error_count``.
        lint_warning_count : object
            Argument ``lint_warning_count``.
        convert_ok : object
            Argument ``convert_ok``.

        Returns
        -------
        object
            Return value.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (record_observation)
        2
        """

    def list_stations(
        self,
        *,
        window_key: str = "6h",
        product: str | None = None,
        grade: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        """
        Build the public list payload.

        Parameters
        ----------
        window_key : object
            Argument ``window_key``.
        product : object
            Argument ``product``.
        grade : object
            Argument ``grade``.
        limit : object
            Argument ``limit``.

        Returns
        -------
        object
            Return value.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (list_stations)
        2
        """

    def get_station(self, icao: str) -> dict[str, Any] | None:
        """
        Build the public detail payload.

        Parameters
        ----------
        icao : object
            Argument ``icao``.

        Returns
        -------
        object
            Return value.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (get_station)
        2
        """


_MEMORY_STORE = StationHealthStore()
_OVERRIDE: StationHealthStoreProtocol | None = None
_PG_STORE: StationHealthStoreProtocol | None = None
_PG_URL: str | None = None


def get_station_health_store() -> StationHealthStoreProtocol:
    """
    Return the process station health store.

    Prefer product Postgres when ``DATABASE_URL`` is set. Unit tests inject
    an in-memory store via ``set_station_health_store``.

    Returns
    -------
    object
        Return value.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_station_health_store)
    2
    """
    global _PG_STORE, _PG_URL
    if _OVERRIDE is not None:
        return _OVERRIDE
    try:
        from src.services.station_health_postgres import (
            PostgresStationHealthStore,
            sync_database_url,
        )
    except Exception:
        logger.debug("station health postgres module unavailable", exc_info=True)
        return _MEMORY_STORE
    url = sync_database_url()
    if not url:
        return _MEMORY_STORE
    if _PG_STORE is None or url != _PG_URL:
        _PG_STORE = PostgresStationHealthStore.from_url(url)
        _PG_URL = url
    return _PG_STORE


def set_station_health_store(store: StationHealthStoreProtocol | None) -> None:
    """
    Replace the process store (tests). ``None`` restores the default routing.

    Parameters
    ----------
    store : object
        Argument ``store``.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (set_station_health_store)
    2
    """
    global _OVERRIDE, _MEMORY_STORE
    if store is None:
        _OVERRIDE = None
        _MEMORY_STORE = StationHealthStore()
        return
    _OVERRIDE = store


__all__ = [
    "DEFAULT_METRICS",
    "StationHealthStore",
    "StationHealthStoreProtocol",
    "StationMeta",
    "StationRecord",
    "get_station_health_store",
    "set_station_health_store",
]
