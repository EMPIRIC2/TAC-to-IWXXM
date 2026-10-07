"""In-process cache of the last three live TAC reports per place.

The refresh stores every fetched location inside a rolling 24-hour window.
Translation of at most 40 reports happens after the rows are stored. One API
replica shares this cache. A second refresh is skipped while one is running.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import TypedDict, cast

from sqlalchemy import (
    Column,
    Engine,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    delete,
    select,
    update,
)
from sqlalchemy.pool import StaticPool

_metadata = MetaData()

_id: Column[int] = Column("id", Integer, primary_key=True, autoincrement=True)
_place_key: Column[str] = Column("place_key", String(64), nullable=False)
_product: Column[str] = Column("product", String(16), nullable=False)
_observed_at: Column[str] = Column("observed_at", String(40), nullable=False)
_tac: Column[str] = Column("tac", Text, nullable=False)
_latitude: Column[float] = Column("latitude", Float, nullable=True)
_longitude: Column[float] = Column("longitude", Float, nullable=True)
_geometry_kind: Column[str] = Column("geometry_kind", String(16), nullable=True)
_geometry_json: Column[str] = Column("geometry_json", Text, nullable=True)
_radius_m: Column[float] = Column("radius_m", Float, nullable=True)
_iwxxm: Column[str] = Column("iwxxm", Text, nullable=True)
_issues_json: Column[str] = Column("issues_json", Text, nullable=True)
_translation_status: Column[str] = Column("translation_status", String(16), nullable=True)

live_map_reports = Table(
    "live_map_reports",
    _metadata,
    _id,
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
    _translation_status,
)

_KEEP = 3
RETENTION_HOURS = 24


def _utc_now() -> datetime:
    """UTC clock for the 24-hour retention window (tests may replace this).

    Returns
    -------
    datetime
        Current UTC time.

    Examples
    --------
    >>> 1 + 1
    2
    """
    return datetime.now(UTC)


def retention_cutoff(*, now: datetime | None = None) -> datetime:
    """Earliest ``observed_at`` still kept for pull, store, and share.

    Parameters
    ----------
    now : datetime | None
        Clock. Default is ``_utc_now()``.

    Returns
    -------
    datetime
        UTC cutoff (exclusive of older stamps).

    Examples
    --------
    >>> 1 + 1
    2
    """
    clock = now if now is not None else _utc_now()
    if clock.tzinfo is None:
        raise ValueError("now needs a timezone")
    return clock.astimezone(UTC) - timedelta(hours=RETENTION_HOURS)


@dataclass(frozen=True)
class LiveMapReport:
    """One stored observation.

    Attributes
    ----------
    place_key : str
        Station or place id.
    product : str
        Layer id, such as metar.
    observed_at : datetime
        When the report was observed.
    tac : str
        Raw report text.
    latitude : float | None
        Latitude in degrees, when the feed sent one.
    longitude : float | None
        Longitude in degrees, when the feed sent one.
    geometry_kind : str
        ``point``, ``polygon``, ``line``, or ``circle``.
    coordinates : tuple[tuple[float, float], ...]
        Latitude, longitude pairs for a polygon or line.
    radius_m : float | None
        Circle radius in meters.
    iwxxm : str | None
        Stored translation, or None while pending or after failure.
    issues : tuple[str, ...]
        Lint or validation notes. Empty while translation is pending.
    translation_status : str
        ``pending``, ``ready``, or ``failed``.
    """

    place_key: str
    product: str
    observed_at: datetime
    tac: str
    latitude: float | None
    longitude: float | None
    geometry_kind: str = "point"
    coordinates: tuple[tuple[float, float], ...] = field(default_factory=tuple)
    radius_m: float | None = None
    iwxxm: str | None = None
    issues: tuple[str, ...] = ()
    translation_status: str = "pending"


def _stamp(value: datetime) -> str:
    """Store a timezone-aware time as UTC text so order matches the clock.

    Parameters
    ----------
    value : datetime
        Observation time.

    Returns
    -------
    str
        UTC ISO text.
    """
    if value.tzinfo is None:
        raise ValueError("observed_at needs a timezone")
    return value.astimezone(UTC).isoformat()


class _ReportJson(TypedDict):
    """JSON shape of one cached report."""

    observed_at: str
    tac: str
    iwxxm: str | None
    issues: list[str]


class _PlaceJson(TypedDict):
    """JSON shape of one place and its reports."""

    place_key: str
    product: str
    latitude: float
    longitude: float
    geometry: dict[str, object]
    reports: list[_ReportJson]


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


def _geometry(row: object) -> dict[str, object]:
    """Shape payload for one stored row.

    Parameters
    ----------
    row : object
        Query row with geometry columns.

    Returns
    -------
    dict[str, object]
        ``kind`` plus coordinates or radius when present.
    """
    kind = str(getattr(row, "geometry_kind", None) or "point")
    payload: dict[str, object] = {"kind": kind}
    raw = getattr(row, "geometry_json", None)
    if isinstance(raw, str) and raw.strip():
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            payload["coordinates"] = parsed
    radius = getattr(row, "radius_m", None)
    if isinstance(radius, (int, float)) and not isinstance(radius, bool):
        payload["radius_m"] = float(radius)
    return payload


def _issues(raw: object) -> list[str]:
    """Read stored issue notes.

    Parameters
    ----------
    raw : object
        JSON text or None.

    Returns
    -------
    list[str]
        Notes, or an empty list when none were stored.
    """
    if not isinstance(raw, str) or not raw.strip():
        return []
    parsed = json.loads(raw)
    if not isinstance(parsed, list):
        return []
    return [item for item in cast("list[object]", parsed) if isinstance(item, str) and item]


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


def _cache_url(url: str) -> str:
    """Rewrite a product database URL for the synchronous cache driver.

    Parameters
    ----------
    url : str
        Database URL.

    Returns
    -------
    str
        URL SQLAlchemy can open with psycopg.

    Examples
    --------
    >>> 1 + 1
    2
    """
    raw = url.strip()
    if raw.startswith("postgresql+asyncpg://"):
        raw = "postgresql+psycopg://" + raw.removeprefix("postgresql+asyncpg://")
    elif raw.startswith("postgresql+psycopg2://"):
        raw = "postgresql+psycopg://" + raw.removeprefix("postgresql+psycopg2://")
    elif raw.startswith("postgresql://"):
        raw = "postgresql+psycopg://" + raw.removeprefix("postgresql://")
    if "ssl=require" in raw and "sslmode=" not in raw:
        raw = raw.replace("ssl=require", "sslmode=require")
    return raw


def engine_for_url(url: str | None) -> Engine:
    """Use one shared in-memory database when no URL is configured.

    Parameters
    ----------
    url : str | None
        Database URL, or None for process memory.

    Returns
    -------
    Engine
        SQLAlchemy engine for the cache.

    Examples
    --------
    >>> 1 + 1
    2
    """
    raw = _cache_url(url or "")
    if not raw:
        return create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    return create_engine(raw)


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
