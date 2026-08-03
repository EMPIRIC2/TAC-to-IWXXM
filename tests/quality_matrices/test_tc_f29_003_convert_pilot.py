"""TC-F29-003 / T1.4 — METAR/SPECI convert pilot matrices (fill or needs-fixture)."""

from __future__ import annotations

from pathlib import Path

import pytest
from tests.quality_matrices.loaders import BUCKETS, RuleCase, load_rule_cases_tree
from tests.quality_matrices.runners import run_rule_case

_CONVERT_ROOT = Path(__file__).resolve().parent / "testdata" / "convert" / "metar_speci"

# T0.2 pilot encode themes (16 stems); #16 = speci_rvr (optional RVR theme).
_PILOT_CONVERT_STEMS: frozenset[str] = frozenset(
    {
        "metar_a3_1",
        "metar_auto",
        "metar_basic",
        "metar_cavok",
        "metar_cor",
        "metar_nil",
        "speci_a3_2",
        "speci_basic",
        "speci_cavok",
        "speci_cor",
        "speci_ncd",
        "speci_nil",
        "speci_nosig",
        "speci_nsc",
        "speci_nsw_trend",
        "speci_rvr",
    }
)


def _convert_cases() -> list[RuleCase]:
    return [c for c in load_rule_cases_tree(_CONVERT_ROOT) if c.engine == "convert"]


def _case_ids(cases: list[RuleCase]) -> list[str]:
    return [c.node_id for c in cases]


def test_pilot_convert_files_cover_inventory_stems() -> None:
    files = {p.stem for p in _CONVERT_ROOT.glob("*.yml")}
    assert files == _PILOT_CONVERT_STEMS


def test_pilot_convert_each_rule_has_20_slots() -> None:
    cases = _convert_cases()
    by_rule: dict[str, list[RuleCase]] = {}
    for case in cases:
        by_rule.setdefault(case.rule_id, []).append(case)
    assert set(by_rule) == _PILOT_CONVERT_STEMS
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


def test_pilot_convert_no_silent_gaps() -> None:
    """Every slot is ready, needs-fixture, or oos — never missing status."""
    for case in _convert_cases():
        assert case.status in {"ready", "needs-fixture", "oos"}


def test_pilot_convert_ready_smoke() -> None:
    """PR smoke: execute only ready convert slots (not the full 16x20 matrix)."""
    ready = [c for c in _convert_cases() if c.status == "ready"]
    assert ready, "pilot convert expects at least one ready slot"
    for case in ready:
        run_rule_case(case)


@pytest.mark.quality_matrix
@pytest.mark.parametrize("case", _convert_cases(), ids=_case_ids(_convert_cases()))
def test_pilot_convert_matrix_runners(case: RuleCase) -> None:
    """Run all convert pilot slots; needs-fixture/oos skip via runner policy."""
    run_rule_case(case)
