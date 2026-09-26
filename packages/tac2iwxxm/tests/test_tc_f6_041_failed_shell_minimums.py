"""TC-F6-041 — failed-shell minimum identity fields.

[Corpus: product §F6] [Corpus: tests §TC-F6-041]
"""

from __future__ import annotations

from tac2iwxxm import convert

_NIL = "http://codes.wmo.int/common/nil/missing"


def _failed(product: str, tac: str):
    result = convert(tac, product=product, profile="annex3", iwxxm_version="2025-2")
    assert result.ok is True, result.issues
    assert result.xml is not None
    xml = result.xml
    assert 'permissibleUsage="OPERATIONAL"' in xml
    assert "INVALID" in xml
    return xml


def test_tc_f6_041_metar_and_speci_keep_the_aerodrome_times() -> None:
    """METAR and SPECI failed shells already carry the three identity fields."""
    for product, lead in (("METAR", "METAR"), ("SPECI", "SPECI")):
        xml = _failed(product, f"{lead} KJFK 121151Z INVALID")
        assert "<iwxxm:issueTime>" in xml
        assert "<iwxxm:aerodrome>" in xml
        assert "<aixm:designator>KJFK</aixm:designator>" in xml
        assert "<iwxxm:observationTime>" in xml
        assert "<iwxxm:validPeriod" not in xml


def test_tc_f6_041_taf_gains_a_valid_period() -> None:
    """A TAF validity group becomes the valid period. A TAF without one is nil."""
    parsed = _failed("TAF", "TAF YUDO 151800Z 1600/1618 INVALID")
    assert "<iwxxm:validPeriod>" in parsed
    assert "<gml:beginPosition>" in parsed
    assert "T00:00:00Z" in parsed
    assert "T18:00:00Z" in parsed
    missing = _failed("TAF", "TAF YUDO 151800Z INVALID")
    assert f'<iwxxm:validPeriod nilReason="{_NIL}"/>' in missing


def test_tc_f6_041_sigmet_and_airmet_gain_the_unit_and_period() -> None:
    """The ATS unit and the validity group are identity fields, not weather."""
    sigmet = _failed("SIGMET", "YUDD SIGMET 1 VALID 151520/151800 YUSO INVALID")
    assert "<iwxxm:issuingAirTrafficServicesUnit>" in sigmet
    assert "<aixm:designator>YUDD</aixm:designator>" in sigmet
    assert "<iwxxm:validPeriod>" in sigmet
    assert "T15:20:00Z" in sigmet
    assert "T18:00:00Z" in sigmet
    airmet = _failed("AIRMET", "AIRMET INVALID")
    assert f'<iwxxm:issuingAirTrafficServicesUnit nilReason="{_NIL}"/>' in airmet
    assert f'<iwxxm:validPeriod nilReason="{_NIL}"/>' in airmet


def test_tc_f6_041_advisories_gain_the_issuing_centre() -> None:
    """Each advisory shell names its centre when the TAC has one."""
    vaa = _failed("VAA", "VA ADVISORY\nVAAC: TOKYO\nINVALID")
    assert "<iwxxm:issuingVolcanicAshAdvisoryCentre>" in vaa
    assert "<aixm:name>TOKYO</aixm:name>" in vaa
    assert "<aixm:designator>" not in vaa
    tca = _failed("TCA", "TC ADVISORY\nTCAC: YUFO\nINVALID")
    assert "<iwxxm:issuingTropicalCycloneAdvisoryCentre>" in tca
    assert "<aixm:designator>YUFO</aixm:designator>" in tca
    swxa = _failed("SWXA", "SWX ADVISORY\nINVALID")
    assert f'<iwxxm:issuingSpaceWeatherCentre nilReason="{_NIL}"/>' in swxa
    named = _failed("SWXA", "SWX ADVISORY\nSWXC: DONLON\nINVALID")
    assert "<aixm:name>DONLON</aixm:name>" in named


def test_tc_f6_041_original_tac_stays_operational() -> None:
    """The failed TAC is kept and the shell stays operational."""
    xml = _failed("METAR", "METAR KJFK 121151Z INVALID 18012KT")
    assert "METAR KJFK 121151Z INVALID 18012KT" in xml
    assert "YUZZ" not in xml
    assert "Fictional translation centre" not in xml
