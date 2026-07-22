"""TC-F20-003 — SPECI annex3 golden expansion (S020 / EV-015 T3.5 / S3).

Asserts annex3 golden pack covers SPECI exceptional themes (NIL/CAVOK/NSC/NCD/
NOSIG/NSW-trend/VV/// / wx // / RVR / wind-sector + basic/COR).
Convert M-parse / M-xsd / M-sch / M-golden assertions land with T3.6.
"""

from __future__ import annotations

import json
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "annex3_golden"
MANIFEST_PATH = FIXTURES / "manifest.json"

SPECI_CASE_IDS = (
    "speci_basic",
    "speci_cor",
    "speci_nil",
    "speci_cavok",
    "speci_nsc",
    "speci_ncd",
    "speci_nosig",
    "speci_nsw_trend",
    "speci_vv_not_obs",
    "speci_wx_slash",
    "speci_rvr",
    "speci_wind_sector",
)


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_tc_f20_003_annex3_speci_themes_present() -> None:
    data = _load_manifest()
    ids = {c["id"] for c in data["cases"]}
    assert set(SPECI_CASE_IDS) <= ids
    for case in data["cases"]:
        if case["id"] in SPECI_CASE_IDS:
            assert case["product"] == "SPECI"
            assert case.get("theme") == "S3"
            assert (FIXTURES / case["tac"]).is_file()
            assert (FIXTURES / case["golden"]).is_file()
            assert "iwxxm:SPECI" in (FIXTURES / case["golden"]).read_text(encoding="utf-8")
