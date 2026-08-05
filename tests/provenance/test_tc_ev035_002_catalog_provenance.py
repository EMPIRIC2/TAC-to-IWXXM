"""TC-EV035-002 — ISSUE_CATALOG code ↔ provenance."""

from __future__ import annotations

import json

import pytest
from tests.provenance._helpers import (
    CATALOG_JSON,
    VALID_CONSUMERS,
    VALID_STATUSES,
    load_map,
)


def _catalog_codes() -> list[str]:
    issues = json.loads(CATALOG_JSON.read_text(encoding="utf-8"))["issues"]
    return [i["code"] for i in issues]


@pytest.mark.parametrize("code", _catalog_codes(), ids=lambda c: c)
def test_tc_ev035_002_catalog_code_provenance(code: str) -> None:
    data = load_map()
    by_code = {r["code"]: r for r in data["catalog_codes"]}
    assert code in by_code, f"ISSUE_CATALOG code missing from PROVENANCE_MAP: {code}"
    row = by_code[code]
    assert row["status"] in VALID_STATUSES
    assert row.get("consumer") in VALID_CONSUMERS
    if row["status"] in {"ok", "paywall"}:
        assert row.get("source_id") or row.get("source_url"), (
            f"{code}: ok/paywall needs cite"
        )
    if row["status"] == "gap":
        assert row.get("ticket"), f"{code}: gap needs ticket/session note"


def test_tc_ev035_002_no_orphan_map_codes() -> None:
    data = load_map()
    catalog = set(_catalog_codes())
    for row in data["catalog_codes"]:
        assert row["code"] in catalog, f"orphan map code: {row['code']}"
