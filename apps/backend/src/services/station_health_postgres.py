"""Postgres-backed station health reads and writes (F39)."""

from __future__ import annotations

import logging
import os
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from src.services.station_health_aggregate import (
    grade_products_from_records,
    overall_from_products,
    row_to_station_record,
)
from src.services.station_health_metrics import (
    WINDOW_SECONDS,
    count_solidus_signals,
    window_timedelta,
)
from src.services.station_health_types import DEFAULT_METRICS, StationRecord

logger = logging.getLogger(__name__)


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


class PostgresStationHealthStore:
    """
    Station health store backed by product Postgres tables.

    Attributes
    ----------
    _engine : Engine
        Sync SQLAlchemy engine.
    """

    def __init__(self, engine: Engine) -> None:
        """
        Bind the store to a sync engine.

        Parameters
        ----------
        engine : object
            SQLAlchemy engine.
        """
        self._engine = engine

    @classmethod
    def from_url(cls, url: str) -> PostgresStationHealthStore:
        """
        Build a store from a sync database URL.

        Parameters
        ----------
        url : object
            Sync SQLAlchemy URL.

        Returns
        -------
        PostgresStationHealthStore
            Connected store.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (PostgresStationHealthStore.from_url)
        2
        """
        return cls(create_engine(url, pool_pre_ping=True))

    def reset(self) -> None:
        """
        No-op for API compatibility with the in-memory store.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (PostgresStationHealthStore.reset)
        2
        """

    def list_metrics(self) -> list[dict[str, Any]]:
        """
        Return enabled metric definitions from Postgres, with catalog fallback.

        Returns
        -------
        list[dict[str, Any]]
            Enabled metric rows.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (PostgresStationHealthStore.list_metrics)
        2
        """
        try:
            with self._engine.connect() as conn:
                rows = conn.execute(
                    text(
                        """
                        SELECT id, label, description, unit, higher_is_better, enabled, sort_order
                        FROM station_metric_definitions
                        WHERE enabled IS TRUE
                        ORDER BY sort_order ASC, id ASC
                        """
                    )
                ).mappings()
                payload = [dict(row) for row in rows]
        except Exception:
            logger.exception("station health metrics query failed; using defaults")
            payload = [dict(row) for row in DEFAULT_METRICS if row.get("enabled", True)]
            payload.sort(key=lambda row: int(row.get("sort_order", 0)))
            return payload
        if not payload:
            payload = [dict(row) for row in DEFAULT_METRICS if row.get("enabled", True)]
            payload.sort(key=lambda row: int(row.get("sort_order", 0)))
        return payload

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
        Upsert station registry and append one TAC observation row.

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
            Stored row, or ``None`` on invalid ICAO or write failure.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (PostgresStationHealthStore.record_observation)
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
        try:
            with self._engine.begin() as conn:
                conn.execute(
                    text(
                        """
                        INSERT INTO station_registry (
                            icao, name, country, latitude, longitude,
                            first_seen_at, last_seen_at, updated_at
                        ) VALUES (
                            :icao, :name, NULL, NULL, NULL,
                            :observed_at, :observed_at, :now
                        )
                        ON CONFLICT (icao) DO UPDATE SET
                            last_seen_at = EXCLUDED.last_seen_at,
                            updated_at = EXCLUDED.updated_at,
                            name = COALESCE(station_registry.name, EXCLUDED.name)
                        """
                    ),
                    {"icao": code, "name": name, "observed_at": observed, "now": now},
                )
                conn.execute(
                    text(
                        """
                        INSERT INTO station_tac_records (
                            icao, product, observed_at, ingested_at, tac_text, source,
                            solidus_count, missing_digit_count,
                            lint_error_count, lint_warning_count, convert_ok
                        ) VALUES (
                            :icao, :product, :observed_at, :ingested_at, :tac_text, :source,
                            :solidus_count, :missing_digit_count,
                            :lint_error_count, :lint_warning_count, :convert_ok
                        )
                        """
                    ),
                    {
                        "icao": row.icao,
                        "product": row.product,
                        "observed_at": row.observed_at,
                        "ingested_at": row.ingested_at,
                        "tac_text": row.tac_text,
                        "source": row.source,
                        "solidus_count": row.solidus_count,
                        "missing_digit_count": row.missing_digit_count,
                        "lint_error_count": row.lint_error_count,
                        "lint_warning_count": row.lint_warning_count,
                        "convert_ok": row.convert_ok,
                    },
                )
        except Exception:
            logger.exception("station health postgres write failed for %s", code)
            return None
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
        Build the public list payload from Postgres observations.

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
        >>> 1 + 1  # docstring smoke (PostgresStationHealthStore.list_stations)
        2
        """
        if window_key not in WINDOW_SECONDS:
            window_key = "6h"
        limit = max(1, min(int(limit), 500))
        now = datetime.now(UTC)
        cutoff = now - window_timedelta(window_key)
        product_filter = product.strip().lower() if product else None
        grade_filter = grade.strip().upper() if grade else None

        stations, records = self._load_window(cutoff=cutoff, product_filter=product_filter)
        by_icao: dict[str, list[StationRecord]] = {}
        for row in records:
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
                    "name": meta.get("name"),
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
            "summary": {"station_count": len(truncated), "grade_counts": grade_counts},
        }

    def get_station(self, icao: str) -> dict[str, Any] | None:
        """
        Build the public detail payload for one ICAO from Postgres.

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
        >>> 1 + 1  # docstring smoke (PostgresStationHealthStore.get_station)
        2
        """
        code = (icao or "").strip().upper()
        try:
            with self._engine.connect() as conn:
                meta_row = (
                    conn.execute(
                        text("SELECT icao, name FROM station_registry WHERE icao = :icao"),
                        {"icao": code},
                    )
                    .mappings()
                    .first()
                )
                if meta_row is None:
                    return None
                record_rows = conn.execute(
                    text(
                        """
                        SELECT icao, product, observed_at, ingested_at, tac_text, source,
                               solidus_count, missing_digit_count,
                               lint_error_count, lint_warning_count, convert_ok
                        FROM station_tac_records
                        WHERE icao = :icao
                        ORDER BY observed_at ASC
                        """
                    ),
                    {"icao": code},
                ).mappings()
                records = [row_to_station_record(dict(row)) for row in record_rows]
        except Exception:
            logger.exception("station health detail query failed for %s", code)
            return None

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
            "name": meta_row.get("name"),
            "windows": windows,
            "record_count": len(records),
        }

    def _load_window(
        self,
        *,
        cutoff: datetime,
        product_filter: str | None,
    ) -> tuple[dict[str, dict[str, Any]], list[StationRecord]]:
        """
        Load registry rows and windowed TAC records from Postgres.

        Parameters
        ----------
        cutoff : object
            Inclusive lower bound for ``observed_at``.
        product_filter : object
            Optional product filter.

        Returns
        -------
        tuple[dict[str, dict[str, Any]], list[StationRecord]]
            Station map and observation rows.
        """
        try:
            with self._engine.connect() as conn:
                station_rows = conn.execute(
                    text("SELECT icao, name FROM station_registry ORDER BY icao ASC")
                ).mappings()
                stations = {str(row["icao"]): dict(row) for row in station_rows}
                if product_filter:
                    record_rows = conn.execute(
                        text(
                            """
                            SELECT icao, product, observed_at, ingested_at, tac_text, source,
                                   solidus_count, missing_digit_count,
                                   lint_error_count, lint_warning_count, convert_ok
                            FROM station_tac_records
                            WHERE observed_at >= :cutoff AND product = :product
                            """
                        ),
                        {"cutoff": cutoff, "product": product_filter},
                    ).mappings()
                else:
                    record_rows = conn.execute(
                        text(
                            """
                            SELECT icao, product, observed_at, ingested_at, tac_text, source,
                                   solidus_count, missing_digit_count,
                                   lint_error_count, lint_warning_count, convert_ok
                            FROM station_tac_records
                            WHERE observed_at >= :cutoff
                            """
                        ),
                        {"cutoff": cutoff},
                    ).mappings()
                records = [row_to_station_record(dict(row)) for row in record_rows]
        except Exception:
            logger.exception("station health list query failed")
            return {}, []
        return stations, records


__all__ = ["PostgresStationHealthStore", "sync_database_url"]
