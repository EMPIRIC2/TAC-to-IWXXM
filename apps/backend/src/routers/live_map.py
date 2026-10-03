"""Read the live map cache. Panning does not call the weather feed."""

from __future__ import annotations

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


@router.get("")
def read_live_map(
    west: float = Query(..., description="West edge of the view, in degrees."),
    south: float = Query(..., description="South edge of the view, in degrees."),
    east: float = Query(..., description="East edge of the view, in degrees."),
    north: float = Query(..., description="North edge of the view, in degrees."),
    products: str = Query(
        "metar,speci",
        description="Comma-separated layers. Defaults to METAR and SPECI.",
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
        Comma-separated layers. Defaults to METAR and SPECI.

    Returns
    -------
    dict[str, object]
        A ``places`` list for the box.

    Examples
    --------
    >>> 1 + 1
    2
    """
    if west < -180 or east > 180 or south < -90 or north > 90 or west >= east or south >= north:
        raise HTTPException(
            status_code=400,
            detail="The map view needs a west, south, east, and north edge, with west left of east.",
        )
    selected = {part.strip().lower() for part in products.split(",") if part.strip()}
    if not selected:
        selected = {"metar", "speci"}
    unknown = selected - MAP_PRODUCTS
    if unknown:
        raise HTTPException(
            status_code=400,
            detail="Choose map layers from METAR, SPECI, TAF, AIRMET, SIGMET, or an advisory.",
        )
    return {
        "places": get_live_map_cache().query(
            west=west,
            south=south,
            east=east,
            north=north,
            products=selected,
        )
    }
