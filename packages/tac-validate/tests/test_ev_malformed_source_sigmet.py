"""Lint regressions for malformed SIGMET source tokens (F15).

[Corpus: product §F15] [Corpus: tests]
"""

from __future__ import annotations

from tac_validate.api import lint


def test_malformed_skbo_at_time_and_foreign_metar() -> None:
    skbo = lint(
        "WVCO31 SKBO 031734\nSKED SIGMET 4 VALID 031730/032240 SKBO-?\n"
        "SKED BOGOTA FIR VA MT VOLCAN PURACE PSN N0219 W07624=",
        product="SIGMET",
    )
    assert any(i.code == "MALFORMED_SOURCE_TOKEN" and "SKBO-?" in i.message for i in skbo.issues)
    atz = lint(
        "WSCO31 SKBO 031950\nSKED SIGMET D1 VALID 031950/032350 SKBO-\n"
        "SKED BOGOTA FIR FRQ TS OBS AT1930Z SE OF LINE N0719 W07208 TOP ABV FL480=",
        product="SIGMET",
    )
    assert any(i.code == "MALFORMED_SOURCE_TOKEN" and "AT1930Z" in i.message for i in atz.issues)
    metar = lint(
        "WSSG31 GOOY 030838\nGOOO SIGMET A05 VALID 030840/031240 GOBD-\n"
        "GOOO DAKAR TERRESTRE FIR EMBD TS OBS\nMETAR DIAP 030830Z 31003KT 9999=",
        product="SIGMET",
    )
    assert any(i.code == "MALFORMED_SOURCE_TOKEN" and "METAR" in i.message for i in metar.issues)
    lat = lint(
        "WSIQ01 ORBI 040027\nORBB SIGMET C1 VALID 040020/040420 ORBI-\n"
        "ORBB BAGHDAD FIR EMBD TS OBS W OF LINE N3160 E04575 MOV E NC=",
        product="SIGMET",
    )
    assert any(i.code == "MALFORMED_SOURCE_TOKEN" and "N3160" in i.message for i in lat.issues)
