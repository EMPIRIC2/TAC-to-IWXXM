"""TC-F29-003 / T1.5 — METAR/SPECI validate pilot matrices (fill or needs-fixture)."""

from __future__ import annotations

from pathlib import Path

import pytest
from tests.quality_matrices.loaders import BUCKETS, RuleCase, load_rule_cases_tree
from tests.quality_matrices.runners import run_rule_case

_VALIDATE_ROOT = (
    Path(__file__).resolve().parent / "testdata" / "validate" / "metar_speci"
)

# T0.2 pilot Schematron patterns (43 METAR_SPECI.* ids).
_PILOT_VALIDATE_PATTERNS: frozenset[str] = frozenset(
    {
        "METAR_SPECI.AerodromeCloud-1",
        "METAR_SPECI.AerodromeCloud-2",
        "METAR_SPECI.AerodromeCloud-3",
        "METAR_SPECI.AerodromeHorizontalVisibility-1",
        "METAR_SPECI.AerodromeHorizontalVisibility-2",
        "METAR_SPECI.AerodromeHorizontalVisibility-3",
        "METAR_SPECI.AerodromePresentWeather",
        "METAR_SPECI.AerodromeRecentWeather",
        "METAR_SPECI.AerodromeRunwayVisualRange-1",
        "METAR_SPECI.AerodromeSeaCondition.seaState",
        "METAR_SPECI.AerodromeSeaState-1",
        "METAR_SPECI.AerodromeSeaState-2",
        "METAR_SPECI.AerodromeSeaState-3",
        "METAR_SPECI.AerodromeSeaState-4",
        "METAR_SPECI.AerodromeSurfaceWind-1",
        "METAR_SPECI.AerodromeSurfaceWind-2",
        "METAR_SPECI.AerodromeSurfaceWind-3",
        "METAR_SPECI.AerodromeSurfaceWind-4",
        "METAR_SPECI.AerodromeSurfaceWind-5",
        "METAR_SPECI.AerodromeSurfaceWind-6",
        "METAR_SPECI.AerodromeSurfaceWind-7",
        "METAR_SPECI.AerodromeWindShear-1",
        "METAR_SPECI.AerodromeWindShear-2",
        "METAR_SPECI.MeteorologicalAerodromeObservation-1",
        "METAR_SPECI.MeteorologicalAerodromeObservation-2",
        "METAR_SPECI.MeteorologicalAerodromeObservation-3",
        "METAR_SPECI.MeteorologicalAerodromeObservation-4",
        "METAR_SPECI.MeteorologicalAerodromeObservation-5",
        "METAR_SPECI.MeteorologicalAerodromeObservation.presentWeather",
        "METAR_SPECI.MeteorologicalAerodromeObservation.recentWeather",
        "METAR_SPECI.MeteorologicalAerodromeObservationReport-1",
        "METAR_SPECI.MeteorologicalAerodromeObservationReport-2",
        "METAR_SPECI.MeteorologicalAerodromeObservationReport-3",
        "METAR_SPECI.MeteorologicalAerodromeObservationReport-4",
        "METAR_SPECI.MeteorologicalAerodromeObservationReport-5",
        "METAR_SPECI.MeteorologicalAerodromeObservationReport-6",
        "METAR_SPECI.MeteorologicalAerodromeObservationReport-7",
        "METAR_SPECI.MeteorologicalAerodromeObservationReport-8",
        "METAR_SPECI.MeteorologicalAerodromeObservationReport-9",
        "METAR_SPECI.MeteorologicalAerodromeTrendForecast-1",
        "METAR_SPECI.MeteorologicalAerodromeTrendForecast-2",
        "METAR_SPECI.MeteorologicalAerodromeTrendForecast.weather",
        "METAR_SPECI.SeaSurfaceState",
    }
)


def _validate_cases() -> list[RuleCase]:
    return [c for c in load_rule_cases_tree(_VALIDATE_ROOT) if c.engine == "validate"]


def _case_ids(cases: list[RuleCase]) -> list[str]:
    return [c.node_id for c in cases]


def test_pilot_validate_files_cover_inventory_patterns() -> None:
    files = {p.stem for p in _VALIDATE_ROOT.glob("*.yml")}
    assert files == _PILOT_VALIDATE_PATTERNS


def test_pilot_validate_each_rule_has_20_slots() -> None:
    cases = _validate_cases()
    by_rule: dict[str, list[RuleCase]] = {}
    for case in cases:
        by_rule.setdefault(case.rule_id, []).append(case)
    assert set(by_rule) == _PILOT_VALIDATE_PATTERNS
    for rule_id, rule_cases in sorted(by_rule.items()):
        assert len(rule_cases) == 20, (
            f"{rule_id} expected 20 slots, got {len(rule_cases)}"
        )
        buckets = {c.bucket for c in rule_cases}
        assert buckets == set(BUCKETS)
        for bucket in BUCKETS:
            ids = sorted(c.case_id for c in rule_cases if c.bucket == bucket)
            assert ids == [f"{n:02d}" for n in range(1, 6)], (
                f"{rule_id}/{bucket}: {ids}"
            )


def test_pilot_validate_no_silent_gaps() -> None:
    """Every slot is ready, needs-fixture, or oos — never missing status."""
    for case in _validate_cases():
        assert case.status in {"ready", "needs-fixture", "oos"}


@pytest.mark.parametrize("case", _validate_cases(), ids=_case_ids(_validate_cases()))
def test_pilot_validate_matrix_runners(case: RuleCase) -> None:
    """Run all validate pilot slots; needs-fixture/oos skip via runner policy."""
    run_rule_case(case)
