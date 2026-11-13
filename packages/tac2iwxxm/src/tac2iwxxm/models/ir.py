"""TypedDict models for package-owned IR nested dicts.

Runtime values remain plain dicts (behavior-preserving). These types document
and validate shapes at boundaries.
"""

from __future__ import annotations

from typing import Any, TypedDict


class LatLonPoint(TypedDict):
    """One lat/lon vertex used in hazard geometry."""

    lat: float
    lon: float


class PolygonGeometry(TypedDict, total=False):
    """Polygon / surface geometry fragment on SIGMET/AIRMET IR."""

    type: str
    pos_list: str
    points: list[tuple[float, float]]
    gml_id: str


class TrendGroup(TypedDict, total=False):
    """METAR/SPECI trend forecast group."""

    change_indicator: str
    nil_nosig: bool
    time_indicator: str
    time_from: str
    time_to: str
    time_at: str
    wind_dir_deg: int
    wind_speed: float
    wind_gust: float
    wind_unit: str
    visibility_m: int
    weather: list[str]
    clouds: list[dict[str, Any]]
    cavok: bool


class LightningSector(TypedDict, total=False):
    """Observed lightning sector remark."""

    in_all_quadrants: bool
    directions: list[str]


class ObservedLightning(TypedDict, total=False):
    """Parsed lightning remark payload."""

    frequency: str
    type_code: str
    sector: LightningSector


class HailstoneSize(TypedDict, total=False):
    """Hail size remark."""

    maximum_diameter_in: float
    size_operator: str


class SkyLevel(TypedDict, total=False):
    """Sky condition / cloud character fragment."""

    href: str
    nil_reason: str
    amount: str
    base_ft: int


class VaLocation(TypedDict, total=False):
    """Volcanic ash location entry on SIGMET IR."""

    name: str
    lat: float
    lon: float
    position: str


class ConvertIr(TypedDict, total=False):
    """
    Top-level convert IR (package-owned nested dict).

    Keys mirror existing wire/M-field checks; unknown keys remain allowed via
    total=False openness for product-specific extensions.
    """

    product: str
    station: str
    day: int
    hour: int
    minute: int
    report_status: str
    remarks_present: bool
    remarks_text: str
    remark_issues: list[str]
    trends: list[TrendGroup]
    geometry: PolygonGeometry
    observed_lightning: ObservedLightning
    hailstone_size: HailstoneSize
    character_of_the_sky: SkyLevel
    va_locations: list[VaLocation]
    phenomenon: str
    fir: str
    sequence: str
    # Catch-all for product extensions (still a dict at runtime)
    extras: dict[str, Any]


class PropagateResidualsConfig(TypedDict, total=False):
    """Per-product defaults for residual→remarks propagation."""

    METAR: bool
    SPECI: bool
    TAF: bool
    SIGMET: bool
    AIRMET: bool
    VAA: bool
    TCA: bool
    SWXA: bool
    VONA: bool


__all__ = [
    "ConvertIr",
    "HailstoneSize",
    "LatLonPoint",
    "LightningSector",
    "ObservedLightning",
    "PolygonGeometry",
    "PropagateResidualsConfig",
    "SkyLevel",
    "TrendGroup",
    "VaLocation",
]
