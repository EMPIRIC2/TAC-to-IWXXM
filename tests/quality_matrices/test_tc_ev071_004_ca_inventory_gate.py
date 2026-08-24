"""TC-EV071-004 — CA_ECCC lint quality matrix inventory gate."""

from __future__ import annotations

from pathlib import Path

from tests.quality_matrices.inventory_gate import (
    DEFAULT_TESTDATA_ROOT,
    assert_inventory_complete,
    load_inventory_spec,
)

_CA_INVENTORY = Path(__file__).resolve().parent / "inventory" / "ca_eccc_lint.yml"


def test_tc_ev071_004_ca_inventory_loads_twelve_rules() -> None:
    spec = load_inventory_spec(_CA_INVENTORY)
    assert len(spec.rules) == 12
    assert spec.matrix_roots == [DEFAULT_TESTDATA_ROOT / "lint" / "ca_eccc"]


def test_tc_ev071_004_ca_inventory_gate_passes() -> None:
    assert_inventory_complete(inventory_path=_CA_INVENTORY)
