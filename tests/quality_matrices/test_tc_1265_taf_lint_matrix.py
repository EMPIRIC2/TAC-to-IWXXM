"""TC-1265 — TAF lint quality matrices are ready cases, not scaffolds.

Annex 3 TAF codes, plus the profile overlays that already exist:
iwxxm_us BECMG and TEMPO limits, ca_eccc non-convective wind shear,
and in_imd TX/TN omission.
"""

from __future__ import annotations

from pathlib import Path

from tests.quality_matrices.loaders import BUCKETS, RuleCase, load_rule_cases_tree
from tests.quality_matrices.runners import run_rule_case

_TAF_ROOT = Path(__file__).resolve().parent / "testdata" / "lint" / "taf"


def test_tc_1265_taf_lint_needs_fixture_cleared() -> None:
    """Filled TAF lint rules are ready on all 20 slots."""
    cases = [case for case in load_rule_cases_tree(_TAF_ROOT) if case.engine == "lint"]
    assert cases, "expected TAF lint RuleCases"
    needs = [case.node_id for case in cases if case.status == "needs-fixture"]
    assert not needs
    by_rule: dict[str, list[RuleCase]] = {}
    for case in cases:
        by_rule.setdefault(case.rule_id, []).append(case)
    assert len(by_rule) == 29
    for rule_id, group in by_rule.items():
        assert len(group) == 20, rule_id
        assert {case.bucket for case in group} == set(BUCKETS)
        assert all(case.status == "ready" for case in group)


def test_tc_1265_taf_lint_ready_smoke() -> None:
    """Execute every ready TAF lint slot."""
    ready = [
        case
        for case in load_rule_cases_tree(_TAF_ROOT)
        if case.engine == "lint" and case.status == "ready"
    ]
    assert len(ready) == 29 * 20
    for case in ready:
        run_rule_case(case)
