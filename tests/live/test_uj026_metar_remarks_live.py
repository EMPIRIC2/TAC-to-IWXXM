"""Live UJ-026 / #667 - annex3 REMARKS_EXCLUDED + iwxxm_us humanReadableText.

Requires LIVE_API_URL (or STAGING_API_URL) and ADMIN_EMAIL / ADMIN_PASSWORD.
"""

from __future__ import annotations

import os

import httpx
import pytest
from tests.live_fixtures import login_with_backoff

pytestmark = [pytest.mark.live, pytest.mark.live_api]

TAC_RMK = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005 RMK AO2 SLP176="
TAC_FREE = "METAR KJFK 231751Z 18012KT 10SM CLR 15/07 A3005 RMK AO2 WND DATA ESTMD="


def _live_api_base() -> str | None:
    return os.environ.get("LIVE_API_URL") or os.environ.get("STAGING_API_URL")


@pytest.fixture(scope="module")
def live_api() -> str:
    base = _live_api_base()
    if not base:
        pytest.skip("LIVE_API_URL / STAGING_API_URL not set")
    return base.rstrip("/")


@pytest.fixture(scope="module")
def live_headers(live_api: str) -> dict[str, str]:
    email = os.environ.get("ADMIN_EMAIL")
    password = os.environ.get("ADMIN_PASSWORD")
    if not email or not password:
        pytest.skip("ADMIN_EMAIL / ADMIN_PASSWORD required for live convert")
    token = login_with_backoff(live_api, email, password)
    return {"Authorization": f"Bearer {token}"}


def _convert(live_api: str, headers: dict[str, str], *, tac: str, profile: str) -> dict:
    with httpx.Client(timeout=120.0) as client:
        resp = client.post(
            f"{live_api}/api/v1/convert",
            headers=headers,
            data={
                "manual_text": tac,
                "product": "METAR",
                "profile": profile,
                "iwxxm_version": "2025-2",
                "lint": "false",
            },
        )
    assert resp.status_code == 200, resp.text[:500]
    return resp.json()


def test_uj026_live_annex3_remarks_excluded(
    live_api: str, live_headers: dict[str, str]
) -> None:
    body = _convert(live_api, live_headers, tac=TAC_RMK, profile="annex3")
    codes = [i.get("code") for i in (body.get("issues") or [])]
    assert "REMARKS_EXCLUDED" in codes, f"issues={body.get('issues')!r}"
    xml = (body.get("results") or [{}])[0].get("content") or ""
    assert "iwxxm-us:Addendum" not in xml


def test_uj026_live_iwxxm_us_human_readable(
    live_api: str, live_headers: dict[str, str]
) -> None:
    body = _convert(live_api, live_headers, tac=TAC_FREE, profile="iwxxm_us")
    codes = [i.get("code") for i in (body.get("issues") or [])]
    assert "REMARKS_EXCLUDED" not in codes
    xml = (body.get("results") or [{}])[0].get("content") or ""
    assert "iwxxm-us:humanReadableText" in xml
    assert "WND DATA ESTMD" in xml
