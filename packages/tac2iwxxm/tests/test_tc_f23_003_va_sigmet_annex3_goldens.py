"""TC-F23-003 - VA SIGMET annex3 golden expansion (S025 / EV-019 T4.1 / F23 theme V3).

Asserts annex3 golden pack covers WMO ``sigmet-VA-EGGX`` seed (+ NO VA EXP),
root ``iwxxm:VolcanicAshSIGMET`` under HTTP ``product=sigmet`` (E19-13), and
convert → XSD+Schematron + M-golden. T4.2 deepens convert fidelity if goldens fail.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from metar_shared.xml_canonical import canonicalize_xml

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "annex3_golden"
MANIFEST_PATH = FIXTURES / "manifest.json"
IWXXM_VERSION = "2025-2"
PROFILE = "annex3"

VA_SIGMET_CASE_IDS = (
    "sigmet_va_eggx",
    "sigmet_va_no_va_exp",
)


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _has_root(xml: str, local: str) -> bool:
    return f"<iwxxm:{local} " in xml


def test_tc_f23_003_annex3_va_sigmet_themes_present() -> None:
    data = _load_manifest()
    ids = {c["id"] for c in data["cases"]}
    assert set(VA_SIGMET_CASE_IDS) <= ids
    for case in data["cases"]:
        if case["id"] in VA_SIGMET_CASE_IDS:
            assert case["product"] == "SIGMET"
            assert case.get("theme") == "V3"
            assert (FIXTURES / case["tac"]).is_file()
            assert (FIXTURES / case["golden"]).is_file()
    eggx = next(c for c in data["cases"] if c["id"] == "sigmet_va_eggx")
    assert eggx.get("seed") == "sigmet-VA-EGGX"


@pytest.mark.parametrize("case_id", VA_SIGMET_CASE_IDS)
def test_tc_f23_003_va_sigmet_m_parse_xsd_sch(case_id: str) -> None:
    from iwxxm_validate import validate

    from tac2iwxxm import convert

    case = next(c for c in _load_manifest()["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    result = convert(
        tac,
        product="SIGMET",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"M-parse failed for {case_id}: {result.issues!r}"
    assert result.product == "SIGMET"
    assert _has_root(result.xml, "VolcanicAshSIGMET")
    assert not _has_root(result.xml, "SIGMET")
    assert "iwxxm:VolcanicAshAdvisory" not in result.xml
    assert not _has_root(result.xml, "TropicalCycloneSIGMET")
    report = validate(
        result.xml,
        iwxxm_version=IWXXM_VERSION,
        profile=PROFILE,
        levels=("xsd", "schematron"),
    )
    blocking = [i for i in report.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
    assert not blocking, f"M-xsd/M-sch blocking for {case_id}: {[(i.code, i.message) for i in blocking]}"


@pytest.mark.parametrize("case_id", VA_SIGMET_CASE_IDS)
def test_tc_f23_003_va_sigmet_m_golden(case_id: str) -> None:
    from tac2iwxxm import convert

    case = next(c for c in _load_manifest()["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    golden = (FIXTURES / case["golden"]).read_text(encoding="utf-8")
    result = convert(
        tac,
        product="SIGMET",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True
    assert canonicalize_xml(result.xml) == canonicalize_xml(golden)


def test_tc_f23_003_va_eggx_content_signals() -> None:
    """sigmet-VA-EGGX seed: VA phenomenon + product=sigmet wire → VolcanicAshSIGMET."""
    from tac2iwxxm.products.sigmet_airmet import parse_sigmet

    from tac2iwxxm import convert

    tac = (FIXTURES / "sigmet_va_eggx.tac").read_text(encoding="utf-8")
    ir = parse_sigmet(tac, product="SIGMET")
    assert ir["phenomenon"] == "VA"
    assert ir.get("iwxxm_root") == "VolcanicAshSIGMET"
    result = convert(tac, product="SIGMET", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok is True
    assert 'gml:id="sigmet.va.' in result.xml
    assert 'xlink:href="http://codes.wmo.int/49-2/SigWxPhenomena/VA"' in result.xml or "SigWxPhenomena/VA" in result.xml


def test_tc_f23_003_va_eggx_ash_cloud_polygon_and_sfc_fl() -> None:
    """#739: prefer VA CLD WI polygon over volcano PSN; encode SFC/FL550."""
    from tac2iwxxm.products.sigmet_airmet import parse_sigmet

    from tac2iwxxm import convert

    tac = (FIXTURES / "sigmet_va_eggx.tac").read_text(encoding="utf-8")
    ir = parse_sigmet(tac, product="SIGMET")
    assert ir.get("geometry", {}).get("kind") == "polygon"
    assert ir.get("lower_surface") == "SFC"
    assert ir.get("upper_fl") == 550
    result = convert(tac, product="SIGMET", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok is True
    assert "<gml:LinearRing>" in result.xml
    assert "<gml:posList>" in result.xml
    assert "<gml:CircleByCenterPoint" not in result.xml
    assert "<aixm:lowerLimit>GND</aixm:lowerLimit>" in result.xml
    assert 'upperLimit uom="FL">550</aixm:upperLimit>' in result.xml


def test_tc_f23_003_no_va_exp_nil_geometry() -> None:
    """#739 NO VA EXP → geometry nilReason nothingOfOperationalSignificance."""
    from tac2iwxxm.products.sigmet_airmet import parse_sigmet

    from tac2iwxxm import convert

    tac = (FIXTURES / "sigmet_va_no_va_exp.tac").read_text(encoding="utf-8")
    ir = parse_sigmet(tac, product="SIGMET")
    assert ir.get("no_va_exp") is True
    assert "geometry" not in ir
    result = convert(tac, product="SIGMET", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok is True
    assert 'nilReason="http://codes.wmo.int/common/nil/nothingOfOperationalSignificance"' in result.xml
