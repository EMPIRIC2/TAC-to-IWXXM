"""TC-EVBRIDGE — library assets API (first-party list + rule preview)."""

from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi import HTTPException
from src.services.conversion_profiles_service import ConversionProfilesService
from tac2iwxxm.library_assets import list_first_party_library_assets


def _svc() -> ConversionProfilesService:
    return ConversionProfilesService(user_id=str(uuid4()))


def test_list_first_party_library_assets_projection() -> None:
    """First-party catalog projects to LibraryAssetOut."""
    svc = _svc()
    items = []
    for asset in list_first_party_library_assets():
        out = svc._first_party_library_out(asset.id)
        assert out is not None
        items.append(out)
    assert len(items) >= 5 * 2
    kinds = {i.kind for i in items}
    assert kinds == {
        "conversion",
        "tac_validation",
        "iwxxm_validation",
        "dissemination",
        "decoding",
    }


def test_preview_library_rule_wind_match() -> None:
    """AC11 preview resolves CV.WIND for a wind group."""
    svc = _svc()
    rule_id, rule_name = svc.preview_library_rule(
        "LIB.CONVERSION.ICAO_2025",
        "18012G20KT",
    )
    assert rule_id == "CV.WIND"
    assert rule_name


def test_preview_library_rule_unmatched_fail_closed() -> None:
    """AC11 unmatched group fails closed."""
    svc = _svc()
    with pytest.raises(HTTPException) as exc:
        svc.preview_library_rule("LIB.CONVERSION.ICAO_2025", "NOTAGROUPXYZ")
    assert exc.value.status_code == 400


def test_delete_first_party_library_forbidden() -> None:
    """AC4: cannot delete first-party defaults."""
    svc = _svc()
    with pytest.raises(HTTPException) as exc:
        svc.delete_library_asset("LIB.DECODING.US_FAA_NWS")
    assert exc.value.status_code == 403
