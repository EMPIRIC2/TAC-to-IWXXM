"""Coverage helpers for F32 VONA parse/emit (pre-push tac2iwxxm ≥95%)."""

from __future__ import annotations

from pathlib import Path

import pytest
from tac2iwxxm.products.vona import parse_vona
from tac2iwxxm.profiles.annex3_products import emit_vona_annex3

from tac2iwxxm import convert, map_t1t2, parse_ahl, split_bulletin

FIXTURES = Path(__file__).resolve().parent / "fixtures"
A7 = FIXTURES / "annex3_golden" / "vona_a7_1.tac"
AHL = FIXTURES / "vona" / "vona_ahl_wm.txt"


def test_parse_vona_strips_ahl_and_maps_kvert_designator() -> None:
    ir = parse_vona(AHL.read_text(encoding="utf-8"), product="VONA")
    assert ir["svo"] == "KVERT"
    assert ir["originating_centre_designator"] == "UHPP"
    assert ir["volcano_name"] == "KARYMSKY"


def test_parse_vona_rejects_wrong_product_and_missing_header() -> None:
    tac = A7.read_text(encoding="utf-8")
    with pytest.raises(ValueError, match="expected product VONA"):
        parse_vona(tac, product="VAA")
    with pytest.raises(ValueError, match="missing VONA header"):
        parse_vona("DTG: 20240216/0130Z\nVOLCANO: X 12345\n", product="VONA")


@pytest.mark.parametrize(
    ("patch", "needle"),
    [
        ("DTG:\t\tBAD\n", "DTG"),
        ("VOLCANO:\t\t\n", "VOLCANO"),
        ("PSN:\t\tBAD\n", "PSN"),
        ("SVO:\t\t\n", "SVO"),
        ("CURRENT COLOUR CODE:\t\t\n", "CURRENT COLOUR"),
    ],
)
def test_parse_vona_required_field_errors(patch: str, needle: str) -> None:
    tac = A7.read_text(encoding="utf-8")
    # Replace the first matching label line content via crude splice.
    lines = tac.splitlines(keepends=True)
    key = patch.split(":", 1)[0]
    out: list[str] = []
    replaced = False
    for line in lines:
        if not replaced and line.lstrip().upper().startswith(key):
            out.append(patch if patch.endswith("\n") else patch + "\n")
            replaced = True
        else:
            out.append(line)
    with pytest.raises(ValueError, match=needle):
        parse_vona("".join(out), product="VONA")


def test_parse_vona_activity_and_hemisphere_edges() -> None:
    tac = (
        "VONA\n"
        "DTG: 20240216/0130Z\n"
        "VOLCANO: UNNAMED\n"
        "PSN: S12305 W045151\n"
        "AREA: TEST\n"
        "SOURCE ELEV: 1.5KM AMSL\n"
        "NOTICE NR: 1/1\n"
        "CURRENT COLOUR CODE: RED\n"
        "PREVIOUS COLOUR CODE: NIL\n"
        "SVO: OTHER\n"
        "ACT STS: HEIGHTENED_UNREST\n"
        "ONSET: NONE\n"
        "DUR: NONE\n"
        "VA CLD HGT: NIL\n"
        "CTC: line1\n"
        "  continued contact\n"
        "RMK: remark one\n"
        "  remark two\n"
    )
    ir = parse_vona(tac, product="VONA")
    assert ir["position"]["lat"] < 0
    assert ir["position"]["lon"] < 0
    assert ir["source_elevation_m"] == 1500.0
    assert ir["ash_cloud_height_m"] is None
    assert ir["activity_status"] == "HEIGHTENED_UNREST"
    assert ir["onset_time"] is None
    assert ir["duration"] is None
    assert ir["originating_centre_designator"] is None
    assert ir["iavcei_number"] is None
    assert "continued contact" in str(ir.get("contacts") or "")
    assert "remark two" in str(ir.get("remarks") or "")

    with pytest.raises(ValueError, match="unknown VONA ACT STS"):
        parse_vona(tac.replace("HEIGHTENED_UNREST", "NOT A STATUS"), product="VONA")


def test_emit_vona_without_ash_and_with_onset() -> None:
    ir = parse_vona(A7.read_text(encoding="utf-8"), product="VONA")
    no_ash = {
        **ir,
        "ash_cloud_height_m": None,
        "onset_time": "2024-02-16T01:00:00Z",
        "duration": "PT2H",
        "previous_colour": None,
        "contacts": None,
        "remarks": None,
        "next_notice": None,
        "iavcei_number": None,
        "originating_centre_designator": None,
        "source_elevation_m": None,
    }
    xml = emit_vona_annex3(no_ash, iwxxm_version="2025-2")
    assert "MeteorologicalFeature/VOLCANIC_ASH" not in xml
    assert "onsetTime" in xml
    assert "PT2H" in xml
    assert "aixm:designator" not in xml
    assert "IAVCEINumber" not in xml
    assert "sourceElevation" not in xml


def test_emit_vona_guards_and_report_status() -> None:
    ir = parse_vona(A7.read_text(encoding="utf-8"), product="VONA")
    with pytest.raises(ValueError, match="expected product VONA"):
        emit_vona_annex3({**ir, "product": "VAA"}, iwxxm_version="2025-2")
    with pytest.raises(ValueError, match="forbidden"):
        emit_vona_annex3({**ir, "iwxxm_root": "VolcanicAshAdvisory"}, iwxxm_version="2025-2")
    with pytest.raises(ValueError, match="unexpected"):
        emit_vona_annex3({**ir, "iwxxm_root": "WeirdRoot"}, iwxxm_version="2025-2")

    xml = emit_vona_annex3({**ir, "report_status": "CORRECTION"}, iwxxm_version="2025-2")
    assert 'reportStatus="CORRECTION"' in xml
    assert "VolcanoObservatoryNoticeForAviation" in xml


def test_convert_vona_with_ahl_body_and_bulletin_split() -> None:
    assert map_t1t2("WM") == "LM"
    parts = parse_ahl("WMCI31 UHPP 160130")
    assert parts.tt == "WM"
    assert parts.iwxxm_tt == "LM"

    text = AHL.read_text(encoding="utf-8")
    split = split_bulletin(text, product="VONA")
    assert split.meta.tt == "WM"
    assert len(split.reports) == 1
    assert split.reports[0].lstrip().startswith("VONA")

    result = convert(text, product="VONA", profile="annex3", iwxxm_version="2025-2")
    assert result.ok is True
    assert "VolcanoObservatoryNoticeForAviation" in result.xml
