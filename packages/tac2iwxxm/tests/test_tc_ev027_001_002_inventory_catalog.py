"""TC-EV027-001 / TC-EV027-002 — official WMO TAC inventory ↔ catalog ∪ gaps (#815)."""

from __future__ import annotations

import sys
from pathlib import Path

_FIXTURES = Path(__file__).resolve().parent / "fixtures"
if str(_FIXTURES) not in sys.path:
    sys.path.insert(0, str(_FIXTURES))

from wmo_official_tac_inventory import (  # noqa: E402
    OFFICIAL_TAC_PEERS,
    annex3_path,
    discover_pin_tac_stems,
    in_scope_pin_stems,
    registered_peers,
)


def test_tc_ev027_001_inventory_covers_in_scope_pin_stems() -> None:
    """Every in-scope pin TAC peer is listed as registered or deferred."""
    pin = in_scope_pin_stems(discover_pin_tac_stems())
    inventoried = {p.stem for p in OFFICIAL_TAC_PEERS}
    missing = pin - inventoried
    extra = inventoried - pin
    assert not missing, f"pin stems missing from inventory: {sorted(missing)}"
    assert not extra, f"inventory stems not on in-scope pin filter: {sorted(extra)}"


def test_tc_ev027_001_deferred_have_rationale() -> None:
    for peer in OFFICIAL_TAC_PEERS:
        if peer.disposition != "deferred":
            continue
        assert peer.deferral_reason and peer.deferral_reason.strip()
        assert peer.issue and peer.issue.strip()


def test_tc_ev027_002_registered_peers_have_annex3_mirrors() -> None:
    for peer in registered_peers():
        path = annex3_path(peer)
        assert path.is_file(), f"missing annex3 mirror for {peer.stem}: {path}"
        assert peer.catalog_id
        assert peer.product in {
            "METAR",
            "SPECI",
            "TAF",
            "SIGMET",
            "AIRMET",
            "VAA",
            "TCA",
        }


def test_tc_ev027_002_catalog_ids_unique() -> None:
    ids = [p.catalog_id for p in registered_peers()]
    assert len(ids) == len(set(ids))
