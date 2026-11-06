"""TC-F29-008 — convert and validate matrices beyond METAR/SPECI.

Filled packs: TAF, SIGMET, AIRMET, VAA, TCA, SWXA, and VONA.
"""

from __future__ import annotations

from pathlib import Path

from tests.quality_matrices.inventory_gate import (
    DEFAULT_TESTDATA_ROOT,
    assert_inventory_complete,
    load_inventory_spec,
)
from tests.quality_matrices.loaders import load_rule_cases_tree
from tests.quality_matrices.runners import run_rule_case

_INVENTORY = Path(__file__).resolve().parent / "inventory" / "product_matrices.yml"
_PRODUCTS = ("taf", "sigmet", "airmet", "vaa", "tca", "swxa", "vona")


def test_tc_f29_008_inventory_loads_all_products() -> None:
    """The product inventory lists convert and validate rules for every filled pack."""
    spec = load_inventory_spec(_INVENTORY)
    assert len(spec.rules) == 110
    by_engine = {"convert": 0, "validate": 0}
    for rule in spec.rules:
        by_engine[rule.engine] += 1
    assert by_engine == {"convert": 22, "validate": 88}
    expected_roots = [
        path
        for product in _PRODUCTS
        for path in (
            DEFAULT_TESTDATA_ROOT / "convert" / product,
            DEFAULT_TESTDATA_ROOT / "validate" / product,
        )
    ]
    assert spec.matrix_roots == expected_roots


def test_tc_f29_008_inventory_gate_passes() -> None:
    """Every listed rule has 20 explicit slots."""
    assert_inventory_complete(inventory_path=_INVENTORY)


def test_tc_f29_008_ready_smoke() -> None:
    """Execute every ready convert and validate slot across the filled packs."""
    spec = load_inventory_spec(_INVENTORY)
    ready = [
        case
        for root in spec.matrix_roots
        for case in load_rule_cases_tree(root)
        if case.status == "ready"
    ]
    # convert: 22*20 ready
    # validate: 17 patterns fully ready (20) + 71 with happy/edge_pass only (10)
    assert len(ready) == (22 * 20) + (17 * 20) + (71 * 10)
    for case in ready:
        run_rule_case(case)
