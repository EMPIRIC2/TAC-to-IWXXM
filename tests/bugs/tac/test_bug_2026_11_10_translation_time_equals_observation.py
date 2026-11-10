"""BUG-2026-11-10 — translationTime must match observationTime on success.

When translation-centre emit includes a bulletin id, METAR/SPECI
``translationTime`` and ``translatedBulletinReceptionTime`` must equal the
``iwxxm:observationTime`` stamp, not wall-clock now.

[Corpus: product §F6] [Corpus: tests]
"""

from __future__ import annotations

import re

from tac2iwxxm import convert

_BULLETIN = "SAUS31 KZNY 121200\nMETAR KJFK 121151Z 18012KT 9999 FEW020 15/07 Q1013=\n"
_OBS = re.compile(
    r"<iwxxm:observationTime>.*?<gml:timePosition>([^<]+)</gml:timePosition>",
    re.DOTALL,
)


def _attr(xml: str, name: str) -> str | None:
    match = re.search(rf'{name}="([^"]*)"', xml)
    return match.group(1) if match else None


def test_bug_2026_11_10_translation_time_equals_observation_time() -> None:
    """Successful on-behalf convert stamps translation times from observation."""
    result = convert(
        _BULLETIN,
        product="METAR",
        profile="annex3",
        iwxxm_version="2025-2",
        bulletin_date="2026-11-12",
        emit_translation_centre=True,
        translation_centre_designator="CWAO",
        translation_centre_name="Test translation centre",
    )
    assert result.ok is True, result.issues
    xml = result.xml or ""
    obs_match = _OBS.search(xml)
    assert obs_match is not None
    obs = obs_match.group(1)
    assert obs == "2026-11-12T11:51:00Z"
    issued = _attr(xml, "translationTime")
    received = _attr(xml, "translatedBulletinReceptionTime")
    assert issued == obs
    assert received == obs
