"""PROB40 stays on its TEMPO group. A bare PROB30 is not folded into the previous forecast."""

from __future__ import annotations

from tac2iwxxm.slot_builders.taf import parse_taf
from tac2iwxxm.taf_prob import is_unqualified_probability, probability_tempo_parts, temporary_probability_indicator

from tac2iwxxm import convert

_MZBZ = "TAF MZBZ 081200Z 0812/0912 12010KT 9999 FEW020 BECMG 0814/0816 14012KT 7000 PROB40 TEMPO 0818/0822 4000 TSRA="
_BARE = "TAF MZBZ 081200Z 0812/0912 12010KT 9999 FEW020 PROB30 4000 TSRA="
_SWALLOWED = "TAF MZBZ 081200Z 0812/0912 12010KT 9999 FEW020 BECMG 0814/0816 14012KT 7000 PROB30 0818/0822 4000 TSRA="


def test_prob40_tempo_keeps_forty_percent_on_the_temporary_group() -> None:
    result = convert(_MZBZ, product="TAF", bulletin_date="2026-10-08")
    assert result.ok is True
    assert result.xml is not None
    assert 'changeIndicator="PROBABILITY_40_TEMPORARY_FLUCTUATIONS"' in result.xml
    assert 'changeIndicator="TEMPORARY_FLUCTUATIONS"' not in result.xml
    ir = parse_taf(_MZBZ, product="TAF")
    changes = ir["change_forecasts"]
    becoming = next(item for item in changes if item["change_indicator"] == "BECOMING")
    temporary = next(item for item in changes if item["change_indicator"] == "PROBABILITY_40_TEMPORARY_FLUCTUATIONS")
    assert "TSRA" not in becoming.get("weather", [])
    assert becoming["visibility_m"] == 7000
    assert temporary["weather"] == ["TSRA"]
    assert temporary["visibility_m"] == 4000
    assert temporary["phenomenon_begin"].endswith("T18:00:00Z")
    assert temporary["phenomenon_end"].endswith("T22:00:00Z")


def test_prob30_tempo_uses_the_thirty_percent_indicator() -> None:
    tac = "TAF MZBZ 081200Z 0812/0912 12010KT 9999 PROB30 TEMPO 0818/0822 4000 TSRA="
    ir = parse_taf(tac, product="TAF")
    changes = ir["change_forecasts"]
    assert len(changes) == 1
    assert changes[0]["change_indicator"] == "PROBABILITY_30_TEMPORARY_FLUCTUATIONS"
    assert changes[0]["weather"] == ["TSRA"]
    assert ir.get("weather") in (None, [])


def test_prob30_without_tempo_is_not_folded_into_the_base_or_becmg() -> None:
    bare = parse_taf(_BARE, product="TAF")
    assert bare.get("weather") in (None, [])
    assert "change_forecasts" not in bare
    swallowed = parse_taf(_SWALLOWED, product="TAF")
    becoming = swallowed["change_forecasts"][0]
    assert becoming["change_indicator"] == "BECOMING"
    assert "TSRA" not in becoming.get("weather", [])
    assert len(swallowed["change_forecasts"]) == 1
    missing_period = parse_taf(
        "TAF MZBZ 081200Z 0812/0912 12010KT 9999 PROB40 TEMPO 4000 TSRA=",
        product="TAF",
    )
    assert missing_period.get("weather") in (None, [])
    assert "change_forecasts" not in missing_period


def test_plain_tempo_stays_a_temporary_fluctuation() -> None:
    tac = "TAF MZBZ 081200Z 0812/0912 12010KT 9999 TEMPO 0818/0822 4000 TSRA="
    ir = parse_taf(tac, product="TAF")
    assert ir["change_forecasts"][0]["change_indicator"] == "TEMPORARY_FLUCTUATIONS"


def test_probability_helper_edges() -> None:
    assert temporary_probability_indicator("30") == "PROBABILITY_30_TEMPORARY_FLUCTUATIONS"
    assert temporary_probability_indicator("40") == "PROBABILITY_40_TEMPORARY_FLUCTUATIONS"
    assert temporary_probability_indicator("50") is None
    assert temporary_probability_indicator("") is None
    assert probability_tempo_parts("PROB40 TEMPO 0818/0822 4000 TSRA") == (
        "PROBABILITY_40_TEMPORARY_FLUCTUATIONS",
        "TEMPO",
        "0818",
        "0822",
        "4000 TSRA",
    )
    assert probability_tempo_parts("PROB30 EMPO 0906/0909 5000 TSRA") is not None
    assert probability_tempo_parts("TEMPO 0818/0822 4000") is None
    assert probability_tempo_parts("PROB40 TEMPO 4000 TSRA") is None
    assert is_unqualified_probability("PROB30 4000 TSRA") is True
    assert is_unqualified_probability("PROB40 0818/0822 4000") is True
    assert is_unqualified_probability("PROB40 TEMPO 0818/0822 4000 TSRA") is False
    assert is_unqualified_probability("TEMPO 0818/0822 4000") is False
