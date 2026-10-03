"""In-process cache of the last three live TAC reports per place.

The refresh stores feed text. It does not convert TAC to IWXXM. One API
replica shares this cache. A second refresh is skipped while one is running.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import UTC, datetime
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
)

_KEEP = 3


@dataclass(frozen=True)
class LiveMapReport:
    """One stored observation."""

    place_key: str
    product: str
    observed_at: datetime
    tac: str
    latitude: float | None
    longitude: float | None


def _stamp(value: datetime) -> str:
    """Store a timezone-aware time as UTC text so order matches the clock."""
    if value.tzinfo is None:
        raise ValueError("observed_at needs a timezone")
    return value.astimezone(UTC).isoformat()


class _ReportJson(TypedDict):
    observed_at: str
    tac: str


class _PlaceJson(TypedDict):
    place_key: str
    product: str
    latitude: float
    longitude: float
    reports: list[_ReportJson]


class LiveMapCache:
    """Last three reports per place and product."""

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
        """Return False when a refresh is already running."""
        if self._refreshing:
            return False
        self._refreshing = True
        return True

    def end_refresh(self) -> None:
        """Allow the next refresh."""
        self._refreshing = False

    def store(self, report: LiveMapReport) -> None:
        """Keep the newest three observations for this place and product."""
        stamp = _stamp(report.observed_at)
        with self._engine.begin() as conn:
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

    def query(
        self,
        *,
        west: float,
        south: float,
        east: float,
        north: float,
        products: set[str],
    ) -> list[_PlaceJson]:
        """Return up to three reports for each place inside the box."""
        if not products:
            return []
        with self._engine.connect() as conn:
            rows = conn.execute(
                select(
                    _place_key,
                    _product,
                    _observed_at,
                    _tac,
                    _latitude,
                    _longitude,
                )
                .where(
                    _product.in_(products),
                    _latitude.is_not(None),
                    _longitude.is_not(None),
                    _latitude >= south,
                    _latitude <= north,
                    _longitude >= west,
                    _longitude <= east,
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
                    "reports": bucket,
                }
            else:
                bucket = current["reports"]
            if len(bucket) < _KEEP:
                bucket.append({"observed_at": str(row.observed_at), "tac": str(row.tac)})
        return list(grouped.values())


def apply_refresh(cache: LiveMapCache, reports: list[LiveMapReport]) -> str:
    """
    Store reports unless a refresh is already running.

    Returns
    -------
    str
        ``stored`` or ``skipped``.
    """
    if not cache.begin_refresh():
        return "skipped"
    try:
        for report in reports:
            cache.store(report)
    finally:
        cache.end_refresh()
    return "stored"


def engine_for_url(url: str | None) -> Engine:
    """Use one shared in-memory database when no URL is configured."""
    raw = (url or "").strip()
    if not raw:
        return create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    return create_engine(raw)


def cache_from_env() -> LiveMapCache:
    """Open the cache from ``LIVE_MAP_CACHE_URL``, or memory when unset."""
    return LiveMapCache(engine_for_url(os.getenv("LIVE_MAP_CACHE_URL")))
