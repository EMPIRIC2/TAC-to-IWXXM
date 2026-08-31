"""TC-EV094 — catalog hygiene + #1098 closeout (M7).

[Corpus: product §F36] [Corpus: domain-profiles] [Corpus: tests §TC-EV094-001]
"""

from __future__ import annotations

from pathlib import Path

import yaml

_REPO = Path(__file__).resolve().parents[3]
_CATALOG = _REPO / "docs" / "domain" / "profiles" / "catalog.yaml"

THIN_COMPAT_IDS = (
    "UK_METOFFICE",
    "BR_DECEA",
    "KR_KMA",
    "JP_JMA",
    "IN_IMD",
    "HK_HKO",
)


def test_tc_ev094_001_catalog_thin_compat_implemented() -> None:
    """Six thin/compat packs are implemented after EV-094 deepen (#1098)."""
    data = yaml.safe_load(_CATALOG.read_text(encoding="utf-8"))
    by_id = {p["id"]: p for p in data["profiles"]}
    for pid in THIN_COMPAT_IDS:
        row = by_id[pid]
        assert row["kind"] == "semantic", pid
        assert row["status"] == "implemented", pid
        impl = row["implementation"]
        assert impl.get("issue") == "#1098", pid
        assert "EV-094" in str(impl.get("cycle", "")), pid
        # Residual corpus gaps OK; do not leave "until #1098" blockers.
        gaps = "\n".join(str(g) for g in (row.get("gaps") or []))
        assert "until #1098" not in gaps, pid
        assert "Catalog status stays" not in gaps, pid
        # Every gap entry must be a plain string (quoted if it contains : or #).
        for g in row.get("gaps") or []:
            assert isinstance(g, str), (pid, g)


def test_tc_ev094_001_catalog_speci_kr_jp_and_in_lint() -> None:
    """KR/JP include SPECI; IN_IMD documents in_imd lint overlay."""
    data = yaml.safe_load(_CATALOG.read_text(encoding="utf-8"))
    by_id = {p["id"]: p for p in data["profiles"]}
    assert "SPECI" in by_id["KR_KMA"]["products"]
    assert "SPECI" in by_id["JP_JMA"]["products"]
    lint = by_id["IN_IMD"].get("lint_profile") or {}
    assert lint.get("id") == "in_imd"
    assert lint.get("registry_code") == "IN_TAF_TX_TN_OMITTED"
    assert "SIGMET" in by_id["HK_HKO"]["products"]
    assert "VAA" in by_id["HK_HKO"]["products"]
