"""List-row helpers for the in-memory station health store (F39)."""

from __future__ import annotations

from typing import Any

from src.services.station_health_aggregate import enrich_station_window
from src.services.station_health_types import StationMeta, StationRecord
from src.services.station_health_wmo_region import wmo_region_for_icao


def region_filter_key(region: str | None) -> str | None:
    """
    Normalize an optional WMO region filter to a store key.

    Parameters
    ----------
    region : str | None
        Raw region filter from the list API.

    Returns
    -------
    str | None
        Canonical filter key, or ``None`` when unset.

    Examples
    --------
    >>> region_filter_key('iv')
    'IV'
    >>> region_filter_key('unknown')
    'unknown'
    >>> region_filter_key(None) is None
    True
    """
    if not region:
        return None
    region_filter = region.strip().lower()
    if region_filter == "unknown":
        return "unknown"
    return region.strip().upper()


def station_list_row(
    *,
    icao: str,
    meta: StationMeta,
    icao_rows: list[StationRecord],
    window_key: str,
    product_filter: str | None,
    grade_filter: str | None,
) -> dict[str, Any] | None:
    """
    Build one list-row dict, or ``None`` when filters exclude the station.

    Parameters
    ----------
    icao : str
        Station ICAO.
    meta : StationMeta
        Registry metadata.
    icao_rows : list[StationRecord]
        Windowed observations for the station.
    window_key : str
        Availability window id.
    product_filter : str | None
        Optional product filter.
    grade_filter : str | None
        Optional letter-grade filter.

    Returns
    -------
    dict[str, Any] | None
        Public list row, or ``None`` when filtered out.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (station_list_row)
    2
    """
    wmo_region = wmo_region_for_icao(icao, country=meta.country)
    enriched = enrich_station_window(
        meta=meta,
        rows=icao_rows,
        window_key=window_key,
    )
    products = enriched["products"]
    if product_filter:
        products = [item for item in products if item["product"] == product_filter]
        if not products:
            return None
        enriched = enrich_station_window(
            meta=meta,
            rows=icao_rows,
            window_key=window_key,
            products=products,
        )
    if grade_filter and enriched["overall_grade"] != grade_filter:
        return None
    return {
        "icao": icao,
        "name": meta.name,
        "wmo_region": wmo_region,
        "overall_grade": enriched["overall_grade"],
        "overall_score": enriched["overall_score"],
        "products": enriched["products"],
        "maintenance_tag_counts": enriched["maintenance_tag_counts"],
        "file_format_counts": enriched["file_format_counts"],
        "issue_code_counts": enriched["issue_code_counts"],
        "centennial_metrics": enriched["centennial_metrics"],
    }


__all__ = ["region_filter_key", "station_list_row"]
