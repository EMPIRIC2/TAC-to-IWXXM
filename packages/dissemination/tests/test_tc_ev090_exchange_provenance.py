"""TC-EV090-001 / TC-EV090-005 — exchange catalog provenance + EV-086 regression.

[Corpus: product §F36] [Corpus: domain-profiles] [Corpus: tests]
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from dissemination.exchange_registry import known_exchange_profile_ids

_REPO = Path(__file__).resolve().parents[3]
_CATALOG = _REPO / "docs" / "domain" / "profiles" / "catalog.yaml"
_EXCHANGE_DIR = _REPO / "docs" / "domain" / "profiles" / "exchange"

_EXCHANGE_IDS = (
    "GLOBAL_AFS",
    "APAC_ROBEX",
    "EUR_RODEX",
    "AFI",
    "CAR_SAM",
)

_OPMET_GUIDELINES_FRAGMENT = "OPMET-IWXXM-Exchange-Guidelines-5th"


def _profiles() -> list[dict]:
    data = yaml.safe_load(_CATALOG.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    profiles = data.get("profiles")
    assert isinstance(profiles, list)
    return [p for p in profiles if isinstance(p, dict)]


def _exchange_row(profile_id: str) -> dict:
    for row in _profiles():
        if row.get("id") == profile_id and row.get("kind") == "exchange":
            return row
    raise AssertionError(f"missing exchange catalog row: {profile_id}")


@pytest.mark.parametrize("profile_id", _EXCHANGE_IDS)
def test_tc_ev090_001_catalog_provenance_for_exchange_stubs(profile_id: str) -> None:
    """TC-EV090-001 — each exchange id has mining notes and/or OPMET Guidelines source."""
    row = _exchange_row(profile_id)
    stub = row.get("stub")
    assert isinstance(stub, str)
    assert stub.endswith(".md")
    stub_path = _EXCHANGE_DIR / Path(stub).name
    assert stub_path.is_file(), f"missing stub: {stub_path}"

    notes = row.get("mining_notes") or []
    sources = row.get("sources") or []
    assert notes or sources, f"{profile_id}: need mining_notes or sources"

    joined_notes = " ".join(str(n) for n in notes)
    source_urls = " ".join(str(s.get("url", "")) for s in sources if isinstance(s, dict))
    provenance_blob = f"{joined_notes}\n{source_urls}\n{stub_path.read_text(encoding='utf-8')}"

    if profile_id == "APAC_ROBEX":
        assert "icao-apac-iwxxm-faqs" in provenance_blob or "APAC" in provenance_blob
        gaps = row.get("gaps") or []
        assert any("ROBEX handbook" in str(g) for g in gaps), (
            "APAC_ROBEX must keep ROBEX handbook durable-URL gap explicit until pinned"
        )
    else:
        assert (
            _OPMET_GUIDELINES_FRAGMENT in provenance_blob
            or "OPMET" in provenance_blob
            or "Guidlines-for-the-Implementation-of-OPMET" in provenance_blob
        ), f"{profile_id}: expected OPMET Guidelines promote"


def test_tc_ev090_001_registry_matches_catalog_exchange_ids() -> None:
    """Catalog exchange wire ids are registered for packaging."""
    ids = known_exchange_profile_ids()
    for wire_id in _EXCHANGE_IDS:
        assert wire_id in ids, f"registry missing {wire_id}"


def test_tc_ev090_005_ev086_packaging_regression() -> None:
    """TC-EV090-005 — regional stubs still resolve (EV-086 regression)."""
    ids = known_exchange_profile_ids()
    for wire_id in ("EUR_RODEX", "AFI", "CAR_SAM", "APAC_ROBEX", "GLOBAL_AFS"):
        assert wire_id in ids
