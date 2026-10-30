"""BUG-2026-10-30 — SIGMET SEV MTW / OCNL TS must emit valid WMO codelist hrefs.

Live-map probe: convert may succeed while validate fails WMO_CODELISTS with
INVALID_CODELIST_VALUE because IR/emit used bare SigWxPhenomena/TS.

[Corpus: product §F6] [Corpus: product §F23] [Corpus: product §F2] [Corpus: tests]
"""

from __future__ import annotations

from pathlib import Path

import pytest
from iwxxm_validate.codelists import validate_codelist_references

from tac2iwxxm import convert

# Representative live-map TAC (2026-10-30 probe place_keys).
SEV_MTW_TAC = """WSUK33 EGRR 300603
EGPX SIGMET 04 VALID 300605/301005 EGRR-
EGPX SCOTTISH FIR SEV MTW FCST WI N5428 W00758 - N5514 W00651 -
N5800 W00628 - N5715 W00232 - N5503 W00537 - N5408 W00543 - N5428
W00758 FL050/150 STNR NC=
"""

OCNL_TS_TAC = """WSMX31 MMMX 301717
MMEX SIGMET B3 VALID 301715/302115 MMMX-
MMFR MEXICO FIR OCNL TS OBS AT 1715Z
WI N2715 W11124 - N2851 W11043 - N2743 W10708 - N2652 W10728 - N2720 W10920
         - N2715 W11124 CB TOP ABV FL390
MOV ESE 15 KT NC.
=
"""

_CODELISTS_DIR = (
    Path(__file__).resolve().parents[2]
    / "packages/iwxxm-validate/src/iwxxm_validate/schemas/iwxxm/2025-2/IWXXM/rule"
)


def _codelist_errors(xml: str) -> list[str]:
    issues = validate_codelist_references(xml, codelists_dir=_CODELISTS_DIR)
    return [i.message for i in issues if i.code == "INVALID_CODELIST_VALUE"]


@pytest.mark.parametrize(
    ("tac", "ir_code", "href_substr"),
    [
        (SEV_MTW_TAC, "SEV_MTW", "SigWxPhenomena/SEV_MTW"),
        (OCNL_TS_TAC, "OCNL_TS", "AirWxPhenomena/OCNL_TS"),
    ],
)
def test_bug_2026_10_30_sigmet_phenomenon_codelist_valid(
    tac: str,
    ir_code: str,
    href_substr: str,
) -> None:
    """SEV MTW and OCNL TS SIGMETs must emit a valid WMO phenomenon href."""
    result = convert(tac, product="sigmet", profile="annex3", iwxxm_version="2025-2")
    assert result.ok, result.issues
    assert result.ir.get("phenomenon") == ir_code
    assert href_substr in result.xml
    assert "SigWxPhenomena/TS" not in result.xml
    assert _codelist_errors(result.xml) == []


def test_bug_2026_10_30_bare_sigwx_ts_href_still_invalid_codelist() -> None:
    """Pre-fix bare SigWxPhenomena/TS href must still fail WMO_CODELISTS."""
    xml = (
        '<?xml version="1.0"?>'
        '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
        '<a xlink:href="http://codes.wmo.int/49-2/SigWxPhenomena/TS"/>'
        "</root>"
    )
    errors = _codelist_errors(xml)
    assert errors
    assert any("TS" in msg for msg in errors)
