"""TC-F29-003 / T1.3 — METAR/SPECI lint pilot matrices (fill or needs-fixture)."""

from __future__ import annotations

from pathlib import Path

import pytest
from tests.quality_matrices.loaders import BUCKETS, RuleCase, load_rule_cases_tree
from tests.quality_matrices.runners import run_rule_case

_LINT_ROOT = Path(__file__).resolve().parent / "testdata" / "lint" / "metar_speci"

# T0.2 pilot set (36 registry codes).
_PILOT_LINT_CODES: frozenset[str] = frozenset(
    {
        "UNKNOWN_PRODUCT",
        "EMPTY_TAC",
        "MISSING_PRODUCT_KEYWORD",
        "MISSING_TERMINATOR",
        "MISSING_CCCC",
        "MISSING_OBS_TIME",
        "ODD_FIELD_ORDER",
        "MISSING_WIND",
        "MISSING_VISIBILITY",
        "INVALID_VISIBILITY",
        "INVALID_WEATHER",
        "MISSING_TEMP_DEWPOINT",
        "MISSING_QNH",
        "INVALID_CLOUD_TOKEN",
        "CLOUD_CB_OR_TCU",
        "REMARK_US_EXTENSION",
        "INVALID_REMARK",
        "AUTO_PRESENT",
        "COR_PRESENT",
        "NIL_REPORT",
        "INVALID_NIL",
        "MULTI_REPORT_BULLETIN",
        "NOSIG_PRESENT",
        "TEMPO_PRESENT",
        "RVR_PRESENT",
        "INVALID_RVR",
        "WIND_VRB_OR_GUST",
        "INVALID_WIND",
        "CAVOK_PRESENT",
        "NSC_PRESENT",
        "NSC_WITH_CLOUD_LAYERS",
        "NCD_PRESENT",
        "NSW_PRESENT",
        "VV_NOT_OBSERVABLE",
        "WX_NOT_OBSERVABLE",
        "WIND_DIR_VARIATION",
    }
)


def _lint_cases() -> list[RuleCase]:
    return [c for c in load_rule_cases_tree(_LINT_ROOT) if c.engine == "lint"]


def _case_ids(cases: list[RuleCase]) -> list[str]:
    return [c.node_id for c in cases]


def test_pilot_lint_files_cover_inventory_codes() -> None:
    files = {p.stem for p in _LINT_ROOT.glob("*.yml")}
    assert files == _PILOT_LINT_CODES


def test_pilot_lint_each_rule_has_20_slots() -> None:
    cases = _lint_cases()
    by_rule: dict[str, list[RuleCase]] = {}
    for case in cases:
        by_rule.setdefault(case.rule_id, []).append(case)
    assert set(by_rule) == _PILOT_LINT_CODES
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


def test_pilot_lint_no_silent_gaps() -> None:
    """Every slot is ready, needs-fixture, or oos — never missing status."""
    for case in _lint_cases():
        assert case.status in {"ready", "needs-fixture", "oos"}


@pytest.mark.parametrize("case", _lint_cases(), ids=_case_ids(_lint_cases()))
def test_pilot_lint_matrix_runners(case: RuleCase) -> None:
    """Run all lint pilot slots; needs-fixture/oos skip via runner policy."""
    run_rule_case(case)
