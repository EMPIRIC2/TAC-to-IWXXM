"""BUG-2026-11-02 — WC/WV AHL must keep TC/VA CNL family roots after heading paste.

``/api/v1/convert`` uses ``reports_for_convert``, which strips the WMO AHL before
``tac2iwxxm.convert``. CNL bodies omit phenomenon, so family selection depends on
``ahl_tt`` (WC → TropicalCycloneSIGMET, WV → VolcanicAshSIGMET). Stripping the
AHL collapses both to ordinary ``SIGMET``.

[Corpus: product §F6] [Corpus: product §F23] [Corpus: api] [Corpus: tests]
"""

from __future__ import annotations

import re

from tac2iwxxm.heading_paste import reports_for_convert

from tac2iwxxm import convert

_TC_CNL_AHL = """\
WCUK31 YUDO 251800
YUCC SIGMET 4 VALID 251800/252200 YUDO-
YUCC AMSWELL FIR CNL SIGMET 3 251600/252200=
"""

_VA_CNL_AHL = """\
WVUK31 EGRR 251800
EGGX SIGMET 5 VALID 251800/252000 EGRR-
EGGX SHANWICK OCEANIC FIR CNL SIGMET 4 251600/252000=
"""


def _root(xml: str) -> str | None:
    match = re.search(
        r"<(?:[\w.-]+:)?(SIGMET|VolcanicAshSIGMET|TropicalCycloneSIGMET)\b",
        xml or "",
    )
    return match.group(1) if match else None


def _convert_after_heading_paste(tac: str) -> str:
    pasted = reports_for_convert(tac, "SIGMET")
    assert pasted is not None
    assert pasted.reports, "expected at least one report after heading paste"
    report, _offset = pasted.reports[0]
    result = convert(report, product="SIGMET", profile="annex3", iwxxm_version="2025-2")
    assert result.ok is True
    return result.xml or ""


def test_bug_2026_11_02_direct_convert_keeps_tc_cnl_root() -> None:
    """Library convert with WC AHL retained selects TropicalCycloneSIGMET."""
    result = convert(
        _TC_CNL_AHL, product="SIGMET", profile="annex3", iwxxm_version="2025-2"
    )
    assert result.ok is True
    assert _root(result.xml) == "TropicalCycloneSIGMET"


def test_bug_2026_11_02_heading_paste_must_keep_tc_cnl_root() -> None:
    """API-equivalent paste path must not collapse WC CNL to ordinary SIGMET."""
    xml = _convert_after_heading_paste(_TC_CNL_AHL)
    assert _root(xml) == "TropicalCycloneSIGMET"


def test_bug_2026_11_02_heading_paste_must_keep_va_cnl_root() -> None:
    """API-equivalent paste path must not collapse WV CNL to ordinary SIGMET."""
    direct = convert(
        _VA_CNL_AHL, product="SIGMET", profile="annex3", iwxxm_version="2025-2"
    )
    assert _root(direct.xml) == "VolcanicAshSIGMET"
    xml = _convert_after_heading_paste(_VA_CNL_AHL)
    assert _root(xml) == "VolcanicAshSIGMET"
