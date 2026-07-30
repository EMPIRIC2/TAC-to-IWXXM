"""TC-EV023-003 — translationFailedTAC quarantine (S030 / EV-023 T3.1).

Locks the official 2025-2 ``*-translation-failed.xml`` attribute matrix and
requires convert of unreliable TAC to emit a quarantine shell with original TAC
on ``@translationFailedTAC`` (no operational observation/baseForecast; no TAC
in XML comments). Convert assertions for METAR failed TAC are xfail until T3.2.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
_VENDOR_EX = _REPO / "vendor" / "schemas" / "iwxxm" / "2025-2" / "IWXXM" / "examples"

IWXXM_VERSION = "2025-2"
PROFILE = "annex3"

QUARANTINE_ATTRS = (
    "reportStatus",
    "permissibleUsage",
    "translationFailedTAC",
    "translationCentreDesignator",
    "translationCentreName",
    "translationTime",
    "translatedBulletinID",
    "translatedBulletinReceptionTime",
)

_OFFICIAL_FAILED = [
    ("metar-translation-failed.xml", "iwxxm:METAR", "METAR YUDO 221630Z INVALID"),
    ("taf-translation-failed.xml", "iwxxm:TAF", "TAF YUDO 151800Z 1600/1618 INVALID"),
    ("airmet-translation-failed.xml", "iwxxm:AIRMET", None),
    ("va-advisory-translation-failed.xml", "iwxxm:VolcanicAshAdvisory", None),
    ("tc-advisory-translation-failed.xml", "iwxxm:TropicalCycloneAdvisory", None),
    ("spacewx-translation-failed.xml", "iwxxm:SpaceWeatherAdvisory", None),
]


def _attr(xml: str, name: str) -> str | None:
    m = re.search(rf'\b{re.escape(name)}="([^"]*)"', xml)
    return m.group(1) if m else None


def assert_quarantine_attr_matrix(xml: str) -> None:
    """
    Fail when any shared official quarantine attribute is missing.

    Parameters
    ----------
    xml : str
        Official or convert quarantine IWXXM text.
    """
    missing = [a for a in QUARANTINE_ATTRS if _attr(xml, a) is None]
    assert not missing, f"missing quarantine attrs: {missing}"
    assert _attr(xml, "reportStatus") == "NORMAL"
    assert _attr(xml, "permissibleUsage") == "OPERATIONAL"
    tac = _attr(xml, "translationFailedTAC")
    assert tac is not None and tac.strip(), "translationFailedTAC must carry original TAC"


def assert_quarantine_shell_no_partial_observation(xml: str) -> None:
    """Quarantine METAR/SPECI/TAF must not include operational observation/baseForecast."""
    assert "<iwxxm:observation>" not in xml
    assert "<iwxxm:baseForecast>" not in xml
    assert "<!--" not in xml or "translationFailedTAC" in xml  # comments discouraged for TAC


def assert_no_tac_in_xml_comments(xml: str) -> None:
    """Operational TAC must not be smuggled via XML comments."""
    for m in re.finditer(r"<!--(.*?)-->", xml, re.DOTALL):
        body = m.group(1).upper()
        assert "METAR " not in body and "TAF " not in body and "SPECI " not in body, (
            "TAC must not appear in XML comments; use translationFailedTAC"
        )


@pytest.mark.parametrize(
    ("xml_name", "root", "tac_substr"),
    _OFFICIAL_FAILED,
    ids=[n.replace("-translation-failed.xml", "") for n, _, _ in _OFFICIAL_FAILED],
)
def test_tc_ev023_003_official_attr_matrix(xml_name: str, root: str, tac_substr: str | None) -> None:
    path = _VENDOR_EX / xml_name
    assert path.is_file(), path
    xml = path.read_text(encoding="utf-8")
    assert f"<{root}" in xml
    assert_quarantine_attr_matrix(xml)
    assert_no_tac_in_xml_comments(xml)
    if tac_substr is not None:
        assert tac_substr in (_attr(xml, "translationFailedTAC") or "")
    # Official failed examples are shells — no observation / baseForecast body.
    assert_quarantine_shell_no_partial_observation(xml)


def test_tc_ev023_003_collect_failed_member_keeps_translation_attrs() -> None:
    path = _VENDOR_EX / "sigmet-translation-failed-collect.xml"
    assert path.is_file(), path
    xml = path.read_text(encoding="utf-8")
    assert "Collect" in xml or "collect" in xml.lower() or "MeteorologicalBulletin" in xml
    assert_quarantine_attr_matrix(xml)
    assert _attr(xml, "translationFailedTAC")


@pytest.mark.xfail(
    reason="T3.2: quarantine shell with translationFailedTAC for unreliable METAR TAC",
    strict=True,
)
def test_tc_ev023_003_metar_invalid_convert_emits_quarantine() -> None:
    """Official metar-translation-failed.tac → quarantine METAR with original TAC."""
    from tac2iwxxm import convert

    tac_path = _VENDOR_EX / "metar-translation-failed.tac"
    tac = tac_path.read_text(encoding="utf-8").strip()
    result = convert(
        tac,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"quarantine convert should soft-ok: {result.issues!r}"
    assert result.xml is not None
    assert "<iwxxm:METAR" in result.xml
    assert_quarantine_attr_matrix(result.xml)
    assert "INVALID" in (_attr(result.xml, "translationFailedTAC") or "")
    assert_quarantine_shell_no_partial_observation(result.xml)
    assert_no_tac_in_xml_comments(result.xml)


@pytest.mark.xfail(
    reason="T3.2: do not partial-translate unreliable TAC — emit quarantine instead",
    strict=True,
)
def test_tc_ev023_003_taf_invalid_must_not_partial_translate() -> None:
    """Unreliable TAF must quarantine rather than emit a partial operational baseForecast."""
    from tac2iwxxm import convert

    tac_path = _VENDOR_EX / "taf-translation-failed.tac"
    tac = tac_path.read_text(encoding="utf-8").strip()
    result = convert(
        tac,
        product="TAF",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"quarantine convert should soft-ok: {result.issues!r}"
    assert result.xml is not None
    assert_quarantine_attr_matrix(result.xml)
    assert_quarantine_shell_no_partial_observation(result.xml)
    assert_no_tac_in_xml_comments(result.xml)
