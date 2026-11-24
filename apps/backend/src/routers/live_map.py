"""Read the live map cache. Panning does not call the weather feed."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import cast

from fastapi import APIRouter, HTTPException, Query, status

from src.services.live_map_cache import LiveMapCache, cache_from_env
from src.services.live_map_eval import compute_and_store, refresh_enabled
from src.services.live_map_eval_store import get_live_map_eval_store

router = APIRouter(prefix="/api/v1/live-map", tags=["Live map"])

# FR-013 / DI-016: G-AIRMET layer removed from live map.
MAP_PRODUCTS = frozenset({"metar", "speci", "taf", "airmet", "sigmet", "vaa", "tca", "vona"})

_cache: LiveMapCache | None = None


def get_live_map_cache() -> LiveMapCache:
    """Return the process cache, creating it on first use.

    Returns
    -------
    LiveMapCache
        Cache shared by this API process.
    """
    global _cache
    if _cache is None:
        _cache = cache_from_env()
    return _cache


def set_live_map_cache(cache: LiveMapCache | None) -> None:
    """Replace the process cache. Tests pass None to clear it.

    Parameters
    ----------
    cache : LiveMapCache | None
        Cache to use, or None to clear it.
    """
    global _cache
    _cache = cache


@router.get(
    "",
    summary="Cached reports in the current map view",
    description="Reports cached for the area in view. The newest report is first. At most two earlier reports follow it.",
)
def read_live_map(
    west: float = Query(..., description="West edge of the view, in degrees."),
    south: float = Query(..., description="South edge of the view, in degrees."),
    east: float = Query(..., description="East edge of the view, in degrees."),
    north: float = Query(..., description="North edge of the view, in degrees."),
    products: str = Query(
        "metar,speci,taf,airmet,sigmet,vaa,tca,vona",
        description="Comma-separated product ids. Defaults to every geographically located product.",
    ),
) -> dict[str, object]:
    """Reports cached for the area in view.

    The newest report is first. At most two earlier reports follow it.


    Parameters
    ----------
    west : float
        West edge of the view, in degrees.
    south : float
        South edge of the view, in degrees.
    east : float
        East edge of the view, in degrees.
    north : float
        North edge of the view, in degrees.
    products : str
        Comma-separated product ids. Defaults to every geographically located product.

    Returns
    -------
    dict[str, object]
        A ``places`` list for the box.
    """
    south = min(90.0, max(-90.0, south))
    north = min(90.0, max(-90.0, north))
    if south >= north:
        raise HTTPException(
            status_code=400,
            detail="The map view needs a west, south, east, and north edge, with west left of east.",
        )
    # Leaflet reports a world view with longitudes outside -180..180.
    if west < -180 or east > 180 or east - west >= 360:
        west, east = -180.0, 180.0
    elif west >= east:
        raise HTTPException(
            status_code=400,
            detail="The map view needs a west, south, east, and north edge, with west left of east.",
        )
    selected = {part.strip().lower() for part in products.split(",") if part.strip()}
    if not selected:
        selected = set(MAP_PRODUCTS)
    unknown = selected - MAP_PRODUCTS
    if unknown:
        raise HTTPException(
            status_code=400,
            detail="Choose map layers from METAR, SPECI, TAF, AIRMET, SIGMET, or an advisory.",
        )
    return {
        "places": _places_for_browser(
            get_live_map_cache().query(
                west=west,
                south=south,
                east=east,
                north=north,
                products=selected,
            )
        ),
        "space_weather": [],
    }


@router.get(
    "/eval",
    summary="Latest live-map evaluation snapshot",
    description=(
        "Aggregate decode/lint/convert/IWXXM counts from the last cron refresh "
        "(about every 15 minutes). Empty cache returns zeros."
    ),
)
def read_live_map_eval() -> dict[str, object]:
    """Return the latest FR-045 evaluation snapshot."""
    return cast(dict[str, object], get_live_map_eval_store().read_latest())


@router.post(
    "/eval/refresh",
    summary="Refresh live-map evaluation snapshot",
    description="Same work as the cron job. Disabled unless LIVE_MAP_EVAL_REFRESH_ENABLED is set.",
)
def refresh_live_map_eval() -> dict[str, object]:
    """Compute and store a fresh snapshot when enabled."""
    if not refresh_enabled():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found",
        )
    return cast(dict[str, object], compute_and_store())


def _places_for_browser(
    places: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    """Leave stored XML and issue notes off the map list.

    Each report keeps ``observed_at`` and ``tac``. When the cache row already
    carries ``valid_from`` / ``valid_to``, those stamps are passed through for
    the Active reports filter on Decode visuals.

    Parameters
    ----------
    places : Sequence[Mapping[str, object]]
        Cache rows. Each report may still hold a translation and notes.

    Returns
    -------
    list[dict[str, object]]
        The same places, with each report reduced to time, TAC, and optional
        validity stamps.
    """
    slim: list[dict[str, object]] = []
    for place in places:
        reports = cast(list[dict[str, object]], place["reports"])
        slim_reports: list[dict[str, object]] = []
        for report in reports:
            row: dict[str, object] = {
                "observed_at": report["observed_at"],
                "tac": report["tac"],
            }
            valid_from = report.get("valid_from")
            valid_to = report.get("valid_to")
            if isinstance(valid_from, str) and valid_from.strip():
                row["valid_from"] = valid_from
            if isinstance(valid_to, str) and valid_to.strip():
                row["valid_to"] = valid_to
            slim_reports.append(row)
        slim.append({**place, "reports": slim_reports})
    return slim
