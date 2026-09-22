#!/usr/bin/env python3
"""Mine Conversion library IWXXM schema blocks from pinned vendor XSDs (EVPYL T-B1 / #1198).

Reads WMO IWXXM (default 2025-2) plus national extension XSDs when present and writes
``packages/tac2iwxxm/src/tac2iwxxm/data/conversion_schema_blocks.yaml``.

National lines with **no** vendored XSD tree (AU/BR/HK/IN/JP/KR/NZ/UK) are listed in
``NATIONAL_VENDOR_EXPECTATIONS`` and skipped until M6 sync pins them (#1198). Do not
invent stub XSD trees.

Usage
-----
::

    uv run python scripts/iwxxm/mine_conversion_schema_blocks.py
    uv run python scripts/iwxxm/mine_conversion_schema_blocks.py --check
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
VENDOR = REPO_ROOT / "vendor" / "schemas"
OUT_PATH = (
    REPO_ROOT
    / "packages"
    / "tac2iwxxm"
    / "src"
    / "tac2iwxxm"
    / "data"
    / "conversion_schema_blocks.yaml"
)

XS_NS = {"xs": "http://www.w3.org/2001/XMLSchema"}
SKIP_WMO_FILES = frozenset(
    {"iwxxm.xsd", "gmliwxxm.xsd", "qvaci.xsd", "iwxxm-collect.xsd"}
)
_CAMEL_SPLIT = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")

# (national_line, vendor_subdir, version_dir, authority, qname_prefix)
# US/CA are present today; others await vendor pins (#1198 unblock).
NATIONAL_VENDOR_EXPECTATIONS: tuple[tuple[str, str, str, str, str], ...] = (
    ("US_FAA_NWS", "iwxxm-us", "3.0", "us", "iwxxm-us"),
    ("CA_ECCC", "iwxxm-ca", "3.0", "ca", "iwxxm-ca"),
    ("AU_BOM", "iwxxm-au", "3.0", "au", "iwxxm-au"),
    ("BR_DECEA", "iwxxm-br", "3.0", "br", "iwxxm-br"),
    ("HK_HKO", "iwxxm-hk", "3.0", "hk", "iwxxm-hk"),
    ("IN_IMD", "iwxxm-in", "3.0", "in", "iwxxm-in"),
    ("JP_JMA", "iwxxm-jp", "3.0", "jp", "iwxxm-jp"),
    ("KR_KMA", "iwxxm-kr", "3.0", "kr", "iwxxm-kr"),
    ("NZ_CAA_MET", "iwxxm-nz", "3.0", "nz", "iwxxm-nz"),
    ("UK_METOFFICE", "iwxxm-uk", "3.0", "uk", "iwxxm-uk"),
)


def _label_from_name(name: str) -> str:
    """Turn CamelCase / kebab into a short operator label."""
    cleaned = name.removesuffix("Type").removesuffix("Extension")
    parts = _CAMEL_SPLIT.sub(" ", cleaned).replace("_", " ").replace("-", " ")
    return " ".join(parts.split())


def _card_id(prefix: str, name: str) -> str:
    base = name.removesuffix("Type")
    return f"{prefix}:{base}"


def _mine_xsd(
    path: Path,
    *,
    authority: str,
    qname_prefix: str,
    national_lines: list[str],
) -> dict[str, Any] | None:
    """Mine one XSD into a schema block dict, or None when empty."""
    tree = ET.parse(path)
    root = tree.getroot()
    cards: list[dict[str, str]] = []
    seen: set[str] = set()

    for elem in root.findall("./xs:element", XS_NS):
        name = elem.get("name")
        if not name or name in seen:
            continue
        if name.endswith("Property") or name.startswith("Abstract"):
            continue
        seen.add(name)
        cards.append(
            {
                "id": _card_id(qname_prefix, name),
                "label": _label_from_name(name),
                "xsd_name": name,
            }
        )

    for ctype in root.findall("./xs:complexType", XS_NS):
        name = ctype.get("name")
        if not name or name.endswith("PropertyType"):
            continue
        local = name.removesuffix("Type")
        if local in seen or name in seen:
            continue
        seen.add(local)
        cards.append(
            {
                "id": _card_id(qname_prefix, local),
                "label": _label_from_name(local),
                "xsd_name": name,
            }
        )

    if not cards:
        return None

    stem = path.stem
    block_id = f"{authority}-{stem}".lower().replace("_", "-")
    return {
        "id": block_id,
        "label": _label_from_name(stem),
        "authority": authority,
        "national_lines": national_lines,
        "xsd_path": str(path.relative_to(REPO_ROOT)),
        "cards": sorted(cards, key=lambda c: c["id"]),
    }


def awaiting_national_vendor_pins(*, vendor: Path | None = None) -> list[str]:
    """Return national_line ids whose expected vendor dirs are not present."""
    root = vendor if vendor is not None else VENDOR
    missing: list[str] = []
    for national_line, subdir, version, _auth, _qname in NATIONAL_VENDOR_EXPECTATIONS:
        if not (root / subdir / version).is_dir():
            missing.append(national_line)
    return missing


def mine_catalog(*, iwxxm_version: str = "2025-2") -> dict[str, Any]:
    """Build the full conversion schema-blocks catalog."""
    blocks: list[dict[str, Any]] = []

    wmo_dir = VENDOR / "iwxxm" / iwxxm_version / "IWXXM"
    if not wmo_dir.is_dir():
        raise FileNotFoundError(f"missing WMO IWXXM tree: {wmo_dir}")
    for xsd in sorted(wmo_dir.glob("*.xsd")):
        if xsd.name in SKIP_WMO_FILES:
            continue
        block = _mine_xsd(
            xsd,
            authority="wmo",
            qname_prefix="iwxxm",
            national_lines=["*"],  # baseline for every national line
        )
        if block:
            blocks.append(block)

    skipped: list[str] = []
    for (
        national_line,
        subdir,
        version,
        authority,
        qname_prefix,
    ) in NATIONAL_VENDOR_EXPECTATIONS:
        national_dir = VENDOR / subdir / version
        if not national_dir.is_dir():
            skipped.append(national_line)
            continue
        for xsd in sorted(national_dir.glob("*.xsd")):
            block = _mine_xsd(
                xsd,
                authority=authority,
                qname_prefix=qname_prefix,
                national_lines=[national_line],
            )
            if block:
                blocks.append(block)

    catalog: dict[str, Any] = {
        "schema_version": 1,
        "source": "vendor/schemas (read-only pins)",
        "iwxxm_version": iwxxm_version,
        "blocks": blocks,
    }
    if skipped:
        # Residual metadata for Profile Builder / operators of the mine script.
        # Does not invent XSD content (#1198).
        catalog["national_residuals"] = {
            "awaiting_vendor_pins": skipped,
            "unblock": "M6 vendor sync must pin national extension XSD trees",
        }
    return catalog


def dump_catalog(catalog: dict[str, Any]) -> str:
    """Serialize catalog YAML with stable key order."""
    return yaml.safe_dump(
        catalog,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=100,
    )


def main(argv: list[str] | None = None) -> int:
    """CLI entry."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--version",
        default="2025-2",
        help="WMO IWXXM vendor version directory (default: 2025-2)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 when committed catalog differs from a fresh mine",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=OUT_PATH,
        help="Output YAML path",
    )
    args = parser.parse_args(argv)

    catalog = mine_catalog(iwxxm_version=args.version)
    text = dump_catalog(catalog)
    if args.check:
        if not args.out.is_file():
            print(f"missing catalog: {args.out}", file=sys.stderr)
            return 1
        existing = args.out.read_text(encoding="utf-8")
        if existing != text:
            print(
                f"conversion schema blocks catalog drift: re-run "
                f"scripts/iwxxm/mine_conversion_schema_blocks.py "
                f"(expected {len(text)} bytes, got {len(existing)})",
                file=sys.stderr,
            )
            return 1
        print(f"OK: {args.out} matches mine ({len(catalog['blocks'])} blocks)")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"Wrote {args.out} ({len(catalog['blocks'])} blocks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
