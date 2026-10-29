"""HF-sigmet-tc-dashed-names — convert keeps hyphenated TC names (F23 / F6).

``product=SIGMET`` only; no new product enum (ADR-045 pack-engine boundary).
"""

from __future__ import annotations

from tac2iwxxm import convert


def test_convert_hyphenated_tc_name_in_fa_round_trip() -> None:
    tac = (
        "WCUK31 EGRR 121200\n"
        "YUCC SIGMET 3 VALID 251600/252200 YUDO-\n"
        "YUCC AMSWELL FIR TC IN-FA PSN N2706 W07306 CB OBS AT 1600Z "
        "WI 250NM OF TC CENTRE TOP FL500 NC\n"
        "FCST AT 2200Z TC CENTRE PSN N2740 W07345="
    )
    result = convert(tac, product="SIGMET")
    xml = result.xml if hasattr(result, "xml") else str(result)
    assert "In-Fa" in xml
    assert "TropicalCycloneSIGMET" in xml or "tropicalCyclone" in xml
