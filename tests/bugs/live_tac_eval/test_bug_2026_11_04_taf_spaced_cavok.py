"""Live TAF spaced CAVOK (HAAB) must decode cleanly and pass TAF.TAF-8.

Live HAAB samples emit spaced ``C A V O K`` (lint warning
``MALFORMED_SOURCE_TOKEN``). Decode left that span as a residual and convert
set ``cloudAndVisibilityOK=false`` with no visibility/cloud, failing native
Schematron ``TAF.TAF-8``.

Product-rule accept/normalize on the TAF path — not a severity soften.

[Corpus: product §F9] [Corpus: product §F6] [Corpus: tests]
"""

from __future__ import annotations

import re

import pytest
from tac2iwxxm.slot_builders.taf import parse_taf
from tac_decoding.decode import decode_tac
from tac_validate.api import lint

from tac2iwxxm import convert

# Live samples (HAAB / #1553 / epic #1551).
_HAAB_SAMPLES = (
    "TAF HAAB 032130Z 0400/0506 14008KT C A V O K",
    "TAF HAAB 031530Z 0318/0424 14008KT C A V O K",
)

_BASE_FCST = re.compile(
    r"<iwxxm:baseForecast>\s*"
    r"<iwxxm:MeteorologicalAerodromeForecast\b(?P<attrs>[^>]*)>"
    r"(?P<body>.*?)"
    r"</iwxxm:MeteorologicalAerodromeForecast>\s*"
    r"</iwxxm:baseForecast>",
    re.DOTALL,
)


def _base_forecast(xml: str) -> tuple[str, str]:
    match = _BASE_FCST.search(xml)
    assert match is not None, "expected non-nil baseForecast"
    return match.group("attrs"), match.group("body")


@pytest.mark.parametrize("tac", _HAAB_SAMPLES, ids=["haab_0400", "haab_0318"])
def test_spaced_cavok_decode_has_no_cavok_residual(tac: str) -> None:
    result = decode_tac(tac, product="TAF")
    residual_text = " ".join(r.text for r in result.residuals)
    assert "C A V O K" not in residual_text, residual_text
    assert "C" not in residual_text.split()
    cavok_segs = [
        s
        for s in result.segments
        if "CAVOK" in s.code.replace(" ", "") or s.code == "C A V O K"
    ]
    assert cavok_segs, (
        f"expected CAVOK segment; got {[s.code for s in result.segments]}"
    )
    assert any("ceiling" in s.explanation.lower() for s in cavok_segs)


@pytest.mark.parametrize("tac", _HAAB_SAMPLES, ids=["haab_0400", "haab_0318"])
def test_spaced_cavok_parse_sets_cavok_and_emits_ok_flag(tac: str) -> None:
    ir = parse_taf(tac, product="TAF")
    assert ir.get("cavok") is True
    result = convert(tac, product="TAF", iwxxm_version="2025-2", profile="annex3")
    assert result.ok is True
    assert result.xml is not None
    attrs, body = _base_forecast(result.xml)
    assert 'cloudAndVisibilityOK="true"' in attrs
    assert "prevailingVisibility" not in body
    assert "<iwxxm:cloud>" not in body
    # TAF.TAF-7 still requires surfaceWind under CAVOK.
    assert "<iwxxm:surfaceWind>" in body


@pytest.mark.parametrize("tac", _HAAB_SAMPLES, ids=["haab_0400", "haab_0318"])
def test_spaced_cavok_still_lints_malformed_source_token_warning(tac: str) -> None:
    """Keep MALFORMED_SOURCE_TOKEN as warning — do not blanket-soften."""
    report = lint(tac, product="TAF")
    matched = [
        i
        for i in report.issues
        if i.code == "MALFORMED_SOURCE_TOKEN" and "C A V O K" in i.message
    ]
    assert matched, [i.code for i in report.issues]
    assert all(i.severity == "warning" for i in matched)


@pytest.mark.parametrize("tac", _HAAB_SAMPLES, ids=["haab_0400", "haab_0318"])
def test_spaced_cavok_passes_native_iwxxm_validate(tac: str) -> None:
    from iwxxm_validate import rust_available, validate_iwxxm

    if not rust_available():
        pytest.skip("iwxxm_validate._rust not built (make build-iwxxm-validate-native)")

    result = convert(tac, product="TAF", iwxxm_version="2025-2", profile="annex3")
    assert result.ok is True
    assert result.xml is not None
    report = validate_iwxxm(result.xml, iwxxm_version="2025-2", profile="annex3")
    hard = [i for i in report.issues if i.severity == "error"]
    taf8 = [i for i in hard if "TAF-8" in (i.message or "") or i.code == "TAF.TAF-8"]
    assert not taf8, taf8
    assert not hard, hard
