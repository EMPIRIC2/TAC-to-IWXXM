"""TC-EV035-004 - encode / SCH / bulletin cite parity (full stack)."""

from __future__ import annotations

import pytest
from tests.provenance._helpers import VALID_ROLES, VALID_STATUSES, load_map


def test_tc_ev035_004_fullstack_nonempty() -> None:
    data = load_map()
    assert data["full_stack_rules"], "full_stack_rules must list revisited ids"


@pytest.mark.parametrize(
    "rule_id",
    [
        "VONA_AHL_WM_LM",
        "VONA_FM205_PACKAGE",
        "VONA_GUIDANCE_SILENT",
        "IWXXM_SCH_PIN",
        "US_SCH_ABSENT",
        "AHL_SPECI_SP_LP",
    ],
)
def test_tc_ev035_004_fullstack_rule(rule_id: str) -> None:
    data = load_map()
    by_id = {r["rule_id"]: r for r in data["full_stack_rules"]}
    assert rule_id in by_id
    row = by_id[rule_id]
    assert row["status"] in VALID_STATUSES
    assert row["role"] in VALID_ROLES
    if row["status"] in {"ok", "paywall"}:
        assert row.get("source_url") or row.get("source_id")
    if row["status"] == "gap":
        assert row.get("ticket")
    if row["role"] == "iwxxm-validation" and row["status"] == "ok":
        assert row.get("pin_version"), f"{rule_id}: SCH/XSD needs pin_version"
        src = (row.get("source_url") or "") + (row.get("source_id") or "")
        assert "sch" in src.lower() or "iwxxm" in src.lower() or "schema" in src.lower()
