"""Profile allowlists for products Annex 3 already converts.

[Corpus: product §F36] [Corpus: domain-profiles] [Corpus: tests]

US TCA, SWXA, and VONA, Australia VAA, and Canadian SIGMET/VAA follow the
existing emitters. G-AIRMET stays out: the public feed is hazard polygons
with no TAC.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from iwxxm_validate import validate
from tac2iwxxm.profiles.ca_eccc import emit_sigmet_ca_eccc, emit_vaa_ca_eccc
from tac2iwxxm.slot_builders.vona import _strip_gateway_question_padding, parse_vona

from tac2iwxxm import convert

_FIXTURES = Path(__file__).resolve().parent / "fixtures"

_KILAUEA_VONA = """\
WMPA01 PHVO 230952
VONA
DTG:???20260923/0952Z
VOLCANO:??KILAUEA 332010
PSN:???N1925 W15517
AREA:???HAWAII
SOURCE ELEV:??4091FT AMSL
NOTICE NR:??2026/62
CURRENT COLOUR CODE:?ORANGE
PREVIOUS COLOUR CODE:?ORANGE
"""

_DARWIN_VAA = """\
FVAU01 ADRM 231450
VA ADVISORY
DTG: 20260923/1450Z
VAAC: DARWIN
VOLCANO: DUKONO 268010
PSN: N0142 E12754
AREA: INDONESIA
SOURCE ELEV: 1229M AMSL
ADVISORY NR: 2026/788
INFO SOURCE: HIMAWARI-9
ERUPTION DETAILS: VA AT 20260922/2230Z FL070 REPORTED
OBS VA DTG: 23/1410Z
OBS VA CLD: SFC/FL070 N0136 E12747 - N0147 E12743 - N0222 E12816 - N0200 E12849 - N0125 E12835 MOV NE 10KT
FCST VA CLD +6 HR: 23/2010Z SFC/FL070 N0309 E12852 - N0139 E12927 - N0124 E12852 - N0122 E12755 - N0219 E12716
FCST VA CLD +12 HR: 24/0210Z SFC/FL070 N0419 E12908 - N0134 E12952 - N0114 E12803 - N0312 E12705
FCST VA CLD +18 HR: 24/0810Z SFC/FL070 N0523 E12916 - N0409 E13011 - N0119 E12951 - N0134 E12749 - N0410 E12705
RMK: VA NOT IDENTIFIABLE ON CURRENT SATELLITE IMAGERY.
NXT ADVISORY: 20260923/2030Z=
"""

_GANDER_SIGMET = """\
WSNT01 CWAO 231522
CZQX SIGMET F2 VALID 231520/231920 CWUL-
CZQX GANDER OCEANIC FIR/CTA SEV TURB OBS AT 1509Z WI 180NM WID LINE BTN N5630 W03900 - N6130 W03200 FL310/360 MOV WNW 10KT WKN=
"""


def _xsd_errors(xml: str, *, iwxxm_version: str, profile: str, product: str | None = None) -> list[str]:
    report = validate(xml, iwxxm_version=iwxxm_version, profile=profile, product=product, levels=["xsd"])
    return [f"{issue.code}: {issue.message}" for issue in report.issues if issue.severity == "error"]


def test_us_profile_converts_tca_swxa_and_vona() -> None:
    cases = (
        ("TCA", _FIXTURES / "annex3_golden" / "tca_a2_2.tac"),
        ("SWXA", _FIXTURES / "annex3_golden" / "swxa_a7_3.tac"),
        ("VONA", _FIXTURES / "annex3_golden" / "vona_a7_1.tac"),
    )
    for product, path in cases:
        result = convert(path.read_text(encoding="utf-8"), product=product, profile="iwxxm_us", iwxxm_version="2025-2")
        assert result.ok, (product, result.issues)
        assert _xsd_errors(result.xml, iwxxm_version="2025-2", profile="iwxxm_us") == []


def test_us_profile_converts_padded_kilauea_vona() -> None:
    result = convert(_KILAUEA_VONA, product="VONA", profile="iwxxm_us", iwxxm_version="2025-2")
    assert result.ok, result.issues
    assert "KILAUEA" in result.xml
    assert _xsd_errors(result.xml, iwxxm_version="2025-2", profile="iwxxm_us") == []


def test_au_bom_converts_darwin_vaa() -> None:
    result = convert(_DARWIN_VAA, product="VAA", profile="au_bom", iwxxm_version="2025-2")
    assert result.ok, result.issues
    assert "DUKONO" in result.xml
    assert _xsd_errors(result.xml, iwxxm_version="2025-2", profile="annex3") == []


def test_ca_eccc_converts_gander_sigmet_and_montreal_vaa() -> None:
    sigmet = convert(_GANDER_SIGMET, product="SIGMET", profile="ca_eccc")
    assert sigmet.ok, sigmet.issues
    assert sigmet.iwxxm_version == "3.0.0"
    assert "http://icao.int/iwxxm/3.0" in sigmet.xml
    assert "SIGMET" in sigmet.xml

    vaa_tac = (_FIXTURES / "profiles" / "CA_ECCC" / "VAA" / "ops" / "vaa_edziza_20260818_001.tac").read_text(
        encoding="utf-8"
    )
    vaa = convert(vaa_tac, product="VAA", profile="ca_eccc")
    assert vaa.ok, vaa.issues
    assert vaa.iwxxm_version == "3.0.0"
    assert "http://icao.int/iwxxm/3.0" in vaa.xml
    assert "EDZIZA" in vaa.xml


def test_gateway_padding_keeps_a_question_mark_in_the_remark() -> None:
    cleaned = _strip_gateway_question_padding("RMK: ASH?\nDTG:???20260923/0952Z\n")
    assert "ASH?" in cleaned
    assert "DTG:20260923/0952Z" in cleaned


def test_empty_vona_does_not_invent_a_centre() -> None:
    with pytest.raises(ValueError, match="VONA header"):
        parse_vona("", product="VONA")


def test_ca_sigmet_and_vaa_emitters_require_the_msc_pin() -> None:
    with pytest.raises(ValueError, match=r"3\.0\.0"):
        emit_sigmet_ca_eccc({}, iwxxm_version="2025-2")
    with pytest.raises(ValueError, match=r"3\.0\.0"):
        emit_vaa_ca_eccc({}, iwxxm_version="2025-2")
