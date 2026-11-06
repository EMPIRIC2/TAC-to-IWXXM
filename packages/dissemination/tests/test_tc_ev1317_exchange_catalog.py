"""TC-EV1317-001 — dissemination catalog rows are package-owned and readable."""

from __future__ import annotations

import pytest
from dissemination.exchange_registry import known_exchange_profile_ids

from dissemination import exchange_catalog as mod


def test_wire_rows_have_public_summaries_and_aliases_point_at_them() -> None:
    rows = {row["id"]: row for row in mod.catalog_entries()}
    assert set(rows) == set(known_exchange_profile_ids())
    wire = rows["GLOBAL_AFS"]
    assert wire["issue_type"] == "profile"
    assert wire["source_access"] == "public"
    assert wire["source_url"].startswith("https://")
    assert "COLLECT" in wire["summary"]
    assert "alias" not in wire["tags"]
    alias = rows["global_afs"]
    assert alias["issue_type"] == "profile"
    assert "GLOBAL_AFS" in alias["summary"]
    assert alias["conform_note"] == "Alias of GLOBAL_AFS."
    assert alias["source_url"] == wire["source_url"]
    for row in rows.values():
        text = f"{row['summary']} {row['conform_note']} {row['source_attribution']}"
        assert "Exchange / dissemination profile" not in text
        assert "EV-" not in text
        assert "docs/" not in text


def test_regional_rows_cite_their_public_source() -> None:
    rows = {row["id"]: row for row in mod.catalog_entries()}
    assert "ROBEX" in rows["APAC_ROBEX"]["summary"]
    assert "RODEX" in rows["EUR_RODEX"]["summary"]
    assert "Africa-Indian Ocean" in rows["AFI"]["summary"]
    assert "region-specific handbook is not applied" in rows["CAR_SAM"]["summary"]


def test_missing_metadata_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(mod, "known_exchange_profile_ids", lambda: frozenset({"NO_SUCH"}))
    with pytest.raises(KeyError, match="NO_SUCH"):
        mod.catalog_entries()
