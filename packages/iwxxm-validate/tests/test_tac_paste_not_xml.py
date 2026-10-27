"""Validate mode must not treat pasted TAC as IWXXM XML.

St Kitts testers saw the same XML_SYNTAX_ERROR on every METAR when they validated
the TAC instead of the convert output. [Corpus: product §F2] [Corpus: tests]
"""

from __future__ import annotations

import pytest
from iwxxm_validate.wellformed import run_wellformed_lxml


def test_metar_paste_explains_that_tac_is_not_xml() -> None:
    issues = run_wellformed_lxml("METAR TKPK 181400Z 08010KT 9999 SCT020 31/25 Q1017=")
    assert len(issues) == 1
    assert issues[0].code == "XML_SYNTAX_ERROR"
    assert "TAC" in issues[0].message
    assert "Convert" in issues[0].message
    assert "Start tag expected" not in issues[0].message


def test_ahl_heading_paste_explains_that_tac_is_not_xml() -> None:
    issues = run_wellformed_lxml("SAXX31 TNCM 081200\nMETAR TNCM 081200Z 14006KT 9999 FEW020 28/24 Q1013=")
    assert issues[0].code == "XML_SYNTAX_ERROR"
    assert "TAC" in issues[0].message


@pytest.mark.parametrize(
    "tac",
    [
        "SPECI TKPK 181400Z 08010KT 9999 SCT020 31/25 Q1017=",
        "TAF TTPP 081600Z 0818/0918 09012KT 9999 SCT018=",
        "SIGMET 3 VALID 251435/251835 TTPP- TTZP PIARCO FIR EMBD TS OBS AT 1410Z N OF N10 TOP FL380 STNR DECR=",
    ],
)
def test_speci_taf_sigmet_paste_explains_that_tac_is_not_xml(tac: str) -> None:
    issues = run_wellformed_lxml(tac)
    assert issues[0].code == "XML_SYNTAX_ERROR"
    assert "TAC" in issues[0].message
    assert "Convert" in issues[0].message
