"""F29 / #831 inventory gate (EV-030 T1.6).

Ensures every in-scope pilot rule has an explicit 20-slot matrix
(``ready`` / ``needs-fixture`` / ``oos``) - no silent gaps (TC-F29-004).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import yaml
from tests.quality_matrices.loaders import BUCKETS, Engine, load_rule_cases_tree

_PACKAGE_ROOT = Path(__file__).resolve().parent
DEFAULT_INVENTORY_PATH = _PACKAGE_ROOT / "inventory" / "metar_speci_pilot.yml"
DEFAULT_TESTDATA_ROOT = _PACKAGE_ROOT / "testdata"
_REQUIRED_SLOT_COUNT = 20
_EXPLICIT_STATUSES = frozenset({"ready", "needs-fixture", "oos"})


@dataclass(frozen=True)
class InventoryRule:
    """One in-scope pilot rule from the unified inventory index."""

    engine: Engine
    rule_id: str


@dataclass(frozen=True)
class InventorySpec:
    """Inventory rules plus scoped matrix roots (EV-071 / TC-EV071-004)."""

    rules: list[InventoryRule]
    matrix_roots: list[Path]


@dataclass(frozen=True)
class InventoryGap:
    """A silent or incomplete matrix coverage failure."""

    engine: str
    rule_id: str
    detail: str

    def __str__(self) -> str:
        return f"{self.engine}/{self.rule_id}: {self.detail}"


def _matrix_roots_from_raw(inv_path: Path, raw: dict[str, object]) -> list[Path]:
    roots_obj = raw.get("matrix_roots")
    if isinstance(roots_obj, list):
        return [
            DEFAULT_TESTDATA_ROOT / str(item).strip()
            for item in cast(list[object], roots_obj)
            if str(item).strip()
        ]
    if inv_path.name == "metar_speci_pilot.yml":
        return [
            DEFAULT_TESTDATA_ROOT / "lint" / "metar_speci",
            DEFAULT_TESTDATA_ROOT / "convert" / "metar_speci",
            DEFAULT_TESTDATA_ROOT / "validate" / "metar_speci",
        ]
    raise ValueError(f"{inv_path}: matrix_roots must list scoped testdata subtrees")


def load_inventory_spec(path: Path | None = None) -> InventorySpec:
    """Load inventory rules and scoped matrix roots."""
    inv_path = path or DEFAULT_INVENTORY_PATH
    raw_obj: object = yaml.safe_load(inv_path.read_text(encoding="utf-8"))
    if not isinstance(raw_obj, dict):
        raise ValueError(f"{inv_path}: root must be a mapping")
    raw = cast(dict[str, object], raw_obj)
    engines_obj = raw.get("engines")
    if not isinstance(engines_obj, dict):
        raise ValueError(f"{inv_path}: engines must be a mapping")
    engines = cast(dict[str, object], engines_obj)

    out: list[InventoryRule] = []
    for engine_name, rules_obj in engines.items():
        if engine_name not in {"lint", "convert", "validate"}:
            raise ValueError(f"{inv_path}: unknown engine {engine_name!r}")
        engine: Engine = engine_name  # narrowed
        if not isinstance(rules_obj, list) or not rules_obj:
            raise ValueError(
                f"{inv_path}: engines.{engine_name} must be a non-empty list"
            )
        for i, item_obj in enumerate(cast(list[object], rules_obj)):
            if not isinstance(item_obj, dict):
                raise ValueError(
                    f"{inv_path}: engines.{engine_name}[{i}] must be a mapping"
                )
            item = cast(dict[str, Any], item_obj)
            rule_id = item.get("id")
            if not isinstance(rule_id, str) or not rule_id.strip():
                raise ValueError(f"{inv_path}: engines.{engine_name}[{i}] missing id")
            out.append(InventoryRule(engine=engine, rule_id=rule_id.strip()))
    return InventorySpec(rules=out, matrix_roots=_matrix_roots_from_raw(inv_path, raw))


def load_pilot_inventory(path: Path | None = None) -> list[InventoryRule]:
    """Load the METAR/SPECI pilot inventory (unified index SoT)."""
    return load_inventory_spec(path).rules


def find_inventory_gaps(
    *,
    inventory: list[InventoryRule] | None = None,
    matrix_roots: list[Path] | None = None,
    inventory_path: Path | None = None,
) -> list[InventoryGap]:
    """Return silent/incomplete coverage gaps for an inventory spec."""
    inv_path = inventory_path or DEFAULT_INVENTORY_PATH
    if inventory is None or matrix_roots is None:
        spec = load_inventory_spec(inv_path)
        rules = inventory if inventory is not None else spec.rules
        roots = matrix_roots if matrix_roots is not None else spec.matrix_roots
    else:
        rules = inventory
        roots = matrix_roots

    cases: list = []
    for root in roots:
        if root.is_dir():
            cases.extend(load_rule_cases_tree(root))

    by_key: dict[tuple[str, str], list] = {}
    for case in cases:
        by_key.setdefault((case.engine, case.rule_id), []).append(case)

    gaps: list[InventoryGap] = []
    expected_keys = {(r.engine, r.rule_id) for r in rules}

    for rule in rules:
        key = (rule.engine, rule.rule_id)
        rule_cases = by_key.get(key, [])
        if not rule_cases:
            gaps.append(
                InventoryGap(
                    engine=rule.engine,
                    rule_id=rule.rule_id,
                    detail="missing matrix file/slots (silent gap)",
                )
            )
            continue
        if len(rule_cases) != _REQUIRED_SLOT_COUNT:
            gaps.append(
                InventoryGap(
                    engine=rule.engine,
                    rule_id=rule.rule_id,
                    detail=f"expected {_REQUIRED_SLOT_COUNT} slots, got {len(rule_cases)}",
                )
            )
        buckets = {c.bucket for c in rule_cases}
        if buckets != set(BUCKETS):
            gaps.append(
                InventoryGap(
                    engine=rule.engine,
                    rule_id=rule.rule_id,
                    detail=f"incomplete buckets {sorted(buckets)}",
                )
            )
        for bucket in BUCKETS:
            ids = sorted(c.case_id for c in rule_cases if c.bucket == bucket)
            expected_ids = [f"{n:02d}" for n in range(1, 6)]
            if ids != expected_ids:
                gaps.append(
                    InventoryGap(
                        engine=rule.engine,
                        rule_id=rule.rule_id,
                        detail=f"{bucket} case_ids {ids} != {expected_ids}",
                    )
                )
        gaps.extend(
            InventoryGap(
                engine=rule.engine,
                rule_id=rule.rule_id,
                detail=f"{case.node_id} has non-explicit status {case.status!r}",
            )
            for case in rule_cases
            if case.status not in _EXPLICIT_STATUSES
        )

    # Extra matrix rules outside inventory are not silent gaps, but report them
    # so CI can decide (pilot gate is inventory-complete, not "no extras").
    extras = sorted(by_key.keys() - expected_keys)
    for engine, rule_id in extras:
        gaps.append(
            InventoryGap(
                engine=engine,
                rule_id=rule_id,
                detail="matrix present but not listed in pilot inventory",
            )
        )
    return gaps


def assert_inventory_complete(
    *,
    inventory: list[InventoryRule] | None = None,
    matrix_roots: list[Path] | None = None,
    inventory_path: Path | None = None,
) -> None:
    """Raise ``AssertionError`` if any inventory gaps exist."""
    gaps = find_inventory_gaps(
        inventory=inventory,
        matrix_roots=matrix_roots,
        inventory_path=inventory_path,
    )
    if gaps:
        lines = "\n".join(f"  - {g}" for g in gaps)
        raise AssertionError(f"inventory gate failed ({len(gaps)} gaps):\n{lines}")
