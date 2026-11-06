"""BUG-2026-10-05 — southern SIGMET highlights and a false altitude error.

The oceanic bulletin in the workbench painted unrelated preview lines and
reported 9000FT/FL290 as an undecoded error.
"""

from __future__ import annotations

from tac2iwxxm.convert import convert
from tac2iwxxm.group_trace import trace_emitted_groups
from tac_decoding.decode import decode_tac
from tac_validate.api import lint

_TAC = """WSPSZ1 NZKL 050806
NZZO SIGMET 2 VALID 050811/051211 NZKL-
NZZO AUCKLAND OCEANIC FIR SEV TURB FCST WI S7520
W14200 - S7728 W13100 - S7700 W14410 - S7520 W14200
9000FT/FL290 MOV
S 20KT INTSF="""


def test_screenshot_sigmet_converts_and_pairs_the_selected_token() -> None:
    decoded = decode_tac(_TAC, product="SIGMET")
    assert [item.text for item in decoded.residuals] == []

    report = lint(_TAC, product="SIGMET")
    assert "SINGLE_ALTITUDE" not in [issue.code for issue in report.issues]

    result = convert(_TAC, product="SIGMET", preview=True)
    assert result.ok
    assert result.xml
    assert "-75.3333 -142.0000" in result.xml
    assert 'uom="[ft_i]">9000</aixm:lowerLimit>' in result.xml

    rows = trace_emitted_groups(_TAC, "SIGMET")
    latitude = next(row for row in rows if row["token"] == "S7520")
    separator = next(row for row in rows if row["token"] == "-")
    assert latitude["element"] == "posList"
    assert separator["element"] == "posList"
