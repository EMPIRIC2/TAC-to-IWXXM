"""TC-1265 — lint matrices for every product beyond METAR/SPECI.

Cases are built from public bulletins retrieved 2026-09-23 (NOAA
Aviation Weather Center international SIGMET, and the NWS tgftp raw
gateway for AIRMET, VAA, TCA, SWXA, and VONA). Happy slots are reports
that lint clean, or that carry an informational finding. Sad slots are
the blocking findings.
"""

from __future__ import annotations

from pathlib import Path

from tests.quality_matrices.loaders import BUCKETS, RuleCase, load_rule_cases_tree
from tests.quality_matrices.runners import run_rule_case

_ROOT = Path(__file__).resolve().parent / "testdata" / "lint"
_PRODUCTS = ("sigmet", "airmet", "vaa", "tca", "swxa", "vona", "ca_eccc")


def _ready(product: str) -> list[RuleCase]:
    return [
        case
        for case in load_rule_cases_tree(_ROOT / product)
        if case.engine == "lint" and case.status == "ready"
    ]


def test_tc_1265_other_products_slots_are_ready() -> None:
    """Each filled rule has 20 ready slots and no empty scaffold."""
    for product in _PRODUCTS:
        cases = _ready(product)
        assert cases, product
        by_rule: dict[str, list[RuleCase]] = {}
        for case in cases:
            by_rule.setdefault(case.rule_id, []).append(case)
        for rule_id, group in by_rule.items():
            assert len(group) == 20, f"{product}/{rule_id}"
            assert {case.bucket for case in group} == set(BUCKETS)
            assert all(case.status == "ready" for case in group)


def test_tc_1265_other_products_ready_smoke() -> None:
    """Execute every ready slot for the non-METAR products and the Canadian profile."""
    ready = [case for product in _PRODUCTS for case in _ready(product)]
    assert len(ready) >= 60 * 20
    for case in ready:
        run_rule_case(case)
