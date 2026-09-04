"""TC-EV027-003 - decode residual matrix for official WMO TAC peers (#815)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from tac2iwxxm.decode import decode_tac

_FIXTURES = Path(__file__).resolve().parent / "fixtures"
if str(_FIXTURES) not in sys.path:
    sys.path.insert(0, str(_FIXTURES))

from wmo_decode_residual_allowlist import (  # noqa: E402
    EXPECTED_RESIDUALS,
    allowlisted_texts,
    allows_any_residual,
)
from wmo_official_tac_inventory import annex3_path, registered_peers  # noqa: E402


def test_tc_ev027_003_allowlist_entries_have_doc_intent_and_issue() -> None:
    for entry in EXPECTED_RESIDUALS:
        assert entry.doc_intent.strip()
        assert entry.issue.strip()
        assert entry.allow_any or (entry.residual_text and entry.residual_text.strip())


@pytest.mark.parametrize(
    "peer",
    registered_peers(),
    ids=[p.catalog_id or p.stem for p in registered_peers()],
)
def test_tc_ev027_003_decode_residuals_empty_or_allowlisted(peer) -> None:
    assert peer.product
    assert peer.catalog_id
    tac = annex3_path(peer).read_text(encoding="utf-8")
    result = decode_tac(tac, product=peer.product)
    if allows_any_residual(peer.catalog_id):
        # F9 G4 / ADR-025 - residuals permitted when allowlist entry cites intent + issue.
        return
    got = {r.text for r in result.residuals}
    allowed = allowlisted_texts(peer.catalog_id)
    unexpected = sorted(got - allowed)
    assert not unexpected, f"{peer.catalog_id}: unexpected residuals {unexpected!r} (allowlisted={sorted(allowed)!r})"
