"""Structured ICAO METAR/SPECI remarks (RMK) code-group models.

[Corpus: product §F9] [Corpus: domain]
"""

from __future__ import annotations

import msgspec

# Catalog of coded-response families after ``RMK`` (FMH-1 / national addenda).
REMARK_FAMILIES: tuple[str, ...] = (
    "marker",
    "sensor_ao",
    "sea_level_pressure",
    "temperature_tenths",
    "six_hour_temperature",
    "day_max_min",
    "precip_hourly",
    "precip_period",
    "pressure_tendency",
    "pressure_rapid",
    "ice_accretion",
    "wx_begin_end",
    "sensor_status",
    "peak_wind",
    "canadian_cloud",
    "prose",
    "plain_national",
    "direction",
    "unknown",
)


class RemarkGroup(msgspec.Struct, frozen=True):
    """
    One coded remarks group after ``RMK``.

    Attributes
    ----------
    start : int
        Start offset in the TAC string.
    end : int
        End offset in the TAC string.
    code : str
        Original token text.
    family : str
        Catalog family id from :data:`REMARK_FAMILIES`.
    explanation : str
        Plain-language meaning when decoded; empty when undecoded.
    valid : bool
        ``True`` when the token matches a known family shape and decoded.
    """

    start: int
    end: int
    code: str
    family: str
    explanation: str = ""
    valid: bool = False


class RemarkDecodeResult(msgspec.Struct, frozen=True):
    """
    Structured decode of the remarks segment.

    Attributes
    ----------
    groups : list[RemarkGroup]
        Ordered code groups after ``RMK`` (marker included when present).
    has_remarks : bool
        ``True`` when an ``RMK`` marker was found.
    """

    groups: list[RemarkGroup] = msgspec.field(default_factory=list)
    has_remarks: bool = False


__all__ = ["REMARK_FAMILIES", "RemarkDecodeResult", "RemarkGroup"]
