"""TC-EV-CND-002 — Code name dictionary tag validation.

[Corpus: product] [Corpus: tests]
"""

from __future__ import annotations

from tac_decoding.dictionary import (
    dictionary_entries,
    dictionary_facets,
    reload_dictionary_meta,
)

_REQUIRED_KEYS = ("id", "code", "meaning", "products", "countries", "wmo_amendment")


def test_dictionary_rows_have_required_keys_and_types() -> None:
    reload_dictionary_meta()
    rows = dictionary_entries()
    assert rows
    for row in rows:
        assert set(row) >= set(_REQUIRED_KEYS)
        assert isinstance(row["id"], str)
        assert row["id"]
        assert isinstance(row["code"], str)
        assert row["code"]
        assert isinstance(row["meaning"], str)
        assert isinstance(row["products"], list)
        assert all(isinstance(p, str) for p in row["products"])
        assert isinstance(row["countries"], list)
        assert all(isinstance(c, str) for c in row["countries"])
        amd = row["wmo_amendment"]
        assert amd is None or isinstance(amd, str)


def test_ts_seeded_tags() -> None:
    by_code = {row["code"]: row for row in dictionary_entries()}
    ts = by_code["TS"]
    assert "INTL" in ts["countries"]
    assert "METAR" in ts["products"]
    assert "SIGMET" in ts["products"]


def test_vaa_has_amendment_label() -> None:
    by_code = {row["code"]: row for row in dictionary_entries()}
    assert "Amd" in (by_code["VAA"]["wmo_amendment"] or "")


def test_facets_sorted_unique() -> None:
    facets = dictionary_facets()
    for key in ("products", "countries", "wmo_amendments"):
        values = facets[key]
        assert values == sorted(values)
        assert len(values) == len(set(values))
