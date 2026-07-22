"""TC-F20-002 — TAF annex3 golden expansion (S020 / EV-015 T2.1 / T4).

Asserts annex3 golden pack covers TAF exceptional themes (NIL/CNL/AMD/COR/CAVOK).
Convert M-parse / M-xsd / M-sch / M-golden assertions land with T2.2.
"""

from __future__ import annotations

import json
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "annex3_golden"
MANIFEST_PATH = FIXTURES / "manifest.json"

TAF_CASE_IDS = (
    "taf_basic",
    "taf_nil",
    "taf_cnl",
    "taf_amd",
    "taf_cor",
    "taf_cavok",
)


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_tc_f20_002_annex3_taf_themes_present() -> None:
    data = _load_manifest()
    ids = {c["id"] for c in data["cases"]}
    assert set(TAF_CASE_IDS) <= ids
    for case in data["cases"]:
        if case["id"] in TAF_CASE_IDS:
            assert case["product"] == "TAF"
            assert case.get("theme") == "T4"
            assert (FIXTURES / case["tac"]).is_file()
            assert (FIXTURES / case["golden"]).is_file()
