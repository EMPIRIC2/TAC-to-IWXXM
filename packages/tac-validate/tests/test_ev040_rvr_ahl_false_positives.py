"""EV-040 - document and fix RVR tendency + AHL YYGGgg false positives."""

from __future__ import annotations

from pathlib import Path

from tac_validate import lint

REPO = Path(__file__).resolve().parents[3]
A3_1 = REPO / "apps" / "frontend" / "src" / "fixtures" / "examples" / "bodies" / "metar_a3_1.tac"
AHL_A31 = REPO / "packages" / "tac2iwxxm" / "tests" / "fixtures" / "ahl" / "sa_metar_a3_1_bulletin.txt"


def test_wmo_a3_1_rvr_tendency_u_not_invalid_rvr() -> None:
    """WMO A3-1 ``R12/1000U`` is valid ICAO RVR with upward tendency (FP fixed)."""
    report = lint(A3_1.read_text(encoding="utf-8"), product="METAR")
    codes = [i.code for i in report.issues]
    assert "INVALID_RVR" not in codes
    assert report.ok is True


def test_ahl_yyggg_not_invalid_visibility() -> None:
    """AHL ``YYGGgg`` (e.g. 121200) must not emit INVALID_VISIBILITY (FP fixed)."""
    report = lint(AHL_A31.read_text(encoding="utf-8"), product="METAR")
    codes = [i.code for i in report.issues]
    assert "INVALID_VISIBILITY" not in codes
    assert not any(i.severity == "error" for i in report.issues)
    assert report.ok is True
