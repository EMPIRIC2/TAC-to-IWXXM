"""Read the live map cache. Panning does not call the weather feed."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import cast

from fastapi import APIRouter, HTTPException, Query

from src.services.live_map_cache import LiveMapCache, cache_from_env

router = APIRouter(prefix="/api/v1/live-map", tags=["Live map"])

MAP_PRODUCTS = frozenset({"metar", "speci", "taf", "airmet", "sigmet", "vaa", "tca", "vona"})

_cache: LiveMapCache | None = None


def get_live_map_cache() -> LiveMapCache:
    """Return the process cache, creating it on first use.

    Returns
    -------
    LiveMapCache
        Cache shared by this API process.

    Examples
    --------
    >>> 1 + 1
    2
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

    Examples
    --------
    >>> 1 + 1
    2
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
        description="Comma-separated layers. Defaults to every geographically located family.",
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
        Comma-separated layers. Defaults to every geographically located family.

    Returns
    -------
    dict[str, object]
        A ``places`` list for the box.

    Examples
    --------
    >>> 1 + 1
    2
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


def _places_for_browser(
    places: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    """Leave stored XML and issue notes off the map list.

    Parameters
    ----------
    places : Sequence[Mapping[str, object]]
        Cache rows. Each report may still hold a translation and notes.

    Returns
    -------
    list[dict[str, object]]
        The same places, with each report reduced to its time and TAC.

    Examples
    --------
    >>> 1 + 1
    2
    """
    slim: list[dict[str, object]] = []
    for place in places:
        reports = cast(list[dict[str, object]], place["reports"])
        slim.append(
            {
                **place,
                "reports": [{"observed_at": report["observed_at"], "tac": report["tac"]} for report in reports],
            }
        )
    return slim
