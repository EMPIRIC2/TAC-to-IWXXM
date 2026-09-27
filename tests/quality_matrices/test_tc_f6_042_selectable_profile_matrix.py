"""Ready 20-slot lint matrices for the four selectable profiles.

[Corpus: product §F6] [Corpus: tests]
"""

from __future__ import annotations

from pathlib import Path

from tests.quality_matrices.loaders import BUCKETS, RuleCase, load_rule_cases_tree
from tests.quality_matrices.runners import run_rule_case

_ROOT = Path(__file__).resolve().parent / "testdata" / "lint" / "selectable"


def _ready() -> list[RuleCase]:
    return [
        case
        for case in load_rule_cases_tree(_ROOT)
        if case.engine == "lint" and case.status == "ready"
    ]


def test_selectable_profile_matrices_have_20_slots() -> None:
    cases = _ready()
    by_rule: dict[str, list[RuleCase]] = {}
    for case in cases:
        by_rule.setdefault(case.rule_id, []).append(case)
    assert set(by_rule) == {
        "US_NWS_CONVECTIVE_SIGMET",
        "US_NWS_G_AIRMET",
        "US_NWS_VONA",
        "CA_MSC_SIGMET",
    }
    for rule_id, group in by_rule.items():
        assert len(group) == 20, rule_id
        assert {case.bucket for case in group} == set(BUCKETS)


def test_selectable_profile_matrices_run() -> None:
    for case in _ready():
        run_rule_case(case)
