"""TC-EV035-001 — dig inventory completeness."""

from __future__ import annotations

import pytest
from tests.provenance._helpers import (
    VALID_ROLES,
    VALID_STATUSES,
    load_map,
    mining_note_files,
)


@pytest.mark.parametrize(
    "dig_path",
    [p for p in mining_note_files()],
    ids=lambda p: p.name,
)
def test_tc_ev035_001_dig_indexed(dig_path) -> None:
    """Every *-mining-notes.md is indexed in PROVENANCE_MAP digs[]."""
    data = load_map()
    rel = f"docs/domain/mining/{dig_path.name}"
    by_path = {d["path"]: d for d in data["digs"]}
    assert rel in by_path, f"orphan dig not in PROVENANCE_MAP: {rel}"
    row = by_path[rel]
    assert dig_path.is_file()
    assert row["status"] in VALID_STATUSES
    assert row.get("date_mined"), f"{rel}: empty date_mined"
    assert isinstance(row.get("products"), list)
    assert row.get("roles"), f"{rel}: roles empty"
    assert set(row["roles"]) <= VALID_ROLES
    if row["status"] in {"ok", "paywall"}:
        assert row.get("source_url") or row.get("source_id"), (
            f"{rel}: ok/paywall needs source_url or source_id"
        )
    if row["status"] == "gap":
        assert row.get("ticket"), f"{rel}: gap needs ticket"


def test_tc_ev035_001_no_extra_dig_rows() -> None:
    """Map dig paths must exist on disk (no stale index)."""
    data = load_map()
    on_disk = {f"docs/domain/mining/{p.name}" for p in mining_note_files()}
    for row in data["digs"]:
        assert row["path"] in on_disk, f"stale dig row: {row['path']}"
        assert row["path"].endswith("-mining-notes.md")
