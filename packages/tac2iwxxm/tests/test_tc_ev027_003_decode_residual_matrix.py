"""TC-EV027-003 — decode residual matrix for official WMO TAC peers (#815)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from tac2iwxxm.decode import decode_tac

_FIXTURES = Path(__file__).resolve().parent / "fixtures"
if str(_FIXTURES) not in sys.path:
    sys.path.insert(0, str(_FIXTURES))

from wmo_decode_residual_allowlist import allowlisted_texts  # noqa: E402
from wmo_official_tac_inventory import annex3_path, registered_peers  # noqa: E402


@pytest.mark.parametrize(
    "peer",
    registered_peers(),
    ids=[p.catalog_id or p.stem for p in registered_peers()],
)
def test_tc_ev027_003_decode_residuals_empty_or_allowlisted(peer) -> None:
    assert peer.product and peer.catalog_id
    tac = annex3_path(peer).read_text(encoding="utf-8")
    result = decode_tac(tac, product=peer.product)
    got = {r.text for r in result.residuals}
    allowed = allowlisted_texts(peer.catalog_id)
    unexpected = sorted(got - allowed)
    assert not unexpected, f"{peer.catalog_id}: unexpected residuals {unexpected!r} (allowlisted={sorted(allowed)!r})"
