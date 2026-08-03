"""TC-F29-004 / TC-EV030-003 / T1.6 — inventory gate (no silent gaps)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from tests.quality_matrices.inventory_gate import (
    DEFAULT_INVENTORY_PATH,
    InventoryRule,
    assert_inventory_complete,
    find_inventory_gaps,
    load_pilot_inventory,
)


def test_pilot_inventory_loads_95_rules() -> None:
    rules = load_pilot_inventory()
    assert DEFAULT_INVENTORY_PATH.is_file()
    assert len(rules) == 95
    by_engine = {e: 0 for e in ("lint", "convert", "validate")}
    for rule in rules:
        by_engine[rule.engine] += 1
    assert by_engine == {"lint": 36, "convert": 16, "validate": 43}


def test_inventory_gate_passes_for_pilot_testdata() -> None:
    assert_inventory_complete()


def test_inventory_gate_fails_on_silent_gap(tmp_path: Path) -> None:
    """Gate must fail when an inventory rule has no matrix slots."""
    inv = tmp_path / "inv.yml"
    inv.write_text(
        yaml.dump(
            {
                "version": 1,
                "engines": {
                    "lint": [
                        {
                            "id": "MISSING_RULE",
                            "native": {"kind": "registry_code", "code": "MISSING_RULE"},
                        }
                    ]
                },
            }
        ),
        encoding="utf-8",
    )
    testdata = tmp_path / "testdata"
    testdata.mkdir()
    inventory = load_pilot_inventory(inv)
    gaps = find_inventory_gaps(inventory=inventory, testdata_root=testdata)
    assert len(gaps) == 1
    assert "silent gap" in gaps[0].detail
    with pytest.raises(AssertionError, match="silent gap"):
        assert_inventory_complete(inventory=inventory, testdata_root=testdata)


def test_inventory_gate_fails_on_incomplete_slots(tmp_path: Path) -> None:
    """Fewer than 20 explicit slots counts as incomplete (not inventory-complete)."""
    inv = [
        InventoryRule(engine="lint", rule_id="PARTIAL"),
    ]
    root = tmp_path / "testdata"
    path = root / "lint" / "metar_speci" / "PARTIAL.yml"
    path.parent.mkdir(parents=True)
    path.write_text(
        "rule_id: PARTIAL\nengine: lint\ncases:\n"
        "  - bucket: happy\n    case_id: '01'\n    status: needs-fixture\n"
        "    meta: {reason: 'only one slot'}\n",
        encoding="utf-8",
    )
    gaps = find_inventory_gaps(inventory=inv, testdata_root=root)
    assert any("expected 20 slots" in g.detail for g in gaps)
    with pytest.raises(AssertionError, match="expected 20 slots"):
        assert_inventory_complete(inventory=inv, testdata_root=root)
