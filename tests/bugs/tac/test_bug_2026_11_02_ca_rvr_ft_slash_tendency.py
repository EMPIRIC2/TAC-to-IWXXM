"""BUG-2026-11-02 — Canadian RVR ``FT/N`` must retain tendency on convert.

Lint already accepts ``R07/3000V4500FT/N`` (slash before U/D/N). Convert regex
previously only allowed tendency *before* ``FT``, so MANOBS ``FT/N`` parsed
metres but ``tendency`` was lost (None).

[Corpus: product §F6] [Corpus: product §F15] [Corpus: tests]
"""

from __future__ import annotations

from tac2iwxxm.slot_builders.metar_speci import parse_metar_speci

_CA_VAR = "METAR CYUL 151800Z 18012KT 1/2SM R07/3000V4500FT/N FG BKN002 10/10 A2990="
_CA_SINGLE = "METAR CYUL 151800Z 18012KT 1/2SM R07/3000FT/N FG BKN002 10/10 A2990="
_ICAO_VAR = "METAR KJFK 151800Z 18012KT 0800 R04/M0200V0600N FG BKN002 10/10 Q1013="


def test_bug_2026_11_02_icao_variable_rvr_tendency_still_works() -> None:
    rvr = parse_metar_speci(_ICAO_VAR, product="METAR")["rvr"]
    assert rvr["tendency"] == "NO_CHANGE"


def test_bug_2026_11_02_ca_variable_rvr_ft_slash_n_keeps_tendency() -> None:
    rvr = parse_metar_speci(_CA_VAR, product="METAR")["rvr"]
    assert rvr["variable"] is True
    assert rvr["min_m"] == 914
    assert rvr["max_m"] == 1372
    assert rvr["tendency"] == "NO_CHANGE"


def test_bug_2026_11_02_ca_single_rvr_ft_slash_n_keeps_tendency() -> None:
    rvr = parse_metar_speci(_CA_SINGLE, product="METAR")["rvr"]
    assert rvr["mean_m"] == 914
    assert rvr["tendency"] == "NO_CHANGE"
