"""Live check against allowlisted open aviation feeds.

Public route. Feed credentials stay on the server. Callers never supply a URL.

[Corpus: product §F6] [Corpus: api]
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from src.schemas.live_check import LiveCheckResponse
from src.services.live_check import (
    LiveCheckError,
    get_live_check_service,
)

router = APIRouter(prefix="/api/v1", tags=["Live check"])


@router.get(
    "/live-check",
    response_model=LiveCheckResponse,
    summary="Live check for one airport and product",
    description=(
        "Fetch an allowlisted open feed for one airport, convert with the "
        "station profile, and return source TAC, our IWXXM, and provider "
        "IWXXM when the feed included a pair. Providers: noaa, met_no, knmi."
    ),
)
def live_check(
    icao: str = Query(..., min_length=4, max_length=4, description="ICAO airport code."),
    product: str = Query("METAR", description="METAR or TAF."),
    provider: str = Query(
        "noaa",
        description="Allowlisted feed: noaa, met_no, or knmi.",
    ),
) -> LiveCheckResponse:
    """Return TAC and IWXXM for one airport from an allowlisted feed."""
    try:
        result = get_live_check_service().check(icao=icao, product=product, provider=provider)
    except LiveCheckError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    return LiveCheckResponse(
        icao=result.icao,
        product=result.product,
        provider=result.provider,
        profile=result.profile,
        source_tac=result.source_tac,
        our_iwxxm=result.our_iwxxm,
        provider_iwxxm=result.provider_iwxxm,
        attribution=result.attribution,
        cached=result.cached,
        convert_ok=result.convert_ok,
        convert_issues=result.convert_issues,
    )
