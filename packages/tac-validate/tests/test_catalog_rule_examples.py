"""The operator catalog example map stays tied to packaged tac-validate fixtures."""

from __future__ import annotations

import json
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent / "fixtures"
REPO = Path(__file__).resolve().parents[3]
EXAMPLES = REPO / "apps" / "frontend" / "src" / "data" / "ruleCatalogExamples.json"


def _text(rel: str) -> str:
    return (FIXTURES / rel).read_text(encoding="utf-8").strip()


def _expected() -> dict[str, dict[str, str]]:
    manifest = json.loads((FIXTURES / "manifest.json").read_text(encoding="utf-8"))
    out: dict[str, dict[str, str]] = {}
    for case in manifest["negative"]:
        theme = case.get("theme") or ""
        product = case.get("product")
        row = {"fail": _text(case["tac"])}
        accept = next(
            (
                item
                for item in manifest["accept"]
                if theme and item.get("product") == product and item.get("theme") == theme
            ),
            None,
        )
        if accept is not None:
            row["pass"] = _text(accept["tac"])
        for code in case.get("expected_codes") or []:
            out.setdefault(code, row)
    return {code: out[code] for code in sorted(out)}


def test_catalog_rule_examples_match_packaged_fixtures() -> None:
    """Each catalog sample is a fixture report, and unused rules are omitted."""
    packaged = json.loads(EXAMPLES.read_text(encoding="utf-8"))
    assert packaged == _expected()
