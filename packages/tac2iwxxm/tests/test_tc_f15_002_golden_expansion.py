"""TC-F15-002 - R6 golden pack expansion stubs (S015 / EV-011 T4.1).

Asserts annex3 + iwxxm_us manifests cover COR/AUTO/CAVOK/NIL themes required by
HARD R6 / research catalog (convert fidelity deepened in T4.2).
"""

from __future__ import annotations

import json
from pathlib import Path

ANNEX3 = Path(__file__).resolve().parent / "fixtures" / "annex3_golden" / "manifest.json"
IWXXM_US = Path(__file__).resolve().parent / "fixtures" / "iwxxm_us_golden" / "manifest.json"


def test_tc_f15_002_annex3_r6_themes_present() -> None:
    data = json.loads(ANNEX3.read_text(encoding="utf-8"))
    ids = {c["id"] for c in data["cases"]}
    assert {"metar_cor", "metar_auto", "metar_cavok", "metar_nil", "speci_cor", "speci_basic"} <= ids


def test_tc_f15_002_iwxxm_us_r5_r8_themes_present() -> None:
    data = json.loads(IWXXM_US.read_text(encoding="utf-8"))
    ids = {c["id"] for c in data["cases"]}
    assert {"metar_us_ao2_slp", "metar_us_pk_wnd", "metar_us_auto_ao2", "speci_us_ao2", "speci_us_cor"} <= ids
