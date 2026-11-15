"""Part 2 of ``live_map_cache.py`` (line-cap split)."""

from __future__ import annotations

import json
import os
from datetime import UTC
from typing import cast

from sqlalchemy import (
    Engine,
    delete,
    select,
    update,
)

from src.services.live_map_cache_part_1 import (
    _KEEP,
    LiveMapReport,
    _geometry,
    _geometry_json,
    _geometry_kind,
    _id,
    _issues,
    _issues_json,
    _iwxxm,
    _latitude,
    _longitude,
    _metadata,
    _observed_at,
    _place_key,
    _PlaceJson,
    _product,
    _radius_m,
    _ReportJson,
    _stamp,
    _tac,
    _translation_status,
    engine_for_url,
    live_map_reports,
    retention_cutoff,
)


class LiveMapCache:
    """Last three reports per place and product.

    Attributes
    ----------
    _engine : Engine
        Database that holds the rows.
    _refreshing : bool
        True while a refresh holds the cache.
    """

    def __init__(self, engine: Engine) -> None:
        """
        Open a cache on an existing engine.

        Parameters
        ----------
        engine : Engine
            SQLite for the API process, or the product database when configured.
        """
        self._engine = engine
        self._refreshing = False
        if engine.dialect.name == "sqlite":
            _metadata.create_all(engine)

    def begin_refresh(self) -> bool:
        """Return False when a refresh is already running.

        Returns
        -------
        bool
            False when a refresh is already running.

        Examples
        --------
        >>> 1 + 1
        2
        """
        if self._refreshing:
            return False
        self._refreshing = True
        return True

    def end_refresh(self) -> None:
        """Allow the next refresh.

        Examples
        --------
        >>> 1 + 1
        2
        """
        self._refreshing = False

    def status_of(self, report: LiveMapReport) -> str | None:
        """Return the stored translation status for one report.

        Parameters
        ----------
        report : LiveMapReport
            Report to look up.

        Returns
        -------
        str | None
            ``pending``, ``ready``, ``failed``, or None when the row is absent.

        Examples
        --------
        >>> 1 + 1
        2
        """
        with self._engine.connect() as conn:
            row = conn.execute(
                select(_translation_status).where(
                    _place_key == report.place_key,
                    _product == report.product,
                    _observed_at == _stamp(report.observed_at),
                )
            ).first()
        if row is None or row[0] is None:
            return None
        return str(row[0])

    def store(self, report: LiveMapReport) -> None:
        """Keep the newest three in-window observations for this place and product.

        Reports older than :data:`RETENTION_HOURS` are ignored. A successful
        write also deletes any stored rows outside that window.

        Parameters
        ----------
        report : LiveMapReport
            Observation to keep.

        Examples
        --------
        >>> 1 + 1
        2
        """
        if report.observed_at.astimezone(UTC) < retention_cutoff():
            return
        stamp = _stamp(report.observed_at)
        cutoff_stamp = _stamp(retention_cutoff())
        with self._engine.begin() as conn:
            existing = conn.execute(
                select(_tac, _iwxxm, _issues_json, _translation_status).where(
                    _place_key == report.place_key,
                    _product == report.product,
                    _observed_at == stamp,
                )
            ).first()
            kept_iwxxm = report.iwxxm
            kept_issues = json.dumps(list(report.issues))
            kept_status = report.translation_status
            if (
                existing is not None
                and existing[0] == report.tac
                and existing[3] == "ready"
                and report.translation_status == "pending"
            ):
                kept_iwxxm = existing[1] if isinstance(existing[1], str) else None
                kept_issues = existing[2] if isinstance(existing[2], str) else "[]"
                kept_status = "ready"
            conn.execute(
                delete(live_map_reports).where(
                    _place_key == report.place_key,
                    _product == report.product,
                    _observed_at == stamp,
                )
            )
            conn.execute(
                live_map_reports.insert().values(
                    place_key=report.place_key,
                    product=report.product,
                    observed_at=stamp,
                    tac=report.tac,
                    latitude=report.latitude,
                    longitude=report.longitude,
                    geometry_kind=report.geometry_kind,
                    geometry_json=json.dumps(report.coordinates) if report.coordinates else None,
                    radius_m=report.radius_m,
                    iwxxm=kept_iwxxm,
                    issues_json=kept_issues,
                    translation_status=kept_status,
                )
            )
            ids = conn.execute(
                select(_id)
                .where(
                    _place_key == report.place_key,
                    _product == report.product,
                )
                .order_by(_observed_at.desc())
            ).all()
            extra = [row[0] for row in ids[_KEEP:]]
            if extra:
                conn.execute(delete(live_map_reports).where(_id.in_(extra)))
            conn.execute(delete(live_map_reports).where(_observed_at < cutoff_stamp))

    def set_translation(
        self,
        report: LiveMapReport,
        iwxxm: str | None,
        issues: list[str],
        status: str,
    ) -> None:
        """Record a translation result for one stored report.

        Parameters
        ----------
        report : LiveMapReport
            Report that was translated.
        iwxxm : str | None
            XML, or None when translation failed.
        issues : list[str]
            Notes for the operator. Empty while the report is still pending.
        status : str
            ``ready`` or ``failed``.

        Examples
        --------
        >>> 1 + 1
        2
        """
        with self._engine.begin() as conn:
            conn.execute(
                update(live_map_reports)
                .where(
                    _place_key == report.place_key,
                    _product == report.product,
                    _observed_at == _stamp(report.observed_at),
                )
                .values(
                    iwxxm=iwxxm,
                    issues_json=json.dumps(issues),
                    translation_status=status,
                )
            )

    def query(
        self,
        *,
        west: float,
        south: float,
        east: float,
        north: float,
        products: set[str],
    ) -> list[_PlaceJson]:
        """Return up to three in-window reports for each place inside the box.

        Parameters
        ----------
        west : float
            West edge in degrees.
        south : float
            South edge in degrees.
        east : float
            East edge in degrees.
        north : float
            North edge in degrees.
        products : set[str]
            Layer ids to include.

        Returns
        -------
        list[_PlaceJson]
            Places inside the box, newest report first. Reports older than
            :data:`RETENTION_HOURS` are omitted.

        Examples
        --------
        >>> 1 + 1
        2
        """
        if not products:
            return []
        cutoff_stamp = _stamp(retention_cutoff())
        with self._engine.connect() as conn:
            rows = conn.execute(
                select(
                    _place_key,
                    _product,
                    _observed_at,
                    _tac,
                    _latitude,
                    _longitude,
                    _geometry_kind,
                    _geometry_json,
                    _radius_m,
                    _iwxxm,
                    _issues_json,
                )
                .where(
                    _product.in_(products),
                    _latitude.is_not(None),
                    _longitude.is_not(None),
                    _latitude >= south,
                    _latitude <= north,
                    _longitude >= west,
                    _longitude <= east,
                    _observed_at >= cutoff_stamp,
                )
                .order_by(
                    _place_key,
                    _product,
                    _observed_at.desc(),
                )
            ).all()
        grouped: dict[tuple[str, str], _PlaceJson] = {}
        for row in rows:
            place_key = str(row.place_key)
            product = str(row.product)
            key = (place_key, product)
            current = grouped.get(key)
            if current is None:
                bucket: list[_ReportJson] = []
                grouped[key] = {
                    "place_key": place_key,
                    "product": product,
                    "latitude": cast(float, row.latitude),
                    "longitude": cast(float, row.longitude),
                    "geometry": _geometry(row),
                    "reports": bucket,
                }
            else:
                bucket = current["reports"]
            if len(bucket) < _KEEP:
                issues = _issues(row.issues_json)
                bucket.append(
                    {
                        "observed_at": str(row.observed_at),
                        "tac": str(row.tac),
                        "iwxxm": str(row.iwxxm) if row.iwxxm else None,
                        "issues": issues,
                    }
                )
        return list(grouped.values())


def apply_refresh(cache: LiveMapCache, reports: list[LiveMapReport]) -> str:
    """Store reports unless a refresh is already running.

    Parameters
    ----------
    cache : LiveMapCache
        Cache to write.
    reports : list[LiveMapReport]
        Observations from one tile.

    Returns
    -------
    str
        ``stored`` or ``skipped``.

    Examples
    --------
    >>> 1 + 1
    2
    """
    if not cache.begin_refresh():
        return "skipped"
    try:
        for report in reports:
            cache.store(report)
    finally:
        cache.end_refresh()
    return "stored"


def cache_from_env() -> LiveMapCache:
    """Open the cache from ``LIVE_MAP_CACHE_URL``, or memory when unset.

    Returns
    -------
    LiveMapCache
        Cache for this process.

    Examples
    --------
    >>> 1 + 1
    2
    """
    return LiveMapCache(engine_for_url(os.getenv("LIVE_MAP_CACHE_URL")))
