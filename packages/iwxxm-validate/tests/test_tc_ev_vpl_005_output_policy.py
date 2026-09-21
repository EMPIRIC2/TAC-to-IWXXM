"""TC-EV-VPL-005 — IWXXM output policy assert map (#1216 M4)."""

from __future__ import annotations

from pathlib import Path

import pytest
from iwxxm_validate.inventory import InventoryError, load_assert_inventory, load_assert_inventory_from
from iwxxm_validate.policy import (
    NON_SELECTABLE,
    PolicyActivationError,
    PolicyError,
    load_output_policy,
    load_output_policy_catalog,
    resolve_output_policy,
)


def test_pin_inventory_contains_known_pattern() -> None:
    ids = load_assert_inventory("2025-2")
    assert "AIRMET.AIRMET-1" in ids
    assert "SCHEMATRON_SKIPPED" in NON_SELECTABLE


def test_inventory_missing_pin_and_empty(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(InventoryError, match="not found"):
        load_assert_inventory("no-such-pin")
    empty = tmp_path / "pin"
    empty.mkdir()
    with pytest.raises(InventoryError, match="no Schematron"):
        load_assert_inventory_from(empty)
    missing = tmp_path / "absent"
    with pytest.raises(InventoryError, match="not found"):
        load_assert_inventory_from(missing)
    sch = empty / "rule"
    sch.mkdir()
    (sch / "a.sch").write_text('<sch:pattern id="DEMO.1"></sch:pattern>', encoding="utf-8")
    assert load_assert_inventory_from(empty) == frozenset({"DEMO.1"})

    bare = tmp_path / "roots"
    (bare / "blank").mkdir(parents=True)
    monkeypatch.setattr("iwxxm_validate.inventory.vendor_iwxxm_root", lambda: bare)
    load_assert_inventory.cache_clear()
    with pytest.raises(InventoryError, match="no Schematron"):
        load_assert_inventory("blank")
    load_assert_inventory.cache_clear()


def test_builtin_policy_enables_full_pin() -> None:
    catalog = load_output_policy_catalog()
    doc = catalog["annex3-iwxxm-output"]
    resolved = resolve_output_policy(doc, policies=catalog)
    inventory = load_assert_inventory("2025-2")
    assert resolved.enabled == inventory
    assert resolved.warnings == ()


def test_select_ignore_and_draft_unknown(tmp_path: Path) -> None:
    inventory = frozenset({"A.1", "A.2", "B.1"})
    path = tmp_path / "child.yaml"
    path.write_text(
        "\n".join(
            [
                "schema_version: 1",
                "id: child",
                "lifecycle: draft",
                "pin: '2025-2'",
                "extends: [parent]",
                "select: [A.1, STALE]",
                "ignore: [A.2]",
            ]
        ),
        encoding="utf-8",
    )
    parent = tmp_path / "parent.yaml"
    parent.write_text(
        "\n".join(
            [
                "schema_version: 1",
                "id: parent",
                "lifecycle: draft",
                "pin: '2025-2'",
                "select: [B.1]",
                "ignore: []",
            ]
        ),
        encoding="utf-8",
    )
    child = load_output_policy(path)
    base = load_output_policy(parent)
    resolved = resolve_output_policy(child, policies={child.id: child, base.id: base}, inventory=inventory)
    assert resolved.enabled == frozenset({"A.1"})
    assert any("STALE" in warning for warning in resolved.warnings)
    with pytest.raises(PolicyActivationError, match="STALE"):
        resolve_output_policy(
            child,
            policies={child.id: child, base.id: base},
            inventory=inventory,
            activate=True,
        )


def test_non_selectable_and_parse_errors(tmp_path: Path) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text(
        "schema_version: 1\nid: bad\nlifecycle: activated\npin: '2025-2'\nselect: [XSD]\n",
        encoding="utf-8",
    )
    doc = load_output_policy(path)
    with pytest.raises(PolicyActivationError, match="not selectable"):
        resolve_output_policy(doc, policies={doc.id: doc}, inventory=frozenset({"A.1"}))

    with pytest.raises(PolicyError, match="mapping"):
        load_output_policy(_write(tmp_path, "list.yaml", "- 1\n"))
    with pytest.raises(PolicyError, match="schema_version"):
        load_output_policy(_write(tmp_path, "sv.yaml", "schema_version: 0\nid: x\npin: p\n"))
    with pytest.raises(PolicyError, match="id is required"):
        load_output_policy(_write(tmp_path, "id.yaml", "schema_version: 1\nid: ' '\npin: p\n"))
    with pytest.raises(PolicyError, match="lifecycle"):
        load_output_policy(_write(tmp_path, "life.yaml", "schema_version: 1\nid: x\npin: p\nlifecycle: no\n"))
    with pytest.raises(PolicyError, match="pin is required"):
        load_output_policy(_write(tmp_path, "pin.yaml", "schema_version: 1\nid: x\npin: ' '\n"))
    with pytest.raises(PolicyError, match="select must be"):
        load_output_policy(_write(tmp_path, "sel.yaml", "schema_version: 1\nid: x\npin: p\nselect: no\n"))
    with pytest.raises(PolicyError, match="entries must be"):
        load_output_policy(_write(tmp_path, "ent.yaml", "schema_version: 1\nid: x\npin: p\nignore: ['']\n"))


def test_extends_cycle_and_missing_parent() -> None:
    from iwxxm_validate.policy import OutputPolicyDocument

    a = OutputPolicyDocument(1, "a", "draft", "2025-2", ("b",), (), ())
    b = OutputPolicyDocument(1, "b", "draft", "2025-2", ("a",), (), ())
    with pytest.raises(PolicyError, match="cycle"):
        resolve_output_policy(a, policies={"a": a, "b": b}, inventory=frozenset({"A.1"}))
    orphan = OutputPolicyDocument(1, "o", "draft", "2025-2", ("missing",), (), ())
    with pytest.raises(PolicyError, match="unknown extends"):
        resolve_output_policy(orphan, policies={"o": orphan}, inventory=frozenset({"A.1"}))
    bare = OutputPolicyDocument(1, "z", "draft", "missing-pin", (), (), ())
    with pytest.raises(PolicyError, match="pin directory"):
        resolve_output_policy(bare, policies={"z": bare})


def test_overlay_catalog(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    overlay = tmp_path / "ov"
    overlay.mkdir()
    (overlay / "extra.yml").write_text(
        "schema_version: 1\nid: extra\nlifecycle: draft\npin: '2025-2'\nselect: []\nignore: []\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("IWXXM_VALIDATE_POLICY_DIR", str(overlay))
    catalog = load_output_policy_catalog()
    assert "extra" in catalog
    assert "annex3-iwxxm-output" in catalog
    monkeypatch.setenv("IWXXM_VALIDATE_POLICY_DIR", str(tmp_path / "not-a-dir"))
    (tmp_path / "not-a-dir").write_text("x", encoding="utf-8")
    again = load_output_policy_catalog()
    assert "annex3-iwxxm-output" in again
    assert "extra" not in again


def _write(tmp_path: Path, name: str, body: str) -> Path:
    path = tmp_path / name
    path.write_text(body, encoding="utf-8")
    return path
