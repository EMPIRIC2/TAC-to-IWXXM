"""TC-F23-002 - General SIGMET annex3 golden expansion (S025 / EV-019 T2.1 / F23 theme G3).

Asserts annex3 golden pack covers WMO ``sigmet-A6-1a-TS`` / CNL seeds (+ STNR expand),
root ``iwxxm:SIGMET``, and convert → XSD+Schematron + M-golden for those cases.
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

SIGMET_CASE_IDS = (
    "sigmet_a6_1a_ts",
    "sigmet_a6_1b_cnl",
    "sigmet_stnr",
)


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_tc_f23_002_annex3_sigmet_themes_present() -> None:
    data = _load_manifest()
    ids = {c["id"] for c in data["cases"]}
    assert set(SIGMET_CASE_IDS) <= ids
    for case in data["cases"]:
        if case["id"] in SIGMET_CASE_IDS:
            assert case["product"] == "SIGMET"
            assert case.get("theme") == "G3"
            assert (FIXTURES / case["tac"]).is_file()
            assert (FIXTURES / case["golden"]).is_file()


@pytest.mark.parametrize("case_id", SIGMET_CASE_IDS)
def test_tc_f23_002_sigmet_m_parse_xsd_sch(case_id: str) -> None:
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
    assert "iwxxm:SIGMET" in result.xml
    assert "iwxxm:VolcanicAshSIGMET" not in result.xml
    assert "iwxxm:TropicalCycloneSIGMET" not in result.xml
    report = validate(
        result.xml,
        iwxxm_version=IWXXM_VERSION,
        profile=PROFILE,
        levels=("xsd", "schematron"),
    )
    blocking = [i for i in report.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
    assert not blocking, f"M-xsd/M-sch blocking for {case_id}: {[(i.code, i.message) for i in blocking]}"


@pytest.mark.parametrize("case_id", SIGMET_CASE_IDS)
def test_tc_f23_002_sigmet_m_golden(case_id: str) -> None:
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


def test_tc_f23_002_cnl_exceptional_encode() -> None:
    """#733 CNL: isCancelReport + cancelled seq/period; omit phenomenon/analysis."""
    from tac2iwxxm import convert

    tac = (FIXTURES / "sigmet_a6_1b_cnl.tac").read_text(encoding="utf-8")
    result = convert(tac, product="SIGMET", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok is True
    xml = result.xml
    assert 'isCancelReport="true"' in xml
    assert "<iwxxm:cancelledReportSequenceNumber>2</iwxxm:cancelledReportSequenceNumber>" in xml
    assert "<iwxxm:cancelledReportValidPeriod>" in xml
    assert "<iwxxm:phenomenon" not in xml
    assert "<iwxxm:analysisCollection>" not in xml


def test_tc_f23_002_stnr_exceptional_encode() -> None:
    """#733 STNR: direction nilReason inapplicable; speedOfMotion 0."""
    from tac2iwxxm import convert

    tac = (FIXTURES / "sigmet_stnr.tac").read_text(encoding="utf-8")
    result = convert(tac, product="SIGMET", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok is True
    xml = result.xml
    assert 'nilReason="http://codes.wmo.int/common/nil/inapplicable"' in xml
    assert 'speedOfMotion uom="[kn_i]">0</iwxxm:speedOfMotion>' in xml or ">0</iwxxm:speedOfMotion>" in xml


def test_tc_f23_002_a6_1a_motion_intensity_encode() -> None:
    """A6-1a-TS: WKN→WEAKEN, MOV E 20KT, TOP FL390 present in evolving condition."""
    from tac2iwxxm import convert

    tac = (FIXTURES / "sigmet_a6_1a_ts.tac").read_text(encoding="utf-8")
    result = convert(tac, product="SIGMET", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok is True
    xml = result.xml
    assert 'intensityChange="WEAKEN"' in xml
    assert "<iwxxm:directionOfMotion" in xml
    assert ">90</iwxxm:directionOfMotion>" in xml
    assert ">20</iwxxm:speedOfMotion>" in xml
    assert 'upperLimit uom="FL">390</aixm:upperLimit>' in xml


def test_tc_f23_002_point_circle_zero_radius() -> None:
    """#733 single point → CircleByCenterPoint radius 0."""
    from tac2iwxxm import convert

    tac = Path(__file__).resolve().parents[2] / "tac-validate" / "tests" / "fixtures" / "accept" / "sigmet_g1_point.tac"
    text = tac.read_text(encoding="utf-8")
    result = convert(text, product="SIGMET", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok is True
    assert "<gml:CircleByCenterPoint" in result.xml
    assert 'radius uom="[nmi_i]">0</gml:radius>' in result.xml


def test_tc_f23_002_single_altitude_same_limits() -> None:
    """#733 single altitude → same lower and upper FL limits."""
    from tac2iwxxm import convert

    tac = (
        Path(__file__).resolve().parents[2]
        / "tac-validate"
        / "tests"
        / "fixtures"
        / "accept"
        / "sigmet_g1_single_alt.tac"
    )
    text = tac.read_text(encoding="utf-8")
    result = convert(text, product="SIGMET", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok is True
    assert 'lowerLimit uom="FL">180</aixm:lowerLimit>' in result.xml
    assert 'upperLimit uom="FL">180</aixm:upperLimit>' in result.xml
