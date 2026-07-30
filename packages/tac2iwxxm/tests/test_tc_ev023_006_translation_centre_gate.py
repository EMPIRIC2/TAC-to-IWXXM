"""TC-EV023-006 — translationCentre* gate (S030 / EV-023 T4.3).

Default in-State convert omits ``translationCentreDesignator`` /
``translationCentreName``. Emit only when ``emit_translation_centre`` is set
(T4.4). Quarantine shells keep Translation Centre attrs (official model).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
_VENDOR_EX = _REPO / "vendor" / "schemas" / "iwxxm" / "2025-2" / "IWXXM" / "examples"

IWXXM_VERSION = "2025-2"
PROFILE = "annex3"

CENTRE_ATTRS = ("translationCentreDesignator", "translationCentreName")

_METAR_OK = "METAR KJFK 231751Z 18012KT 9999 FEW020 15/07 Q1013="


def _attr(xml: str, name: str) -> str | None:
    m = re.search(rf'\b{re.escape(name)}="([^"]*)"', xml)
    return m.group(1) if m else None


def assert_omits_translation_centre(xml: str) -> None:
    """
    Fail when successful convert includes translationCentre* attributes.

    Parameters
    ----------
    xml : str
        IWXXM document from a successful in-State convert.
    """
    for name in CENTRE_ATTRS:
        assert _attr(xml, name) is None, f"default convert must omit {name}"


def assert_emits_translation_centre(
    xml: str,
    *,
    designator: str,
    name: str,
) -> None:
    """
    Fail when gated convert lacks the expected translationCentre* values.

    Parameters
    ----------
    xml : str
        IWXXM document emitted with ``emit_translation_centre=True``.
    designator : str
        Expected ``translationCentreDesignator``.
    name : str
        Expected ``translationCentreName``.
    """
    assert _attr(xml, "translationCentreDesignator") == designator
    assert _attr(xml, "translationCentreName") == name


def test_tc_ev023_006_default_convert_omits_translation_centre() -> None:
    """Successful METAR convert omits translationCentre* (FAQ §14.5 in-State)."""
    from tac2iwxxm import convert

    result = convert(
        _METAR_OK,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, result.issues
    assert result.xml is not None
    assert_omits_translation_centre(result.xml)
    # Operational attrs remain.
    assert _attr(result.xml, "reportStatus") == "NORMAL"
    assert _attr(result.xml, "permissibleUsage") == "OPERATIONAL"


def test_tc_ev023_006_quarantine_keeps_translation_centre_model() -> None:
    """Official / convert quarantine shells retain Translation Centre attrs."""
    from tac2iwxxm import convert

    official = (_VENDOR_EX / "metar-translation-failed.xml").read_text(encoding="utf-8")
    for name in CENTRE_ATTRS:
        assert _attr(official, name), f"official quarantine missing {name}"

    tac = (_VENDOR_EX / "metar-translation-failed.tac").read_text(encoding="utf-8").strip()
    result = convert(
        tac,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True
    assert result.xml is not None
    for name in CENTRE_ATTRS:
        assert _attr(result.xml, name), f"quarantine convert missing {name}"


@pytest.mark.xfail(
    reason="T4.4: convert emit_translation_centre + optional designator/name",
    strict=True,
)
def test_tc_ev023_006_flag_emits_translation_centre() -> None:
    """``emit_translation_centre=True`` adds designator/name on successful convert."""
    from tac2iwxxm import convert

    result = convert(
        _METAR_OK,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
        emit_translation_centre=True,
        translation_centre_designator="KWBC",
        translation_centre_name="Washington",
    )
    assert result.ok is True, result.issues
    assert result.xml is not None
    assert_emits_translation_centre(
        result.xml,
        designator="KWBC",
        name="Washington",
    )


@pytest.mark.xfail(
    reason="T4.4: flag false / omitted must still omit centre attrs",
    strict=True,
)
def test_tc_ev023_006_explicit_false_still_omits() -> None:
    """Explicit ``emit_translation_centre=False`` keeps default omit behaviour."""
    from tac2iwxxm import convert

    result = convert(
        _METAR_OK,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
        emit_translation_centre=False,
        translation_centre_designator="KWBC",
        translation_centre_name="Washington",
    )
    assert result.ok is True, result.issues
    assert result.xml is not None
    assert_omits_translation_centre(result.xml)
