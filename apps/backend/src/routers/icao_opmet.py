"""
ICAO OPMET Translation Statistics Router.

Implements REST API endpoints for querying translation centre statistics
as per ICAO Doc 10003 Section 7 requirements.
"""

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from ..config.icao_opmet import (
    SUPPORTED_IWXXM_VERSIONS,
    get_icao_region,
    get_translation_centre_info,
)
from ..schemas.icao_opmet import (
    ICAORegion,
    TranslationCentreInfo,
    TranslationStatistics,
    TranslationStatisticsRequest,
)
from ..services.statistics import statistics_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/translation", tags=["ICAO OPMET Statistics"])


@router.get("/centre-info", response_model=TranslationCentreInfo, summary="Translation centre information")
async def get_centre_info() -> TranslationCentreInfo:
    """
    Return this translation centre's name, designator, location, supported IWXXM versions, and products.

    No login is required.


    Returns
    -------
    object
        Return value.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_centre_info)
    2
    """
    info = get_translation_centre_info()

    # Parse online_since date if provided
    online_since = None
    if info.get("serviceOnlineSince"):
        online_since = datetime.fromisoformat(info["serviceOnlineSince"].replace("Z", "+00:00"))

    return TranslationCentreInfo(
        centre_name=info["translationCentreName"],
        centre_designator=info["translationCentreDesignator"],
        icao_location_indicator=info["icaoLocationIndicator"],
        supported_iwxxm_versions=info["supportedIwxxmVersions"],
        supported_products=info["supportedProducts"],
        online_since=online_since,
        contact_email=info.get("technicalContact"),
    )


@router.post("/statistics", response_model=TranslationStatistics, summary="Translation statistics")
async def get_translation_statistics(
    request: TranslationStatisticsRequest,
) -> object:
    """
    Return aggregated translation statistics for a time range.

    Optional filters are ICAO region, IWXXM version, and airport. No login is required.


    Parameters
    ----------
    request : object
        Argument ``request``.

    Returns
    -------
    object
        Return value.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_translation_statistics)
    2
    """
    # Validate date range
    if request.end_date < request.start_date:
        raise HTTPException(status_code=400, detail="end_date must be after start_date")

    # Validate date range is not too large (prevent expensive queries)
    max_range_days = 90
    date_diff = (request.end_date - request.start_date).days
    if date_diff > max_range_days:
        raise HTTPException(
            status_code=400, detail=f"Date range cannot exceed {max_range_days} days. Requested: {date_diff} days"
        )

    # Query statistics from database
    logger.info(
        f"Statistics query: {request.start_date} to {request.end_date}, "
        f"region={request.icao_region}, version={request.iwxxm_version}"
    )

    stats_data = await statistics_service.get_statistics(
        start_date=request.start_date,
        end_date=request.end_date,
        icao_region=request.icao_region.value if request.icao_region else None,
        iwxxm_version=request.iwxxm_version,
        airport_code=request.airport_code,
        include_airport_breakdown=request.include_airport_breakdown,
        include_error_details=request.include_error_details,
    )

    return TranslationStatistics(**stats_data)


@router.get("/statistics/recent", response_model=TranslationStatistics, summary="Recent translation statistics")
async def get_recent_statistics(
    hours: int = Query(24, ge=1, le=168, description="Number of hours to query (1-168)"),
    icao_region: ICAORegion | None = Query(None, description="Filter by ICAO region"),
    iwxxm_version: str | None = Query(None, description="Filter by IWXXM version"),
) -> object:
    """
    Return translation statistics for the last N hours.

    No login is required.


    Parameters
    ----------
    hours : object
        Argument ``hours``.
    icao_region : object
        Argument ``icao_region``.
    iwxxm_version : object
        Argument ``iwxxm_version``.

    Returns
    -------
    object
        Return value.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_recent_statistics)
    2
    """
    end_date = datetime.now(UTC).replace(tzinfo=None)
    start_date = end_date - timedelta(hours=hours)

    # Validate date range is not too large (prevent expensive queries)
    max_range_days = 90
    date_diff = (end_date - start_date).days
    if date_diff > max_range_days:
        raise HTTPException(
            status_code=400, detail=f"Date range cannot exceed {max_range_days} days. Requested: {date_diff} days"
        )

    # Query statistics from database
    logger.info(f"Recent statistics query: last {hours} hours")

    stats_data = await statistics_service.get_statistics(
        start_date=start_date,
        end_date=end_date,
        icao_region=icao_region.value if icao_region else None,
        iwxxm_version=iwxxm_version,
        airport_code=None,
        include_airport_breakdown=False,
        include_error_details=False,
    )

    return TranslationStatistics(**stats_data)


@router.get("/statistics/by-region", response_model=dict, summary="Translation statistics by ICAO region")
async def get_statistics_by_region(
    start_date: datetime = Query(..., description="Statistics period start (ISO 8601)"),
    end_date: datetime = Query(..., description="Statistics period end (ISO 8601)"),
) -> object:
    """
    Return translation counts grouped by ICAO region for a time range.

    No login is required.


    Parameters
    ----------
    start_date : object
        Argument ``start_date``.
    end_date : object
        Argument ``end_date``.

    Returns
    -------
    object
        Return value.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_statistics_by_region)
    2
    """
    # Query region-grouped statistics from database
    logger.info(f"Region statistics query: {start_date} to {end_date}")

    return await statistics_service.get_statistics_by_region(
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/airport-region/{airport_code}", summary="ICAO region for an airport")
async def get_airport_region(airport_code: str) -> dict[str, Any]:
    """
    Return the ICAO region for a four-letter airport code.

    No login is required.


    Parameters
    ----------
    airport_code : object
        Argument ``airport_code``.

    Returns
    -------
    object
        Return value.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_airport_region)
    2
    """
    try:
        region = get_icao_region(airport_code)
        region_names = {
            "AFI": "Africa-Indian Ocean",
            "APAC": "Asia Pacific",
            "EUR": "European",
            "MID": "Middle East",
            "NAM": "North American",
            "SAM": "South American",
            "NAT": "North Atlantic",
            "WAFR": "West African",
            "ESAF": "Eastern and Southern African",
        }

        return {
            "airport_code": airport_code.upper(),
            "icao_region": region,
            "region_name": region_names.get(region, "Unknown"),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


# =============================================================================
# Health and Status Endpoints
# =============================================================================


@router.get("/health", summary="Translation statistics health")
async def statistics_health() -> object:
    """
    Return translation statistics service status.

    No login is required.


    Returns
    -------
    object
        Return value.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (statistics_health)
    2
    """
    from ..config.icao_opmet import (
        ENABLE_STATISTICS,
        ENABLE_WEBHOOKS,
        STATISTICS_RETENTION_DAYS,
    )

    return {
        "service": "translation-statistics",
        "status": "healthy",
        "statistics_enabled": ENABLE_STATISTICS,
        "webhook_enabled": ENABLE_WEBHOOKS,
        "retention_policy": "indefinite" if STATISTICS_RETENTION_DAYS is None else f"{STATISTICS_RETENTION_DAYS} days",
        "supported_regions": [region.value for region in ICAORegion],
        "supported_versions": SUPPORTED_IWXXM_VERSIONS,
    }
