"""Pipeline stage outcomes map onto TAC issue severities (live 30d overlay).

Partial decode (decode residuals remain) must surface as TAC validate warning
``PARTIAL_DECODE``. Convert hard fail stays critical and IWXXM validate fail
stays error per the accepted severity ladder — covered here for the partial
decode gap only; convert/IWXXM promotion already has unit coverage.

[Corpus: product] [Corpus: api] [Corpus: tests]
"""

from __future__ import annotations

from tac_validate.issue_registry import by_code

from tac2iwxxm import convert, decode_tac

# Undecoded body token (CA RMK trailers are known-ignore; use junk for residual).
_PARTIAL_TAF = "TAF CYUL 031340Z 0314/0414 28008KT P6SM SCT040 ZZQQ="


def test_registry_partial_decode_is_warning() -> None:
    spec = by_code("PARTIAL_DECODE")
    assert spec.severity == "warning"
    assert (
        "partial" in spec.message_template.lower()
        or "decode" in spec.message_template.lower()
    )


def test_partial_decode_sample_has_residuals() -> None:
    decoded = decode_tac(_PARTIAL_TAF, product="TAF")
    assert any(r.text and r.text.strip() for r in decoded.residuals)


def test_convert_emits_partial_decode_warning_when_residuals_remain() -> None:
    result = convert(
        _PARTIAL_TAF,
        product="TAF",
        iwxxm_version="2025-2",
        profile="annex3",
    )
    assert result.ok is True
    codes = [issue.code for issue in result.issues]
    assert "PARTIAL_DECODE" in codes
    warning = next(issue for issue in result.issues if issue.code == "PARTIAL_DECODE")
    assert warning.severity == "warning"


def test_full_decode_does_not_emit_partial_decode() -> None:
    tac = "METAR YUDO 121200Z 00000KT CAVOK 10/10 Q1000="
    decoded = decode_tac(tac, product="METAR")
    assert not any(r.text and r.text.strip() for r in decoded.residuals)
    result = convert(tac, product="METAR", iwxxm_version="2025-2", profile="annex3")
    assert result.ok is True
    assert "PARTIAL_DECODE" not in [issue.code for issue in result.issues]
