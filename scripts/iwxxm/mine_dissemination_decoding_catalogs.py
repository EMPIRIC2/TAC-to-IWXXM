#!/usr/bin/env python3
"""Mine Dissemination + Decoding library catalogs (EVPYL T-B3).

Writes:
  packages/tac2iwxxm/src/tac2iwxxm/data/dissemination_transforms.yaml
  packages/tac2iwxxm/src/tac2iwxxm/data/decoding_library_entries.yaml

Decoding entries are projected from ``decode_glossary.yaml`` (F9 SoT).
Dissemination transforms are the pattern-only first-party transform set
(envelope / topic_filename / bulletin_rewrap / checksum) — never credentials.

Usage
-----
::

    uv run python scripts/iwxxm/mine_dissemination_decoding_catalogs.py
    uv run python scripts/iwxxm/mine_dissemination_decoding_catalogs.py --check
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA = REPO_ROOT / "packages" / "tac2iwxxm" / "src" / "tac2iwxxm" / "data"
DISSEM_OUT = DATA / "dissemination_transforms.yaml"
DECODE_OUT = DATA / "decoding_library_entries.yaml"
GLOSSARY = DATA / "decode_glossary.yaml"  # overlay only; full table via load_glossary()

FIRST_PARTY_TRANSFORMS: tuple[dict[str, str], ...] = (
    {
        "id": "envelope",
        "type": "envelope",
        "label": "Message envelope",
        "note": "Pattern-only wrapper; no destination URIs or credentials.",
    },
    {
        "id": "topic_filename",
        "type": "topic_filename",
        "label": "Topic / filename pattern",
        "note": "Template for topic or file name tokens only.",
    },
    {
        "id": "bulletin_rewrap",
        "type": "bulletin_rewrap",
        "label": "Bulletin rewrap",
        "note": "Bulletin header/footer pattern rewrite.",
    },
    {
        "id": "checksum",
        "type": "checksum",
        "label": "Checksum annotation",
        "note": "Integrity annotation pattern; no secrets.",
    },
)


def mine_dissemination() -> dict[str, Any]:
    """Build dissemination transform catalog."""
    return {
        "schema_version": 1,
        "source": "first-party pattern-only transforms (ADR-021/029/030)",
        "transforms": list(FIRST_PARTY_TRANSFORMS),
        "annotations": [],
    }


def mine_decoding() -> dict[str, Any]:
    """Project decoding library entries from F9 glossary (official + overlay)."""
    # Import after path setup so package data resolves under uv run.
    from tac2iwxxm.glossary import load_glossary

    glossary = load_glossary()
    entries: list[dict[str, str]] = []
    for token, meaning in sorted(glossary.items()):
        entries.append(
            {
                "id": f"DEC.{token}",
                "token": token,
                "label": token,
                "explanation": meaning,
                "source": "decode_tac",
            }
        )
    return {
        "schema_version": 1,
        "source": "tac2iwxxm.glossary.load_glossary (official + decode_glossary.yaml)",
        "entries": entries,
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

    dissem = mine_dissemination()
    decode = mine_decoding()
    dissem_text = dump_yaml(dissem)
    decode_text = dump_yaml(decode)

    if args.check:
        ok = True
        for path, text, label in (
            (DISSEM_OUT, dissem_text, "dissemination"),
            (DECODE_OUT, decode_text, "decoding"),
        ):
            if not path.is_file():
                print(f"missing {label} catalog: {path}", file=sys.stderr)
                ok = False
                continue
            if path.read_text(encoding="utf-8") != text:
                print(f"{label} catalog drift: {path}", file=sys.stderr)
                ok = False
        if not ok:
            return 1
        print(
            f"OK: transforms={len(dissem['transforms'])} "
            f"decode_entries={len(decode['entries'])}"
        )
        return 0

    DATA.mkdir(parents=True, exist_ok=True)
    DISSEM_OUT.write_text(dissem_text, encoding="utf-8")
    DECODE_OUT.write_text(decode_text, encoding="utf-8")
    print(f"Wrote {DISSEM_OUT} ({len(dissem['transforms'])} transforms)")
    print(f"Wrote {DECODE_OUT} ({len(decode['entries'])} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
