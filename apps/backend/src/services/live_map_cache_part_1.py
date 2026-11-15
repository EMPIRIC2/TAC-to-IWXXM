"""Part 1 of ``live_map_cache.py`` (line-cap split)."""

from __future__ import annotations

import json
from dataclasses import field
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
