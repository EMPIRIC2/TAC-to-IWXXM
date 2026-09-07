"""TC-F15-005 / R7 - METAR↔SPECI adjacency; no silent cross-product pass (T4.3)."""

from __future__ import annotations

from pathlib import Path

from tac_validate import lint
from tac_validate.issue_registry import by_code

from tac2iwxxm import convert

ANNEX3 = Path(__file__).resolve().parent / "fixtures" / "annex3_golden"


def test_r7_lint_rejects_speci_tac_under_metar_product() -> None:
    tac = (ANNEX3 / "speci_basic.tac").read_text(encoding="utf-8")
    report = lint(tac, product="METAR")
    assert report.ok is False
    codes = {i.code for i in report.issues}
    assert "MISSING_PRODUCT_KEYWORD" in codes
    assert by_code("MISSING_PRODUCT_KEYWORD").severity == "error"


def test_r7_lint_rejects_metar_tac_under_speci_product() -> None:
    tac = (ANNEX3 / "metar_basic.tac").read_text(encoding="utf-8")
    report = lint(tac, product="SPECI")
    assert report.ok is False
    assert "MISSING_PRODUCT_KEYWORD" in {i.code for i in report.issues}


def test_r7_convert_rejects_cross_product() -> None:
    speci = (ANNEX3 / "speci_basic.tac").read_text(encoding="utf-8")
    metar = (ANNEX3 / "metar_basic.tac").read_text(encoding="utf-8")
    bad_m = convert(speci, product="METAR", profile="annex3", iwxxm_version="2025-2")
    bad_s = convert(metar, product="SPECI", profile="annex3", iwxxm_version="2025-2")
    assert bad_m.ok is False
    assert bad_s.ok is False
    assert any(i.code == "PARSE_ERROR" for i in bad_m.issues)
    assert any(i.code == "PARSE_ERROR" for i in bad_s.issues)
    assert any("product mismatch" in (i.message or "").lower() for i in bad_m.issues)
    assert any("product mismatch" in (i.message or "").lower() for i in bad_s.issues)


def test_r7_shared_pack_speci_and_metar_each_ok() -> None:
    """Same rule pack / convert path; product identity preserved."""
    for name, product in (("metar_basic", "METAR"), ("speci_basic", "SPECI"), ("speci_cor", "SPECI")):
        tac = (ANNEX3 / f"{name}.tac").read_text(encoding="utf-8")
        lint_report = lint(tac, product=product)
        assert lint_report.ok is True, name
        conv = convert(tac, product=product, profile="annex3", iwxxm_version="2025-2")
        assert conv.ok is True, name
        assert conv.product == product


def test_r7_bulletin_neighbor_keeps_per_report_identity() -> None:
    """Paired METAR+SPECI bulletin fragment: each report keeps its product."""
    bulletin = (
        "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=\nSPECI KJFK 232045Z 18012KT 5SM BKN015 15/07 A3005=\n"
    )
    lines = [ln.strip() for ln in bulletin.splitlines() if ln.strip()]
    assert lines[0].startswith("METAR")
    assert lines[1].startswith("SPECI")
    assert lint(lines[0], product="METAR").ok is True
    assert lint(lines[1], product="SPECI").ok is True
    assert lint(lines[1], product="METAR").ok is False
    assert convert(lines[0], product="METAR", profile="annex3", iwxxm_version="2025-2").ok is True
    assert convert(lines[1], product="SPECI", profile="annex3", iwxxm_version="2025-2").ok is True
