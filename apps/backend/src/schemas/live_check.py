"""Response models for the live-check API (open aviation feeds).

[Corpus: product §F6] [Corpus: api]
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class LiveCheckResponse(BaseModel):
    """GET /api/v1/live-check payload."""

    icao: str = Field(description="ICAO airport code.")
    product: str = Field(description="Product id: METAR or TAF.")
    provider: str = Field(description="Allowlisted feed id: noaa, met_no, or knmi.")
    profile: str = Field(description="Conversion profile used for this station.")
    source_tac: str = Field(description="Traditional alphanumeric report from the feed.")
    our_iwxxm: str | None = Field(
        default=None,
        description="IWXXM produced by this service from source_tac.",
    )
    provider_iwxxm: str | None = Field(
        default=None,
        description="Provider IWXXM when the feed returned a pair.",
    )
    attribution: str | None = Field(
        default=None,
        description="License attribution for CC BY sources.",
    )
    cached: bool = Field(description="True when served from the short server cache.")
    convert_ok: bool = Field(description="True when conversion produced IWXXM.")
    convert_issues: list[str] = Field(
        default_factory=list,
        description="Non-fatal or fatal convert issue messages.",
    )
