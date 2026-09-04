"""TC-F24-002 / TC-F24-003 - AIRMET annex3 golden (S026 / EV-020 T2.1 / F24 theme A3).

Asserts WMO ``airmet-A6-1a-TS`` is in the annex3 pack, root ``iwxxm:AIRMET``,
geometry is not nil-only, convert → M-xsd/M-sch, and ``canonicalize_xml`` equals
vendor golden under default convert settings (ADR-032 / E20-D3).
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

AIRMET_CASE_IDS = ("airmet_a6_1a_ts",)


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_tc_f24_002_annex3_airmet_theme_present() -> None:
    data = _load_manifest()
    ids = {c["id"] for c in data["cases"]}
    assert set(AIRMET_CASE_IDS) <= ids
    for case in data["cases"]:
        if case["id"] in AIRMET_CASE_IDS:
            assert case["product"] == "AIRMET"
            assert case.get("theme") == "A3"
            assert case.get("seed") == "airmet-A6-1a-TS"
            assert (FIXTURES / case["tac"]).is_file()
            assert (FIXTURES / case["golden"]).is_file()


@pytest.mark.parametrize("case_id", AIRMET_CASE_IDS)
def test_tc_f24_002_airmet_root_and_geometry(case_id: str) -> None:
    from tac2iwxxm import convert

    case = next(c for c in _load_manifest()["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    result = convert(
        tac,
        product="AIRMET",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"M-parse failed for {case_id}: {result.issues!r}"
    assert "iwxxm:AIRMET" in result.xml
    assert "iwxxm:SIGMET" not in result.xml
    # TC-F24-002: geometry not nil-only - AirspaceVolume / vertical / horizontal.
    assert "<aixm:AirspaceVolume" in result.xml
    assert "gml:posList" in result.xml or "<gml:pos>" in result.xml
    assert (
        'nilReason="http://codes.wmo.int/common/nil/missing"'
        not in result.xml.split("<iwxxm:geometry", 1)[-1].split("</iwxxm:geometry>", 1)[0]
    )


@pytest.mark.parametrize("case_id", AIRMET_CASE_IDS)
def test_tc_f24_003_airmet_m_xsd_sch(case_id: str) -> None:
    from iwxxm_validate import validate

    from tac2iwxxm import convert

    case = next(c for c in _load_manifest()["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    result = convert(
        tac,
        product="AIRMET",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"M-parse failed for {case_id}: {result.issues!r}"
    report = validate(
        result.xml,
        iwxxm_version=IWXXM_VERSION,
        profile=PROFILE,
        levels=("xsd", "schematron"),
    )
    blocking = [i for i in report.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
    assert not blocking, f"M-xsd/M-sch blocking for {case_id}: {[(i.code, i.message) for i in blocking]}"


@pytest.mark.parametrize("case_id", AIRMET_CASE_IDS)
def test_tc_f24_002_airmet_m_golden(case_id: str) -> None:
    from tac2iwxxm import convert

    case = next(c for c in _load_manifest()["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    golden = (FIXTURES / case["golden"]).read_text(encoding="utf-8")
    result = convert(
        tac,
        product="AIRMET",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True
    assert canonicalize_xml(result.xml) == canonicalize_xml(golden)


def test_tc_f24_002_a6_1a_ts_encode_shape() -> None:
    """A6-1a-TS: ISOL_TS, OBS, TOP ABV FL100, STNR WKN → vendor-shaped AirspaceVolume."""
    from tac2iwxxm import convert

    tac = (FIXTURES / "airmet_a6_1a_ts.tac").read_text(encoding="utf-8")
    result = convert(tac, product="AIRMET", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok is True
    xml = result.xml
    assert 'reportStatus="NORMAL"' in xml
    assert 'permissibleUsage="OPERATIONAL"' in xml
    assert "ISOL_TS" in xml
    assert 'timeIndicator="OBSERVATION"' in xml
    assert 'intensityChange="WEAKEN"' in xml
    assert 'upperLimit uom="FL">100</aixm:upperLimit>' in xml
    assert 'nilReason="unknown"' in xml  # TOP ABV → maximumLimit nil unknown
    assert "gml:posList" in xml
    # #731 shared STNR rule (encoder golden; vendor XML omits motion fields).
    assert 'nilReason="http://codes.wmo.int/common/nil/inapplicable"' in xml
    assert ">0</iwxxm:speedOfMotion>" in xml
    # TAC MWO is YUSO (vendor example incorrectly labels MWO as YUDD).
    assert "<aixm:designator>YUSO</aixm:designator>" in xml
