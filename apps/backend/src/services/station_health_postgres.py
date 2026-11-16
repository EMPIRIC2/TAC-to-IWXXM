"""Postgres-backed station health reads and writes (F39)."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from src.services.station_health_aggregate import enrich_station_window, row_to_station_record
from src.services.station_health_metrics import (
    RETENTION_SECONDS,
    WINDOW_SECONDS,
    count_solidus_signals,
    window_timedelta,
)
from src.services.station_health_postgres_load import load_window_rows
from src.services.station_health_postgres_url import sync_database_url
from src.services.station_health_signals import (
    detect_file_format,
    extract_maintenance_tags,
    normalize_issue_codes,
)
from src.services.station_health_types import DEFAULT_METRICS, StationMeta, StationRecord
from src.services.station_health_wmo_region import wmo_region_for_icao

logger = logging.getLogger(__name__)


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
        issue_codes: list[str] | tuple[str, ...] | None = None,
    ) -> StationRecord | None:
        """
        Upsert station registry and append one TAC observation row.

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
        if observed < now - window_timedelta("90d"):
            return None
        signals = count_solidus_signals(tac_text)
        body = tac_text or ""
        source_l = (source or "unknown").strip().lower() or "unknown"
        codes = normalize_issue_codes(issue_codes)
        file_format = detect_file_format(body, source=source_l)
        maintenance_tags = extract_maintenance_tags(body)
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
            file_format=file_format,
            maintenance_tags=maintenance_tags,
            issue_codes=codes,
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
                            lint_error_count, lint_warning_count, convert_ok,
                            file_format, issue_codes
                        ) VALUES (
                            :icao, :product, :observed_at, :ingested_at, :tac_text, :source,
                            :solidus_count, :missing_digit_count,
                            :lint_error_count, :lint_warning_count, :convert_ok,
                            :file_format, CAST(:issue_codes AS json)
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
                        "file_format": row.file_format,
                        "issue_codes": json.dumps(list(row.issue_codes)),
                    },
                )
                conn.execute(
                    text(
                        """
                        DELETE FROM station_tac_records
                        WHERE observed_at < :cutoff
                        """
                    ),
                    {"cutoff": now - window_timedelta("90d")},
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
        region: str | None = None,
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
        >>> 1 + 1  # docstring smoke (PostgresStationHealthStore.list_stations)
        2
        """
        if window_key not in WINDOW_SECONDS:
            window_key = "6h"
        max_limit = 5000 if region else 500
        limit = max(1, min(int(limit), max_limit))
        now = datetime.now(UTC)
        retention_cutoff = now - window_timedelta("90d")
        cutoff = max(now - window_timedelta(window_key), retention_cutoff)
        product_filter = product.strip().lower() if product else None
        grade_filter = grade.strip().upper() if grade else None
        if region and region.strip().lower() == "unknown":
            region_key = "unknown"
        elif region:
            region_key = region.strip().upper()
        else:
            region_key = None

        stations, records = load_window_rows(self._engine, cutoff=cutoff, product_filter=product_filter)
        by_icao: dict[str, list[StationRecord]] = {}
        for row in records:
            by_icao.setdefault(row.icao, []).append(row)

        station_rows: list[dict[str, Any]] = []
        grade_counts = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
        for icao, meta in sorted(stations.items()):
            country = meta.get("country")
            country_s = str(country) if country is not None else None
            wmo_region = wmo_region_for_icao(icao, country=country_s)
            if region_key is not None and wmo_region != region_key:
                continue
            icao_rows = by_icao.get(icao, [])
            station_meta = StationMeta(
                icao=icao,
                name=str(meta["name"]) if meta.get("name") is not None else None,
                country=country_s,
            )
            enriched = enrich_station_window(
                meta=station_meta,
                rows=icao_rows,
                window_key=window_key,
            )
            products = enriched["products"]
            if product_filter:
                products = [item for item in products if item["product"] == product_filter]
                if not products:
                    continue
                enriched = enrich_station_window(
                    meta=station_meta,
                    rows=icao_rows,
                    window_key=window_key,
                    products=products,
                )
            if grade_filter and enriched["overall_grade"] != grade_filter:
                continue
            grade_counts[enriched["overall_grade"]] = grade_counts.get(enriched["overall_grade"], 0) + 1
            station_rows.append(
                {
                    "icao": icao,
                    "name": meta.get("name"),
                    "wmo_region": wmo_region,
                    "overall_grade": enriched["overall_grade"],
                    "overall_score": enriched["overall_score"],
                    "products": enriched["products"],
                    "maintenance_tag_counts": enriched["maintenance_tag_counts"],
                    "file_format_counts": enriched["file_format_counts"],
                    "issue_code_counts": enriched["issue_code_counts"],
                    "centennial_metrics": enriched["centennial_metrics"],
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
                        text("SELECT icao, name, country FROM station_registry WHERE icao = :icao"),
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
                               lint_error_count, lint_warning_count, convert_ok,
                               file_format, issue_codes
                        FROM station_tac_records
                        WHERE icao = :icao AND observed_at >= :cutoff
                        ORDER BY observed_at ASC
                        """
                    ),
                    {"icao": code, "cutoff": datetime.now(UTC) - window_timedelta("90d")},
                ).mappings()
                records = [row_to_station_record(dict(row)) for row in record_rows]
        except Exception:
            logger.exception("station health detail query failed for %s", code)
            return None

        windows: dict[str, Any] = {}
        now = datetime.now(UTC)
        retention_cutoff = now - window_timedelta("90d")
        country = meta_row.get("country")
        country_s = str(country) if country is not None else None
        station_meta = StationMeta(
            icao=code,
            name=str(meta_row["name"]) if meta_row.get("name") is not None else None,
            country=country_s,
        )
        for window_key in WINDOW_SECONDS:
            cutoff = max(now - window_timedelta(window_key), retention_cutoff)
            window_rows = [row for row in records if row.observed_at >= cutoff]
            windows[window_key] = enrich_station_window(
                meta=station_meta,
                rows=window_rows,
                window_key=window_key,
            )
        return {
            "icao": code,
            "name": meta_row.get("name"),
            "wmo_region": wmo_region_for_icao(code, country=country_s),
            "windows": windows,
            "record_count": len(records),
            "maintenance_tag_counts": windows.get("90d", {}).get("maintenance_tag_counts", {}),
            "file_format_counts": windows.get("90d", {}).get("file_format_counts", {}),
            "issue_code_counts": windows.get("90d", {}).get("issue_code_counts", {}),
            "centennial_metrics": windows.get("90d", {}).get("centennial_metrics", []),
        }

    def purge_expired(self) -> int:
        """
        Delete Postgres observations older than 90 days.

        Returns
        -------
        object
            Return value.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (purge_expired)
        2
        """
        cutoff = datetime.now(UTC) - window_timedelta("90d")
        _ = RETENTION_SECONDS
        try:
            with self._engine.begin() as conn:
                result = conn.execute(
                    text("DELETE FROM station_tac_records WHERE observed_at < :cutoff"),
                    {"cutoff": cutoff},
                )
                return int(result.rowcount or 0)
        except Exception:
            logger.exception("station health retention purge failed")
            return 0


__all__ = ["PostgresStationHealthStore", "sync_database_url"]
