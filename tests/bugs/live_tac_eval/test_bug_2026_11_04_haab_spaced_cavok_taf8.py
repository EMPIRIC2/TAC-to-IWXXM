"""Spaced ``C A V O K`` on TAF must parse as CAVOK (TAF.TAF-8).

Live 30d: HAAB TAF samples with spaced CAVOK converted without
``cloudAndVisibilityOK=true`` and failed Schematron TAF.TAF-8.

[Corpus: product §F6] [Corpus: tests]
"""

from __future__ import annotations

import re

from tac2iwxxm.slot_builders.taf import parse_taf

from tac2iwxxm import convert, decode_tac

_HAAB_SPACED = "TAF HAAB 031530Z 0318/0424 14008KT C A V O K"

_BASE_FCST = re.compile(
    r"<iwxxm:baseForecast>\s*"
    r"<iwxxm:MeteorologicalAerodromeForecast\b(?P<attrs>[^>]*)>"
    r"(?P<body>.*?)"
    r"</iwxxm:MeteorologicalAerodromeForecast>\s*"
    r"</iwxxm:baseForecast>",
    re.DOTALL,
)


def test_parse_taf_recognizes_spaced_cavok() -> None:
    ir = parse_taf(_HAAB_SPACED, product="TAF")
    assert ir.get("cavok") is True


def test_decode_explains_spaced_cavok_as_one_group() -> None:
    decoded = decode_tac(_HAAB_SPACED, product="TAF")
    residual_text = " ".join(r.text for r in decoded.residuals)
    assert "C A V O K" not in residual_text
    cavok_segments = [
        s
        for s in decoded.segments
        if "visibility OK" in s.explanation.lower()
        or s.code.upper().replace(" ", "") == "CAVOK"
    ]
    assert cavok_segments


def test_haab_spaced_cavok_emits_cloud_and_visibility_ok() -> None:
    result = convert(
        _HAAB_SPACED,
        product="TAF",
        iwxxm_version="2025-2",
        profile="annex3",
    )
    assert result.ok is True
    assert result.xml is not None
    match = _BASE_FCST.search(result.xml)
    assert match is not None
    assert 'cloudAndVisibilityOK="true"' in match.group("attrs")
