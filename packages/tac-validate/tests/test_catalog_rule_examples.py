"""The operator catalog example map stays tied to packaged tac-validate fixtures."""

from __future__ import annotations

import json
import re
from pathlib import Path

from tac2iwxxm.profile_registry import known_semantic_profile_ids
from tac_validate.issue_registry import ISSUES

FIXTURES = Path(__file__).resolve().parent / "fixtures"
REPO = Path(__file__).resolve().parents[3]
EXAMPLES = REPO / "apps" / "frontend" / "src" / "data" / "ruleCatalogExamples.json"
IWXXM_CATALOG = REPO / "apps" / "backend" / "src" / "services" / "iwxxm_validation_catalog.py"


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
    """Fixture-backed samples keep the packaged fail text and the matching pass."""
    packaged = json.loads(EXAMPLES.read_text(encoding="utf-8"))
    expected = _expected()
    for code, row in expected.items():
        assert packaged[code]["fail"] == row["fail"]
        if "pass" in row:
            assert packaged[code]["pass"] == row["pass"]


def test_every_catalog_item_has_pass_and_fail() -> None:
    """Lint codes, conversion profiles, and IWXXM checks each have both examples."""
    packaged = json.loads(EXAMPLES.read_text(encoding="utf-8"))
    iwxxm_codes = re.findall(
        r'"code": "([A-Z0-9_]+)"',
        IWXXM_CATALOG.read_text(encoding="utf-8"),
    )
    required = {spec.code for spec in ISSUES}
    required.update(known_semantic_profile_ids())
    required.update(iwxxm_codes)
    missing = sorted(
        code
        for code in required
        if not str((packaged.get(code) or {}).get("pass") or "").strip()
        or not str((packaged.get(code) or {}).get("fail") or "").strip()
    )
    assert missing == []
