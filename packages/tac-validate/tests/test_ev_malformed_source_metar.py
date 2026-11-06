"""Lint regressions for malformed METAR/SPECI source tokens (F15).

[Corpus: product §F15] [Corpus: tests]
"""

from __future__ import annotations

from tac_validate.api import lint


def test_malformed_cabok_and_t_group_and_a02() -> None:
    cabok = lint("METAR HAAB 031200Z 00000KT 9999 CABOK 20/10 Q1013", product="METAR")
    assert any(i.code == "MALFORMED_SOURCE_TOKEN" for i in cabok.issues)
    tgroup = lint(
        "METAR KMOB 031456Z 08011KT 7SM OVC014 23/19 A3005 RMK A02 T024400206",
        product="METAR",
    )
    codes = {i.code for i in tgroup.issues}
    assert "MALFORMED_SOURCE_TOKEN" in codes
    a02 = lint("METAR KJFK 051200Z 18010KT 10SM SCT020 20/10 A2990 RMK A02", product="METAR")
    assert any(i.code == "MALFORMED_SOURCE_TOKEN" and "A02" in i.message for i in a02.issues)
