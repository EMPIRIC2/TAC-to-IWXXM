#!/usr/bin/env python3
"""Mine TAC + IWXXM validation library catalogs (EVPYL T-B2).

Writes:
  packages/tac2iwxxm/src/tac2iwxxm/data/tac_validation_rules.yaml
  packages/tac2iwxxm/src/tac2iwxxm/data/iwxxm_validation_asserts.yaml

Usage
-----
::

    uv run python scripts/iwxxm/mine_validation_library_catalogs.py
    uv run python scripts/iwxxm/mine_validation_library_catalogs.py --check
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA = REPO_ROOT / "packages" / "tac2iwxxm" / "src" / "tac2iwxxm" / "data"
TAC_OUT = DATA / "tac_validation_rules.yaml"
IWXXM_OUT = DATA / "iwxxm_validation_asserts.yaml"
SCH = (
    REPO_ROOT
    / "vendor"
    / "schemas"
    / "iwxxm"
    / "2025-2"
    / "IWXXM"
    / "rule"
    / "iwxxm.sch"
)
SCH_NS = {"sch": "http://purl.oclc.org/dsdl/schematron"}


def mine_tac_validation() -> dict[str, Any]:
    """Build TAC validation cards from tac-validate issue registry."""
    from tac_validate.issue_registry import catalog_entries

    rules: list[dict[str, Any]] = []
    for spec in catalog_entries():
        rules.append(
            {
                "id": f"TAC.{spec.code}",
                "code": spec.code,
                "label": spec.code.replace("_", " ").title(),
                "severity": spec.severity,
                "message_template": spec.message_template,
                "product": spec.product,
                "tags": list(spec.tags),
            }
        )
    rules.sort(key=lambda r: r["id"])
    return {
        "schema_version": 1,
        "source": "tac_validate.issue_registry.catalog_entries",
        "rules": rules,
    }


def mine_iwxxm_validation(*, sch_path: Path = SCH) -> dict[str, Any]:
    """Build IWXXM validation cards from pinned Schematron asserts."""
    if not sch_path.is_file():
        raise FileNotFoundError(f"missing Schematron: {sch_path}")
    tree = ET.parse(sch_path)
    root = tree.getroot()
    asserts: list[dict[str, Any]] = []
    for pattern in root.findall("sch:pattern", SCH_NS):
        pattern_id = pattern.get("id") or "pattern"
        for rule in pattern.findall("sch:rule", SCH_NS):
            context = rule.get("context") or ""
            for assert_el in rule.findall("sch:assert", SCH_NS):
                test = assert_el.get("test") or ""
                text = "".join(assert_el.itertext()).strip()
                # Prefer leading RULE.ID: prefix when present
                rule_id = pattern_id
                if ":" in text:
                    head = text.split(":", 1)[0].strip()
                    if "." in head and " " not in head:
                        rule_id = head
                asserts.append(
                    {
                        "id": rule_id,
                        "pattern_id": pattern_id,
                        "label": text[:120] + ("…" if len(text) > 120 else ""),
                        "context": context,
                        "test": test,
                        "enabled_default": True,
                    }
                )
    # Dedupe by id keeping first
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for item in asserts:
        if item["id"] in seen:
            continue
        seen.add(item["id"])
        unique.append(item)
    unique.sort(key=lambda a: a["id"])
    return {
        "schema_version": 1,
        "source": str(sch_path.relative_to(REPO_ROOT)),
        "iwxxm_version": "2025-2",
        "asserts": unique,
    }


def dump_yaml(data: dict[str, Any]) -> str:
    """Stable YAML dump."""
    return yaml.safe_dump(
        data,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=100,
    )


def main(argv: list[str] | None = None) -> int:
    """CLI entry."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    tac = mine_tac_validation()
    iwxxm = mine_iwxxm_validation()
    tac_text = dump_yaml(tac)
    iwxxm_text = dump_yaml(iwxxm)

    if args.check:
        ok = True
        for path, text, label in (
            (TAC_OUT, tac_text, "TAC"),
            (IWXXM_OUT, iwxxm_text, "IWXXM"),
        ):
            if not path.is_file():
                print(f"missing {label} catalog: {path}", file=sys.stderr)
                ok = False
                continue
            if path.read_text(encoding="utf-8") != text:
                print(f"{label} validation catalog drift: {path}", file=sys.stderr)
                ok = False
        if not ok:
            return 1
        print(
            f"OK: TAC rules={len(tac['rules'])} IWXXM asserts={len(iwxxm['asserts'])}"
        )
        return 0

    DATA.mkdir(parents=True, exist_ok=True)
    TAC_OUT.write_text(tac_text, encoding="utf-8")
    IWXXM_OUT.write_text(iwxxm_text, encoding="utf-8")
    print(f"Wrote {TAC_OUT} ({len(tac['rules'])} rules)")
    print(f"Wrote {IWXXM_OUT} ({len(iwxxm['asserts'])} asserts)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
