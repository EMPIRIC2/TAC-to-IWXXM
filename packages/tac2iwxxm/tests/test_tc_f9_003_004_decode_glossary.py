"""TC-F9-003 / TC-F9-004 - decode glossary registry (S026 / EV-020 T5.1 / F9 deepen).

Plain-English token meanings from official/near-official tables with YAML
overrides (ADR-032 / E20-E2). OpenAIP/F3 miss keeps ICAO designator (no fail).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from tac2iwxxm.decode import decode_tac

AIRMET_GOLDEN = "YUDD AIRMET 1 VALID 151520/151800 YUSO- YUDD SHANLON FIR ISOL TS OBS N OF S50 TOP ABV FL100 STNR WKN="
SIGMET_GOLDEN = (
    "YUDD SIGMET 2 VALID 101200/101600 YUSO- "
    "YUDD SHANLON FIR/UIR OBSC TS FCST S OF N54 AND E OF W012 TOP FL390 MOV E 20KT WKN="
)
METAR_GOLDEN = "METAR KJFK 121251Z 18004KT 10SM FEW250 24/18 A3011="


def _explanation_for(tac: str, product: str, code: str) -> str:
    result = decode_tac(tac, product=product)
    for seg in result.segments:
        if seg.code == code:
            return seg.explanation
    raise AssertionError(f"no segment for {code!r} in {product} decode of {tac!r}")


# --- TC-F9-003 - seven-product glossary meanings ---


def test_tc_f9_003_sigmet_obsc_ts_meanings() -> None:
    """SIGMET OBSC/TS use English meanings, not category-only labels."""
    obsc = _explanation_for(SIGMET_GOLDEN, "SIGMET", "OBSC")
    ts = _explanation_for(SIGMET_GOLDEN, "SIGMET", "TS")
    assert "obscured" in obsc.lower()
    assert "thunderstorm" in ts.lower()
    assert "hazard phenomenon" not in ts.lower()
    assert "intensity / distribution" not in obsc.lower()


def test_tc_f9_003_airmet_isol_stnr_wkn_meanings() -> None:
    """AIRMET ISOL/STNR/WKN expand to official-ish English (research seeds)."""
    isol = _explanation_for(AIRMET_GOLDEN, "AIRMET", "ISOL")
    stnr = _explanation_for(AIRMET_GOLDEN, "AIRMET", "STNR")
    wkn = _explanation_for(AIRMET_GOLDEN, "AIRMET", "WKN")
    assert "isolated" in isol.lower()
    assert "stationar" in stnr.lower()  # stationary / stationary
    assert "weaken" in wkn.lower()


def test_tc_f9_003_metar_speci_taf_remain_value_aware() -> None:
    """METAR/SPECI/TAF keep value-aware quality (regression for F9 deepen)."""
    wind = _explanation_for(METAR_GOLDEN, "METAR", "18004KT")
    assert "180°" in wind
    assert "4 kt" in wind
    speci = "SPECI KJFK 232045Z 24012G22KT 8SM BKN020 12/06 A3001="
    gust = _explanation_for(speci, "SPECI", "24012G22KT")
    assert "gust" in gust.lower()
    assert "22 kt" in gust
    taf = "TAF KJFK 151800Z 1600/1618 13005KT 9999 TEMPO 1606/1612 4000 -RA="
    tempo = _explanation_for(taf, "TAF", "TEMPO")
    assert "temporary" in tempo.lower() or "fluctuation" in tempo.lower()


def test_tc_f9_003_vaa_tca_keywords_expanded_where_sourced() -> None:
    vaa = "VA ADVISORY DTG: 20260716/0100Z VAAC: TOKYO VOLCANO: ASAMA"
    result = decode_tac(vaa, product="VAA")
    assert any("volcanic ash" in s.explanation.lower() for s in result.segments)
    tca = "TC ADVISORY DTG: 20260716/0100Z TCAC: MIAMI"
    result_tca = decode_tac(tca, product="TCA")
    assert any("tropical cyclone" in s.explanation.lower() for s in result_tca.segments)


def test_tc_f9_003_openaip_miss_keeps_designator_no_fail() -> None:
    """Missing OpenAIP/F3 name → ICAO designator only; decode must not raise."""
    from tac2iwxxm.glossary import set_location_name_resolver

    def _always_miss(_icao: str) -> str | None:
        return None

    set_location_name_resolver(_always_miss)
    try:
        result = decode_tac(METAR_GOLDEN, product="METAR")
        station = next(s for s in result.segments if s.code == "KJFK")
        assert "KJFK" in station.explanation or "station" in station.explanation.lower()
        # Must not invent a place name on miss.
        assert "John F" not in station.explanation
    finally:
        set_location_name_resolver(None)


# --- TC-F9-004 - official tables + YAML override merge ---


def test_tc_f9_004_official_tables_and_packaged_yaml_load() -> None:
    from tac2iwxxm.glossary import load_glossary, meaning_for

    table = load_glossary()
    assert "OBSC" in table
    assert "TS" in table
    assert meaning_for("OBSC").lower() == "obscured" or "obscured" in meaning_for("OBSC").lower()
    assert "thunderstorm" in meaning_for("TS").lower()


def test_tc_f9_004_yaml_override_wins(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """YAML overlay merges on top of official; override wins when set."""
    from tac2iwxxm import glossary as gloss

    override = tmp_path / "decode_glossary.yaml"
    override.write_text(
        "tokens:\n  OBSC: totally hidden for test\n  ZZTEST: custom override only\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("TAC2IWXXM_DECODE_GLOSSARY_PATH", str(override))
    gloss.reload_glossary()
    try:
        assert "totally hidden for test" in gloss.meaning_for("OBSC").lower()
        assert "custom override only" in gloss.meaning_for("ZZTEST").lower()
        # Official TS still present when not overridden.
        assert "thunderstorm" in gloss.meaning_for("TS").lower()
    finally:
        monkeypatch.delenv("TAC2IWXXM_DECODE_GLOSSARY_PATH", raising=False)
        gloss.reload_glossary()
