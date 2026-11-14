"""Centennial recognition-criteria proxies for Station health (F39).

Maps a practical subset of WMO Centennial Observing Stations mandatory
criteria to values we can compute from live TAC aggregates and station
registry metadata. Criteria we cannot measure are returned as
``insufficient_data`` - never as invented green scores.

Source (operator reference only; not shown as planning ids in UI):
https://wmo.int/activities/centennial-observing-stations/centennial-observing-stations/recognition-criteria-meteorological-observing-stations
"""

from __future__ import annotations

from typing import Any, Final

from src.services.station_health_types import StationMeta, StationRecord

STATUS_AVAILABLE: Final[str] = "available"
STATUS_INSUFFICIENT: Final[str] = "insufficient_data"

# Continuity proxy: Centennial C2 allows ≤10% inactivity → ≥90% availability.
CONTINUITY_THRESHOLD: Final[float] = 90.0


def _insufficient(criterion_id: str, label: str, reason: str) -> dict[str, Any]:
    """Build an insufficient-data metric row."""
    return {
        "id": criterion_id,
        "label": label,
        "status": STATUS_INSUFFICIENT,
        "score": None,
        "detail": reason,
    }


def _available(
    criterion_id: str,
    label: str,
    score: float,
    detail: str,
) -> dict[str, Any]:
    """Build a computed metric row."""
    return {
        "id": criterion_id,
        "label": label,
        "status": STATUS_AVAILABLE,
        "score": round(score, 2),
        "detail": detail,
    }


def observing_continuity_metric(
    *,
    availability_score: float | None,
    expected_count: int,
    actual_count: int,
) -> dict[str, Any]:
    """
    Proxy for Centennial criterion 2 (inactivity ≤ 10%).

    Uses the same availability score as Station health grades when a cadence
    expectation exists for the window.
    """
    label = "Observing continuity"
    if expected_count <= 0 and actual_count <= 0:
        return _insufficient(
            "centennial_continuity",
            label,
            "Not enough reports in this window to judge continuity.",
        )
    if expected_count <= 0:
        # Irregular products: presence-only - treat as insufficient for C2 %.
        return _insufficient(
            "centennial_continuity",
            label,
            "This product has no fixed report cadence, so continuity percent is not available.",
        )
    score = float(availability_score if availability_score is not None else 0.0)
    if score >= CONTINUITY_THRESHOLD:
        detail = (
            f"Availability {score:.1f}% meets the 90% continuity proxy "
            f"({actual_count} of {expected_count} expected reports)."
        )
    else:
        detail = (
            f"Availability {score:.1f}% is below the 90% continuity proxy "
            f"({actual_count} of {expected_count} expected reports)."
        )
    return _available("centennial_continuity", label, score, detail)


def metadata_completeness_metric(meta: StationMeta | None) -> dict[str, Any]:
    """
    Partial proxy for Centennial criterion 3 (station metadata).

    Scores presence of name, country, latitude, and longitude on the registry
    row. Historic depth, elevation, and schedule history are not stored.
    """
    label = "Station metadata"
    if meta is None:
        return _insufficient(
            "centennial_metadata",
            label,
            "No station registry row is available yet.",
        )
    fields = {
        "name": bool(meta.name),
        "country": bool(meta.country),
        "latitude": meta.latitude is not None,
        "longitude": meta.longitude is not None,
    }
    present = sum(1 for ok in fields.values() if ok)
    total = len(fields)
    score = 100.0 * present / total if total else 0.0
    missing = [name for name, ok in fields.items() if not ok]
    if present == 0:
        detail = (
            "Only the station identifier is known. Name, country, and coordinates "
            "are missing. Historic elevation and observing schedules are not stored."
        )
    elif missing:
        detail = (
            f"Present: {present} of {total} live metadata fields. "
            f"Missing: {', '.join(missing)}. "
            "Historic elevation and observing schedules are not stored."
        )
    else:
        detail = (
            "Name, country, and coordinates are present. Historic elevation and observing schedules are not stored."
        )
    return _available("centennial_metadata", label, score, detail)


def observation_quality_proxy_metric(
    *,
    solidus_rate: float,
    missing_digit_rate: float,
    lint_severity_score: float,
    record_count: int,
) -> dict[str, Any]:
    """
    Combined proxy for Centennial criteria 6 and 8 (standards / routine QC).

    Blends solidus quality, missing-digit quality, and lint severity already
    used in Station health grades. Not a substitute for WIGOS site audits.
    """
    label = "Observation quality"
    if record_count <= 0:
        return _insufficient(
            "centennial_quality",
            label,
            "No reports in this window to score observation quality.",
        )
    solidus_q = max(0.0, 100.0 - min(100.0, max(0.0, solidus_rate) * 500.0))
    missing_q = max(0.0, 100.0 - min(100.0, max(0.0, missing_digit_rate) * 40.0))
    score = (solidus_q * 0.35) + (missing_q * 0.25) + (float(lint_severity_score) * 0.40)
    detail = (
        f"Quality proxy from solidus rate, missing-digit rate, and lint severity "
        f"across {record_count} report(s). Site classification and full WIGOS "
        "audits are not available here."
    )
    return _available("centennial_quality", label, score, detail)


def deferred_centennial_metrics() -> list[dict[str, Any]]:
    """Criteria that cannot be measured from live TAC / registry data."""
    return [
        _insufficient(
            "centennial_founding_age",
            "Station founding age",
            "Founding year and 100-year operation history are not in live station data.",
        ),
        _insufficient(
            "centennial_homogenization",
            "Relocation and measurement changes",
            "Relocation and instrument-change records are not stored.",
        ),
        _insufficient(
            "centennial_digital_archive",
            "Digital archive and data rescue",
            "Archive and data-rescue status are not stored.",
        ),
        _insufficient(
            "centennial_siting_class",
            "Siting classification",
            "WMO siting class and OSCAR metadata are not stored.",
        ),
        _insufficient(
            "centennial_data_sharing",
            "Data sharing for research",
            "Research data-sharing status is not stored.",
        ),
    ]


def build_centennial_metrics(
    *,
    meta: StationMeta | None,
    rows: list[StationRecord],
    availability_score: float,
    expected_count: int,
    actual_count: int,
    solidus_rate: float,
    missing_digit_rate: float,
    lint_severity_score: float,
) -> list[dict[str, Any]]:
    """
    Build the Centennial-aligned metric list for one station window.

    Parameters
    ----------
    meta : StationMeta | None
        Registry metadata when known.
    rows : list[StationRecord]
        Windowed observations.
    availability_score : float
        Overall or primary availability score for the window.
    expected_count : int
        Expected report count used for continuity.
    actual_count : int
        Actual report count.
    solidus_rate : float
        Aggregate solidus rate.
    missing_digit_rate : float
        Aggregate missing-digit rate.
    lint_severity_score : float
        Aggregate lint severity score.

    Returns
    -------
    list[dict[str, Any]]
        Metric rows with ``status`` ``available`` or ``insufficient_data``.
    """
    metrics = [
        observing_continuity_metric(
            availability_score=availability_score,
            expected_count=expected_count,
            actual_count=actual_count,
        ),
        metadata_completeness_metric(meta),
        observation_quality_proxy_metric(
            solidus_rate=solidus_rate,
            missing_digit_rate=missing_digit_rate,
            lint_severity_score=lint_severity_score,
            record_count=len(rows),
        ),
    ]
    metrics.extend(deferred_centennial_metrics())
    return metrics


__all__ = [
    "CONTINUITY_THRESHOLD",
    "STATUS_AVAILABLE",
    "STATUS_INSUFFICIENT",
    "build_centennial_metrics",
    "deferred_centennial_metrics",
    "metadata_completeness_metric",
    "observation_quality_proxy_metric",
    "observing_continuity_metric",
]
