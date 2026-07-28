"""
ICAO OPMET Translation Statistics Router.

Implements REST API endpoints for querying translation centre statistics
as per ICAO Doc 10003 Section 7 requirements.
"""

import logging
from datetime import UTC, datetime, timedelta
from typing import Optional

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


@router.get("/centre-info", response_model=TranslationCentreInfo)
async def get_centre_info():
    """
    Get Translation Centre identification and capabilities.

    Returns metadata about this Translation Centre as per ICAO OPMET guidelines.
    This endpoint is public and does not require authentication.

    **Returns**:
    - Translation centre name and designator
    - ICAO location indicator
    - Supported IWXXM versions
    - Supported aviation product types
    - Service online date
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


@router.post("/statistics", response_model=TranslationStatistics)
async def get_translation_statistics(
    request: TranslationStatisticsRequest,
):
    """
    Query aggregated translation statistics.

    Retrieves translation centre statistics for a specified time period with optional filters.
    Implements ICAO OPMET Data Exchange Guidelines Section 7 reporting requirements.

    **Authentication**: Public (no JWT) — F21 / ADR-031.

    **Request Parameters**:
    - **start_date** (required): Statistics period start (ISO 8601)
    - **end_date** (required): Statistics period end (ISO 8601)
    - **icao_region** (optional): Filter by ICAO region (AFI, APAC, EUR, MID, NAM, SAM)
    - **iwxxm_version** (optional): Filter by IWXXM version (2025-2, 2023-1)
    - **airport_code** (optional): Filter by specific ICAO airport code
    - **include_airport_breakdown** (optional): Include per-airport statistics (default: false)
    - **include_error_details** (optional): Include detailed error analysis (default: false)

    **Returns**:
    - Aggregated translation statistics including:
      - Total, successful, and failed translation counts
      - Success rate percentage
      - Average and median processing duration
      - Breakdown by ICAO region
      - Breakdown by IWXXM version
      - Validation layer success rates
      - Optional airport-level details
      - Optional error frequency analysis

    **Example**:
    ```json
    {
        "start_date": "2026-02-01T00:00:00Z",
        "end_date": "2026-02-13T23:59:59Z",
        "icao_region": "NAM",
        "include_airport_breakdown": true
    }
    ```
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


@router.get("/statistics/recent", response_model=TranslationStatistics)
async def get_recent_statistics(
    hours: int = Query(24, ge=1, le=168, description="Number of hours to query (1-168)"),
    icao_region: Optional[ICAORegion] = Query(None, description="Filter by ICAO region"),
    iwxxm_version: Optional[str] = Query(None, description="Filter by IWXXM version"),
):
    """
    Get recent translation statistics (last N hours).

    Convenience endpoint for querying recent activity without specifying exact dates.

    **Authentication**: Public (no JWT) — F21 / ADR-031.

    **Query Parameters**:
    - **hours**: Number of hours to look back (1-168, default: 24)
    - **icao_region**: Optional ICAO region filter
    - **iwxxm_version**: Optional IWXXM version filter

    **Returns**:
    Aggregated translation statistics for the specified time window.
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


@router.get("/statistics/by-region", response_model=dict)
async def get_statistics_by_region(
    start_date: datetime = Query(..., description="Statistics period start (ISO 8601)"),
    end_date: datetime = Query(..., description="Statistics period end (ISO 8601)"),
):
    """
    Get translation statistics grouped by ICAO region.

    Returns translation activity summary for all ICAO regions.
    Useful for identifying regional distribution and capacity planning.

    **Authentication**: Public (no JWT) — F21 / ADR-031.

    **Query Parameters**:
    - **start_date**: Statistics period start (ISO 8601)
    - **end_date**: Statistics period end (ISO 8601)

    **Returns**:
    Dictionary mapping ICAO region codes to statistics:
    ```json
    {
        "NAM": {"total": 1500, "success_rate": 98.5},
        "EUR": {"total": 890, "success_rate": 97.2},
        "APAC": {"total": 456, "success_rate": 99.1}
    }
    ```
    """

    # Query region-grouped statistics from database
    logger.info(f"Region statistics query: {start_date} to {end_date}")

    return await statistics_service.get_statistics_by_region(
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/airport-region/{airport_code}")
async def get_airport_region(airport_code: str):
    """
    Determine ICAO region for a given airport code.

    Utility endpoint for testing ICAO region mapping.
    This endpoint is public and does not require authentication.

    **Path Parameters**:
    - **airport_code**: 4-letter ICAO airport identifier

    **Returns**:
    ```json
    {
        "airport_code": "KJFK",
        "icao_region": "NAM",
        "region_name": "North American"
    }
    ```

    **Example**:
    - `GET /api/v1/translation/airport-region/KJFK` → `{"icao_region": "NAM"}`
    - `GET /api/v1/translation/airport-region/EGLL` → `{"icao_region": "EUR"}`
    - `GET /api/v1/translation/airport-region/RJAA` → `{"icao_region": "APAC"}`
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
        raise HTTPException(status_code=400, detail=str(e))


# =============================================================================
# Health and Status Endpoints
# =============================================================================


@router.get("/health")
async def statistics_health():
    """
    Translation statistics service health check.

    Returns service status and configuration.
    Public endpoint (no authentication required).
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
