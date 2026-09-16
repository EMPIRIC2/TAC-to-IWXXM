#!/usr/bin/env python3
"""Mine TAC + IWXXM validation library catalogs (EVPYL T-B2 / #1199).

Writes:
  packages/tac2iwxxm/src/tac2iwxxm/data/tac_validation_rules.yaml
  packages/tac2iwxxm/src/tac2iwxxm/data/iwxxm_validation_asserts.yaml

IWXXM asserts include core ``iwxxm.sch`` plus latest WMO foundation Schematron
(metce / opm / saf / collect). OpenGIS SCH under ``externalSchema`` is excluded.

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
VENDOR_IWXXM = REPO_ROOT / "vendor" / "schemas" / "iwxxm"
SCH_CORE = VENDOR_IWXXM / "2025-2" / "IWXXM" / "rule" / "iwxxm.sch"
# Backward-compatible alias used by older tests / callers.
SCH = SCH_CORE
WMO_FOUNDATION = VENDOR_IWXXM / "externalSchema" / "schemas.wmo.int"
SCH_NS = {"sch": "http://purl.oclc.org/dsdl/schematron"}

# Latest pin per family (D-EVPYL-R-06).
FOUNDATION_PINS: tuple[tuple[str, str, str], ...] = (
    ("wmo-metce", "metce", "1.2"),
    ("wmo-opm", "opm", "1.2"),
    ("wmo-saf", "saf", "1.1"),
    ("wmo-collect", "collect", "1.2"),
)


def iwxxm_sch_sources() -> list[tuple[Path, str]]:
    """Return (path, authority) pairs for Schematron files to mine."""
    sources: list[tuple[Path, str]] = [(SCH_CORE, "wmo-iwxxm")]
    for authority, family, version in FOUNDATION_PINS:
        path = WMO_FOUNDATION / family / version / "rule" / f"{family}.sch"
        sources.append((path, authority))
    return sources


def mine_tac_validation() -> dict[str, Any]:
    """Build TAC validation cards from tac-validate issue registry."""
    from tac_validate.issue_registry import catalog_entries

    rules: list[dict[str, Any]] = [
        {
            "id": f"TAC.{spec.code}",
            "code": spec.code,
            "label": spec.code.replace("_", " ").title(),
            "severity": spec.severity,
            "message_template": spec.message_template,
            "product": spec.product,
            "tags": list(spec.tags),
        }
        for spec in catalog_entries()
    ]
    rules.sort(key=lambda r: r["id"])
    return {
        "schema_version": 1,
        "source": "tac_validate.issue_registry.catalog_entries",
        "rules": rules,
    }


def mine_sch_file(
    sch_path: Path,
    *,
    authority: str,
    namespace_ids: bool = False,
) -> list[dict[str, Any]]:
    """Parse one Schematron file into assert card dicts.

    Parameters
    ----------
    sch_path :
        Path to a ``.sch`` file.
    authority :
        Authority tag stored on each assert (e.g. ``wmo-iwxxm``).
    namespace_ids :
        When True, prefix assert ids with ``{authority}:`` to avoid collisions
        across foundation Schematron files.

    Returns
    -------
    list[dict[str, Any]]
        Assert cards (may include duplicate ids before catalog-level dedupe).

    Raises
    ------
    FileNotFoundError
        If ``sch_path`` is missing.
    """
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
                rule_id = pattern_id
                if ":" in text:
                    head = text.split(":", 1)[0].strip()
                    if "." in head and " " not in head:
                        rule_id = head
                if namespace_ids:
                    rule_id = f"{authority}:{rule_id}"
                asserts.append(
                    {
                        "id": rule_id,
                        "pattern_id": pattern_id,
                        "label": text[:120] + ("…" if len(text) > 120 else ""),
                        "context": context,
                        "test": test,
                        "enabled_default": True,
                        "authority": authority,
                    }
                )
    return asserts


def mine_iwxxm_validation(*, sch_path: Path | None = None) -> dict[str, Any]:
    """Build IWXXM validation cards from pinned Schematron asserts.

    When ``sch_path`` is set, mines only that file (authority ``wmo-iwxxm``) for
    backward-compatible single-file callers. Otherwise mines core ``iwxxm.sch``
    plus latest WMO foundation Schematron pins.
    """
    if sch_path is not None:
        items = mine_sch_file(sch_path, authority="wmo-iwxxm", namespace_ids=False)
        rel = (
            str(sch_path.relative_to(REPO_ROOT))
            if sch_path.is_relative_to(REPO_ROOT)
            else str(sch_path)
        )
        return {
            "schema_version": 1,
            "source": rel,
            "sources": [{"path": rel, "authority": "wmo-iwxxm"}],
            "iwxxm_version": "2025-2",
            "asserts": _dedupe_asserts(items),
        }

    all_items: list[dict[str, Any]] = []
    sources_meta: list[dict[str, str]] = []
    for path, authority in iwxxm_sch_sources():
        namespace = authority != "wmo-iwxxm"
        all_items.extend(
            mine_sch_file(path, authority=authority, namespace_ids=namespace)
        )
        sources_meta.append(
            {
                "path": str(path.relative_to(REPO_ROOT)),
                "authority": authority,
            }
        )
    unique = _dedupe_asserts(all_items)
    return {
        "schema_version": 1,
        "source": sources_meta[0]["path"] if sources_meta else "",
        "sources": sources_meta,
        "iwxxm_version": "2025-2",
        "asserts": unique,
    }


def _dedupe_asserts(asserts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Dedupe by id keeping first; sort by id."""
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for item in asserts:
        if item["id"] in seen:
            continue
        seen.add(item["id"])
        unique.append(item)
    unique.sort(key=lambda a: a["id"])
    return unique


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
