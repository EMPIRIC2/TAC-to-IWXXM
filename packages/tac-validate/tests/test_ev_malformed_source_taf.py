"""Lint regressions for malformed TAF source tokens (F15).

[Corpus: product §F15] [Corpus: tests]
"""

from __future__ import annotations

from tac_validate.api import lint


def test_malformed_spaced_cavok_and_vctsra_and_validity() -> None:
    cavok = lint("TAF HAAB 032130Z 0400/0506 14008KT C A V O K", product="TAF")
    assert any(i.code == "MALFORMED_SOURCE_TOKEN" and "C A V O K" in i.message for i in cavok.issues)
    wx = lint(
        "TAF AMD KPOE 032240Z 0322/0421 15010G15KT 9000 -VCTSRA BKN015 QNH2984INS",
        product="TAF",
    )
    assert any(i.code == "MALFORMED_SOURCE_TOKEN" and "-VCTSRA" in i.message for i in wx.issues)
    bad = lint(
        "TAF KJFK 031200Z 0318/03222 18010KT 9999 FEW040",
        product="TAF",
    )
    assert any(i.code == "MALFORMED_SOURCE_TOKEN" and "0318/03222" in i.message for i in bad.issues)
    cloud = lint("TAF KJFK 031200Z 0312/0412 18010KT 9999 SC045", product="TAF")
    assert any(i.code == "MALFORMED_SOURCE_TOKEN" and "SC045" in i.message for i in cloud.issues)
