"""TC-F20-003 — SPECI iwxxm_us golden expansion (S020 / EV-015 T3.5 / S3).

Asserts iwxxm_us golden pack covers SPECI S3 themes (AO2/COR + CAVOK/NIL/NOSIG/AUTO).
Convert M-parse / M-xsd / M-sch / M-golden assertions land with T3.6.
"""

from __future__ import annotations

import json
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "iwxxm_us_golden"
MANIFEST_PATH = FIXTURES / "manifest.json"

SPECI_US_CASE_IDS = (
    "speci_us_ao2",
    "speci_us_cor",
    "speci_us_cavok",
    "speci_us_nil",
    "speci_us_nosig",
    "speci_us_auto",
)


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_tc_f20_003_iwxxm_us_speci_themes_present() -> None:
    data = _load_manifest()
    assert data.get("profile") == "iwxxm_us"
    ids = {c["id"] for c in data["cases"]}
    assert set(SPECI_US_CASE_IDS) <= ids
    for case in data["cases"]:
        if case["id"] in SPECI_US_CASE_IDS:
            assert case["product"] == "SPECI"
            assert case.get("theme") == "S3"
            assert (FIXTURES / case["tac"]).is_file()
            assert (FIXTURES / case["golden"]).is_file()
            golden = (FIXTURES / case["golden"]).read_text(encoding="utf-8")
            assert "iwxxm:SPECI" in golden
            if case["id"] != "speci_us_nil":
                assert "iwxxm-us" in golden or "weather.gov/iwxxm-us" in golden
