"""TC-F15-001 / E11-22 — ISSUE_CATALOG drift vs ``issue_registry.ISSUES``.

Committed ``docs/domain/rules/ISSUE_CATALOG.{md,json}`` must match a fresh
export from the registry (``make catalog-regen``).
"""

from __future__ import annotations

import json
from pathlib import Path

from tac_validate.issue_registry import ISSUES

REPO = Path(__file__).resolve().parents[3]
CATALOG_JSON = REPO / "docs" / "domain" / "rules" / "ISSUE_CATALOG.json"
CATALOG_MD = REPO / "docs" / "domain" / "rules" / "ISSUE_CATALOG.md"


def _registry_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for spec in ISSUES:
        rows.append(
            {
                "code": spec.code,
                "severity": spec.severity,
                "message_template": spec.message_template,
                "product": spec.product,
                "tags": list(spec.tags),
            }
        )
    rows.sort(key=lambda r: str(r["code"]))
    return rows


def test_issue_catalog_json_matches_registry() -> None:
    assert CATALOG_JSON.is_file(), "missing ISSUE_CATALOG.json — run make catalog-regen"
    payload = json.loads(CATALOG_JSON.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert "generated from tac_validate.issue_registry" in payload["source"]
    assert payload["issues"] == _registry_rows()


def test_issue_catalog_md_lists_every_code() -> None:
    assert CATALOG_MD.is_file(), "missing ISSUE_CATALOG.md — run make catalog-regen"
    text = CATALOG_MD.read_text(encoding="utf-8")
    assert "generated from tac_validate.issue_registry" in text
    assert "Registry module pending" not in text
    for spec in ISSUES:
        assert f"`{spec.code}`" in text, f"catalog MD missing {spec.code}"
        assert f"`{spec.severity}`" in text
