"""Smoke: WMO-782 permutation shards exist with ≥1000 rows per base issue."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

_SESSION_REPORTS = Path.home() / ".cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/wmo-782-metar-speci-quality/reports"
_PRIORITY = (
    "ODD_FIELD_ORDER",
    "FIRST_GROUPS_FORMAT",
    "CAVOK_CONDITIONS_NOT_MET",
    "WIND_VRB_MISUSE",
    "WIND_PHYSICAL_RANGE",
    "MISSING_MANDATORY_DIGIT_AS_SOLIDUS",
    "AUTO_VISIBILITY_NOT_OBSERVABLE",
    "VISIBILITY_SCALE_STEP",
    "DIRECTIONAL_VISIBILITY_FORMAT",
    "COR_MISPLACED",
    "AUTO_MISPLACED",
    "NIL_AUTO_CONFLICT",
)


@pytest.mark.skipif(
    not (_SESSION_REPORTS / "permutations").is_dir(),
    reason="session permutation shards not present on this machine",
)
@pytest.mark.parametrize("base_issue_id", _PRIORITY)
def test_priority_permutation_shard_has_at_least_1000_rows(base_issue_id: str) -> None:
    path = _SESSION_REPORTS / "permutations" / f"part-{base_issue_id}.csv"
    assert path.is_file(), f"missing shard {path}"
    with path.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) >= 1000
    assert all(row["base_issue_id"] == base_issue_id for row in rows)
    assert all(row["permutation_id"] for row in rows)
