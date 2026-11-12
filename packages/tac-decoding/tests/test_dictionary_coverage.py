"""Coverage guards for tac_decoding.dictionary helpers.

[Corpus: tests]
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from tac_decoding import dictionary as dictionary_mod
from tac_decoding.dictionary import (
    _string_list,
    _token_fields_from_value,
    _tokens_dictionary_from_mapping,
    dictionary_facets,
    filter_dictionary_entries,
    reload_dictionary_meta,
)


def test_string_list_accepts_csv_and_list_and_dedupes() -> None:
    assert _string_list("a, b, a") == ["a", "b"]
    assert _string_list(["x", " ", 1, "y"]) == ["x", "y"]
    assert _string_list(None) == []
    assert _string_list(12) == []


def test_tokens_dictionary_from_mapping_guards() -> None:
    assert _tokens_dictionary_from_mapping(None) == {}
    assert _tokens_dictionary_from_mapping(["x"]) == {}
    assert _tokens_dictionary_from_mapping({"tokens": "bad"}) == {}
    assert _tokens_dictionary_from_mapping({"tokens": {"": {"products": ["METAR"]}}}) == {}
    assert _tokens_dictionary_from_mapping({"tokens": {"  ": {"products": ["METAR"]}}}) == {}
    assert _tokens_dictionary_from_mapping({"tokens": {"xx": "not-a-map"}}) == {}
    out = _tokens_dictionary_from_mapping(
        {
            "tokens": {
                "ab": {
                    "products": ["metar"],
                    "countries": ["ca"],
                    "wmo_amendment": " Amd 77 ",
                },
                "cd": {"wmo_amendment": None},
            }
        }
    )
    assert out["AB"]["products"] == ["METAR"]
    assert out["AB"]["countries"] == ["CA"]
    assert out["AB"]["wmo_amendment"] == "Amd 77"
    assert out["CD"]["wmo_amendment"] is None


def test_token_fields_skips_blank_amendment_string() -> None:
    assert _token_fields_from_value({"wmo_amendment": "  "}) == {}


def test_load_raw_catalog_meta_missing_and_bad_yaml(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing.yaml"
    monkeypatch.setattr(dictionary_mod, "_CATALOG_META_PATH", missing)
    assert dictionary_mod._load_raw_catalog_meta_doc() == {}

    bad = tmp_path / "bad.yaml"
    bad.write_text(": [", encoding="utf-8")
    monkeypatch.setattr(dictionary_mod, "_CATALOG_META_PATH", bad)
    assert dictionary_mod._load_raw_catalog_meta_doc() == {}

    empty = tmp_path / "empty.yaml"
    empty.write_text("", encoding="utf-8")
    monkeypatch.setattr(dictionary_mod, "_CATALOG_META_PATH", empty)
    assert dictionary_mod._load_raw_catalog_meta_doc() == {}


def test_reload_clears_caches(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    meta = tmp_path / "catalog_meta.yaml"
    meta.write_text(
        yaml.safe_dump(
            {
                "schema_version": 1,
                "tokens": {
                    "TS": {
                        "products": ["METAR"],
                        "countries": ["US"],
                        "wmo_amendment": "test-amd",
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(dictionary_mod, "_CATALOG_META_PATH", meta)
    reload_dictionary_meta()
    rows = filter_dictionary_entries(country="US", product="METAR", q="TS")
    assert any(row["code"] == "TS" for row in rows)
    facets = dictionary_facets(rows)
    assert "US" in facets["countries"]
    assert "test-amd" in facets["wmo_amendments"]
    # Restore packaged meta for later tests in the same session.
    monkeypatch.setattr(
        dictionary_mod,
        "_CATALOG_META_PATH",
        Path(dictionary_mod.__file__).resolve().parent / "data" / "catalog_meta.yaml",
    )
    reload_dictionary_meta()


def test_filter_rejects_non_matching_amendment_and_query() -> None:
    assert filter_dictionary_entries(wmo_amendment="no-such-amd") == []
    assert filter_dictionary_entries(q="zzzz-not-a-code") == []


def test_token_fields_products_only_without_amendment_key() -> None:
    fields = _token_fields_from_value({"products": ["taf"]})
    assert fields == {"products": ["TAF"]}


def test_tokens_mapping_skips_empty_field_maps() -> None:
    assert _tokens_dictionary_from_mapping({"tokens": {"ZZ": {"wmo_amendment": "   "}}}) == {}


def test_resolved_tags_override_without_defaults() -> None:
    products, countries, amd = dictionary_mod._resolved_tags(
        "NODEFAULT",
        {
            "products": ["SWXA"],
            "countries": ["CA"],
            "wmo_amendment": 12,
        },
    )
    assert products == ["SWXA"]
    assert countries == ["CA"]
    assert amd is None


def test_resolved_tags_partial_overrides_on_defaults() -> None:
    products, countries, amd = dictionary_mod._resolved_tags(
        "TS",
        {"products": ["METAR"]},
    )
    assert products == ["METAR"]
    assert "INTL" in countries
    assert amd == "WMO No. 306"

    products2, countries2, amd2 = dictionary_mod._resolved_tags(
        "TS",
        {"countries": ["CA"]},
    )
    assert "METAR" in products2
    assert countries2 == ["CA"]
    assert amd2 == "WMO No. 306"

    products3, countries3, amd3 = dictionary_mod._resolved_tags(
        "TS",
        {"wmo_amendment": "Amd 99"},
    )
    assert "METAR" in products3
    assert "INTL" in countries3
    assert amd3 == "Amd 99"


def test_facets_ignore_blank_and_non_string_amendment() -> None:
    facets = dictionary_facets(
        [
            {
                "products": [],
                "countries": [],
                "wmo_amendment": "   ",
            },
            {
                "products": ["METAR"],
                "countries": None,
                "wmo_amendment": 7,
            },
        ]
    )
    assert facets["products"] == ["METAR"]
    assert facets["wmo_amendments"] == []
