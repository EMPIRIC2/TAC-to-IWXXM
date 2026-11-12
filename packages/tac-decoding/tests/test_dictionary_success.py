"""TC-EV-CND-003 — Code name dictionary filter success paths.

[Corpus: product] [Corpus: tests]
"""

from __future__ import annotations

from tac_decoding.dictionary import dictionary_entries, filter_dictionary_entries


def test_search_thunder_finds_ts() -> None:
    rows = filter_dictionary_entries(q="thunder")
    assert any(row["code"] == "TS" for row in rows)


def test_product_metar_filters() -> None:
    rows = filter_dictionary_entries(product="METAR")
    assert rows
    assert all("METAR" in row["products"] for row in rows)


def test_country_intl_filters() -> None:
    rows = filter_dictionary_entries(country="INTL")
    assert rows
    assert all("INTL" in row["countries"] for row in rows)


def test_amendment_amd77_finds_advisory_codes() -> None:
    rows = filter_dictionary_entries(wmo_amendment="Amd 77")
    codes = {row["code"] for row in rows}
    assert "VAA" in codes or "TCA" in codes


def test_combined_product_and_query() -> None:
    rows = filter_dictionary_entries(product="SIGMET", q="fir")
    assert any(row["code"] == "FIR" for row in rows)


def test_dictionary_entries_include_fir() -> None:
    codes = {row["code"] for row in dictionary_entries()}
    assert "FIR" in codes
    assert len(codes) > 20
