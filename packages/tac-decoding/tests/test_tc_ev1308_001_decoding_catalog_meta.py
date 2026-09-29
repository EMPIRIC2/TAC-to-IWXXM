"""TC-EV1308-001 — Decoding catalog additive metadata.

[Corpus: product §F9] [Corpus: tests] #1308
"""

from __future__ import annotations

from tac_decoding.catalog import (
    catalog_entries,
    count_issue_types,
    default_issue_type_for_token,
)


def test_catalog_entries_include_additive_keys() -> None:
    rows = catalog_entries()
    assert rows
    sample = rows[0]
    for key in (
        "issue_type",
        "severity",
        "source_url",
        "source_attribution",
        "source_access",
        "source_locator",
        "conform_note",
    ):
        assert key in sample


def test_ts_row_has_yaml_meta() -> None:
    by_id = {row["id"]: row for row in catalog_entries()}
    ts = by_id["TS"]
    assert ts["issue_type"] == "content"
    assert ts["severity"] == "info"
    assert ts["source_url"] is not None
    assert ts["source_url"].startswith("https://")
    assert ts["source_access"] == "public"
    assert ts["conform_note"]


def test_function_word_and_does_not_default_content() -> None:
    assert default_issue_type_for_token("AND") is None
    by_id = {row["id"]: row for row in catalog_entries()}
    assert by_id["AND"]["issue_type"] is None


def test_official_token_defaults_content_when_meta_omits_type() -> None:
    # ICE is official; not in catalog_meta.yaml seed → classifier default
    assert default_issue_type_for_token("ICE") == "content"
    by_id = {row["id"]: row for row in catalog_entries()}
    assert by_id["ICE"]["issue_type"] == "content"
    assert by_id["ICE"]["source_url"] is None


def test_count_issue_types_includes_content_and_null() -> None:
    counts = count_issue_types()
    assert counts.get("content", 0) > 0
    assert "other" not in counts or counts["other"] == 0
    # Function words remain null
    assert counts.get("null", 0) >= 1
