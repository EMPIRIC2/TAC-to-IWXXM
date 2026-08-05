"""TC-EV035-005 — dense behavioral asserts for revisited executable rules."""

from __future__ import annotations

import pytest
from tests.provenance._helpers import REPO, load_map


def test_tc_ev035_005_revisited_nonempty() -> None:
    data = load_map()
    assert data["revisited_executable"], "revisited_executable required"


@pytest.mark.parametrize(
    "rule_id",
    ["VONA_AHL_WM_LM", "VONA_FM205_PACKAGE", "IWXXM_SCH_PIN"],
)
def test_tc_ev035_005_dense_assert_sites(rule_id: str) -> None:
    data = load_map()
    by_id = {r["rule_id"]: r for r in data["revisited_executable"]}
    assert rule_id in by_id, f"missing revisited rule {rule_id}"
    row = by_id[rule_id]
    sites = row.get("assert_sites") or []
    assert len(sites) >= 3, f"{rule_id}: need ≥3 assert sites, got {len(sites)}"
    for site in sites:
        # Allow directory paths and markdown anchors (strip #frag)
        path_part = site.split("#", 1)[0]
        target = REPO / path_part
        assert target.exists(), f"{rule_id}: assert site missing: {site}"
        if target.is_file():
            assert target.stat().st_size > 0, f"{rule_id}: empty site {site}"
